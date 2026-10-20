"""S35: Phase 3 ledger (prefix moved from s33 at 21:34: s33 taken by a peer's s33_line_scales_interlock.py) and verdict (step 4, workflow/phases/phase-3.md; no new compute).

PRE-REGISTRATION (frozen in s35_phase3_ledger.prereg.sha256 before the run).
Reads results_s27.txt, results_s28.txt, results_s10.txt (their CELL| / PREDCELL| / FAMILY| / PVAL| lines) and prints:
  1. the prediction table (plan, "Pre-committed predictions") with HOLD / FAIL per cell for s10 (L) and s28 (G),
     ZL3b decision column, RF1b / IT2a beside, UNSTABLE marks; the s27 bound rows beside, no count;
  2. the verdict by the plan's rule (verbatim): the family whose three unbanded predictions (CHARWIN sign,
     F1 reached/missed, Moran reached/missed) all hold on untouched material, while the other family misses at
     least one, earns a "registered lean" (Tier 2 is explicitly not available from this pair). If both hold or
     both miss, the result is "tie at this design", and the roadmap's Phase 4 condition is not met;
  3. the Benjamini-Hochberg block, q = 0.05, over the round's p-values (PREREG-v2.1 item 6.2: every p-value the
     three result files print; seed replicates enter as one p = the median over seeds per (entrant, T, test);
     floor-bound p (p <= its exact / Monte-Carlo floor) listed unranked, "floor, not ranked", excluded from m;
     format of results_s23.txt block (d));
  4. a power line per negative (item 6.1): for every prediction cell observed "missed" (and every cell whose
     DELTA interval includes zero), the smallest |DELTA| detectable at power 0.8 = 2.8 x median bootstrap SE
     over the ZL3b measurement seeds, in the TEST / FILED / POWER / STATUS format;
  5. sha256sum -c of the three entrant stubs (s27, s28, s10) and of this file's own stub.
Writes ONLY results_s35.txt. CONSTRAINTS-MAP.md is NOT edited by this script (the plan's "CONSTRAINTS-MAP gains
the entrant rows" is left to the coordinator; the rows to add are printed at the end).
Run: python -I s35_phase3_ledger.py
"""
from __future__ import annotations

import hashlib
import re
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

SELF = ROOT / "s35_phase3_ledger.py"
STUB = ROOT / "s35_phase3_ledger.prereg.sha256"
OUT = ROOT / "results_s35.txt"
FILES = {"s27": ROOT / "results_s27.txt", "s28": ROOT / "results_s28.txt", "s10": ROOT / "results_s10.txt"}
STUBS = {k: ROOT / f"{v}.prereg.sha256" for k, v in
         {"s27": "s27_k4_bound", "s28": "s28_generator_mechanism", "s10": "s10_cipher_mechanism", "s35": "s35_phase3_ledger"}.items()}
Q = 0.05
PRED = {
    "s10": {"CHARWIN": "positive, missed", "F1": "reached", "MORAN": "missed, negative", "NMI": "below bar"},
    "s28": {"CHARWIN": "negative, missed", "F1": "missed", "MORAN": "missed, positive but below", "NMI": "below bar"},
}
VOY = {"CHARWIN": "+0.094", "F1": "+0.046 [0.036, 0.056]", "MORAN": "0.157 [0.109, 0.170]", "NMI": "0.275 (bar 0.206, 1/55 floor)"}


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def clock() -> str:
    try:
        r = subprocess.run(["date"], capture_output=True, text=True, timeout=10)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip() + " (`date`)"
    except Exception:  # noqa: BLE001
        pass
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " (datetime.now)"


