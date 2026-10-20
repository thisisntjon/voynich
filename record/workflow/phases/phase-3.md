# Phase 3 plan (redesign) — one mechanism per family, predictions first

Stamped 2026-10-17 21:14 PDT from `date`. Linked from `workflow/PLAN.md` Phase 3. Investigation:
`workflow/research/phase-3.md` (21:03). Jon's gate choice 21:05: "Redesign: predictions first." Governing
rule: PREREG-v2.1.md item 7 (frozen 20:55). Constraints that bind this plan: `workflow/CONSTRAINTS-MAP.md`
A1–A12 with the s32 size clause on A1 and the s24 kill (D-046).

## What changed since the 21:03 investigation

1. **s24 done (21:11, 7 s):** musical/hybrid notation NOT SUPPORTED on all three predictions and all three
   transliterations. The two-family framing (L cipher vs G generation) is the live framing; liturgy, conlang
   and copied-without-understanding remain untested but no current statistic motivates them.
2. **s32 done (21:08):** A1 holds against verse at ≥500 lines; two single short Latin verse/formulaic hands sit
   inside the Voynich draw interval at 114–201 lines. Consequence: edge metrics are judged on 41 held-out
   pages (~770 lines), where verse is separable; no entrant gets credit for line edges (A2, A4, v2.1 item 8).
3. **The entrant pair as planned ties on 7 of 10 judged quantities by construction** (research §4). This plan
   therefore does not ask the pair to "win the board". It asks each family's one mechanism to make three
   numerical predictions in advance and scores them once.

## The design

**One mechanism per family, fixed before the stub is frozen; nothing tuned to CHARWIN, F1 or Moran I.**

| family | mechanism (s-prefix) | plaintext / lexicon | what the mechanism fixes by itself |
|---|---|---|---|
| L (cipher) | **s10**: letter-level verbose homophonic cipher with nulls, period profile (3 homophones per vowel, 2 per consonant; null rate by one seed-0 bisection to the type count); handed edge table `R_la_syll`; m5 line-edge pools | k2 Latin stream (Caesar/Augustine per hand × illustration) | Latin word-length sequence → Moran I; letter-level → no section vocabulary (NMI-h1 predicted below bar) |
| G (generation) | **s28**: c2 copy/mutate + N2 habit table + 7k glyph lexicon (n6), same `R_la_syll`, same pools, same M2 glyph model, same calibration | none (self-sourced) | copy-mutate rhythm → Moran I; no plaintext → F1 at the n6 level |
| bound rows (no count) | **s27**: K4 lossy nomenclator at its middle setting; `flow_cipher_layer` (real Naibbe key, Voynich-measured tables) | — | what even a circular word code reaches |

Shared construction (same table, pools, M2 model, calibration target, seeds) is declared in both stubs, and the
M2 mid-line fix (`ws[1:-1]`) is applied to both or neither (decision: both; stated in each stub).

## Pre-committed predictions (frozen in each stub's docstring before `sha256sum`)

