"""PREREG v2 scorer: one corpus, the v2 metric set, optional family in/out.

    python -m scoreboard.run_v2 --meta <sidecar.meta.json> [--lang A|B] [--family L|C|G|X]
                                [--ranges results_m4_phase1_board.json] [--out results_<prefix>.txt]
    python -m scoreboard.run_v2 --voynich [--lang A|B] [--ranges ...] [--out ...]

What it does (PREREG-v2.md, frozen; this file is hashed in scoreboard/PREREG-v2.sha256):
  * the seven FROZEN v1 bands come from scoreboard/score.py loaded by path and called
    exactly as g0_score_filed.py / m4_phase1_board.py do: score.score_corpus(name, words,
    lines) with the g0 band checks copied verbatim;
  * the v2 extras come from scoreboard/metrics_new.py (extra_signatures, information_profile,
    lexicon_growth, slot_structure, heldout_bakeoff), same keys as m4_phase1_board.py so the
    row is comparable with results_m4_phase1_board.json, plus `types_25k` (word types in
    the first 25,000 tokens, scored jointly with x_edge_mi_word per PREREG-v2 §4);
  * corpus subsetting by Currier language uses the sidecar page field "lang" (or the IVTFF
    $L via vparse for --voynich); pages whose lang is not the requested letter are dropped;
  * every non-Voynich corpus is cut to its first 25,000 tokens (whole lines) as in m4;
    Voynich is scored whole (profile metrics cap at 25k inside score.py, as filed);
  * with --ranges, Voynich-style in/out is printed per family (L, C, G and X when the file
    carries an "X" range) with the 10 %-of-width extension, the file's tight flags and
    its no-weight list.  Weight classes follow PREREG-v2 §3-§4 and are printed per row.
Writes the table to --out (default stdout only) and the row as JSON next to it.
Does not touch scoreboard.json, results_m4_*, or any PREREG file.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

_spec = importlib.util.spec_from_file_location("scoreboard_score", HERE / "score.py")
score = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(score)

from scoreboard import metrics_new as M  # noqa: E402

SEED = 20261017
N_SAMPLE = 25000
N_SHUFFLES = 5
EXTEND = 0.10

V1_KEYS = ["h2", "sd_len", "jsd_first_fg", "p_init_enrich", "m_final_enrich",
           "cross_excess_eva", "redup_pct"]
# (key, weight class, description).  WEIGHTED = carries weight in the v2 family rule
# (subject to the overlap rule); REPORT = reported, no content weight (PREREG-v2 §4).
NEW_KEYS = [
    ("x_edge_mi_word", "WEIGHTED", "edge MI last glyph -> next first glyph, shuffle-corrected (bits)"),
    ("types_25k", "WEIGHTED*", "word types in first 25k tokens (joint with x_edge_mi_word)"),
    ("x_position_entropy", "WEIGHTED", "glyph position entropy (bits, max 2.32)"),
    ("x_ltr_minus_rtl", "WEIGHTED", "bits/char ltr minus rtl (order-3 char model, held out)"),
    ("x_moran_I", "WEIGHTED", "Moran's I word length lag 1"),
    ("lex_beta", "WEIGHTED", "Heaps beta (all)"),
    ("lex_rate_late_early", "WEIGHTED", "new-type rate last20% / first20%"),
    ("lex_edit1_excess", "WEIGHTED", "edit-1 share of new types, recent-200 minus far"),
    ("slot_occupancy_pc", "WEIGHTED", "slot occupancy prefix x core"),
    ("slot_table_likeness", "WEIGHTED", "slot table-likeness, token-weighted"),
    ("slot_core_crowding", "WEIGHTED", "core edit-1 neighbour share"),
    ("info_mi_adjacent", "WEIGHTED", "MI adjacent words, boundaries given (bits)"),
    ("info_samecol_minus_othercol", "WEIGHTED", "MI prev-line same column minus other column"),
    ("bake_char3_minus_unigram", "WEIGHTED", "bake-off: char-3 WB minus unigram-GT bits/token"),
    ("x_hapax_10k", "REPORT", "hapax share at 10k tokens (no weight, audit item 13)"),
    ("info_mi_page", "REPORT", "page-level MI same_page_far (no content weight after n3)"),
    ("info_bpe_adjacent", "REPORT", "MI adjacent after BPE re-segmentation (M6 premise check vs 0.851 null)"),
]
NEW_NUMERIC = [k for k, _, _ in NEW_KEYS]


def bands(row):
    """Frozen v1 bands, copied verbatim from g0_score_filed.py."""
    return {
        "h2": 1.98 <= row["h2"] <= 2.28,
        "sd_len": 1.41 <= row["sd_len"] <= 2.11,
        "jsd_first_fg": row["jsd_first_fg"] >= 0.10,
        "p_init_enrich": row["p_init_enrich"] >= 8,
        "m_final_enrich": row["m_final_enrich"] >= 8,
        "cross_excess_eva": row["cross_excess_eva"] >= 0.09,
        "redup_pct": 0.4 <= row["redup_pct"] <= 1.8,
    }


# ---------------------------------------------------------------------------
# corpora
# ---------------------------------------------------------------------------
def load_meta(path):
    """m4's tolerant loader: page key 'id' or 'page'; keeps 'lang'."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for p in d["pages"]:
        pid = p.get("id", p.get("page", len(out)))
        out.append(dict(id=str(pid), section=str(p.get("section", "?")),
                        hand=str(p.get("hand", "?")), lang=str(p.get("lang", "?")),
                        quire=p.get("quire"),
                        lines=[[str(t) for t in ln] for ln in p["lines"] if ln]))
    return d.get("name"), [p for p in out if p["lines"]]


