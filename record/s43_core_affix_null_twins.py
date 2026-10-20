"""S43: two cipher twins on the v2.1 board — cores-as-nulls (N1) and affixes-as-nulls (N2); scored once.

PRE-REGISTRATION (frozen in s43_core_affix_null_twins.prereg.sha256 before the run; PREREG-v2.1.md items 6-8 govern;
scoring library = s27_k4_bound.py imported unchanged, hash printed in the header; ranges s15_ranges.json; scorer
run_v2.score_one via s27.Board; sidecars under runs/s43/ only).  Mechanisms fixed before run, scored once.

Question: "Under the two-layer picture (A13/A14), which layer can carry a letter-level cipher and which can be nulls?
Does a cipher written in the affix layer with cores as nulls (N1), or in the core layer with affixes as nulls (N2),
reach CHARWIN, F1 and the within-line Moran I of the manuscript?"

Construction, per transliteration T in {ZL3b, RF1b, IT2a} (n1_habit_table.load through s27.load_T, which adds
para_start; nothing is tuned to CHARWIN, F1 or Moran I):
  Segmenter: scoreboard/metrics_new.SlotSegmenter fitted on all tokens of T (ZL3b: 28 prefix candidates + empty =
    29 prefix classes, 18 suffix candidates + empty = 19 suffix classes, 2,335 cores).  Inventories with token
    frequencies: pair_freq over (prefix, suffix) pairs as they co-occur in T's tokens (the "29 x 19 alphabet", only
    attested pairs), core_freq, prefix_freq, suffix_freq.
  Plaintext: k2.plaintext_streams(by) (Caesar / Augustine alternating per (hand, illus) key); the LETTER stream of
    each key = the letters a-z of its words concatenated (word boundaries not encoded; one cipher token per plaintext
    letter; this is the verbose shape of A11 at ~1 letter per token).
  Homophone table (random.Random(20261017), independent of the run seed): letters ranked by frequency in the whole
    letter stream; letter with share f gets k = max(1, round(lam * f * S)) homophone symbols, S = size of the symbol
    inventory (N1: attested affix pairs; N2: cores), drawn WITHOUT replacement across letters, each draw weighted by
    the symbol's token frequency (frequent letters are assigned first; when the inventory is exhausted later letters
    keep what they have, never fewer than 1).  Encoding a letter chooses among its homophones with weight = symbol
    frequency.
  N1 (cores-as-nulls): token = prefix + core + suffix, where (prefix, suffix) is the letter's homophone pair and the
    core is drawn from core_freq independently of everything (a null).
  N2 (affixes-as-nulls): token = prefix + core + suffix, where the core is the letter's homophone and prefix, suffix
    are drawn independently from prefix_freq and suffix_freq (nulls conditioned on nothing).
  Both twins keep T's page / line structure exactly (one token per manuscript token slot, per (hand, illus) key in
    page order); no line-edge pools, no reduplication rule, no edge table: jsd_first / p_init / coupling are what the
    mechanism gives (no weight claimed for them).
  Calibration: seed 0, lam by 14-step bisection on [0.02, 2.0] to T's manuscript type count; the evaluated lam with
    the closest type count is used; if every evaluated lam gives more types than the target this is reported as
    "calibration floor" and the closest value is used as pre-registered (n6 / s10 rule), never repaired by hand.
    Seeds 1-3 measure.  By construction the type count is dominated by the null layer's independent draws, so a
    floor is expected and is part of the result.
  Scoring (s27 library, as s10/s28): board rows full all/A/B and the 41 held-out pages via s27.Board (run_v2.score_one,
    s15_ranges.json, within-manuscript widths); extras CHARWIN (m3 page split), within-line Moran I (s21 estimator,
    999-draw line-shuffle null), F1 (n1.residual quires with its own 1000-draw interval) each with DELTA = twin -
    Voynich and a page-bootstrap (quires for F1) 95 % interval, B = 1000; "reached" = interval includes zero or lies
    above, "missed" = entirely below zero; NMI-h1 reported, not counted.  Majority over seeds 1-3 on ZL3b decides;
    RF1b / IT2a beside (UNSTABLE if the call flips).
  Predictions (fixed): neither twin orders its affix draws within a line (N1's pairs follow the Latin letter order,
    N2's affixes are i.i.d.), so BOTH twins are predicted to MISS Moran I.  The informative output is which twin
    reaches F1 and CHARWIN: N1 (cipher in the affixes) is predicted to reach F1 (letter-order carries into the affix
    pair sequence, as letter-level ciphers do) and N2 is predicted to miss F1 (its only ordered layer is the core
    stream, which in the manuscript sits below its shuffle baseline, A14); CHARWIN sign predicted positive for both
    (Voynich-derived pieces), reached/missed reported.
  Wall-clock guard: 35 min (s27.wall_guard with WALL_LIMIT_S overridden); ZL3b (both twins, seeds 1-3) runs first so
    a stop leaves the deciding transliteration complete; a stop is reported in the file.

Constraints: python -I, one CPU process, no GPU, no paid calls, no new data; sidecars only under runs/s43/.
Run: python -I s43_core_affix_null_twins.py          Writes: results_s43.txt (+ runs/s43/).
"""
from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