Values are the Voynich references from CONSTRAINTS-MAP (ZL3b; RF1b/IT2a beside). Δ = entrant − Voynich with a
page-bootstrap 95 % interval (B = 1000; pages for CHARWIN and Moran I, quires for F1 as n6). "Reached" =
interval includes zero or lies above; "missed" = interval entirely below zero. Per-dataset own-null q99 lines
are printed, not decisive (Sylvie's relayed note; research §4 rule).

| metric | Voynich | s10 (L) predicts | s28 (G) predicts | if the prediction fails |
|---|---|---|---|---|
| CHARWIN (held-out character model minus word list) | +0.094 | positive, missed (pilot +0.057; letter-level ciphers give positive sign) | negative, missed (pilot −0.021; n5 G max +0.038) | a family reaching +0.094 ± its interval is the first entrant to do so; recorded as "reached" for that family |
| F1 held-out word-order residual | +0.046 [0.036, 0.056] | reached (letter-level codes give +0.04–0.05: Naibbe, K4) | missed (n6 +0.027 [0.016, 0.039]) | L missing F1 removes the one quantity the cipher family was expected to hold |
| within-line Moran I (s21 estimator, line-shuffle null 999) | 0.157 [0.109, 0.170] | missed, negative (Latin word lengths: prose15 −0.033) | missed, positive but below (G max 0.129) | a family reaching 0.157 closes O-043 for that mechanism |
| NMI-h1 (hand-1 section vocabulary) | 0.275 (bar 0.206, 1/55 floor) | below bar (letter-level) | below bar (n6 0.087) | reaching it would be a surprise for either; reported, not counted (floor) |
| board metrics on the 41 held-out pages (types_25k, h2, jsd_first_fg, p_init, m_final, redup; s15 widths) | s15_ranges g1_heldout_41 | in for calibrated ones; jsd_first/p_init fixed by the pools (no weight); m_final in only with the M2 fix | same | a tight-out on an unhanded metric is a kill-candidate under v2 §7 arithmetic, recorded per row |
| coupling (cross_excess, edge MI) | B 0.232 / 0.240 | overshoot (+0.6) | overshoot (+0.6) | no weight (handed table, A4) |

**Verdict rule (pre-registered):** the family whose three unbanded predictions (CHARWIN sign, F1 reached/missed,
Moran reached/missed) all hold on untouched material, while the other family misses at least one, earns a
"registered lean" (Tier 2 is explicitly not available from this pair; research §4). If both hold or both miss,
the result is "tie at this design", and the roadmap's Phase 4 condition ("Phase 3 favours the cipher twin")
is not met. BH q=0.05 over the round's p-values; every negative carries a power line (v2.1 item 6).

## Steps (done-when in brackets)

### s27 — bound rows (first, ~20 min)
K4 middle setting × 3 transliterations × 3 seeds + `flow_cipher_layer`, v2.1 rows all/A/B full book, 41-page
board rows, CHARWIN, Moran I, F1, NMI-h1. [done when results_s27.txt has the bound lines per target metric]

### s28 — generation mechanism (~25 min)
Stub frozen with the predictions table verbatim; seed 0 calibration (lam bisection to each T's type count),
seeds 1–3 measurement; sidecars in `runs/s28/`. [done when results_s28.txt prints the three Δ intervals, the
board rows and the own-null lines, and the stub verifies]

### s10 — cipher mechanism (~25 min)
Same stub discipline; letter-level design (decision 1 of research §"Decisions": period-plausible, L-107);
`flow_cipher_layer` as the family anchor only (no decode step). [done when results_s10.txt prints the same
blocks as s28]

### s33 — ledger and verdict (~5 min, no new compute)
Reads results_s27/s28/s10; prints the prediction table with hold/fail per cell, the verdict by the rule above,
BH block, power lines, hash checks of the three stubs. [done when results_s33.txt exists and CONSTRAINTS-MAP
gains the entrant rows]

## Decisions taken (from the investigation's six)
1. s10 letter-level (period-plausible); NMI-h1 predicted below bar for both, reported not counted.
2. `flow_cipher_layer` and K4 are bound rows; no decode in Phase 3.
3. Board metrics on the 41 held-out pages; CHARWIN/F1/Moran/NMI on the full book with their own nulls.
4. s31's Voynich edge pools inherited; jsd_first/p_init declared "fixed by the pools, no weight".
5. Δ-with-page-bootstrap rule adopted as written above.
6. M2 mid-line fix applied to both entrants.

## Order, concurrency, prefixes, cost
Sequential on one CPU: s27 → s28 → s10 → s33, ~75 min total; one board-scale job at a time; no GPU; no
scoreboard.json writes; sidecars under `runs/<prefix>/`. Prefixes s10, s27, s28 are claimed (TEAM-HANDOFF
line 266); s33 to be claimed at launch. Hazards carried from research §6.

## Roadmap deltas
- Phase 4's trigger is now "s33 verdict = registered lean toward L" (not "favours the cipher twin" on the
  board). A tie or a lean toward G ends the computational effort as the 20:02 stop rule says, and Phase 4
  keeps only its human-input items (O-021, O-018, O-030, O-016).
- Success criterion 6's Tier-2 clause is downgraded to "registered lean" for this effort; stated in PLAN.md.
