"""S10: the cipher-family mechanism (L), scored once (Phase 3 step 3, workflow/phases/phase-3.md).

PRE-REGISTRATION (frozen in s10_cipher_mechanism.prereg.sha256 before the run; PREREG-v2.1.md item 7 governs;
scoring library = s27_k4_bound.py, imported unchanged, its hash printed in the header).

Mechanism (decision 1: letter-level, period-plausible, L-107; nothing tuned to CHARWIN, F1 or Moran I), per
transliteration T in {ZL3b, RF1b, IT2a}:
  Plaintext: k2.plaintext_streams(by) (Caesar / Augustine alternating per (hand, illus) key, word tokens).
  Letter-level verbose homophonic alphabet with the period profile: 3 homophones per vowel (a e i o u y),
  2 per consonant. Homophone pieces are T's word-internal glyph pieces ranked by token frequency, unigram
  glyphs first then attested bigrams (the "verbose" pieces); letters are ranked by plaintext frequency and take
  their pieces in that order from the top of the remaining piece list (frequent letters -> frequent short
  pieces, as k2 / k4 rank-map codewords). The piece inventory is Voynich-derived exactly as s28's M2 lexicon
  is (shared construction). A cipher word = the Latin word encoded letter by letter (word boundaries kept), so
  the word-length sequence is Latin's -> the Moran I prediction.
  Choice: per plaintext word, M_CAND = 8 candidate encodings, each letter's homophone drawn with base weight =
  piece token frequency (f3.cipher_stream convention); the candidate is chosen with weight R_la_syll(prev_last,
  first)^1.5 (flow beta 1.5, inherited). Immediate reduplication 0.0085 (s31:276).
  Nulls: with probability p_null per word slot an M2 null WORD is written instead (n6.sample_word_m2 from the
  word-internal order-2 model, M2 MID-LINE FIX applied as in s28: fitted on ws[1:-1] of every line) and the
  plaintext word is NOT consumed (15th-century null insertion). p_null is the one calibrated parameter: seed 0,
  14-step bisection on [0, 0.6] to T's manuscript type count; the evaluated p_null whose type count is closest
  is used (n6 rule). The Latin stream has ~9.1k types for ~35k tokens (> 7,025), so the bisection may sit at
  its floor; that is reported as "calibration floor", never repaired by hand.
  Line edges inherited from s31 verbatim: M5 pools (s31.build_m5_edge_pools: para-initial pool for paragraph
  first words; ordinary line-initial pool drawn with 0.55; line-final pool with 0.48; M_CAND 8 candidates
  weighted R_la_syll^1.5) -> jsd_first_fg and p_init_enrich "fixed by the pools, no weight".
  Edge table: R_la_syll = s31.build_latin_syllable_edge_table(by), the same object handed to s28.
  Seeds: 0 calibrates, 1-3 measure. flow_cipher_layer is the family anchor only (scored in s27; no decode).

Plan table rows carried verbatim (workflow/phases/phase-3.md):
| L (cipher) | **s10**: letter-level verbose homophonic cipher with nulls, period profile (3 homophones per vowel, 2 per consonant; null rate by one seed-0 bisection to the type count); handed edge table `R_la_syll`; m5 line-edge pools | k2 Latin stream (Caesar/Augustine per hand × illustration) | Latin word-length sequence → Moran I; letter-level → no section vocabulary (NMI-h1 predicted below bar) |
| metric | Voynich | s10 (L) predicts | if the prediction fails |
| CHARWIN (held-out character model minus word list) | +0.094 | positive, missed (pilot +0.057; letter-level ciphers give positive sign) | a family reaching +0.094 ± its interval is the first entrant to do so; recorded as "reached" for that family |
| F1 held-out word-order residual | +0.046 [0.036, 0.056] | reached (letter-level codes give +0.04–0.05: Naibbe, K4) | L missing F1 removes the one quantity the cipher family was expected to hold |
| within-line Moran I (s21 estimator, line-shuffle null 999) | 0.157 [0.109, 0.170] | missed, negative (Latin word lengths: prose15 −0.033) | a family reaching 0.157 closes O-043 for that mechanism |
| NMI-h1 (hand-1 section vocabulary) | 0.275 (bar 0.206, 1/55 floor) | below bar (letter-level) | reaching it would be a surprise for either; reported, not counted (floor) |
| board metrics on the 41 held-out pages (types_25k, h2, jsd_first_fg, p_init, m_final, redup; s15 widths) | s15_ranges g1_heldout_41 | in for calibrated ones; jsd_first/p_init fixed by the pools (no weight); m_final in only with the M2 fix | a tight-out on an unhanded metric is a kill-candidate under v2 §7 arithmetic, recorded per row |
| coupling (cross_excess, edge MI) | B 0.232 / 0.240 | overshoot (+0.6) | no weight (handed table, A4) |

DELTA / page-bootstrap rule (plan, verbatim): Δ = entrant − Voynich with a page-bootstrap 95 % interval (B = 1000;
pages for CHARWIN and Moran I, quires for F1 as n6). "Reached" = interval includes zero or lies above; "missed" =
interval entirely below zero. Per-dataset own-null q99 lines are printed, not decisive.
Cell calls: ZL3b, majority over seeds 1-3; CHARWIN cell = sign (reached/missed reported beside), F1 cell =
reached/missed, Moran cell = reached/missed (sign reported beside), NMI-h1 = below/reaches 0.206 (not counted).
RF1b / IT2a beside; UNSTABLE if the majority call flips on another file. HOLD = observed call equals the prediction.
Verdict rule (plan, verbatim; applied in s35): the family whose three unbanded predictions (CHARWIN sign,
F1 reached/missed, Moran reached/missed) all hold on untouched material, while the other family misses at
least one, earns a "registered lean" (Tier 2 is explicitly not available from this pair). If both hold or
both miss, the result is "tie at this design". BH q=0.05 over the round's p-values; every negative carries a
power line (v2.1 item 6).

Constraints: python -I, one CPU process, no GPU, no paid calls, no new data; sidecars only under runs/s10/;
scoreboard/scoreboard.json never written; wall-clock guard 40 min. Writes: results_s10.txt (+ runs/s10/).
Run: python -I s10_cipher_mechanism.py
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

import k2_nomenclator as k2  # noqa: E402
import n6_habit7k_glyph as n6  # noqa: E402
import s27_k4_bound as L  # noqa: E402  (shared Phase 3 scoring library)
import s31_null_glyph_charwin_pilot as s31  # noqa: E402

SELF = ROOT / "s10_cipher_mechanism.py"
STUB = ROOT / "s10_cipher_mechanism.prereg.sha256"
OUT = ROOT / "results_s10.txt"
RUN_DIR = ROOT / "runs" / "s10"
SEED = L.SEED
BETA, M_CAND = 1.5, 8
P_REDUP = 0.0085
P_INIT, P_FIN = 0.55, 0.48
VOWELS = set("aeiouy")
NULL_HI, NULL_STEPS = 0.6, 14
SEEDS = (1, 2, 3)
PRED = {"CHARWIN": ("positive", "missed"), "F1": ("reached", None), "MORAN": ("missed", "negative"), "NMI": ("below", None)}


def midline_freq(by):
    c = Counter()
    for recs in by.values():
        for r in recs:
            c.update(r["words"][1:-1])
    return c


def homophone_table(by, streams):
    """Letter -> [(piece, base weight)]: 3 pieces per vowel, 2 per consonant, from T's ranked glyph pieces."""
    uni, big = Counter(), Counter()
    for recs in by.values():
        for r in recs:
            for w in r["words"]:
                uni.update(w)
                big.update(w[i:i + 2] for i in range(len(w) - 1))
    pieces = [(p, c) for p, c in uni.most_common()] + [(p, c) for p, c in big.most_common()]
    letters = Counter(ch for v in streams.values() for w in v for ch in w)
    table, it = {}, iter(pieces)
    for ch, _ in letters.most_common():
        k = 3 if ch in VOWELS else 2
        table[ch] = [next(it) for _ in range(k)]
    return table, len(uni), len(big), letters


