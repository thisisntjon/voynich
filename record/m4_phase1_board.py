"""M4: Phase 1 joint family-discrimination board (PREREG-v2-DRAFT decision rule).

Every corpus is scored by
  (i)  the FROZEN v1 seven-band board, scoreboard/score.py loaded by path and called
       exactly as g0_score_filed.py does (score.score_corpus(name, words, lines) with the
       g0 band checks copied verbatim); and
  (ii) the five metric families of scoreboard/metrics_new.py (lexicon growth, slot
       structure, information profile, held-out bake-off, extra signatures).

Corpora (families):  V = Voynich ZL3b EVA paragraphs (all, Currier A pages, Currier B pages)
  L = natural languages: the six corpora.CONTROLS + corpora_ext.NATURAL
  C = nomen_* synthetic nomenclators
  G = generators: markov1, rugg_grille, timm_schinner*, schwartz_reuse, c2_best
  X = other (naibbe_like, latin_merged, lull table, constructed texts); reported, no range.
Every non-Voynich corpus is cut to its first 25,000 tokens (whole lines, corpus order) before
BOTH (i) and (ii); Voynich is scored whole (34,857 tokens; v1 profile metrics cap at 25k
internally, as filed).  Flat natural-language controls are wrapped to 8 tokens/line,
20 lines/page; page section = the '## ' marker in force for most of the page's tokens, else
4 contiguous blocks.  Seed 20261017.  Lexicon-growth page-shuffle null uses 5 shuffles
(the null is not a board column).

Decision rule (PREREG-v2-DRAFT): for each family F and metric, Voynich is IN if it lies in
[min - 0.1*w, max + 0.1*w] of F's controls (w = max - min), else OUT.  A metric whose L, C
and G ranges mutually overlap (non-empty triple intersection) carries no weight.  "Tight" =
range width < half the spread over all corpora (kill-rule precondition).

Writes results_m4_phase1_board.txt and results_m4_phase1_board.json.  Does not touch
scoreboard/scoreboard.json or any PREREG file.
"""
import glob
import importlib.util
import json
import math
import sys
import time
import traceback
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

