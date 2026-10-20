"""S28: the generation-family mechanism (G), scored once (Phase 3 step 2, workflow/phases/phase-3.md).

PRE-REGISTRATION (frozen in s28_generator_mechanism.prereg.sha256 before the run; PREREG-v2.1.md item 7 governs;
scoring library = s27_k4_bound.py, imported unchanged, its hash printed in the header).

Mechanism (fixed here, nothing tuned to CHARWIN, F1 or Moran I), per transliteration T in {ZL3b, RF1b, IT2a}:
  s31_null_glyph_charwin_pilot.gen_s31_generator_m5_direct (verbatim): c2.Gen copy/lexicon/mutate (p_seed 0.6,
  p_mut 0.6, M_CAND 8, flow beta 1.5), N2 habit table p_hab = 0.04 (n4.habit_table_over over g.types + the
  synthetic forms, seed 20261017), 7k glyph lexicon = c2 seed lexicon (300 types) + round(lam * N_key) synthetic
  forms per (hand, section) key sampled from the word-internal order-2 glyph model M2 (n6.fit_char_markov2 /
  n6.sample_word_m2, length 2..10, not a manuscript type, linked in g.nb to a parent of the key's base lexicon,
  n6.synth_glyph_forms rule re-implemented here ONLY to swap the M2 training set), the handed edge table
  R_la_syll (s31.build_latin_syllable_edge_table: Latin Macer syllables rank-mapped to T's characters, the same
  object handed to s10), and the M5 line-edge pools inherited from s31 verbatim (s31.build_m5_edge_pools:
  para-initial / ordinary line-initial / line-final Voynich tokens with counts; draw rates 0.55 line-initial,
  0.48 line-final; jsd_first_fg and p_init_enrich are therefore "fixed by the pools, no weight").
  M2 MID-LINE FIX (decision 6, applied to BOTH s28 and s10): M2 is fitted on the token-weighted frequencies of
  the mid-line words ws[1:-1] of every line (line-initial and line-final words excluded), not on all words.
  Calibration: seed 0 only, p_hab = 0, lam by 14-step bisection on [0, 3.0] to T's manuscript type count; the
  evaluated lam whose type count is closest is used (n6 rule). Seeds 1, 2, 3 measure (p_hab 0.04).
  No plaintext (self-sourced). Shared with s10: table, pools, M2 model + fix, calibration target, seeds.

Plan table rows carried verbatim (workflow/phases/phase-3.md):
| G (generation) | **s28**: c2 copy/mutate + N2 habit table + 7k glyph lexicon (n6), same `R_la_syll`, same pools, same M2 glyph model, same calibration | none (self-sourced) | copy-mutate rhythm → Moran I; no plaintext → F1 at the n6 level |
| metric | Voynich | s28 (G) predicts | if the prediction fails |
| CHARWIN (held-out character model minus word list) | +0.094 | negative, missed (pilot −0.021; n5 G max +0.038) | a family reaching +0.094 ± its interval is the first entrant to do so; recorded as "reached" for that family |
| F1 held-out word-order residual | +0.046 [0.036, 0.056] | missed (n6 +0.027 [0.016, 0.039]) | L missing F1 removes the one quantity the cipher family was expected to hold |
| within-line Moran I (s21 estimator, line-shuffle null 999) | 0.157 [0.109, 0.170] | missed, positive but below (G max 0.129) | a family reaching 0.157 closes O-043 for that mechanism |
| NMI-h1 (hand-1 section vocabulary) | 0.275 (bar 0.206, 1/55 floor) | below bar (n6 0.087) | reaching it would be a surprise for either; reported, not counted (floor) |
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

Constraints: python -I, one CPU process, no GPU, no paid calls, no new data; sidecars only under runs/s28/;
scoreboard/scoreboard.json never written; wall-clock guard 40 min. Writes: results_s28.txt (+ runs/s28/).
Run: python -I s28_generator_mechanism.py
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

import c2_section_generator as c2  # noqa: E402
import n4_habit7k as n4  # noqa: E402
import n6_habit7k_glyph as n6  # noqa: E402
import s27_k4_bound as L  # noqa: E402  (shared Phase 3 scoring library)
import s31_null_glyph_charwin_pilot as s31  # noqa: E402

SELF = ROOT / "s28_generator_mechanism.py"
STUB = ROOT / "s28_generator_mechanism.prereg.sha256"
OUT = ROOT / "results_s28.txt"
RUN_DIR = ROOT / "runs" / "s28"
SEED = L.SEED
LAM_HI, LAM_STEPS = 3.0, 14
P_HAB = 0.04
SEEDS = (1, 2, 3)
PRED = {"CHARWIN": ("negative", "missed"), "F1": ("missed", None), "MORAN": ("missed", "positive"), "NMI": ("below", None)}


def midline_freq(by):
    """M2 mid-line fix: token-weighted frequencies of ws[1:-1] of every line."""
    c = Counter()
    for recs in by.values():
        for r in recs:
            c.update(r["words"][1:-1])
    return c


def synth_glyph_forms_mid(g, by, m2):
    """n6.synth_glyph_forms with the mid-line M2 handed in (everything else identical)."""
    rng = random.Random(SEED)
    ntok = Counter((r["hand"], r["illus"]) for recs in by.values() for r in recs for _ in r["words"])
    made, out, nb_links = set(), {}, {}
    for i, key in enumerate(n4.keys_in_order(by)):
        base = [w for w in g.lexicon(random.Random(SEED + i))[0] if w in g.nb]
        forms, want = [], round(LAM_HI * ntok[key])
        while len(forms) < want:
            v = n6.sample_word_m2(m2, rng)
            if v and v not in g.freq and v not in made:
                made.add(v)
                forms.append(v)
                parent = rng.choice(base)
                nb_links[v] = g.nb[parent]
        out[key] = forms
    return out, ntok, nb_links


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

    L.header(emit, "S28: generation mechanism (c2 + N2 habit + 7k glyph lexicon, R_la_syll, s31 pools, M2 mid-line fix), 3 T x seeds 1-3 (phase-3.md step s28)", SELF, STUB)
    emit(f"s31 pilot (pools / table / generator source) sha256={L.sha256(ROOT / 's31_null_glyph_charwin_pilot.py')[:16]}...; n6 sha256={L.sha256(ROOT / 'n6_habit7k_glyph.py')[:16]}...")
    emit(f"predictions (ZL3b, majority of seeds 1-3): CHARWIN negative & missed; F1 missed; Moran missed & positive; NMI-h1 below {L.NMI_BAR}")
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
        # shared construction
        R_la = s31.build_latin_syllable_edge_table(by)
        pools = s31.build_m5_edge_pools(by)
        fmid = midline_freq(by)
        m2 = n6.fit_char_markov2(fmid)
        g = c2.Gen(by)
        forms, ntok, nb_links = synth_glyph_forms_mid(g, by, m2)
        g.nb.update(nb_links)
        emit(f"construction {T}: M2 fitted on {sum(fmid.values())} mid-line tokens ({len(fmid)} types); pools para {len(pools[0][0])} / init {len(pools[1][0])} / final {len(pools[2][0])} types; "
             f"{sum(len(v) for v in forms.values())} synthetic forms available over {len(forms)} keys")

        def lex_fn(key, rng, lam):
            ws, wt = g.lexicon(rng)
            ex = forms[key][: round(lam * ntok[key])]
            return ws + ex, wt + [1] * len(ex)

        # calibration: seed 0, p_hab 0, lam bisection to the type count
        lo, hi, tried = 0.0, LAM_HI, []
        for _ in range(LAM_STEPS):
            lam = (lo + hi) / 2
            by0 = s31.gen_s31_generator_m5_direct(g, by, lambda k, r, _l=lam: lex_fn(k, r, _l), pools, R_la, {}, p_hab=0.0, seed=0)
            t = n_types(by0)
            tried.append((abs(t - target), lam, t))
            lo, hi = (lam, hi) if t < target else (lo, lam)
        _, lam_cal, t_cal = min(tried)
        calib[T] = (lam_cal, t_cal, target)
        emit(f"calibration {T} (seed 0, p_hab 0): lam={lam_cal:.4f} -> {t_cal} types (target {target}, gap {100 * (t_cal - target) / target:+.1f} %); steps " + " ".join(f"{l:.3f}:{t}" for _, l, t in tried))
        extra = [f for k in forms for f in forms[k][: round(lam_cal * ntok[k])]]
        table = n4.habit_table_over(g.types + extra, g.tw + [1.0] * len(extra))
        for s in SEEDS:
            L.wall_guard(t0, emit, flush)
            gb = s31.gen_s31_generator_m5_direct(g, by, lambda k, r: lex_fn(k, r, lam_cal), pools, R_la, table, p_hab=P_HAB, seed=s)
            name = f"s28_gen_{T}_s{s}"
            L.write_sidecar(RUN_DIR, name, gb)
            emit(f"--- {name} (seed {s}, lam {lam_cal:.4f}, p_hab {P_HAB}): {n_types(gb)} types ---")
            board.hdr()
            board.block(name, L.pages_of(gb), ref.ids41)
            L.extras(emit, "s28_gen", T, s, gb, ref, cells, pvals)
            emit(f"    elapsed {time.time() - t0:.0f}s")
            flush()
        emit()
    # ---- prediction cells
    emit("=== PREDICTION CELLS (HOLD = observed majority call over seeds 1-3 equals the pre-registered prediction) ===")
    cell = {}
    for ln in lines_out:
        if ln.startswith("CELL|s28_gen|"):
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
            side = {T: v[1] for T, v in calls_T.items()}
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
            emit(f"PREDCELL|s28|{T}|{metric}|{p_main}|{obs[T]}|{'HOLD' if obs[T] == p_main else 'FAIL'}|side_pred={p_side};side_obs={side.get(T)}|values={','.join(v[2])}")
        verdict_rows.append((metric, hold))
    n_hold = sum(h for m, h in verdict_rows if m != "NMI")
    emit(f"s28 (G): {n_hold}/3 unbanded predictions hold on ZL3b (CHARWIN sign, F1, Moran); NMI-h1 reported not counted; calibration " +
         "; ".join(f"{T} lam {c[0]:.3f} types {c[1]} (target {c[2]})" for T, c in calib.items()))
    emit(f"FAMILY|s28|G|{n_hold}")
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
