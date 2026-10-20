"""s44 — Currier-A-only line-initial draw (red-team request, FINDINGS-REPORT §6 "Whether Currier A alone sits inside
the Latin range on the line-initial profile").

PRE-REGISTERED QUESTION (verbatim; frozen in s44_a_only_line_initial.prereg.sha256 before the run):
"Does Currier A alone, at the line counts of the s18/s32 Latin manuscripts, sit inside the Latin range on the
line-initial JSD excess, or is the A1 line-initial anomaly an A property as well as a B property?"

Method (fixed before the run)
  Voynich lines: ZL3b exactly as run_v2 --voynich loads them (R2.M.voynich_pages("eva"), run_v2 imported by
    path); Currier A = pages whose IVTFF $L is "A" (114 pages, 1557 lines); Currier B = pages with $L "B"
    (83 pages, 2478 lines); pages with "?" are in neither.
  Draw sizes: 114, 131, 160, 201, 492, 773 lines (the s18/s32 manuscript, pooled-verse and prose-pool sizes).
    If A (or B) has fewer lines than a size, that size is reported as "skipped: only N lines" for that language.
  Draws: per size k, rng = random.Random(20261017) re-seeded per k and per language; 200 x rng.sample(lines, k);
    per draw raw jsd_first = a2_position.stats(draw, w[0])[0]; null = mean of a2_position.null(draw, w[0], n=30)
    [:, 0] (30 within-line shuffles, random.Random(i), lines with >= 3 words); excess = raw - null (as s32).
  Comparison rows (values copied from results_s18.txt pooling-guard table and results_s32.txt; not recomputed):
    the 21 per-manuscript jsd_first_exc rows (results_s18.txt lines 239-259), the s32 pooled Latin-verse row
    (+0.0941 at 492 lines) and the CREMMA prose pool (cremma_prose15, +0.0078 at 773 lines).
  Prediction (red team, fixed before the run): A's draw interval at 773 lines includes the top Latin manuscripts
    (>= +0.132: LaurPlut33.31 +0.1370, Egerton821 +0.1324) -> "A inside".
  Rule (fixed before the run): "A inside" if the A 2.5 % draw bound lies below +0.132 at >= 201 lines (i.e. at
    every available size >= 201: 201, 492, 773); otherwise "A outside".  The B-only draws at the same sizes are
    printed beside for comparison and do not enter the rule.  Margins printed: (A 2.5 % bound - 0.132) per size,
    and the position (below / inside / above) of each Latin row against the A and B intervals at its own size.
  Checks reproduced: ZL3b full-text excess (+0.1740 in results_s32.txt / s18) and the all-pages draw at 773
    (+0.1734 [+0.1528, +0.1980] in results_s32.txt) are recomputed and printed.

Run:    python -I s44_a_only_line_initial.py
Writes: results_s44.txt only.  No other file is touched.
"""
from __future__ import annotations

import hashlib
import importlib.util
import random
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

OUT = ROOT / "results_s44.txt"
STUB = ROOT / "s44_a_only_line_initial.prereg.sha256"
SELF = ROOT / "s44_a_only_line_initial.py"
JSD_NULL_N = 30
SEED = 20261017
DRAWS = 200
SIZES = [114, 131, 160, 201, 492, 773]
TOP_LATIN = 0.132
RULE_MIN_K = 201
# (label, lines, jsd_first_exc) from results_s18.txt pooling-guard table (lines 239-259) + s32 pooled rows
S18_ROWS = [
    ("Arras-861", 351, 0.0239), ("BGO-511", 54, 0.0122), ("BIS-193", 598, 0.0393), ("CCCC-MSS-165", 148, 0.0047),
    ("CCCC-MSS-236", 160, 0.0642), ("CLM13027", 609, 0.0483), ("Egerton821", 114, 0.1324), ("H318", 414, 0.0152),
    ("Latin16195", 430, 0.0083), ("Latin6395", 622, 0.0583), ("Latin8236", 206, 0.0579), ("LaurPlut33.31", 201, 0.1370),
    ("LaurPlut39.34", 131, 0.1017), ("LaurPlut53.08", 216, 0.0073), ("LaurPlut53.09", 125, 0.0203), ("Mazarine915", 418, 0.0192),
    ("PalLat373", 432, 0.0202), ("Phi_10a135", 139, 0.0241), ("SBB_PK_Hdschr25", 234, 0.0023), ("UBL758", 469, 0.0306),
    ("WettF0015", 380, 0.0525),
    ("Latin-verse-pool (s32)", 492, 0.0941), ("cremma_prose15 (s18)", 773, 0.0078),
]
log: list[str] = []