def subsample(pages, n):
    out, k = [], 0
    for p in pages:
        q = dict(p, lines=[])
        for ln in p["lines"]:
            if k >= n:
                break
            q["lines"].append(ln)
            k += len(ln)
        if q["lines"]:
            out.append(q)
        if k >= n:
            break
    return out


def family_of(name):
    """PREREG-v2 §8 filename-prefix rule."""
    if name.startswith("nomen_"):
        return "C"
    if name.startswith(("markov1", "rugg", "timm", "schwartz", "c2", "n2hab")):
        return "G"
    if name.startswith("gib_"):
        return "X"
    return "-"


def subset_lang(pages, lang):
    if not lang:
        return pages
    keep = [p for p in pages if str(p.get("lang", "?")) == lang]
    return keep


# ---------------------------------------------------------------------------
# scoring
# ---------------------------------------------------------------------------
def fin(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def score_one(name, pages, log):
    words = M.flat_tokens(pages)
    lines = [ln for p in pages for ln in p["lines"]]
    row = {"name": name, "tokens": len(words), "types": len(set(words)),
           "pages": len(pages), "lines": len(lines), "errors": {}}
    row["types_25k"] = len(set(words[:N_SAMPLE]))

    def step(label, fn):
        t = time.time()
        try:
            fn()
        except Exception as e:  # small corpora make several metrics undefined
            row["errors"][label] = f"{type(e).__name__}: {e}"
        log(f"    {label} {time.time() - t:.1f}s" + (f"  [{row['errors'][label]}]" if label in row["errors"] else ""))

    def v1():
        r = score.score_corpus(name, words, lines)
        ch = bands(r)
        for k in V1_KEYS:
            row[k] = r[k]
        row["v1_pass"] = all(ch.values())
        row["v1_missed"] = [k for k, ok in ch.items() if not ok]
        row["v1_full"] = r

    def extra():
        ex = M.extra_signatures(pages)
        row["x_edge_mi_word"] = ex["edge_mi_word"]
        row["x_hapax_10k"] = ex["hapax_share_10k"]
        row["x_moran_I"] = ex["moran_I_wordlen_lag1"]
        row["x_position_entropy"] = ex["position_entropy_bits"]
        row["x_ltr_minus_rtl"] = ex["directional_asymmetry_ltr_minus_rtl"]

    def info():
        inf = M.information_profile(pages)
        g = inf["word_boundaries_given"]
        row["info_mi_adjacent"] = g["adjacent"]["mi"]
        row["info_mi_page"] = g["same_page_far"]["mi"]
        row["info_samecol_minus_othercol"] = g["prev_line_same_col"]["mi"] - g["prev_line_other_col"]["mi"]
        row["info_bpe_adjacent"] = inf["bpe_resegmented"]["adjacent"]["mi"]

    def lex():
        a = M.lexicon_growth(pages, n_shuffles=N_SHUFFLES)["all"]
        row["lex_beta"] = a["beta"]
        row["lex_rate_late_early"] = a["rate_ratio_last20_first20"]
        row["lex_edit1_excess"] = a["edit1_share_recent200"] - a["edit1_share_far"]

    def slot():
        s = M.slot_structure(pages)[0]["all_types"]
        row["slot_occupancy_pc"] = s["occupancy_prefix_core"]
        row["slot_table_likeness"] = s["table_likeness_weighted"]
        row["slot_core_crowding"] = s["core_edit1_share"]

    def bake():
        ov = M.heldout_bakeoff(pages)["overall"]
        row["bake_winner"] = min(ov, key=lambda m: ov[m]["bits_per_token"])
        row["bake_char3_minus_unigram"] = ov["markov3"]["bits_per_token"] - ov["unigram_gt"]["bits_per_token"]
        row["bake_bits"] = {m: ov[m]["bits_per_token"] for m in ov}

    for label, fn in (("v1", v1), ("extra", extra), ("info", info), ("lex", lex),
                      ("slot", slot), ("bake", bake)):
        step(label, fn)
    for k in V1_KEYS + NEW_NUMERIC:
        row.setdefault(k, None)
    row.setdefault("bake_winner", None)
    return row


# ---------------------------------------------------------------------------
# ranges / in-out
# ---------------------------------------------------------------------------
def in_out(v, rg):
    if v is None or not rg:
        return "NA"
    w = rg["max"] - rg["min"]
    return "IN" if rg["min"] - EXTEND * w <= v <= rg["max"] + EXTEND * w else "OUT"


def fmt(v, d=4):
    if v is None:
        return "nan"
    if isinstance(v, bool):
        return "PASS" if v else "FAIL"
    if isinstance(v, (list, tuple)):
        return ",".join(v) if v else "-"
    if isinstance(v, str):
        return v
    return f"{v:.{d}f}"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--meta", help="sidecar .meta.json (PREREG-v2 §8 format)")
    src.add_argument("--voynich", action="store_true", help="ZL3b EVA paragraph text via vparse")
    ap.add_argument("--lang", choices=["A", "B"], help="Currier language subset (page field 'lang' / IVTFF $L)")
    ap.add_argument("--family", choices=list("LCGX"), help="override the filename-prefix family")
    ap.add_argument("--name", help="override the corpus name")
    ap.add_argument("--ranges", type=Path, help="results_m4_phase1_board.json-style ranges file")
    ap.add_argument("--n-sample", type=int, default=N_SAMPLE, help="token cap for non-Voynich corpora")
    ap.add_argument("--out", type=Path, help="write the table here (and the row as <out>.json)")
    args = ap.parse_args(argv)

    lines_out = []

    def log(s=""):
        print(s, flush=True)
        lines_out.append(s)

    if args.voynich:
        pages = M.voynich_pages("eva")
        name = "voynich" + (f"_{args.lang}" if args.lang else "_all")
        fam = "V"
        note = "ZL3b EVA paragraphs (vparse), whole"
        src_desc = str(M.vparse.DATA)
    else:
        mname, pages = load_meta(args.meta)
        name = mname or Path(args.meta).name.replace(".meta.json", "")
        fam = family_of(name)
        note = f"{args.meta}; {len(M.flat_tokens(pages))} tokens full"
        src_desc = str(args.meta)
    if args.name:
        name = args.name
    if args.family:
        fam = args.family
    n_before = len(pages)
    pages = subset_lang(pages, args.lang)
    if args.lang:
        name = name if args.voynich else f"{name}_{args.lang}"
        note += f"; lang={args.lang}: {len(pages)}/{n_before} pages"
    if not pages:
        raise SystemExit(f"no pages left after lang subset ({args.lang}); the sidecar carries no 'lang' field?")
    if not args.voynich:
        pages = subsample(pages, args.n_sample)

    log(f"# PREREG-v2 score: {name}  family={fam}  run={datetime.now().strftime('%Y-%m-%d %H:%M')} (system clock)  seed={SEED}")
    log(f"# source: {src_desc}")
    log(f"# {note}")
    log("# v1 bands: scoreboard/score.py via path + g0 band checks; extras: scoreboard/metrics_new.py; "
        f"sample cap {args.n_sample} (non-Voynich)")
    toks = M.flat_tokens(pages)
    log(f"# pages={len(pages)} lines={sum(len(p['lines']) for p in pages)} tokens={len(toks)} types={len(set(toks))} "
        f"sections={sorted({p['section'] for p in pages})[:8]} hands={len({p['hand'] for p in pages})} "
        f"langs={sorted({str(p.get('lang')) for p in pages})}")
    log()
    row = score_one(name, pages, log)
    row["family"], row["note"], row["lang"] = fam, note, args.lang
    log()

    ranges = tight = noweight = None
    fams = []
    if args.ranges:
        R = json.loads(args.ranges.read_text(encoding="utf-8"))
        ranges, tight, noweight = R["ranges"], R.get("tight", {}), set(R.get("no_weight", []))
        # An "X" range counts as the gibberish family only when the file says so: in
        # results_m4_phase1_board.json "X" means "other, no family" (PREREG-v2 §8).
        x_ok = R.get("x_family") == "gibberish"
        fams = ["L", "C", "G"] + (["X"] if x_ok and any("X" in ranges.get(k, {}) for k in ranges) else [])
        if "types_25k" not in ranges and R.get("rows"):
            # m4 rows carry 'types' over the first 25k tokens for every non-Voynich corpus
            ranges["types_25k"] = {}
            for f in fams:
                vals = [r["types"] for r in R["rows"] if r.get("family") == f and r.get("types")
                        and r.get("tokens") and r["tokens"] >= args.n_sample]
                if vals:
                    ranges["types_25k"][f] = dict(min=min(vals), max=max(vals), n=len(vals))
        log(f"# ranges: {args.ranges} (run {R.get('run')}, extend {R.get('extend', EXTEND)}); families {fams}; "
            "X range present" if "X" in fams else f"# ranges: {args.ranges} (run {R.get('run')}); X range absent -> X printed NA")

    log("=== v1 seven bands (frozen; PREREG v1 thresholds) ===")
    log(f"{'band':20} {'value':>10} {'band':>14} {'ok':>4}" + ("".join(f" {f:>4}" for f in fams)))
    bdesc = {"h2": "1.98-2.28", "sd_len": "1.41-2.11", "jsd_first_fg": ">=0.10", "p_init_enrich": ">=x8",
             "m_final_enrich": ">=x8", "cross_excess_eva": ">=+0.09", "redup_pct": "0.4-1.8%"}
    ch = bands(row["v1_full"]) if row.get("v1_full") else {}
    io = {}
    for k in V1_KEYS:
        v = fin(row.get(k))
        cells = ""
        if ranges:
            io[k] = {f: in_out(v, ranges.get(k, {}).get(f)) for f in fams}
            cells = "".join(f" {io[k][f]:>4}" for f in fams)
        log(f"{k:20} {fmt(v):>10} {bdesc[k]:>14} {('ok' if ch.get(k) else ('--' if k in ch else 'na')):>4}{cells}")
    log(f"v1 joint: {fmt(row.get('v1_pass'))}  missed: {fmt(row.get('v1_missed'))}")
    log()
    log("=== v2 extras (metrics_new) ===")
    log(f"{'metric':28} {'value':>10} {'class':>10}" + ("".join(f" {f:>4}" for f in fams)) + ("  tightLCG ovl" if ranges else ""))
    for k, cls, _ in NEW_KEYS:
        v = fin(row.get(k))
        cells = ""
        if ranges:
            io[k] = {f: in_out(v, ranges.get(k, {}).get(f)) for f in fams}
            tg = "".join("t" if tight.get(k, {}).get(f) else "." for f in "LCG")
            ov = "yes" if k in noweight else "no"
            cells = "".join(f" {io[k][f]:>4}" for f in fams) + f"  {tg:>8} {ov:>3}"
        log(f"{k:28} {fmt(v):>10} {cls:>10}{cells}")
    log(f"bake_winner: {row.get('bake_winner')}  bake bits: " +
        (" ".join(f"{m}={b:.3f}" for m, b in row["bake_bits"].items()) if row.get("bake_bits") else "nan"))
    log()
    if ranges:
        weighted = [k for k in V1_KEYS + NEW_NUMERIC
                    if k not in noweight and dict((a, b) for a, b, _ in NEW_KEYS).get(k, "WEIGHTED") != "REPORT"]
        log("=== per-family in/out (weighted metrics = v1 bands + WEIGHTED extras, minus the ranges file's no-weight list) ===")
        row["in_out"] = {}
        for f in fams:
            outs = [k for k in weighted if io.get(k, {}).get(f) == "OUT"]
            ins = [k for k in weighted if io.get(k, {}).get(f) == "IN"]
            na = [k for k in weighted if io.get(k, {}).get(f) == "NA"]
            outs_tight = [k for k in outs if tight.get(k, {}).get(f)]
            row["in_out"][f] = dict(ins=len(ins), outs=len(outs), na=len(na), out_metrics=outs, out_tight=outs_tight)
            log(f"  {f}: in={len(ins):2} out={len(outs):2} na={len(na):2}  out: {', '.join(outs) or '-'}  | tight-outs ({len(outs_tight)}): {', '.join(outs_tight) or '-'}")
        log(f"  weighted metrics ({len(weighted)}): {', '.join(weighted)}")
        log("  (kill = >=3 weighted outs on tight ranges; favoured = fewest outs by >=2; both need the A/B rule of PREREG-v2 §6)")
        log()
    if row["errors"]:
        log(f"errors: {json.dumps(row['errors'])}")
    prov = {p: hashlib.sha256((HERE / p).read_bytes()).hexdigest()[:16]
            for p in ("score.py", "metrics_new.py", "run_v2.py")}
    log(f"provenance sha256[:16]: {prov}")

    if args.out:
        args.out.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

        def clean(o):
            if isinstance(o, dict):
                return {str(k): clean(v) for k, v in o.items()}
            if isinstance(o, (list, tuple)):
                return [clean(v) for v in o]
            if isinstance(o, float) and not math.isfinite(o):
                return None
            if isinstance(o, (bool, int, float, str)) or o is None:
                return o
            return str(o)
        js = args.out.with_suffix(".json")
        js.write_text(json.dumps(clean(dict(row=row, seed=SEED, provenance=prov,
                                            ranges_file=str(args.ranges) if args.ranges else None)),
                                 indent=1), encoding="utf-8")
        print(f"wrote {args.out} and {js}", flush=True)


if __name__ == "__main__":
    main()