def gen_s10_cipher(by, streams, table, m2, pools, R_tab, p_null, seed):
    rng = random.Random(seed)
    para_pool, init_pool, fin_pool = pools
    its = {k: iter(v) for k, v in streams.items()}
    pw = {ch: ([p for p, _ in v], [c for _, c in v]) for ch, v in table.items()}

    def encode(word):
        return "".join(rng.choices(*pw[ch])[0] for ch in word if ch in pw) or "o"

    out = {}
    for page, recs in by.items():
        lines = []
        for r in recs:
            n = len(r["words"])
            line = []
            for i in range(n):
                prev_last = line[-1][-1] if line else None
                if i == 0 and r["para_start"]:
                    line.append(rng.choices(para_pool[0], para_pool[1])[0])
                    continue
                if i == 0 and rng.random() < P_INIT:
                    cands = rng.choices(init_pool[0], init_pool[1], k=M_CAND)
                    wts = [(R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0 for c in cands]
                    line.append(rng.choices(cands, wts)[0])
                    continue
                if i == n - 1 and n >= 3 and rng.random() < P_FIN:
                    cands = rng.choices(fin_pool[0], fin_pool[1], k=M_CAND)
                    wts = [(R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0 for c in cands]
                    line.append(rng.choices(cands, wts)[0])
                    continue
                if line and rng.random() < P_REDUP:
                    line.append(line[-1])
                    continue
                if rng.random() < p_null:
                    w_null = n6.sample_word_m2(m2, rng)
                    line.append(w_null if w_null else "o")
                    continue
                plain_w = next(its[(r["hand"], r["illus"])])
                cands = [encode(plain_w) for _ in range(M_CAND)]
                wts = [(R_tab(prev_last, c[0]) ** BETA) if prev_last else 1.0 for c in cands]
                line.append(rng.choices(cands, wts)[0])
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

    L.header(emit, "S10: cipher mechanism (letter-level verbose homophonic + M2 null words, k2 Latin, R_la_syll, s31 pools, M2 mid-line fix), 3 T x seeds 1-3 (phase-3.md step s10)", SELF, STUB)
    emit(f"s31 pilot (pools / table source) sha256={L.sha256(ROOT / 's31_null_glyph_charwin_pilot.py')[:16]}...; k2 sha256={L.sha256(ROOT / 'k2_nomenclator.py')[:16]}...")
    emit(f"predictions (ZL3b, majority of seeds 1-3): CHARWIN positive & missed; F1 reached; Moran missed & negative; NMI-h1 below {L.NMI_BAR}")
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
        R_la = s31.build_latin_syllable_edge_table(by)
        pools = s31.build_m5_edge_pools(by)
        fmid = midline_freq(by)
        m2 = n6.fit_char_markov2(fmid)
        streams = k2.plaintext_streams(by, shuffle=False)
        allw = [w for v in streams.values() for w in v]
        table, n_uni, n_big, letters = homophone_table(by, streams)
        emit(f"construction {T}: Latin stream {len(allw)} tokens, {len(set(allw))} types, mean length {sum(map(len, allw)) / len(allw):.2f}; "
             f"{len(table)} letters, {sum(len(v) for v in table.values())} homophone pieces from {n_uni} unigram + {n_big} bigram glyph pieces "
             f"({sum(1 for v in table.values() for p, _ in v if len(p) == 1)} unigram, {sum(1 for v in table.values() for p, _ in v if len(p) == 2)} bigram); "
             f"M2 fitted on {sum(fmid.values())} mid-line tokens; pools para {len(pools[0][0])} / init {len(pools[1][0])} / final {len(pools[2][0])} types")
        emit("  homophones: " + " ".join(f"{ch}=[{','.join(p for p, _ in v)}]" for ch, v in table.items()))
        lo, hi, tried = 0.0, NULL_HI, []
        for _ in range(NULL_STEPS):
            p = (lo + hi) / 2
            by0 = gen_s10_cipher(by, streams, table, m2, pools, R_la, p, seed=0)
            t = n_types(by0)
            tried.append((abs(t - target), p, t))
            lo, hi = (p, hi) if t < target else (lo, p)
        _, p_cal, t_cal = min(tried)
        floor = all(t > target for _, _, t in tried)
        calib[T] = (p_cal, t_cal, target, floor)
        emit(f"calibration {T} (seed 0): p_null={p_cal:.5f} -> {t_cal} types (target {target}, gap {100 * (t_cal - target) / target:+.1f} %)"
             f"{'; CALIBRATION FLOOR: every evaluated p_null gives more types than the target (Latin stream types > manuscript types); the closest evaluated value is used as pre-registered' if floor else ''}; "
             "steps " + " ".join(f"{p:.4f}:{t}" for _, p, t in tried))
        for s in SEEDS:
            L.wall_guard(t0, emit, flush)
            enc = gen_s10_cipher(by, streams, table, m2, pools, R_la, p_cal, seed=s)
            name = f"s10_cipher_{T}_s{s}"
            L.write_sidecar(RUN_DIR, name, enc)
            emit(f"--- {name} (seed {s}, p_null {p_cal:.5f}): {n_types(enc)} types ---")
            board.hdr()
            board.block(name, L.pages_of(enc), ref.ids41)
            L.extras(emit, "s10_cipher", T, s, enc, ref, cells, pvals)
            emit(f"    elapsed {time.time() - t0:.0f}s")
            flush()
        emit()
    emit("=== PREDICTION CELLS (HOLD = observed majority call over seeds 1-3 equals the pre-registered prediction) ===")
    cell = {}
    for ln in lines_out:
        if ln.startswith("CELL|s10_cipher|"):
            f = ln.split("|")
            cell.setdefault((f[2], f[4]), []).append(f)
    verdict_rows = []
    for metric in ("CHARWIN", "F1", "MORAN", "NMI"):
        calls_T = {}
        for T in L.TRANSLITS:
            fs = cell.get((T, metric), [])
            if not fs:
                continue
            rm = Counter(f[10] for f in fs).most_common(1)[0][0]
            sg = Counter(f[11].split("sign=")[1].split(";")[0] for f in fs if "sign=" in f[11]).most_common(1)[0][0] if any("sign=" in f[11] for f in fs) else None
            calls_T[T] = (rm, sg, [f[5] for f in fs], [f"[{f[8]},{f[9]}]" for f in fs])
        p_main, p_side = PRED[metric]
        if metric == "CHARWIN":
            obs = {T: v[1] for T, v in calls_T.items()}
            side = {T: v[0] for T, v in calls_T.items()}
        elif metric == "MORAN":
            obs = {T: v[0] for T, v in calls_T.items()}
            side = {T: ("negative" if v[1] == "non-positive" else v[1]) for T, v in calls_T.items()}
        else:
            obs = {T: v[0] for T, v in calls_T.items()}
            side = {}
        hold = obs.get("ZL3b") == p_main
        unstable = [T for T in obs if T != "ZL3b" and obs[T] != obs["ZL3b"]]
        side_ok = (side.get("ZL3b") == p_side) if p_side else None
        emit(f"  {metric:8s} predicted {p_main}{(' & ' + p_side) if p_side else ''}; observed ZL3b {obs.get('ZL3b')}{(' & ' + str(side.get('ZL3b'))) if side else ''} "
             f"-> {'HOLD' if hold else 'FAIL'}{'' if side_ok is None else (' (side prediction ' + ('holds' if side_ok else 'fails') + ')')}"
             f"{'  UNSTABLE on ' + ','.join(unstable) if unstable else '  (same call on ' + ', '.join(T for T in obs if T != 'ZL3b') + ')'}"
             f"; values ZL3b {' '.join(calls_T.get('ZL3b', ('', '', [], []))[2])} intervals {' '.join(calls_T.get('ZL3b', ('', '', [], []))[3])}")
        for T, v in calls_T.items():
            emit(f"PREDCELL|s10|{T}|{metric}|{p_main}|{obs[T]}|{'HOLD' if obs[T] == p_main else 'FAIL'}|side_pred={p_side};side_obs={side.get(T)}|values={','.join(v[2])}")
        verdict_rows.append((metric, hold))
    n_hold = sum(h for m, h in verdict_rows if m != "NMI")
    emit(f"s10 (L): {n_hold}/3 unbanded predictions hold on ZL3b (CHARWIN sign, F1, Moran); NMI-h1 reported not counted; calibration " +
         "; ".join(f"{T} p_null {c[0]:.5f} types {c[1]} (target {c[2]}){' FLOOR' if c[3] else ''}" for T, c in calib.items()))
    emit(f"FAMILY|s10|L|{n_hold}")
    emit()
    L.power_lines(emit, list(lines_out))
    emit("=== p-values printed by this file (round family members for s35; floor-bound = 'floor, not ranked') ===")
    for p in pvals:
        emit(p)
    emit()
    (RUN_DIR / "rows.json").write_text(json.dumps(board.rows, default=str), encoding="utf-8")
    emit(f"sidecars: {RUN_DIR} ({len(list(RUN_DIR.glob('*.meta.json')))} files); rows.json written there")
    emit(f"elapsed {time.time() - t0:.0f}s; run ended {L.clock()}")
    flush()


if __name__ == "__main__":
    main()