def emit(s=""):
    print(s, flush=True)
    log.append(s)


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


def load_by_path(modname: str, path: Path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stub_match() -> str:
    if not STUB.exists():
        return "NO STUB"
    want = {}
    for ln in STUB.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        want[f.lstrip("*").strip()] = h
    bad = [f for f, h in want.items() if not (ROOT / f).exists() or sha256(ROOT / f) != h]
    return "True" if want and not bad else f"False (mismatch: {', '.join(bad) or 'empty stub'})"


def pct(vals, q):
    import numpy as np
    return float(np.percentile(np.array(vals, dtype=float), q))


FEAT = (lambda w: w[0])


def jsd_first(a2, lines) -> dict:
    raw, _ = a2.stats(lines, FEAT)
    nf = a2.null(lines, FEAT, n=JSD_NULL_N)[:, 0]
    return dict(raw=float(raw), null=float(nf.mean()), exc=float(raw - nf.mean()), lines=len(lines))


def draws(a2, lines, k) -> dict:
    rng = random.Random(SEED)
    raws, nulls, excs = [], [], []
    for _ in range(DRAWS):
        d = rng.sample(lines, k)
        jb = jsd_first(a2, d)
        raws.append(jb["raw"]); nulls.append(jb["null"]); excs.append(jb["exc"])
    return dict(k=k, raw_med=pct(raws, 50), null_med=pct(nulls, 50),
                exc_med=pct(excs, 50), exc_lo=pct(excs, 2.5), exc_hi=pct(excs, 97.5))


def position(exc, v) -> str:
    if v is None:
        return "n/a"
    if exc < v["exc_lo"]:
        return "below"
    if exc > v["exc_hi"]:
        return "above"
    return "inside"


def main() -> int:
    t0 = time.time()
    started = clock()
    emit("S44: Currier-A-only line-initial JSD excess draws vs the s18 Latin manuscripts (red-team request)")
    emit(f"run started {started}")
    emit(f"s44_a_only_line_initial.py sha256={sha256(SELF)}  prereg stub_match={stub_match()}")
    emit(f"estimator: a2_position.stats (feat w[0]) raw jsd_first; null = mean of a2_position.null n={JSD_NULL_N}; "
         f"excess = raw - null; {DRAWS} draws per size, random.Random({SEED}).sample re-seeded per size and language")
    emit(f"prediction (red team): A 773-line draw interval includes >= +{TOP_LATIN:.3f} -> 'A inside'. "
         f"Rule: 'A inside' if A 2.5 % bound < +{TOP_LATIN:.3f} at every available size >= {RULE_MIN_K}; else 'A outside'.")
    emit()

    R2 = load_by_path("run_v2_s44", ROOT / "scoreboard" / "run_v2.py")
    a2 = load_by_path("a2_position", ROOT / "a2_position.py")
    pages = R2.M.voynich_pages("eva")
    sets = {
        "all": [ln for q in pages for ln in q["lines"]],
        "A": [ln for q in pages if q["lang"] == "A" for ln in q["lines"]],
        "B": [ln for q in pages if q["lang"] == "B" for ln in q["lines"]],
    }
    for name, lines in sets.items():
        np_ = sum(1 for q in pages if name == "all" or q["lang"] == name)
        f = jsd_first(a2, lines)
        emit(f"ZL3b {name:3}: {np_} pages, {f['lines']} lines, {sum(len(l) for l in lines)} tokens; "
             f"jsd_first raw {f['raw']:.4f} null {f['null']:.4f} excess {f['exc']:+.4f}")
    emit("check: results_s32.txt ZL3b full excess +0.1740 (all pages)")
    emit()

    V = {"A": {}, "B": {}, "all": {}}
    emit(f"=== draws: {DRAWS} per size; excess median [2.5 %, 97.5 %]; margin = (2.5 % bound - {TOP_LATIN:.3f}) ===")
    emit(f"{'k':>4} | {'A excess':>30} {'A margin':>9} | {'B excess':>30} | {'all excess (check)':>30}")
    for k in SIZES:
        row = {}
        for name in ("A", "B", "all"):
            lines = sets[name]
            if len(lines) < k:
                V[name][k] = None
                row[name] = f"skipped: only {len(lines)} lines".rjust(30)
                continue
            if name == "all" and k != 773:
                V[name][k] = None
                row[name] = "-".rjust(30)
                continue
            v = draws(a2, lines, k)
            V[name][k] = v
            row[name] = f"{v['exc_med']:+.4f} [{v['exc_lo']:+.4f}, {v['exc_hi']:+.4f}]".rjust(30)
        am = V["A"][k]
        mg = f"{am['exc_lo'] - TOP_LATIN:+.4f}" if am else "n/a"
        emit(f"{k:4d} | {row['A']} {mg:>9} | {row['B']} | {row['all']}")
    if V["all"][773]:
        v = V["all"][773]
        emit(f"check: all-pages draw at 773 -> {v['exc_med']:+.4f} [{v['exc_lo']:+.4f}, {v['exc_hi']:+.4f}]; "
             f"results_s32.txt gives +0.1734 [+0.1528, +0.1980]")
    emit()

    emit("=== Latin rows (results_s18.txt lines 239-259 + s32 pooled rows) against the A and B draw intervals at the nearest draw size >= row lines (or the largest available) ===")
    emit(f"{'row':24} | {'lines':>5} | {'exc':>8} | {'A size':>6} {'A pos':>7} | {'B size':>6} {'B pos':>7}")
    for label, k, exc in S18_ROWS:
        out = f"{label:24} | {k:5d} | {exc:+8.4f}"
        for name in ("A", "B"):
            cand = [s for s in SIZES if s >= k and V[name][s] is not None]
            s = cand[0] if cand else max(s for s in SIZES if V[name][s] is not None)
            out += f" | {s:6d} {position(exc, V[name][s]):>7}"
        emit(out)
    emit()

    emit("=== READING (pre-registered rule) ===")
    rule_sizes = [k for k in SIZES if k >= RULE_MIN_K and V["A"][k] is not None]
    inside_flags = {k: V["A"][k]["exc_lo"] < TOP_LATIN for k in rule_sizes}
    for k in rule_sizes:
        emit(f"  A at {k}: 2.5 % bound {V['A'][k]['exc_lo']:+.4f} vs +{TOP_LATIN:.3f} -> {'below (inside)' if inside_flags[k] else 'at/above (outside)'}; "
             f"margin {V['A'][k]['exc_lo'] - TOP_LATIN:+.4f}")
    if V["A"][773] is not None:
        v = V["A"][773]
        emit(f"  prediction check (A at 773 includes >= +{TOP_LATIN:.3f}): interval [{v['exc_lo']:+.4f}, {v['exc_hi']:+.4f}] -> "
             f"{'includes' if v['exc_lo'] <= TOP_LATIN <= v['exc_hi'] else ('entirely above' if v['exc_lo'] > TOP_LATIN else 'entirely below')} -> "
             f"prediction {'CONFIRMED' if v['exc_lo'] < TOP_LATIN else 'FAILED'}")
    reading = "A inside" if rule_sizes and all(inside_flags.values()) else "A outside"
    emit(f"reading: {reading} (rule sizes {rule_sizes}; sizes with A 2.5 % bound below +{TOP_LATIN:.3f}: "
         f"{[k for k in rule_sizes if inside_flags[k]]})")
    for name in ("A", "B"):
        ks = [k for k in SIZES if V[name][k] is not None]
        if ks:
            k = max(ks)
            emit(f"  {name} largest size {k}: 2.5 % bound {V[name][k]['exc_lo']:+.4f}; highest Latin row +0.1370 (LaurPlut33.31); "
                 f"pooled Latin verse +0.0941; CREMMA prose pool +0.0078")
    emit()
    emit(f"elapsed {time.time() - t0:.1f} s")
    emit(f"run finished {clock()}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