spec = importlib.util.spec_from_file_location(
    "scoreboard_score", ROOT / "scoreboard" / "score.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)

import corpora  # noqa: E402
import corpora_ext  # noqa: E402
from scoreboard import metrics_new as M  # noqa: E402

SEED = 20261017
N_SAMPLE = 25000
N_SHUFFLES = 5
OUT = ROOT / "results_m4_phase1_board.txt"
OUTJ = ROOT / "results_m4_phase1_board.json"
EXTEND = 0.10
log = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


# ---------------------------------------------------------------------------
# frozen v1 bands, copied verbatim from g0_score_filed.py
# ---------------------------------------------------------------------------
def bands(row):
    checks = {
        "h2": 1.98 <= row["h2"] <= 2.28,
        "sd_len": 1.41 <= row["sd_len"] <= 2.11,
        "jsd_first_fg": row["jsd_first_fg"] >= 0.10,
        "p_init_enrich": row["p_init_enrich"] >= 8,
        "m_final_enrich": row["m_final_enrich"] >= 8,
        "cross_excess_eva": row["cross_excess_eva"] >= 0.09,
        "redup_pct": 0.4 <= row["redup_pct"] <= 1.8,
    }
    return checks


# ---------------------------------------------------------------------------
# corpus construction
# ---------------------------------------------------------------------------
def subsample(pages, n):
    """First n tokens in corpus order (whole lines)."""
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


def wrap_labelled(tokens, labels, line_len=8, page_len=20, hand="ctrl"):
    """Wrap a flat token stream with a per-token section label into 8x20 pages.
    Page section = most common label among the page's tokens; if only one label exists
    in the stream, 4 contiguous blocks s1..s4 instead."""
    lines = [tokens[i:i + line_len] for i in range(0, len(tokens), line_len)]
    llabs = [labels[i:i + line_len] for i in range(0, len(tokens), line_len)]
    chunks = [(lines[i:i + page_len], llabs[i:i + page_len]) for i in range(0, len(lines), page_len)]
    n = len(chunks)
    multi = len(set(labels)) > 1
    pages = []
    for k, (ch, lb) in enumerate(chunks):
        if multi:
            sec = Counter(t for ln in lb for t in ln).most_common(1)[0][0]
        else:
            sec = ["s1", "s2", "s3", "s4"][min(3, k * 4 // n)]
        pages.append(dict(id=f"p{k:04d}", section=sec, hand=hand, quire=None, lines=ch))
    return pages


def natural_from_control(name):
    ws = corpora.control(name)
    n_full = len(ws)
    ws = ws[:N_SAMPLE]
    return wrap_labelled(ws, ["0"] * len(ws)), n_full


def natural_from_ext(name):
    lines, secs = corpora_ext.control_ext_lines(name, with_sections=True)
    toks, labs = [], []
    for ln, s in zip(lines, secs):
        toks.extend(ln)
        labs.extend([s] * len(ln))
    n_full = len(toks)
    return wrap_labelled(toks[:N_SAMPLE], labs[:N_SAMPLE]), n_full


def load_meta(path):
    """Like metrics_new.meta_json_pages but accepts a page key of 'id' or 'page'."""
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for p in d["pages"]:
        pid = p.get("id", p.get("page", len(out)))
        out.append(dict(id=str(pid), section=str(p.get("section", "?")),
                        hand=str(p.get("hand", "?")), quire=p.get("quire"),
                        lines=[[str(t) for t in ln] for ln in p["lines"] if ln]))
    return [p for p in out if p["lines"]]


def family_of_synthetic(name):
    if name.startswith("nomen_"):
        return "C"
    if name.startswith(("markov1", "rugg", "timm", "schwartz", "c2")):
        return "G"
    return "X"


def build_corpora():
    """Returns list of (name, family, pages, note)."""
    out = []
    voy = M.voynich_pages("eva")
    out.append(("voynich_all", "V", voy, "ZL3b EVA paragraphs, whole"))
    out.append(("voynich_A", "V", [p for p in voy if p["lang"] == "A"], "Currier A pages"))
    out.append(("voynich_B", "V", [p for p in voy if p["lang"] == "B"], "Currier B pages"))

    found = sorted(glob.glob(str(ROOT / "data" / "controls_synthetic" / "*.meta.json")))
    emit(f"synthetic meta.json found ({len(found)}): " + ", ".join(Path(f).name for f in found))
    expected = ["nomen_word", "nomen_syll", "nomen_lines", "markov1", "rugg_grille", "naibbe_like",
                "latin_merged", "lull_ars_brevis_table", "timm_schinner", "schwartz_reuse", "c2_best"]
    names_found = {Path(f).name[:-len(".meta.json")] for f in found}
    missing = [e for e in expected if e not in names_found and not any(n.startswith(e) for n in names_found)]
    emit(f"expected-but-missing synthetic corpora: {missing or 'none'}")
    for f in found:
        name = Path(f).name[:-len(".meta.json")]
        pg = load_meta(f)
        n_full = len(M.flat_tokens(pg))
        pg = subsample(pg, N_SAMPLE)
        out.append((name, family_of_synthetic(name), pg, f"meta.json; {n_full} tokens full"))

    for name in corpora.CONTROLS:
        pg, n_full = natural_from_control(name)
        out.append((name, "L", pg, f"corpora.control; {n_full} tokens full"))
    for name in corpora_ext.NATURAL:
        try:
            pg, n_full = natural_from_ext(name)
            out.append((name, "L", pg, f"corpora_ext; {n_full} tokens full"))
        except FileNotFoundError:
            emit(f"natural control missing: {name}")
    for name in corpora_ext.CONSTRUCTED:
        if name == "lull_ars_brevis_table":
            continue  # scored from its meta.json above
        try:
            pg, n_full = natural_from_ext(name)
            out.append((name, "X", pg, f"corpora_ext constructed; {n_full} tokens full"))
        except FileNotFoundError:
            emit(f"constructed control missing: {name}")
    return out, missing


# ---------------------------------------------------------------------------
# metric extraction
# ---------------------------------------------------------------------------
V1_KEYS = ["h2", "sd_len", "jsd_first_fg", "p_init_enrich", "m_final_enrich",
           "cross_excess_eva", "redup_pct"]
NEW_KEYS = [
    ("lex_beta", "lexicon_growth: Heaps beta (all)"),
    ("lex_rate_late_early", "lexicon_growth: new-type rate last20%/first20%"),
    ("lex_edit1_excess", "lexicon_growth: edit-1 share of new types, recent-200 minus far-window"),
    ("slot_occupancy_pc", "slot_structure: occupancy prefix x core (all types)"),
    ("slot_table_likeness", "slot_structure: table-likeness token-weighted (all types)"),
    ("slot_core_crowding", "slot_structure: core edit-1 neighbour share (all types)"),
    ("info_mi_adjacent", "information_profile: MI adjacent, word boundaries given (bits)"),
    ("info_mi_page", "information_profile: MI same_page_far (bits)"),
    ("info_samecol_minus_othercol", "information_profile: MI prev_line_same_col minus prev_line_other_col"),
    ("bake_winner", "heldout_bakeoff: overall winner (bits/token)"),
    ("bake_char3_minus_unigram", "heldout_bakeoff: markov3 (char-3 WB) minus unigram_gt bits/token"),
    ("x_edge_mi_word", "extra_signatures: edge MI last glyph -> next first glyph (shuffle-corrected)"),
    ("x_hapax_10k", "extra_signatures: hapax share at 10k tokens"),
    ("x_moran_I", "extra_signatures: Moran's I word length lag 1"),
    ("x_position_entropy", "extra_signatures: glyph position entropy (bits, max 2.32)"),
    ("x_ltr_minus_rtl", "extra_signatures: bits/char ltr minus rtl"),
]
NUMERIC = V1_KEYS + [k for k, _ in NEW_KEYS if k != "bake_winner"]
ALL_COLS = V1_KEYS + ["v1_pass", "v1_missed"] + [k for k, _ in NEW_KEYS]


def fin(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def score_one(name, pages):
    words = M.flat_tokens(pages)
    lines = [ln for p in pages for ln in p["lines"]]
    row = {"tokens": len(words), "types": len(set(words)), "pages": len(pages), "lines": len(lines)}
    errors = {}
    t = time.time()
    try:
        v1 = score.score_corpus(name, words, lines)
        checks = bands(v1)
        for k in V1_KEYS:
            row[k] = v1[k]
        row["v1_pass"] = all(checks.values())
        row["v1_missed"] = [k for k, ok in checks.items() if not ok]
        row["_v1_full"] = v1
    except Exception as e:
        errors["v1"] = f"{type(e).__name__}: {e}"
        for k in V1_KEYS:
            row[k] = None
        row["v1_pass"] = None
        row["v1_missed"] = None
    print(f"    v1 {time.time() - t:.1f}s", flush=True)

    t = time.time()
    try:
        lex = M.lexicon_growth(pages, n_shuffles=N_SHUFFLES)
        a = lex["all"]
        row["lex_beta"] = a["beta"]
        row["lex_rate_late_early"] = a["rate_ratio_last20_first20"]
        row["lex_edit1_excess"] = a["edit1_share_recent200"] - a["edit1_share_far"]
    except Exception as e:
        errors["lex"] = f"{type(e).__name__}: {e}"
    print(f"    lex {time.time() - t:.1f}s", flush=True)

    t = time.time()
    try:
        slot, _ = M.slot_structure(pages)
        s = slot["all_types"]
        row["slot_occupancy_pc"] = s["occupancy_prefix_core"]
        row["slot_table_likeness"] = s["table_likeness_weighted"]
        row["slot_core_crowding"] = s["core_edit1_share"]
    except Exception as e:
        errors["slot"] = f"{type(e).__name__}: {e}"
    print(f"    slot {time.time() - t:.1f}s", flush=True)

    t = time.time()
    try:
        info = M.information_profile(pages)
        g = info["word_boundaries_given"]
        row["info_mi_adjacent"] = g["adjacent"]["mi"]
        row["info_mi_page"] = g["same_page_far"]["mi"]
        row["info_samecol_minus_othercol"] = g["prev_line_same_col"]["mi"] - g["prev_line_other_col"]["mi"]
        row["_info_bpe_adjacent"] = info["bpe_resegmented"]["adjacent"]["mi"]
    except Exception as e:
        errors["info"] = f"{type(e).__name__}: {e}"
    print(f"    info {time.time() - t:.1f}s", flush=True)

    t = time.time()
    try:
        bake = M.heldout_bakeoff(pages)
        ov = bake["overall"]
        row["bake_winner"] = min(ov, key=lambda m: ov[m]["bits_per_token"])
        row["bake_char3_minus_unigram"] = ov["markov3"]["bits_per_token"] - ov["unigram_gt"]["bits_per_token"]
        row["_bake_bits"] = {m: ov[m]["bits_per_token"] for m in ov}
    except Exception as e:
        errors["bake"] = f"{type(e).__name__}: {e}"
    print(f"    bake {time.time() - t:.1f}s", flush=True)

    t = time.time()
    try:
        ex = M.extra_signatures(pages)
        row["x_edge_mi_word"] = ex["edge_mi_word"]
        row["x_hapax_10k"] = ex["hapax_share_10k"]
        row["x_moran_I"] = ex["moran_I_wordlen_lag1"]
        row["x_position_entropy"] = ex["position_entropy_bits"]
        row["x_ltr_minus_rtl"] = ex["directional_asymmetry_ltr_minus_rtl"]
    except Exception as e:
        errors["extra"] = f"{type(e).__name__}: {e}"
    print(f"    extra {time.time() - t:.1f}s", flush=True)

    for k, _ in NEW_KEYS:
        row.setdefault(k, None)
    row["errors"] = errors
    return row


# ---------------------------------------------------------------------------
# ranges and decision rule
# ---------------------------------------------------------------------------
EDGE_KEYS = {"jsd_first_fg", "p_init_enrich", "m_final_enrich", "info_samecol_minus_othercol"}
POURED = {"timm_schinner"}  # Java T&S output poured into the Voynich line shape: no line-edge
                            # behaviour of its own; line-edge metrics come from timm_schinner_ownlines


def fam_range(rows, fam, key):
    use = [r for r in rows if r["family"] == fam and not (key in EDGE_KEYS and r["name"] in POURED)]
    vals = [fin(r[key]) for r in use]
    vals = [v for v in vals if v is not None]
    if not vals:
        return None
    return dict(min=min(vals), max=max(vals), n=len(vals),
                members=[r["name"] for r in use if fin(r[key]) is not None])


def in_out(v, rg):
    if v is None or rg is None:
        return "NA"
    w = rg["max"] - rg["min"]
    lo, hi = rg["min"] - EXTEND * w, rg["max"] + EXTEND * w
    return "IN" if lo <= v <= hi else "OUT"


def overlap3(ranges):
    rs = [ranges.get(f) for f in "LCG"]
    if any(r is None for r in rs):
        return None
    lo = max(r["min"] for r in rs)
    hi = min(r["max"] for r in rs)
    return lo <= hi


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


def main():
    t0 = time.time()
    emit("# results_m4_phase1_board: Phase 1 joint family-discrimination board")
    emit(f"# run {datetime.now().strftime('%Y-%m-%d %H:%M')} (system clock), seed {SEED}, "
         f"sample {N_SAMPLE} tokens per non-Voynich corpus, lexicon null shuffles {N_SHUFFLES}")
    emit("# v1 = scoreboard/score.py loaded by path, score_corpus + g0 band checks; "
         "new = scoreboard/metrics_new.py")
    emit()
    corp, missing = build_corpora()
    emit()
    emit("corpora:")
    for name, fam, pg, note in corp:
        toks = M.flat_tokens(pg)
        emit(f"  {fam} {name:32} pages={len(pg):4} lines={sum(len(p['lines']) for p in pg):5} "
             f"tokens={len(toks):6} types={len(set(toks)):6} sections={len({p['section'] for p in pg}):3}  [{note}]")
    emit()

    rows = []
    for i, (name, fam, pg, note) in enumerate(corp):
        print(f"[{i + 1}/{len(corp)}] {name} ({fam}) ... elapsed {time.time() - t0:.0f}s", flush=True)
        try:
            r = score_one(name, pg)
        except Exception as e:
            r = {k: None for k in ALL_COLS}
            r["errors"] = {"corpus": f"{type(e).__name__}: {e}"}
            traceback.print_exc()
        r["name"], r["family"], r["note"] = name, fam, note
        rows.append(r)

    # Voynich-all reproduction check vs filed TARGETS (score.py)
    voy = next(r for r in rows if r["name"] == "voynich_all")
    emit("Voynich-all reproduction vs score.py TARGETS:")
    for key, (want, tol, src) in score.TARGETS.items():
        got = voy.get("_v1_full", {}).get(key)
        ok = got is not None and abs(got - want) <= tol
        emit(f"  {'PASS' if ok else 'FAIL'} {key}: got {got} want {want}+-{tol} ({src})")
    emit()

    # ---- 1. wide table ----
    emit("=== 1. WIDE TABLE (rows = corpora, columns = metrics) ===")
    emit("v1 bands: h2 1.98-2.28, sd 1.41-2.11, JSDf>=0.10, p>=x8, m>=x8, excess>=+0.09, redup 0.4-1.8%")
    hdr = f"{'F':1} {'corpus':30} {'tokens':>6} " + " ".join(f"{k:>14}" for k in ALL_COLS)
    emit(hdr)
    for r in rows:
        cells = []
        for k in ALL_COLS:
            v = r.get(k)
            if k == "v1_missed":
                s = fmt(v)
                cells.append(f"{s[:14]:>14}")
            elif k == "bake_winner":
                cells.append(f"{fmt(v)[:14]:>14}")
            else:
                cells.append(f"{fmt(v):>14}")
        emit(f"{r['family']:1} {r['name']:30} {r['tokens'] if r.get('tokens') else 0:>6} " + " ".join(cells))
    emit()
    emit("column key:")
    for k in V1_KEYS:
        emit(f"  {k:28} frozen v1 (score.py)")
    for k, d in NEW_KEYS:
        emit(f"  {k:28} {d}")
    emit()
    emit("bake-off bits/token per model (markov2, markov3, slot, unigram_gt, copy0.3, copy0.1, copy0.05):")
    for r in rows:
        b = r.get("_bake_bits")
        if b:
            emit(f"  {r['name']:30} " + " ".join(f"{m}={b[m]:.3f}" for m in b))
    emit()

    # ---- 2. ranges and in/out ----
    emit("=== 2. FAMILY CONTROL RANGES (min..max) AND VOYNICH IN/OUT (range extended by 10% of width) ===")
    emit("tight = width < 0.5 * spread over all corpora; weight=0 if L, C, G ranges mutually overlap")
    emit(f"G range for line-edge metrics {sorted(EDGE_KEYS)} excludes {sorted(POURED)} (poured into the Voynich "
         "line shape, so its line edges are Voynich's, not the generator's); timm_schinner_ownlines supplies them")
    vnames = ["voynich_all", "voynich_A", "voynich_B"]
    vrows = {n: next(r for r in rows if r["name"] == n) for n in vnames}
    ranges, verdict, noweight, tight = {}, {}, [], {}
    emit(f"{'metric':28} {'L range':>19} {'C range':>19} {'G range':>19} {'spread':>8} {'tightLCG':>8} {'ovl':>4} "
         + " ".join(f"{'V' + n[8:] + ' val':>10} {'L':>3} {'C':>3} {'G':>3}" for n in vnames))
    for key in NUMERIC:
        ranges[key] = {f: fam_range(rows, f, key) for f in "LCG"}
        allv = [fin(r[key]) for r in rows]
        allv = [v for v in allv if v is not None]
        spread = (max(allv) - min(allv)) if allv else None
        tight[key] = {f: (ranges[key][f] is not None and spread is not None and spread > 0
                          and (ranges[key][f]["max"] - ranges[key][f]["min"]) < 0.5 * spread)
                      for f in "LCG"}
        ov = overlap3(ranges[key])
        if ov:
            noweight.append(key)
        verdict[key] = {}
        cells = []
        for n in vnames:
            v = fin(vrows[n].get(key))
            verdict[key][n] = {f: in_out(v, ranges[key][f]) for f in "LCG"}
            cells.append(f"{fmt(v):>10} " + " ".join(f"{verdict[key][n][f]:>3}" for f in "LCG"))

        def rs(f):
            rg = ranges[key][f]
            return "nan" if rg is None else f"{rg['min']:.4f}..{rg['max']:.4f}"
        emit(f"{key:28} {rs('L'):>19} {rs('C'):>19} {rs('G'):>19} {fmt(spread):>8} "
             f"{''.join('t' if tight[key][f] else '.' for f in 'LCG'):>8} {('yes' if ov else 'no') if ov is not None else 'na':>4} "
             + " ".join(cells))
    # categorical: bake winner
    key = "bake_winner"
    ranges[key] = {f: sorted({r[key] for r in rows if r["family"] == f and r.get(key)}) for f in "LCG"}
    verdict[key] = {}
    for n in vnames:
        w = vrows[n].get(key)
        verdict[key][n] = {f: ("NA" if w is None else ("IN" if w in ranges[key][f] else "OUT")) for f in "LCG"}
    emit(f"{key:28} L={ranges[key]['L']} C={ranges[key]['C']} G={ranges[key]['G']}  "
         + "  ".join(f"V{n[8:]}={vrows[n].get(key)} " + "".join(f"{f}:{verdict[key][n][f]} " for f in "LCG") for n in vnames))
    wins = set(ranges[key]["L"]) & set(ranges[key]["C"]) & set(ranges[key]["G"])
    if wins:
        noweight.append(key)
    emit()

    # ---- 3. per-family out counts ----
    emit("=== 3. PER-FAMILY OUT COUNTS (weighted metrics only; all-metric count in brackets) ===")
    weighted = [k for k in NUMERIC + ["bake_winner"] if k not in noweight]
    summary = {}
    for n in vnames:
        summary[n] = {}
        emit(f"[{n}]")
        for f in "LCG":
            outs_w = [k for k in weighted if verdict[k][n][f] == "OUT"]
            outs_all = [k for k in NUMERIC + ["bake_winner"] if verdict[k][n][f] == "OUT"]
            outs_tight = [k for k in outs_w if k != "bake_winner" and tight[k][f]]
            ins_w = sum(1 for k in weighted if verdict[k][n][f] == "IN")
            summary[n][f] = dict(outs_weighted=len(outs_w), ins_weighted=ins_w, outs_all=len(outs_all),
                                 out_metrics=outs_w, out_metrics_all=outs_all, out_tight=outs_tight)
            emit(f"  {f}: in={ins_w:2} out={len(outs_w):2} [all metrics out={len(outs_all)}]  "
                 f"out-metrics: {', '.join(outs_w) or '-'}  | tight-outs ({len(outs_tight)}): {', '.join(outs_tight) or '-'}")
        counts = {f: summary[n][f]["outs_weighted"] for f in "LCG"}
        order = sorted(counts, key=counts.get)
        best, second = order[0], order[1]
        margin = counts[second] - counts[best]
        tie = [f for f in counts if counts[f] == counts[best]]
        if len(tie) > 1:
            emit(f"  fewest outs: tie {tie} at {counts[best]}; no family favoured")
            summary[n]["fewest"] = dict(family=None, tie=tie, margin=0)
        else:
            emit(f"  fewest outs: {best} ({counts[best]}) vs {second} ({counts[second]}); margin {margin} "
                 f"-> {'FAVOURED (>=2)' if margin >= 2 else 'not favoured (<2)'}")
            summary[n]["fewest"] = dict(family=best, margin=margin, tie=tie)
        outside_all = [k for k in NUMERIC + ["bake_winner"] if all(verdict[k][n][f] == "OUT" for f in "LCG")]
        summary[n]["outside_all_families"] = outside_all
        emit(f"  outside ALL families (L, C and G): {', '.join(outside_all) or '-'}")
        kill = [f for f in "LCG" if len(summary[n][f]["out_tight"]) >= 3]
        summary[n]["kill_precondition"] = kill
        emit(f"  kill precondition (>=3 weighted outs on tight ranges): {kill or 'none'}")
    emit()

    # ---- 4. overlap flag ----
    emit("=== 4. METRICS WHERE L, C AND G RANGES OVERLAP (no weight) ===")
    emit(", ".join(noweight) or "none")
    emit(f"weighted metrics ({len(weighted)}): {', '.join(weighted)}")
    emit()

    errs = {r["name"]: r["errors"] for r in rows if r.get("errors")}
    emit("=== 5. RUN NOTES ===")
    emit(f"missing synthetic corpora: {missing or 'none'}")
    emit(f"corpora with errors: {json.dumps(errs) if errs else 'none'}")
    emit(f"total runtime {time.time() - t0:.0f}s")

    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")

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
    OUTJ.write_text(json.dumps(clean(dict(
        run=datetime.now().strftime("%Y-%m-%d %H:%M"), seed=SEED, n_sample=N_SAMPLE,
        n_shuffles=N_SHUFFLES, extend=EXTEND, columns=ALL_COLS, rows=rows, ranges=ranges,
        tight=tight, verdict=verdict, no_weight=noweight, weighted=weighted, summary=summary,
        missing=missing, errors=errs)), indent=1), encoding="utf-8")
    print(f"wrote {OUT} and {OUTJ}", flush=True)


if __name__ == "__main__":
    main()
