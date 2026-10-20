"""n7: where does the manuscript fall relative to real human gibberish on the frozen v2 board?

PRE-REGISTRATION (written before any n7 scoring; stamped 2026-10-17 19:38 PDT from `date`;
SHA-256 of this file is frozen in n7_gibberish_family.prereg.sha256 before the first run;
run ONCE, no tuning after seeing results). Closes OPEN O-031 (Gaskell-Bowern gibberish never
scored on our board). Instrument: PREREG-v2.md (frozen 19:27, `sha256sum -c
scoreboard/PREREG-v2.sha256` checked OK at 19:35), scorer scoreboard/run_v2.py unchanged.

Data. Family X = the 38 Gaskell & Bowern (2022) volunteer gibberish texts as converted by
tools/gibberish_to_meta.py (data/controls_gibberish/gib_<writer>.meta.json, 79-480 tokens
each) plus gib_pooled.meta.json (10,023 tokens). L/C/G = the ranges in
results_m4_phase1_board.json, unchanged (C is m4's six nomen_* files; the k4 nomen_k2_*
files are scored as entrants, not folded into C, because the task fixes "m4's ranges plus X").

Steps (all in this one run, in this order):
 (a) run `python -m scoreboard.run_v2 --meta <gib sidecar> --family X --ranges
     results_m4_phase1_board.json --out results_n7_<name>.txt` for all 39 gib_ sidecars.
 (b) build n7_gibberish_ranges.json = m4's ranges file plus "x_family": "gibberish" and an
     X range per metric:
       * v1 seven bands and x_position_entropy: min/max over the 38 per-writer values
         (PREREG-v2 §7). x_position_entropy per writer is computed by a verbatim copy of
         metrics_new.extra_signatures block (d), because the whole function fails on a 3-page
         file (fold split). GATE: the copy must reproduce extra_signatures' value on
         gib_pooled and on the Voynich to 1e-12, else the run stops.
       * every other extra (edge MI, ltr-rtl, Moran I, lex_*, slot_*, info_*, bake_*):
         from gib_pooled only (PREREG-v2 §7). A single corpus gives a zero-width range, so
         the X range is min/max over gib_pooled plus its 38 leave-one-writer-out corpora
         (jackknife, scored with run_v2.score_one). This range is narrow by construction
         and is flagged "pooled" in every line; the pooled corpus mixes 38 writers, so
         lexicon/slot metrics on it describe a 38-author mixture, not one gibberish text.
       * types_25k: X = NA (undefined at 25k; pooled has 10,023 tokens). x_hapax_10k
         (REPORT, no weight) from pooled.
       * no_weight recomputed per PREREG-v2 §7: a metric is no-weight if the raw (unextended)
         L, C, G and X ranges have a non-empty common intersection; where X is NA the m4
         three-family result is kept; REPORT-class keys and bake_winner stay no-weight.
       * tight recomputed for L, C, G, X: width < 0.5 x spread over all corpora (m4 rows +
         38 writers + gib_pooled; jackknife corpora are not corpora and are excluded).
       * types_25k L/C/G ranges written exactly as run_v2 derives them (m4 rows with
         tokens >= 25,000).
 (c) rescore with --ranges n7_gibberish_ranges.json: the manuscript (`--voynich`, all/A/B);
     RF1b and IT2a (data/translit/*.meta.json, all/A/B, --n-sample 1000000 so they are
     whole like --voynich) for the PREREG-v2 §2 robustness rule; every synthetic sidecar in
     data/controls_synthetic/ (19 entrants/controls, all). The 21 L controls have no sidecar:
     their X in/out is computed from their stored results_m4 rows (same pipeline,
     run_v2 docstring), not re-run.
 (d) matched-length check (metric-length dependence): the X per-writer values are at
     79-480 tokens while the board scores at 25k. For each writer length n_w (38 lengths):
       * Voynich: 20 windows of n_w tokens (whole ZL3b paragraph lines, contiguous, random
         start line, rng seed 20261017) per subset all/A/B -> 760 windows per subset;
       * L: one window of n_w tokens from L control number (i mod 21) (first 25k tokens,
         wrapped 8 tokens/line as m4), random start line -> 38 windows, same lengths as X;
       * metrics: the seven v1 keys (score.score_corpus) and x_position_entropy.
     L_ml range = min/max of the 38 L windows, X_ml = min/max of the 38 writers;
     Voynich_ml point = median over its 760 windows (share of windows inside each range is
     printed too). Same 10 %-of-width extension.

Decision rule (fixed now).
 Per metric, per subset (all/A/B), per scale (full / matched), with in/out as run_v2:
   Voynich IN X and OUT L -> FAV_X (favours gibberish); IN L and OUT X -> FAV_L;
   IN both -> NONDIAG; OUT both -> ANOM (anomalous vs L and X); either NA -> NA.
 Counted metrics at full scale: weighted = v1 seven + WEIGHTED-class extras of run_v2 minus
 n7 no_weight; a metric whose in/out (any family) flips between ZL3b, RF1b and IT2a on that
 subset is zero-weighted (PREREG-v2 §2). REPORT-class metrics are printed, never counted.
 Matched scale counts all eight metrics computed there.

 Overall verdict:
  PRIMARY = PREREG-v2 §7 family rule (it is defined, so it is used): for each family F in
   L, C, G, X: outs(F) = weighted outs, tight_outs(F) = outs on F-tight ranges.
   KILL-precondition F: tight_outs(F) >= 3 (the "no single parameter change" clause is not
   tested here and is stated as untested). FAVOURED F: outs(F) <= outs(R) - 2 for every
   rival R. A verdict holds only if it is the same on all, A and B (§6); else it is reported
   A-only / B-only and the headline is UNDECIDED.
  SECONDARY = the X-vs-L count: per subset n(FAV_X) vs n(FAV_L). LEAN X if n(FAV_X) > n(FAV_L)
   on all three subsets, LEAN L if the reverse on all three, else MIXED. Reported at full
   and matched scale separately; if the two scales disagree the lean is called
   SIZE-DEPENDENT and no X-vs-L lean is claimed.
  Also reported: metrics outside every family (OUT on L, C, G and X) at full scale per subset.
 Not a decipherment claim; X is gibberish written in a-z by modern volunteers, so the EVA-
 specific v1 keys (p_init_enrich counts 'p', m_final_enrich counts 'm', h2/sd_len are set at
 EVA character level, PREREG-v2 §2) measure Latin letters for X exactly as they already do
 for L; that caveat travels with every X in/out.

Outputs: results_n7_<gib name>.txt/.json (39), results_n7_voy_{all,A,B}, results_n7_RF1b_*,
results_n7_IT2a_*, results_n7_ent_<name> (run_v2 files), n7_gibberish_ranges.json,
results_n7.txt + results_n7.json (verdict). Edits no other file. System Python 3.11.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from scoreboard import run_v2 as R2  # noqa: E402
from scoreboard import metrics_new as M  # noqa: E402
import corpora  # noqa: E402
import corpora_ext  # noqa: E402

SEED = 20261017
EXT = 0.10
GIB = ROOT / "data" / "controls_gibberish"
SYN = ROOT / "data" / "controls_synthetic"
TRL = ROOT / "data" / "translit"
M4 = ROOT / "results_m4_phase1_board.json"
RANGES = ROOT / "n7_gibberish_ranges.json"
OUT = ROOT / "results_n7.txt"
STUB = ROOT / "n7_gibberish_family.prereg.sha256"
V1 = R2.V1_KEYS
CLS = {k: c for k, c, _ in R2.NEW_KEYS}
ALL_KEYS = V1 + R2.NEW_NUMERIC
PER_WRITER = V1 + ["x_position_entropy"]
SUBSETS = ["all", "A", "B"]
TRANSLITS = ["ZL3b", "RF1b", "IT2a"]
N_WIN = 20

lines_out = []


def emit(s=""):
    print(s, flush=True)
    lines_out.append(s)


def fin(x):
    return R2.fin(x)


def in_out(v, rg):
    if v is None or not rg:
        return "NA"
    w = rg["max"] - rg["min"]
    return "IN" if rg["min"] - EXT * w <= v <= rg["max"] + EXT * w else "OUT"


def classify(io):
    x, l = io.get("X", "NA"), io.get("L", "NA")
    if "NA" in (x, l):
        return "NA"
    return {("IN", "OUT"): "FAV_X", ("OUT", "IN"): "FAV_L",
            ("IN", "IN"): "NONDIAG", ("OUT", "OUT"): "ANOM"}[(x, l)]


def rng_of(vals):
    vals = [v for v in vals if v is not None]
    return dict(min=min(vals), max=max(vals), n=len(vals)) if vals else None


def fmt(v, d=4):
    return "nan" if v is None else f"{v:.{d}f}"


# --- verbatim copy of metrics_new.extra_signatures blocks (c) and (d) -------------------
def position_entropy(toks):
    q = defaultdict(Counter)
    tot = Counter()
    for w in toks:
        L = len(w)
        for i, ch in enumerate(w):
            rp = i / (L - 1) if L > 1 else 0.5
            q[ch][min(4, int(rp * 5))] += 1
            tot[ch] += 1
    N = sum(tot.values())
    return sum(tot[ch] / N * M.entropy_counts(q[ch]) for ch in tot)


def moran(toks):
    x = np.array([len(t) for t in toks], dtype=float)
    z = x - x.mean()
    return float(len(z) / (len(z) - 1) * (z[:-1] * z[1:]).sum() / (z * z).sum())


def run_cli(args, out):
    cmd = [sys.executable, "-m", "scoreboard.run_v2"] + args + ["--out", str(out)]
    t = time.time()
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        emit(f"  CLI FAILED {out.name}: {p.stderr.strip()[-400:]}")
        return None
    emit(f"  {out.name}  {time.time() - t:.0f}s")
    return json.loads(out.with_suffix(".json").read_text(encoding="utf-8"))["row"]


def main():
    t0 = time.time()
    me = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    stub = STUB.read_text(encoding="utf-8").split()[0] if STUB.exists() else None
    emit(f"# results_n7: gibberish family X on the frozen v2 board  run={datetime.now().strftime('%Y-%m-%d %H:%M')} "
         f"(system clock)  seed={SEED}")
    emit(f"# script sha256 {me}  stub {stub}  -> {'MATCH' if me == stub else 'MISMATCH (report, not scored)'}")
    emit(f"# ranges file: {RANGES.name} (built in step b from {M4.name})")
    emit()

    # ---------------- gate: verbatim copy reproduces extra_signatures ----------------
    _, pooled_pages = R2.load_meta(GIB / "gib_pooled.meta.json")
    voy = M.voynich_pages("eva")
    for nm, pg in (("gib_pooled", pooled_pages), ("voynich", voy)):
        ex = M.extra_signatures(pg)
        toks = M.flat_tokens(pg)
        d1 = abs(ex["position_entropy_bits"] - position_entropy(toks))
        d2 = abs(ex["moran_I_wordlen_lag1"] - moran(toks))
        emit(f"gate copy-check {nm}: |dPosEnt|={d1:.2e} |dMoran|={d2:.2e}")
        if d1 > 1e-12 or d2 > 1e-12:
            raise SystemExit("GATE FAILED: copy of extra_signatures (c)/(d) differs")
    emit()

    # ---------------- (a) score the 39 gib sidecars ----------------
    emit("=== (a) run_v2 on the 39 gib_ sidecars (--family X --ranges results_m4_phase1_board.json) ===")
    gib_files = sorted(GIB.glob("gib_*.meta.json"))
    gib_rows = {}
    for f in gib_files:
        name = f.name[:-len(".meta.json")]
        row = run_cli(["--meta", str(f.relative_to(ROOT)), "--family", "X", "--ranges", M4.name],
                      ROOT / f"results_n7_{name}.txt")
        _, pg = R2.load_meta(f)
        toks = M.flat_tokens(pg)
        row["x_position_entropy"] = position_entropy(toks) if row.get("x_position_entropy") is None else row["x_position_entropy"]
        row["_moran_desc"] = moran(toks)
        row["_ntok"] = len(toks)
        gib_rows[name] = row
    writers = [n for n in gib_rows if n != "gib_pooled"]
    emit(f"writers scored: {len(writers)}; tokens {sum(gib_rows[w]['_ntok'] for w in writers)}; "
         f"pooled {gib_rows['gib_pooled']['_ntok']}")
    emit()
    emit(f"{'writer':10} {'tok':>4} " + " ".join(f"{k[:9]:>9}" for k in PER_WRITER) + f" {'moran*':>7}")
    for w in writers:
        r = gib_rows[w]
        emit(f"{w[4:]:10} {r['_ntok']:>4} " + " ".join(f"{fmt(fin(r.get(k)), 3):>9}" for k in PER_WRITER)
             + f" {r['_moran_desc']:+7.3f}")
    emit("(* Moran I per writer is descriptive only; the weighted X Moran range is from the pooled corpus)")
    emit()

    # ---------------- jackknife over writers for pooled-only extras ----------------
    emit("=== jackknife: gib_pooled minus one writer (38 corpora), run_v2.score_one ===")
    by_writer = defaultdict(list)
    for p in pooled_pages:
        by_writer[p["hand"]].append(p)
    jack = []
    for h in sorted(by_writer):
        pg = [p for p in pooled_pages if p["hand"] != h]
        r = R2.score_one(f"gib_pooled_minus_{h}", pg, lambda s: None)
        if r["errors"]:
            emit(f"  minus {h}: errors {r['errors']}")
        jack.append(r)
    emit(f"  {len(jack)} jackknife corpora scored")
    emit()

    # ---------------- (b) build the ranges file ----------------
    R = json.loads(M4.read_text(encoding="utf-8"))
    m4rows = R["rows"]
    ranges = R["ranges"]
    if "types_25k" not in ranges:
        ranges["types_25k"] = {}
        for f in "LCG":
            vals = [r["types"] for r in m4rows if r.get("family") == f and r.get("types")
                    and r.get("tokens") and r["tokens"] >= 25000]
            if vals:
                ranges["types_25k"][f] = dict(min=min(vals), max=max(vals), n=len(vals))
    x_src = {}
    for k in ALL_KEYS:
        ranges.setdefault(k, {})
        if k in PER_WRITER:
            rg = rng_of([fin(gib_rows[w].get(k)) for w in writers])
            x_src[k] = "per-writer (38)"
        elif k == "types_25k":
            rg, x_src[k] = None, "NA (undefined at 25k)"
        else:
            rg = rng_of([fin(gib_rows["gib_pooled"].get(k))] + [fin(j.get(k)) for j in jack])
            x_src[k] = "pooled + 38 jackknife"
        if rg:
            ranges[k]["X"] = dict(rg, source=x_src[k])
    # no-weight over four families
    noweight = []
    for k in ALL_KEYS:
        if CLS.get(k) == "REPORT":
            noweight.append(k)
            continue
        fams = [ranges[k].get(f) for f in "LCGX"]
        if ranges[k].get("X") is None:
            if k in R["no_weight"]:
                noweight.append(k)
            continue
        if any(r is None for r in fams):
            continue
        if max(r["min"] for r in fams) <= min(r["max"] for r in fams):
            noweight.append(k)
    noweight.append("bake_winner")
    # tight over all corpora
    tight = {}
    for k in ALL_KEYS:
        allv = [fin(r.get(k if k != "types_25k" else "types")) for r in m4rows
                if k != "types_25k" or (r.get("tokens") or 0) >= 25000]
        if k != "types_25k":  # gib files are < 25k tokens: no types_25k value
            allv += [fin(gib_rows[n].get(k)) for n in gib_rows]
        allv = [v for v in allv if v is not None]
        spread = max(allv) - min(allv) if allv else None
        tight[k] = {f: bool(ranges[k].get(f) and spread and (ranges[k][f]["max"] - ranges[k][f]["min"]) < 0.5 * spread)
                    for f in "LCGX"}
    newR = dict(R, x_family="gibberish", ranges=ranges, tight=tight, no_weight=noweight,
                n7=dict(built=datetime.now().strftime("%Y-%m-%d %H:%M"), from_file=M4.name,
                        x_source=x_src, note="L/C/G = m4 ranges unchanged; X per n7 prereg"))
    RANGES.write_text(json.dumps(newR, indent=1), encoding="utf-8")
    emit("=== (b) n7_gibberish_ranges.json ===")
    emit(f"{'metric':28} {'X range':>21} {'X source':>22} {'L range':>21} {'tight LCGX':>10} {'noW(m4->n7)':>12}")
    for k in ALL_KEYS:
        rx, rl = ranges[k].get("X"), ranges[k].get("L")
        rs = lambda r: "nan" if not r else f"{r['min']:.4f}..{r['max']:.4f}"
        emit(f"{k:28} {rs(rx):>21} {x_src[k]:>22} {rs(rl):>21} "
             f"{''.join('t' if tight[k][f] else '.' for f in 'LCGX'):>10} "
             f"{('y' if k in R['no_weight'] else 'n') + '->' + ('y' if k in noweight else 'n'):>12}")
    emit()

    # ---------------- (c) rescore manuscript, translits, entrants ----------------
    emit("=== (c) run_v2 with --ranges n7_gibberish_ranges.json ===")
    vrows = {t: {} for t in TRANSLITS}
    for s in SUBSETS:
        la = [] if s == "all" else ["--lang", s]
        vrows["ZL3b"][s] = run_cli(["--voynich"] + la + ["--ranges", RANGES.name], ROOT / f"results_n7_voy_{s}.txt")
        for t in ("RF1b", "IT2a"):
            vrows[t][s] = run_cli(["--meta", f"data/translit/{t}.meta.json", "--name", f"voynich_{t}"] + la +
                                  ["--n-sample", "1000000", "--ranges", RANGES.name], ROOT / f"results_n7_{t}_{s}.txt")
    ent_rows = {}
    for f in sorted(SYN.glob("*.meta.json")):
        name = f.name[:-len(".meta.json")]
        ent_rows[name] = run_cli(["--meta", str(f.relative_to(ROOT)), "--ranges", RANGES.name],
                                 ROOT / f"results_n7_ent_{name}.txt")
    emit()

    weighted_base = [k for k in ALL_KEYS if k not in noweight and CLS.get(k, "WEIGHTED") != "REPORT"]

    def io_of(row):
        return {k: {f: in_out(fin(row.get(k)), ranges[k].get(f)) for f in "LCGX"} for k in ALL_KEYS}

    io = {t: {s: io_of(vrows[t][s]) for s in SUBSETS if vrows[t][s]} for t in TRANSLITS}

    # ---------------- full-scale decisions ----------------
    emit("=== FULL SCALE: Voynich ZL3b per metric (in/out L C G X; class; flips across ZL3b/RF1b/IT2a) ===")
    res = {"full": {}, "matched": {}}
    for s in SUBSETS:
        emit(f"-- subset {s} --")
        flipped = []
        for k in weighted_base:
            for f in "LCGX":
                vals = {io[t][s][k][f] for t in TRANSLITS if s in io[t]} - {"NA"}
                if len(vals) > 1:
                    flipped.append(k)
                    break
        wk = [k for k in weighted_base if k not in flipped]
        cls = {k: classify(io["ZL3b"][s][k]) for k in ALL_KEYS}
        outside_all = [k for k in ALL_KEYS if all(io["ZL3b"][s][k][f] == "OUT" for f in "LCGX")]
        emit(f"{'metric':28} {'ZL3b':>9} {'RF1b':>9} {'IT2a':>9}  L   C   G   X   class    weight")
        for k in ALL_KEYS:
            vv = [fmt(fin(vrows[t][s].get(k)), 3) if vrows[t].get(s) else "-" for t in TRANSLITS]
            w = ("W" if k in wk else ("flip0" if k in flipped else ("REPORT" if CLS.get(k) == "REPORT" else "noW")))
            emit(f"{k:28} {vv[0]:>9} {vv[1]:>9} {vv[2]:>9}  " +
                 " ".join(f"{io['ZL3b'][s][k][f]:>3}" for f in "LCGX") + f"  {cls[k]:8} {w}")
        fam = {}
        for f in "LCGX":
            outs = [k for k in wk if io["ZL3b"][s][k][f] == "OUT"]
            fam[f] = dict(outs=outs, tight_outs=[k for k in outs if tight[k][f]],
                          na=[k for k in wk if io["ZL3b"][s][k][f] == "NA"])
        kill = [f for f in "LCGX" if len(fam[f]["tight_outs"]) >= 3]
        fav = [f for f in "LCGX" if all(len(fam[f]["outs"]) <= len(fam[r]["outs"]) - 2 for r in "LCGX" if r != f)]
        nX = [k for k in wk if cls[k] == "FAV_X"]
        nL = [k for k in wk if cls[k] == "FAV_L"]
        for f in "LCGX":
            emit(f"  {f}: outs={len(fam[f]['outs']):2} tight-outs={len(fam[f]['tight_outs'])} na={len(fam[f]['na'])}  "
                 f"out: {', '.join(fam[f]['outs']) or '-'}")
        emit(f"  counted metrics ({len(wk)}): {', '.join(wk)}")
        emit(f"  zero-weighted by translit flip: {', '.join(flipped) or '-'}")
        emit(f"  KILL-precondition (>=3 tight outs): {kill or 'none'}   FAVOURED (fewest outs by >=2): {fav or 'none'}")
        emit(f"  FAV_X ({len(nX)}): {', '.join(nX) or '-'}")
        emit(f"  FAV_L ({len(nL)}): {', '.join(nL) or '-'}")
        emit(f"  NONDIAG: {', '.join(k for k in wk if cls[k] == 'NONDIAG') or '-'}")
        emit(f"  ANOM (out L and X): {', '.join(k for k in wk if cls[k] == 'ANOM') or '-'}")
        emit(f"  outside every family (L,C,G,X all OUT, any class): {', '.join(outside_all) or '-'}")
        emit()
        res["full"][s] = dict(fam=fam, kill=kill, fav=fav, fav_x=nX, fav_l=nL, counted=wk, flipped=flipped,
                              cls=cls, outside_all=outside_all)

    # ---------------- other corpora against X ----------------
    emit("=== entrants/controls vs X (n7 ranges; synthetic via run_v2, L controls from stored m4 rows) ===")
    other = {}
    for name, row in ent_rows.items():
        if row:
            other[name] = ("run_v2", row)
    for r in m4rows:
        if r.get("family") == "L":
            other[r["name"]] = ("m4 row", r)
    for name, (src, row) in other.items():
        ioo = io_of(row)
        xs = [k for k in weighted_base if ioo[k]["X"] == "OUT"]
        ls = [k for k in weighted_base if ioo[k]["L"] == "OUT"]
        emit(f"  {name:30} [{src:6}] X-outs={len(xs):2} L-outs={len(ls):2}  X out: {', '.join(xs) or '-'}")
    emit()

    # ---------------- (d) matched length ----------------
    emit("=== (d) MATCHED LENGTH: Voynich windows and L windows at the 38 writer lengths ===")
    rng = np.random.default_rng(SEED)
    lens = [gib_rows[w]["_ntok"] for w in writers]

    def window(lines, n):
        i = int(rng.integers(0, len(lines)))
        out, k = [], 0
        while k < n:
            ln = lines[i % len(lines)]
            out.append(ln)
            k += len(ln)
            i += 1
        return out

    def mscore(lines):
        words = [t for ln in lines for t in ln]
        r = R2.score.score_corpus("w", words, lines)
        d = {k: fin(r[k]) for k in V1}
        d["x_position_entropy"] = position_entropy(words)
        return d

    Lnames = corpora.CONTROLS + corpora_ext.NATURAL
    Llines = {}
    for nm in Lnames:
        if nm in corpora.CONTROLS:
            ws = corpora.control(nm)[:25000]
        else:
            lns = corpora_ext.control_ext_lines(nm)
            ws = [t for ln in lns for t in ln][:25000]
        Llines[nm] = [ws[i:i + 8] for i in range(0, len(ws), 8)]
    Lwin = [mscore(window(Llines[Lnames[i % len(Lnames)]], n)) for i, n in enumerate(lens)]
    Xw = {k: [fin(gib_rows[w].get(k)) for w in writers] for k in PER_WRITER}
    mr = {k: dict(L=rng_of([d[k] for d in Lwin]), X=rng_of(Xw[k])) for k in PER_WRITER}
    for s in SUBSETS:
        pg = voy if s == "all" else [p for p in voy if p["lang"] == s]
        vl = [ln for p in pg for ln in p["lines"]]
        vw = [mscore(window(vl, n)) for n in lens for _ in range(N_WIN)]
        emit(f"-- subset {s}: {len(vw)} Voynich windows --")
        emit(f"{'metric':20} {'V median':>9} {'L_ml range':>17} {'X_ml range':>17} {'V%inL':>6} {'V%inX':>6}  L   X   class")
        cl = {}
        for k in PER_WRITER:
            vals = [d[k] for d in vw if d[k] is not None]
            med = float(np.median(vals)) if vals else None
            ioL, ioX = in_out(med, mr[k]["L"]), in_out(med, mr[k]["X"])
            cl[k] = classify({"L": ioL, "X": ioX})
            sh = lambda f: (100 * np.mean([in_out(v, mr[k][f]) == "IN" for v in vals])) if vals else float("nan")
            rs = lambda r: "nan" if not r else f"{r['min']:.3f}..{r['max']:.3f}"
            emit(f"{k:20} {fmt(med, 3):>9} {rs(mr[k]['L']):>17} {rs(mr[k]['X']):>17} {sh('L'):6.1f} {sh('X'):6.1f}  "
                 f"{ioL:>3} {ioX:>3}  {cl[k]}")
        nX = [k for k in PER_WRITER if cl[k] == "FAV_X"]
        nL = [k for k in PER_WRITER if cl[k] == "FAV_L"]
        emit(f"  FAV_X ({len(nX)}): {', '.join(nX) or '-'}   FAV_L ({len(nL)}): {', '.join(nL) or '-'}")
        emit()
        res["matched"][s] = dict(cls=cl, fav_x=nX, fav_l=nL)
    res["matched_ranges"] = mr

    # ---------------- verdict ----------------
    def lean(scale):
        ls = [("X" if len(res[scale][s]["fav_x"]) > len(res[scale][s]["fav_l"]) else
               "L" if len(res[scale][s]["fav_l"]) > len(res[scale][s]["fav_x"]) else "tie") for s in SUBSETS]
        return ("LEAN X" if all(v == "X" for v in ls) else "LEAN L" if all(v == "L" for v in ls) else "MIXED"), ls

    favs = [tuple(res["full"][s]["fav"]) for s in SUBSETS]
    kills = [tuple(res["full"][s]["kill"]) for s in SUBSETS]
    if len(set(favs)) == 1 and favs[0]:
        primary = f"FAVOURED {favs[0][0]} (all/A/B agree)"
    else:
        primary = "UNDECIDED (no family favoured on all three subsets: " + \
                  ", ".join(f"{s}={list(f) or 'none'}" for s, f in zip(SUBSETS, favs)) + ")"
    kill_all = sorted(set(kills[0]).intersection(*map(set, kills[1:])))
    lf, lfs = lean("full")
    lm, lms = lean("matched")
    secondary = lf if lf == lm else f"SIZE-DEPENDENT (full {lf} {lfs}, matched {lm} {lms})"
    emit("=== VERDICT (pre-registered rule) ===")
    emit(f"PRIMARY  (PREREG-v2 §7 family rule): {primary}")
    emit(f"         kill-precondition on all/A/B: {kill_all or 'none'}  (per subset: "
         + ", ".join(f"{s}={list(k) or 'none'}" for s, k in zip(SUBSETS, kills)) + "; parameter-change clause untested)")
    emit(f"SECONDARY (X-vs-L count): {secondary}")
    emit(f"         full: " + "; ".join(f"{s} X{len(res['full'][s]['fav_x'])}/L{len(res['full'][s]['fav_l'])}" for s in SUBSETS)
         + f"   matched: " + "; ".join(f"{s} X{len(res['matched'][s]['fav_x'])}/L{len(res['matched'][s]['fav_l'])}" for s in SUBSETS))
    emit(f"outside every family (full, ZL3b): " + "; ".join(f"{s}: {', '.join(res['full'][s]['outside_all']) or '-'}" for s in SUBSETS))
    emit(f"elapsed {time.time() - t0:.0f}s")
    OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8")

    def clean(o):
        if isinstance(o, dict):
            return {str(k): clean(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [clean(v) for v in o]
        if isinstance(o, float) and not math.isfinite(o):
            return None
        return o
    OUT.with_suffix(".json").write_text(json.dumps(clean(dict(
        script_sha256=me, stub=stub, primary=primary, kill_all=kill_all, secondary=secondary,
        full=res["full"], matched=res["matched"], matched_ranges=res["matched_ranges"],
        ranges_file=RANGES.name)), indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