import k2_nomenclator as k2  # noqa: E402
import s27_k4_bound as L  # noqa: E402  (shared Phase 3 scoring library)
from scoreboard import metrics_new as M  # noqa: E402

SELF = ROOT / "s43_core_affix_null_twins.py"
STUB = ROOT / "s43_core_affix_null_twins.prereg.sha256"
OUT = ROOT / "results_s43.txt"
RUN_DIR = ROOT / "runs" / "s43"
TABLE_SEED = 20261017
LAM_LO, LAM_HI, STEPS = 0.02, 2.0, 14
SEEDS = (1, 2, 3)
WALL = 35 * 60
PRED = {"N1": {"CHARWIN": ("positive", None), "F1": ("reached", None), "MORAN": ("missed", None)},
        "N2": {"CHARWIN": ("positive", None), "F1": ("missed", None), "MORAN": ("missed", None)}}
L.WALL_LIMIT_S = WALL


def inventories(by):
    toks = [w for recs in by.values() for r in recs for w in r["words"]]
    seg = M.SlotSegmenter(toks)
    pair, core, pre, suf = Counter(), Counter(), Counter(), Counter()
    for w in toks:
        p, k, s = seg.segment(w)
        pair[(p, s)] += 1; core[k] += 1; pre[p] += 1; suf[s] += 1
    return seg, pair, core, pre, suf


def letter_streams(by):
    streams = k2.plaintext_streams(by, shuffle=False)
    return {k: [ch for w in v for ch in w if "a" <= ch <= "z"] for k, v in streams.items()}


def homophones(letters_freq, inv: Counter, lam):
    rng = random.Random(TABLE_SEED)
    total = sum(letters_freq.values())
    S = len(inv)
    avail = dict(inv)
    table = {}
    for ch, c in letters_freq.most_common():
        k = max(1, round(lam * (c / total) * S))
        got = []
        for _ in range(k):
            if not avail:
                break
            syms = list(avail); wts = [avail[s] for s in syms]
            s = rng.choices(syms, wts)[0]
            got.append((s, inv[s])); del avail[s]
        if not got:  # inventory exhausted: share the most frequent symbol (never zero homophones)
            s = inv.most_common(1)[0][0]; got = [(s, inv[s])]
        table[ch] = got
    return table


def gen_twin(by, streams, kind, table, core_f, pre_f, suf_f, seed):
    rng = random.Random(seed)
    its = {k: iter(v) for k, v in streams.items()}
    tw = {ch: ([s for s, _ in v], [c for _, c in v]) for ch, v in table.items()}
    cores, cw = list(core_f), list(core_f.values())
    pres, pw = list(pre_f), list(pre_f.values())
    sufs, sw = list(suf_f), list(suf_f.values())
    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            line = []
            for _ in r["words"]:
                try:
                    ch = next(its[(r["hand"], r["illus"])])
                except StopIteration:
                    its[(r["hand"], r["illus"])] = iter(streams[(r["hand"], r["illus"])]); ch = next(its[(r["hand"], r["illus"])])
                sym = rng.choices(*tw[ch])[0]
                if kind == "N1":
                    p, s = sym
                    k = rng.choices(cores, cw)[0]
                else:
                    k = sym
                    p = rng.choices(pres, pw)[0]; s = rng.choices(sufs, sw)[0]
                line.append((p + k + s) or "o")
            lines.append(dict(r, words=line))
        out[page] = lines
    return out


def n_types(by):
    return len(set(w for recs in by.values() for r in recs for w in r["words"]))