def check_stub(stub: Path):
    """sha256sum -c if available, else the same check in Python (printed as such)."""
    if not stub.exists():
        return [f"{stub.name}: MISSING STUB"], False
    try:
        r = subprocess.run(["sha256sum", "-c", stub.name], cwd=ROOT, capture_output=True, text=True, timeout=30)
        if r.returncode in (0, 1) and r.stdout.strip():
            return [f"sha256sum -c {stub.name}: " + " | ".join(r.stdout.strip().splitlines())], r.returncode == 0
    except Exception:  # noqa: BLE001
        pass
    lines, ok = [], True
    for ln in stub.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        h, f = ln.split(None, 1)
        f = f.lstrip("*").strip()
        good = (ROOT / f).exists() and sha256(ROOT / f) == h
        ok &= good
        lines.append(f"(python sha256 check, sha256sum unavailable) {f}: {'OK' if good else 'FAILED'}")
    return lines, ok


def main():
    t0 = time.time()
    out = []

    def emit(s=""):
        print(s, flush=True)
        out.append(s)

    emit("S35: Phase 3 ledger (prefix moved from s33 at 21:34: s33 taken by a peer's s33_line_scales_interlock.py) and verdict (reads results_s27 / s28 / s10; no new compute)")
    emit(f"run started {clock()}")
    emit(f"s35_phase3_ledger.py sha256={sha256(SELF)}")
    texts = {}
    for k, p in FILES.items():
        if not p.exists():
            emit(f"MISSING {p.name}; ledger incomplete")
            texts[k] = ""
            continue
        texts[k] = p.read_text(encoding="utf-8")
        head = texts[k].splitlines()[:3]
        emit(f"read {p.name} sha256={sha256(p)}  | " + " | ".join(head[1:3]))
    emit()

    # ---- parse
    cells = defaultdict(list)      # (entrant, T, metric) -> list of field lists (per seed)
    predcells = {}                 # (prefix, T, metric) -> fields
    family = {}
    pvals = []
    for k, txt in texts.items():
        for ln in txt.splitlines():
            if ln.startswith("CELL|"):
                f = ln.split("|")
                cells[(f[1], f[2], f[4])].append(f)
            elif ln.startswith("PREDCELL|"):
                f = ln.split("|")
                predcells[(f[1], f[2], f[3])] = f
            elif ln.startswith("FAMILY|"):
                f = ln.split("|")
                family[f[1]] = (f[2], int(f[3]))
            elif ln.startswith("PVAL|"):
                f = ln.split("|")
                pvals.append((k, f[1], f[2], int(f[3]), f[4], float(f[5]), float(f[6]), f[7] if len(f) > 7 else ""))

    # ---- 1. prediction table
    emit("=== 1. PREDICTION TABLE (plan 'Pre-committed predictions'; decision column ZL3b, majority of seeds 1-3; RF1b / IT2a beside) ===")
    emit(f"{'metric':8s} {'Voynich':28s} | {'s10 (L) predicted':30s} {'ZL3b observed':22s} {'cell':5s} {'RF1b':10s} {'IT2a':10s} | "
         f"{'s28 (G) predicted':30s} {'ZL3b observed':22s} {'cell':5s} {'RF1b':10s} {'IT2a':10s}")
    holds = {"s10": {}, "s28": {}}
    for metric in ("CHARWIN", "F1", "MORAN", "NMI"):
        parts = [f"{metric:8s} {VOY[metric]:28s}"]
        for pre in ("s10", "s28"):
            z = predcells.get((pre, "ZL3b", metric))
            if z is None:
                parts.append(f"| {PRED[pre][metric]:30s} {'(no cell)':22s} {'n/a':5s} {'':10s} {'':10s}")
                holds[pre][metric] = None
                continue
            side = z[7].split("side_obs=")[1] if "side_obs=" in z[7] else ""
            obs = z[5] + (f", {side}" if side and side != "None" else "")
            cell_call = z[6]
            sides = []
            for T in ("RF1b", "IT2a"):
                o = predcells.get((pre, T, metric))
                sides.append("n/a" if o is None else (o[5] + ("" if o[5] == z[5] else " UNSTABLE")))
            parts.append(f"| {PRED[pre][metric]:30s} {obs:22s} {cell_call:5s} {sides[0]:10s} {sides[1]:10s}")
            holds[pre][metric] = cell_call == "HOLD"
        emit(" ".join(parts))
    emit("(NMI-h1 reported, not counted: 1/55 floor. CHARWIN cell = sign; Moran cell = reached/missed, sign beside; F1 cell = reached/missed.)")
    emit()
    emit("values behind the cells (ZL3b, seeds 1-3: value | DELTA [lo, hi] | call):")
    for pre, ent in (("s10", "s10_cipher"), ("s28", "s28_gen"), ("s27", "s27_k4"), ("s27", "s27_flow_cipher_layer")):
        for metric in ("CHARWIN", "F1", "MORAN", "NMI"):
            fs = cells.get((ent, "ZL3b", metric), [])
            if fs:
                emit(f"  {ent:22s} {metric:8s} " + "  ".join(f"s{f[3]}: {f[5]} Δ{f[7]} [{f[8]},{f[9]}] {f[10]}" for f in fs))
    emit()

    # ---- 2. verdict
    emit("=== 2. VERDICT (plan rule, verbatim in the docstring) ===")
    nL = sum(1 for m in ("CHARWIN", "F1", "MORAN") if holds["s10"].get(m))
    nG = sum(1 for m in ("CHARWIN", "F1", "MORAN") if holds["s28"].get(m))
    missL = [m for m in ("CHARWIN", "F1", "MORAN") if not holds["s10"].get(m)]
    missG = [m for m in ("CHARWIN", "F1", "MORAN") if not holds["s28"].get(m)]
    emit(f"s10 (L): {nL}/3 hold (fails: {', '.join(missL) or 'none'}); file FAMILY line: {family.get('s10')}")
    emit(f"s28 (G): {nG}/3 hold (fails: {', '.join(missG) or 'none'}); file FAMILY line: {family.get('s28')}")
    if nL == 3 and nG < 3:
        verdict = "registered lean toward L (cipher)"
    elif nG == 3 and nL < 3:
        verdict = "registered lean toward G (generation)"
    else:
        verdict = "tie at this design"
    emit(f"VERDICT: {verdict}")
    emit(f"Phase 4 trigger (plan: 's33 verdict = registered lean toward L', ledger now s35): {'MET' if verdict.endswith('(cipher)') else 'NOT MET'}; "
         f"Tier 2 not available from this pair (research §4); stop rule (PLAN 20:02): the pair is scored once, no re-tuning.")
    unstable = [(pre, T, m) for (pre, T, m), f in predcells.items() if T != "ZL3b" and predcells.get((pre, "ZL3b", m)) and f[5] != predcells[(pre, "ZL3b", m)][5]]
    emit(f"three-file robustness (v2 §2): {'all cells carry the same call on RF1b and IT2a' if not unstable else 'UNSTABLE cells: ' + ', '.join(f'{p} {t} {m}' for p, t, m in unstable)}")
    emit()
    emit("--- rule provenance (red-team addition relayed by the coordinator during the s10 run; the verdict rule itself is unchanged) ---")
    emit(f"{'rule used in this verdict':58s} | triggering result / document")
    for rule, src in (
        ("coupling (cross_excess_eva, x_edge_mi_word) no family weight; B row only", "results_s20.txt (PREREG-v2.1 item 5); s2 Part 2B, s30 Part 1B (handed tables regenerate coupling)"),
        ("m_final_enrich no weight for Currier-A rows", "results_n6_ab_split.txt line 17 (PREREG-v2.1 item 4); s30 stratification record"),
        ("CHARWIN / F1 / Moran I as the judged unbanded targets", "results_n5.txt (+0.094), results_n6.txt (F1 reopened), results_s21.txt (Moran); s31 pilot H2 (PREREG-v2.1 item 7)"),
        ("DELTA = entrant - Voynich with page bootstrap, reached/missed by interval", "workflow/phases/phase-3.md 'Pre-committed predictions' (coordinator addendum 20:58, workflow/research/phase-3.md §4)"),
        ("NMI-h1 reported, not counted (1/55 floor)", "results_n6.txt line 18; PREREG-v2.1 items 6.3 and 7.7"),
        ("jsd_first_fg / p_init_enrich fixed by the pools, no weight", "phase-3.md decision 4; workflow/research/phase-3.md §6 hazard 5 (s31 pools)"),
        ("board metrics judged on the 41 held-out pages", "results_s32.txt (A1 holds at >= 500 lines; verse separable at 41 pages); phase-3.md 'What changed' 2"),
        ("one BH family per round, power line per negative", "PREREG-v2.1 item 6 (results_s23.txt blocks (c), (d))"),
    ):
        emit(f"{rule:58s} | {src}")
    emit()
    emit("--- design provenance (red-team addition; read before the verdict) ---")
    emit("* The M5 edge pools (s31.build_m5_edge_pools) and the R_la_syll rank map (s31.build_latin_syllable_edge_table) were built")
    emit("  from the FULL page set of each transliteration, including the 41 held-out pages (s28_generator_mechanism.py construction")
    emit("  line, s10_cipher_mechanism.py construction line). The board rows on the 41 pages are therefore 'held-out for scoring,")
    emit("  not for pool construction'.")
    emit("* Both generators descend from the s31 pilot (results_s31_null_glyph_charwin.txt, one seed, full book): s28 reuses")
    emit("  gen_s31_generator_m5_direct verbatim; s10 keeps s31's line-edge draws, flow weight and reduplication rate.")
    emit("* The M2 mid-line fix (train on ws[1:-1]) was chosen after the pilot missed m_final_enrich (TEAM-HANDOFF line 70) and")
    emit("  pre-committed in workflow/phases/phase-3.md (decision 6) before this run; it was not chosen on this round's results.")
    emit("* Honest label for the round: 'mechanisms fixed after pilots, scored once', not 'scored once on untouched material'.")
    emit("* The three judged predictions (CHARWIN, F1, Moran I) are whole-book statistics with their own nulls (m3 page split,")
    emit("  quire split with within-line-shuffle correction, 999-draw line shuffle) and are unaffected by the 41-page split.")
    emit()

    # ---- 3. BH
    emit(f"=== 3. P-VALUE LEDGER  --  Phase 3 family = every p-value results_s27/s28/s10 print; Benjamini-Hochberg q = {Q} ===")
    emit("Seed replicates enter as one p (median over seeds per entrant x T x test); p <= its floor is 'floor, not ranked' and excluded from m.")
    groups = defaultdict(list)
    for (k, ent, T, seed, test, p, floor, note) in pvals:
        groups[(k, ent, T, test)].append((p, floor, seed, note))
    ranked, unranked = [], []
    for (k, ent, T, test), vs in sorted(groups.items()):
        p = statistics.median(v[0] for v in vs)
        floor = vs[0][1]
        label = f"{ent} {T} {test} (median of seeds {','.join(str(v[2]) for v in vs)})  [results_{k}.txt]"
        if p <= floor + 1e-12:
            unranked.append((p, floor, label))
        else:
            ranked.append((p, floor, label))
    ranked.sort()
    m = len(ranked)
    emit(f"m = {m} ranked p-values (q = {Q}); {len(unranked)} floor-bound entries listed unranked")
    emit(f"{'rank':>4s} {'raw_p':>8s} {'BH_cutoff':>10s} pass   floor      test  [source]")
    survivors = []
    for i, (p, floor, label) in enumerate(ranked, 1):
        cut = i / m * Q
        ok = p <= cut
        emit(f"{i:4d} {p:8.4f} {cut:10.4f} {'PASS' if ok else 'fail'}   {floor:<10.4f} {label}")
        if ok:
            survivors.append(i)
    # BH: all ranks up to the largest passing rank survive
    k_max = max(survivors) if survivors else 0
    emit(f"BH survivors at q={Q}: {'NONE' if not k_max else ', '.join(ranked[i - 1][2] for i in range(1, k_max + 1))}")
    for p, floor, label in unranked:
        emit(f"   -  {p:8.4f} {'floor':>10s} n/a    {floor:<10.4f} {label}  'floor, not ranked'")
    emit()

    # ---- 4. power lines
    emit("=== 4. POWER LINES (v2.1 item 6.1): one per negative prediction cell (observed 'missed') and per cell whose DELTA interval includes zero ===")
    for pre, ent in (("s10", "s10_cipher"), ("s28", "s28_gen")):
        for metric in ("CHARWIN", "F1", "MORAN"):
            fs = cells.get((ent, "ZL3b", metric), [])
            if not fs:
                continue
            ses = [float(f[11].split("se=")[1].split(";")[0]) for f in fs if "se=" in f[11]]
            se = statistics.median(ses) if ses else float("nan")
            deltas = [float(f[7]) for f in fs]
            los = [float(f[8]) for f in fs]
            his = [float(f[9]) for f in fs]
            calls = [f[10] for f in fs]
            neg = calls.count("missed") >= 2
            null_diff = sum(1 for lo, hi in zip(los, his) if lo <= 0 <= hi) >= 2
            if not (neg or null_diff):
                continue
            mde = 2.8 * se
            emit(f"TEST    : {pre} ({ent}) ZL3b {metric}: DELTA = entrant - Voynich, page bootstrap B=1000, seeds 1-3")
            emit(f"FILED   : DELTA per seed " + ", ".join(f"{d:+.4f} [{lo:+.4f}, {hi:+.4f}] {c}" for d, lo, hi, c in zip(deltas, los, his, calls))
                 + f"; majority {'missed (negative: entrant does not reproduce Voynich)' if neg else 'reached with interval including zero (no detected difference)'}")
            emit(f"POWER   : smallest |DELTA| detectable at power 0.8 (two-sided 0.05) = 2.8 x median bootstrap SE {se:.4f} = {mde:.4f}; median observed |DELTA| {statistics.median(abs(d) for d in deltas):.4f}")
            emit(f"STATUS  : {'POWERED (the observed shortfall exceeds the minimum detectable difference)' if statistics.median(abs(d) for d in deltas) >= mde else 'UNDERPOWERED for a difference of the observed size'}")
            emit()

    # ---- 5. stub checks
    emit("=== 5. STUB CHECKS (sha256sum -c) ===")
    all_ok = True
    for k, stub in STUBS.items():
        lines, ok = check_stub(stub)
        all_ok &= ok
        for ln in lines:
            emit(ln)
    emit(f"all stubs verify: {all_ok}")
    emit()

    # ---- rows for CONSTRAINTS-MAP (not written by this script)
    emit("=== rows for workflow/CONSTRAINTS-MAP.md (to be added by the coordinator; this script edits nothing else) ===")
    for pre, name in (("s10", "s10 cipher mechanism (L)"), ("s28", "s28 generation mechanism (G)")):
        cellstr = "; ".join(f"{m} {PRED[pre][m]} -> {'HOLD' if holds[pre].get(m) else 'FAIL'}" for m in ("CHARWIN", "F1", "MORAN"))
        emit(f"| {name} | {cellstr} | NMI-h1 {predcells.get((pre, 'ZL3b', 'NMI'), ['', '', '', '', '', 'n/a'])[5]} (not counted) | results_{pre}.txt, results_s35.txt | verdict: {verdict} |")
    emit()
    emit(f"elapsed {time.time() - t0:.1f}s; run ended {clock()}")
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
