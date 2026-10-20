"""s20 — Currier A/B on the coupling metrics vs s15 widths and real-line ranges
(workflow/phases/phase-2.md step s20; investigation workflow/research/phase-2.md §1).

PRE-REGISTRATION (frozen in s20_ab_coupling_v2.prereg.sha256 before any run_v2 call; nothing below
changes after results are seen).

Decision metrics: cross_excess_eva and x_edge_mi_word (the two coupling keys of the v2 scorer).

Runs (unchanged scorer, scoreboard/run_v2.py; python -I; one process at a time; ~20 s each):
  python -I scoreboard/run_v2.py --voynich --lang A --ranges s15_ranges.json --out results_s20_ZL3b_A.txt
  python -I scoreboard/run_v2.py --voynich --lang B --ranges s15_ranges.json --out results_s20_ZL3b_B.txt
  python -I scoreboard/run_v2.py --meta data/translit/RF1b.meta.json --lang A --n-sample 40000
                                 --ranges s15_ranges.json --out results_s20_RF1b_A.txt      (and B)
  python -I scoreboard/run_v2.py --meta data/translit/IT2a.meta.json --lang A --n-sample 40000
                                 --ranges s15_ranges.json --out results_s20_IT2a_A.txt      (and B)
  --n-sample 40000 on the sidecar runs so that neither half is capped (B is ~23k tokens, under the
  25k default anyway; --voynich is never capped). The six rows are read from <out>.json ["row"].

Real-line L range (the decision range), per metric: min..max over the POOLED real-line rows, native
only (no _relined8, no _marks):
  results_s18_cremma_all.json, results_s18_cremma_c15.json, results_s18_cremma_prose15.json,
  results_s17_gib_realline_pooled.json, results_s17_mhg_nibelungenlied.json,
  results_s17_oldfrench_roland.json, results_s17_occitan_croisade.json, results_s17_italian_dante.json
(phase-2.md "Decisions taken" item 2). A pooled row whose metric is None is listed as NA and skipped
for that metric. Per-manuscript CREMMA rows (results_s18_cremma_<ms>.json, native) with tokens >= 5000
are REPORTED BESIDE the range, not included in it (the sub-5k rows inflate both ways; x_edge_mi_word
is None on most per-manuscript rows because the extras step died on small manuscripts, results_s18:309).

Pre-registered reading (evaluated per transliteration; "inside" = min <= value <= max of the pooled
real-line range; "outside" = below min or above max, direction printed):
  * B outside the real-line range on both metrics AND A inside on both
        -> "coupling anomaly is a B-text property";
  * A and B both outside on both metrics
        -> "whole-text property";
  * B inside on either metric
        -> "coupling claim withdrawn";
  * anything else
        -> "mixed, reported as is".
The filed reading is the one shared by all three transliterations (ZL3b, RF1b, IT2a); if they
disagree, the filed reading is "mixed, reported as is" with the per-transliteration readings listed.

Also printed, no decision attached: the s15 within_manuscript 95 % half-width (hi95 - lo95)/2 for
both metrics from s15_ranges.json, and whether |A - B| exceeds one half-width per transliteration;
the m4-derived s15 L range (s15_ranges.json["ranges"][metric]["L"]) in/out for each row as context;
h2, types_25k, jsd_first_fg per row for context; and the s30 Part 1 survival numbers copied verbatim
from results_s30_phase2_deltas.txt lines 3-14 (the filed A/B stratified null; s20 does not re-run it,
"Decisions taken" item 1).

Run:   python -I s20_ab_coupling_v2.py [--reuse]   (--reuse skips run_v2 where results_s20_<t>_<h>.json exists)
Writes: results_s20_<translit>_<half>.txt/.json (six, via run_v2 --out), results_s20.txt. Nothing else.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RANGES = ROOT / "s15_ranges.json"
S30 = ROOT / "results_s30_phase2_deltas.txt"
OUT = ROOT / "results_s20.txt"
STUB = ROOT / "s20_ab_coupling_v2.prereg.sha256"
TRANSLIT = ["ZL3b", "RF1b", "IT2a"]
HALVES = ["A", "B"]
SIDECAR = {"RF1b": ROOT / "data" / "translit" / "RF1b.meta.json",
           "IT2a": ROOT / "data" / "translit" / "IT2a.meta.json"}
METRICS = ["cross_excess_eva", "x_edge_mi_word"]
CONTEXT = ["h2", "types_25k", "jsd_first_fg"]
POOLED = ["results_s18_cremma_all.json", "results_s18_cremma_c15.json", "results_s18_cremma_prose15.json",
          "results_s17_gib_realline_pooled.json", "results_s17_mhg_nibelungenlied.json",
          "results_s17_oldfrench_roland.json", "results_s17_occitan_croisade.json",
          "results_s17_italian_dante.json"]
FLOOR = 5000
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
    except Exception:
        pass
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now; `date` unavailable)"


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


def fmt(v, nd=4):
    if v is None:
        return "NA"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def run_v2(translit: str, half: str, out_txt: Path):
    cmd = [sys.executable, "-I", str(ROOT / "scoreboard" / "run_v2.py")]
    if translit == "ZL3b":
        cmd += ["--voynich"]
    else:
        cmd += ["--meta", str(SIDECAR[translit]), "--n-sample", "40000"]
    cmd += ["--lang", half, "--ranges", str(RANGES), "--out", str(out_txt)]
    emit(f"  $ {' '.join(Path(c).name if i == 0 else c for i, c in enumerate(cmd))}")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        emit(r.stdout[-2000:])
        emit(r.stderr[-2000:])
        raise SystemExit(f"run_v2 failed on {translit} {half} (exit {r.returncode})")
    head = [ln for ln in r.stdout.splitlines() if ln.startswith("# pages=")]
    emit(f"    {head[0] if head else '(no page header line)'}")


def load_row(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))["row"]


def pos(v, lo, hi):
    """inside / below / above the [lo, hi] range; NA if any piece is missing."""
    if v is None or lo is None or hi is None:
        return "NA"
    if v < lo:
        return "below"
    if v > hi:
        return "above"
    return "inside"


def reading(a_pos: dict, b_pos: dict) -> str:
    """Pre-registered reading from per-metric positions ('inside'/'below'/'above'/'NA')."""
    if any(p == "NA" for p in list(a_pos.values()) + list(b_pos.values())):
        return "mixed, reported as is (a position is NA)"
    b_out = all(p != "inside" for p in b_pos.values())
    a_in = all(p == "inside" for p in a_pos.values())
    a_out = all(p != "inside" for p in a_pos.values())
    if any(p == "inside" for p in b_pos.values()):
        return "coupling claim withdrawn"
    if b_out and a_in:
        return "coupling anomaly is a B-text property"
    if b_out and a_out:
        return "whole-text property"
    return "mixed, reported as is"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--reuse", action="store_true", help="skip run_v2 where results_s20_<t>_<h>.json exists")
    args = ap.parse_args(argv)

    if not RANGES.exists():
        raise SystemExit(f"STOP: {RANGES.name} absent; nothing scored or written.")
    for t, p in SIDECAR.items():
        if not p.exists():
            raise SystemExit(f"STOP: sidecar {p} absent; nothing scored or written.")
    missing = [f for f in POOLED if not (ROOT / f).exists()]
    if missing:
        raise SystemExit(f"STOP: pooled real-line rows missing: {missing}; nothing scored or written.")

    started = clock()
    emit("=== s20: Currier A/B on the coupling metrics vs s15 widths and real-line ranges ===")
    emit(f"run started {started}")
    emit(f"script: s20_ab_coupling_v2.py sha256 {sha256(Path(__file__).resolve())}; stub_match={stub_match()}")
    emit(f"ranges: {RANGES.name} sha256 {sha256(RANGES)}")
    emit(f"scorer: scoreboard/run_v2.py sha256 {sha256(ROOT / 'scoreboard' / 'run_v2.py')}")
    emit(f"decision metrics: {', '.join(METRICS)}; real-line range = min..max over pooled native rows "
         f"({len(POOLED)} files); per-manuscript CREMMA rows with tokens >= {FLOOR} reported beside")
    emit()

    # ---------------------------------------------------------------- six run_v2 calls
    emit("--- run_v2 calls (python -I scoreboard/run_v2.py; one process at a time) ---")
    rows: dict[tuple[str, str], dict] = {}
    for t in TRANSLIT:
        for h in HALVES:
            out_txt = ROOT / f"results_s20_{t}_{h}.txt"
            out_json = out_txt.with_suffix(".json")  # run_v2 writes args.out.with_suffix(".json")
            if args.reuse and out_json.exists():
                emit(f"  (reuse) {out_json.name}")
            else:
                run_v2(t, h, out_txt)
            rows[(t, h)] = load_row(out_json)
    emit()

    # ---------------------------------------------------------------- s15 widths and m4 L ranges
    R = json.loads(RANGES.read_text(encoding="utf-8"))
    wm = R.get("within_manuscript", {})
    hw = {}
    for m in METRICS:
        w = wm.get(m)
        hw[m] = (w["hi95"] - w["lo95"]) / 2 if w and w.get("hi95") is not None and w.get("lo95") is not None else None
    m4L = {m: R["ranges"].get(m, {}).get("L") for m in METRICS}

    # ---------------------------------------------------------------- real-line range from pooled rows
    pooled = []
    for f in POOLED:
        r = load_row(ROOT / f)
        pooled.append(dict(file=f, name=r.get("name"), tokens=r.get("tokens"),
                           **{m: r.get(m) for m in METRICS}))
    rl = {}
    for m in METRICS:
        vals = [(p[m], p["name"]) for p in pooled if p[m] is not None]
        if vals:
            lo = min(vals)
            hi = max(vals)
            rl[m] = dict(min=lo[0], min_member=lo[1], max=hi[0], max_member=hi[1], n=len(vals))
        else:
            rl[m] = dict(min=None, min_member=None, max=None, max_member=None, n=0)

    permss = []
    for f in sorted(ROOT.glob("results_s18_cremma_*.json")):
        n = f.name
        if n.endswith("_marks.json") or "_relined8" in n or n in POOLED:
            continue
        r = load_row(f)
        if (r.get("tokens") or 0) >= FLOOR:
            permss.append(dict(file=n, name=r.get("name"), tokens=r.get("tokens"), **{m: r.get(m) for m in METRICS}))

    # ---------------------------------------------------------------- six rows
    emit("--- the six A/B rows (run_v2 .json 'row'; decision metrics, then context) ---")
    emit(f"{'translit':6} {'half':4} {'tokens':>7} {'pages':>5} | {'cross_excess_eva':>16} {'x_edge_mi_word':>14} | "
         f"{'h2':>7} {'types_25k':>9} {'jsd_first_fg':>12} | m4-L cross / edge")
    for t in TRANSLIT:
        for h in HALVES:
            r = rows[(t, h)]
            m4pos = [pos(r.get(m), m4L[m]["min"], m4L[m]["max"]) if m4L[m] else "NA" for m in METRICS]
            emit(f"{t:6} {h:4} {fmt(r.get('tokens')):>7} {fmt(r.get('pages')):>5} | "
                 f"{fmt(r.get('cross_excess_eva')):>16} {fmt(r.get('x_edge_mi_word')):>14} | "
                 f"{fmt(r.get('h2')):>7} {fmt(r.get('types_25k')):>9} {fmt(r.get('jsd_first_fg')):>12} | "
                 f"{m4pos[0]} / {m4pos[1]}")
    emit(f"m4-derived s15 L ranges (context only): " + "; ".join(
        f"{m} L {fmt(m4L[m]['min'])}..{fmt(m4L[m]['max'])} (n={m4L[m]['n']})" if m4L[m] else f"{m} L n/a" for m in METRICS))
    emit()

    # ---------------------------------------------------------------- s15 half-widths
    emit("--- s15 within_manuscript 95 % half-widths (hi95-lo95)/2, ZL3b 41-page subsets, s15_ranges.json ---")
    for m in METRICS:
        w = wm.get(m, {})
        emit(f"{m}: hw={fmt(hw[m])} (lo95 {fmt(w.get('lo95'))}, hi95 {fmt(w.get('hi95'))}, median {fmt(w.get('median'))}, "
             f"n_splits {w.get('n_splits')})")
    for t in TRANSLIT:
        parts = []
        for m in METRICS:
            a, b = rows[(t, 'A')].get(m), rows[(t, 'B')].get(m)
            if a is None or b is None or hw[m] is None:
                parts.append(f"{m}: |A-B|=NA")
            else:
                d = abs(a - b)
                parts.append(f"{m}: |A-B|={d:.4f} = {d / hw[m]:.1f} hw -> {'> one half-width' if d > hw[m] else '<= one half-width'}")
        emit(f"{t}: " + "; ".join(parts))
    emit()

    # ---------------------------------------------------------------- real-line range
    emit("--- real-line L range: pooled native rows (the decision range) ---")
    emit(f"{'row':24} {'tokens':>7} {'>=5k':>5} | {'cross_excess_eva':>16} {'x_edge_mi_word':>14} | file")
    for p in pooled:
        emit(f"{p['name']:24} {fmt(p['tokens']):>7} {'yes' if (p['tokens'] or 0) >= FLOOR else 'NO':>5} | "
             f"{fmt(p['cross_excess_eva']):>16} {fmt(p['x_edge_mi_word']):>14} | {p['file']}")
    for m in METRICS:
        emit(f"real-line range {m}: {fmt(rl[m]['min'])} ({rl[m]['min_member']}) .. {fmt(rl[m]['max'])} "
             f"({rl[m]['max_member']}); n={rl[m]['n']} of {len(pooled)} pooled rows carry the metric")
    emit()
    emit(f"--- per-manuscript CREMMA rows with tokens >= {FLOOR} (reported beside, NOT in the range) ---")
    if permss:
        for p in permss:
            parts = []
            for m in METRICS:
                parts.append(f"{m}={fmt(p[m])} ({pos(p[m], rl[m]['min'], rl[m]['max'])} pooled range)")
            emit(f"{p['name']:24} tokens={p['tokens']} | " + "; ".join(parts))
    else:
        emit("(none)")
    emit(f"{len(permss)} per-manuscript rows at >= {FLOOR} tokens")
    emit()

    # ---------------------------------------------------------------- s30 Part 1 beside
    emit("--- s30 Part 1 survival (filed A/B stratified null; copied verbatim from results_s30_phase2_deltas.txt lines 3-14) ---")
    if S30.exists():
        emit(f"results_s30_phase2_deltas.txt sha256 {sha256(S30)}")
        s30 = S30.read_text(encoding="utf-8", errors="replace").splitlines()
        for i in range(2, min(14, len(s30))):
            emit(f"  s30:{i + 1}: {s30[i]}")
    else:
        emit("results_s30_phase2_deltas.txt absent")
    emit()

    # ---------------------------------------------------------------- reading
    emit("--- pre-registered reading (positions vs the pooled real-line range) ---")
    per_t = {}
    for t in TRANSLIT:
        a_pos = {m: pos(rows[(t, 'A')].get(m), rl[m]['min'], rl[m]['max']) for m in METRICS}
        b_pos = {m: pos(rows[(t, 'B')].get(m), rl[m]['min'], rl[m]['max']) for m in METRICS}
        per_t[t] = reading(a_pos, b_pos)
        emit(f"{t}: A " + ", ".join(f"{m} {fmt(rows[(t, 'A')].get(m))} {a_pos[m]}" for m in METRICS)
             + " | B " + ", ".join(f"{m} {fmt(rows[(t, 'B')].get(m))} {b_pos[m]}" for m in METRICS)
             + f" -> {per_t[t]}")
    uniq = set(per_t.values())
    filed = per_t[TRANSLIT[0]] if len(uniq) == 1 else "mixed, reported as is (transliterations disagree: " + \
        "; ".join(f"{t}: {v}" for t, v in per_t.items()) + ")"
    emit(f"READING: {filed}")
    emit()
    done = all(rows[(t, h)].get(m) is not None for t in TRANSLIT for h in HALVES for m in METRICS)
    emit(f"done-when (s20): results_s20.txt holds the six rows, the real-line range, and the printed reading -> "
         f"{'MET' if done else 'NOT MET (a decision metric is NA)'}")
    emit(f"run finished {clock()}")
    OUT.write_text("\n".join(log) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