def main():
    t0 = time.time()
    lines_out = []

    def emit(s=""):
        print(s, flush=True)
        lines_out.append(s)

    def flush():
        OUT.write_text("\n".join(lines_out) + "\n", encoding="utf-8", newline="\n")

    L.header(emit, "S43: cores-as-nulls (N1) and affixes-as-nulls (N2) cipher twins on the v2.1 board, 3 T x seeds 1-3; mechanisms fixed before run, scored once", SELF, STUB)
    emit(f"k2 sha256={L.sha256(ROOT / 'k2_nomenclator.py')[:16]}...; metrics_new sha256={L.sha256(ROOT / 'scoreboard' / 'metrics_new.py')[:16]}...; wall guard {WALL} s")
    emit("predictions (ZL3b, majority of seeds 1-3): N1 CHARWIN positive, F1 reached, Moran missed; N2 CHARWIN positive, F1 missed, Moran missed")
    emit()
    board = L.Board(emit)
    cells, pvals = [], []
    calib = {}
    for T in L.TRANSLITS:
        by, n_exact, n_fb = L.load_T(T)
        ref = L.VoyRef(T, by)
        target = n_types(by)
        emit(f"=== {T}: {len(by)} pages, {sum(len(r['words']) for recs in by.values() for r in recs)} tokens, {target} types; para_start exact on {n_exact} pages, fallback {n_fb}; 41 held-out pages {len(ref.ids41)} ===")
        emit(f"Voynich {T} references: CHARWIN {ref.charwin:+.4f}  Moran I {ref.moran:+.4f} (line-shuffle q99 {ref.moran_null['q99']:+.4f}, p={ref.moran_null['p']:.3f})  "
             f"F1 {ref.f1v:+.4f} [{ref.f1ci[0]:+.4f}, {ref.f1ci[1]:+.4f}]  NMI-h1 {ref.nmi['obs']:.3f} (quire p {ref.nmi['pq']:.3f}, bifolio p {ref.nmi['pb']:.3f})")
        pvals.append(f"PVAL|voynich|{T}|0|moran_line_shuffle|{ref.moran_null['p']:.4f}|{1 / (L.N_DRAWS + 1):.4f}|reference row, not an entrant")
        board.hdr()
        board.block(f"Voynich {T}", ref.pages, ref.ids41)
        seg, pair_f, core_f, pre_f, suf_f = inventories(by)
        streams = letter_streams(by)
        lf = Counter(ch for v in streams.values() for ch in v)
        emit(f"construction {T}: SlotSegmenter {len(seg.prefixes)} prefix candidates (+empty -> {len(pre_f)} classes), {len(seg.suffixes)} suffix candidates (+empty -> {len(suf_f)} classes), "
             f"{len(core_f)} cores, {len(pair_f)} attested (prefix, suffix) pairs; Latin letter stream {sum(lf.values())} letters, {len(lf)} letters, "
             f"top {', '.join(f'{c}:{n}' for c, n in lf.most_common(6))}")
        for kind in ("N1", "N2"):
            inv = pair_f if kind == "N1" else core_f
            lo, hi, tried = LAM_LO, LAM_HI, []
            for _ in range(STEPS):
                lam = (lo + hi) / 2
                tab = homophones(lf, inv, lam)
                t = n_types(gen_twin(by, streams, kind, tab, core_f, pre_f, suf_f, seed=0))
                tried.append((abs(t - target), lam, t))
                lo, hi = (lam, hi) if t < target else (lo, lam)
            _, lam_c, t_c = min(tried)
            floor = all(t > target for _, _, t in tried)
            ceil = all(t < target for _, _, t in tried)
            calib[(T, kind)] = (lam_c, t_c, target, floor or ceil)
            tab = homophones(lf, inv, lam_c)
            emit(f"calibration {T} {kind} (seed 0): lam={lam_c:.4f} -> {t_c} types (target {target}, gap {100 * (t_c - target) / target:+.1f} %); "
                 f"{sum(len(v) for v in tab.values())} homophone symbols over {len(inv)} ({'pairs' if kind == 'N1' else 'cores'}); "
                 f"{'CALIBRATION FLOOR: every evaluated lam gives more types than the target; closest used as pre-registered; ' if floor else ''}"
                 f"{'CALIBRATION CEILING: every evaluated lam gives fewer types than the target; closest used; ' if ceil else ''}"
                 "steps " + " ".join(f"{l:.3f}:{t}" for _, l, t in tried))
            emit("  homophones (first 12 letters; N1 symbol = prefix|suffix): " +
                 " ".join(f"{ch}=[{','.join(('%s|%s' % s) if kind == 'N1' else s for s, _ in v)}]" for ch, v in list(tab.items())[:12]) + " ...")
            for s in SEEDS:
                L.wall_guard(t0, emit, flush)
                enc = gen_twin(by, streams, kind, tab, core_f, pre_f, suf_f, seed=s)
                name = f"s43_{kind}_{T}_s{s}"
                L.write_sidecar(RUN_DIR, name, enc)
                emit(f"--- {name} (seed {s}, lam {lam_c:.4f}): {n_types(enc)} types ---")
                board.hdr()
                board.block(name, L.pages_of(enc), ref.ids41)
                L.extras(emit, f"s43_{kind}", T, s, enc, ref, cells, pvals)
                emit(f"    elapsed {time.time() - t0:.0f}s")
                flush()
        emit()
    emit("=== PREDICTION CELLS (HOLD = observed majority call over seeds 1-3 equals the pre-registered prediction) ===")
    cell = {}
    for ln in lines_out:
        if ln.startswith("CELL|s43_"):
            f = ln.split("|")
            cell.setdefault((f[1], f[2], f[4]), []).append(f)
    summary = {}
    for kind in ("N1", "N2"):
        ent = f"s43_{kind}"
        n_hold = 0
        for metric in ("CHARWIN", "F1", "MORAN", "NMI"):
            calls_T = {}
            for T in L.TRANSLITS:
                fs = cell.get((ent, T, metric), [])
                if not fs:
                    continue
                rm = Counter(f[10] for f in fs).most_common(1)[0][0]
                sg = Counter(f[11].split("sign=")[1].split(";")[0] for f in fs if "sign=" in f[11]).most_common(1)[0][0] if any("sign=" in f[11] for f in fs) else None
                calls_T[T] = (rm, sg, [f[5] for f in fs], [f"[{f[8]},{f[9]}]" for f in fs])
            if not calls_T:
                emit(f"  {kind} {metric:8s}: no cells (stopped before this twin was scored)")
                continue
            if metric == "NMI":
                emit(f"  {kind} NMI-h1  : " + "; ".join(f"{T} {v[0]} {' '.join(v[2])}" for T, v in calls_T.items()) + " (reported, not counted)")
                continue
            p_main, _ = PRED[kind][metric]
            obs = {T: (v[1] if metric == "CHARWIN" else v[0]) for T, v in calls_T.items()}
            side = {T: (v[0] if metric == "CHARWIN" else v[1]) for T, v in calls_T.items()}
            hold = obs.get("ZL3b") == p_main
            n_hold += int(hold)
            unstable = [T for T in obs if T != "ZL3b" and obs[T] != obs["ZL3b"]]
            emit(f"  {kind} {metric:8s} predicted {p_main}; observed ZL3b {obs.get('ZL3b')} (beside: {side.get('ZL3b')}) -> {'HOLD' if hold else 'FAIL'}"
                 f"{'  UNSTABLE on ' + ','.join(unstable) if unstable else '  (same call on ' + ', '.join(T for T in obs if T != 'ZL3b') + ')' if len(obs) > 1 else '  (ZL3b only)'}"
                 f"; values ZL3b {' '.join(calls_T.get('ZL3b', ('', '', [], []))[2])} intervals {' '.join(calls_T.get('ZL3b', ('', '', [], []))[3])}")
            for T, v in calls_T.items():
                emit(f"PREDCELL|s43_{kind}|{T}|{metric}|{p_main}|{obs[T]}|{'HOLD' if obs[T] == p_main else 'FAIL'}|side_obs={side.get(T)}|values={','.join(v[2])}")
            summary.setdefault(kind, {})[metric] = (obs.get("ZL3b"), side.get("ZL3b"))
        emit(f"{ent}: {n_hold}/3 predictions hold on ZL3b (CHARWIN sign, F1, Moran); calibration " +
             "; ".join(f"{T} lam {c[0]:.4f} types {c[1]} (target {c[2]}){' FLOOR/CEIL' if c[3] else ''}" for (T, k), c in calib.items() if k == kind))
        emit(f"FAMILY|s43_{kind}|L-twin|{n_hold}")
    emit()
    emit("=== READING ===")
    for kind in ("N1", "N2"):
        s = summary.get(kind, {})
        emit(f"  {kind} ({'cipher in affixes, cores null' if kind == 'N1' else 'cipher in cores, affixes null'}): "
             f"CHARWIN {s.get('CHARWIN', ('n/a', ''))[1]} ({s.get('CHARWIN', ('n/a', ''))[0]}); F1 {s.get('F1', ('n/a',))[0]}; Moran {s.get('MORAN', ('n/a',))[0]}")
    both_miss_moran = all(summary.get(k, {}).get("MORAN", ("n/a",))[0] == "missed" for k in ("N1", "N2"))
    emit(f"  'both twins miss Moran' prediction: {'HOLDS' if both_miss_moran else 'FAILS or incomplete'}; "
         f"F1 reached by: {[k for k in ('N1', 'N2') if summary.get(k, {}).get('F1', ('n/a',))[0] == 'reached'] or 'neither'}; "
         f"CHARWIN reached by: {[k for k in ('N1', 'N2') if summary.get(k, {}).get('CHARWIN', ('n/a',))[1] == 'reached'] or 'neither'}")
    emit()
    L.power_lines(emit, list(lines_out))
    emit("=== p-values printed by this file ===")
    for p in pvals:
        emit(p)
    emit()
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "rows.json").write_text(json.dumps(board.rows, default=str), encoding="utf-8")
    emit(f"sidecars: {RUN_DIR} ({len(list(RUN_DIR.glob('*.meta.json')))} files); rows.json written there")
    emit(f"elapsed {time.time() - t0:.0f}s; run ended {L.clock()}")
    flush()


if __name__ == "__main__":
    main()
