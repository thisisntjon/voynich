# Phase 2 plan — coupling, unit, power repair, v2.1 amendment

Stamped 2026-10-17 20:45 PDT from `date`. Linked from `workflow/PLAN.md` Phase 2. Investigation:
`workflow/research/phase-2.md`. Prior work folded in: `results_s2_u123_controls.txt` (U2a/U2b/U2c, U3a/U3b),
`results_s30_phase2_deltas.txt` (peer, pre-registered 20:19, hash OK: A/B stratified null at each half's size,
per-alphabet 41-page widths, ink-convention row), `results_n6_ab_split.txt`, `results_s15.txt`.

## What the investigation changed

1. **U2 is retired for both halves.** s30 Part 1: Currier A's coupling survives a (hand, section, slot) null at
   A's own size (104.8–105.4 % on three transliterations) and B's survives at 103.0–103.1 %. s30 Part 1B: a Latin
   herbal syllable table and a Dante-rank table drive +0.21 to +0.67 on both halves, so any skewed table is
   mechanical. s20 is therefore a filing-and-comparison step, not a new null.
2. **U3 has its table and widths.** s2 Part 3A (alphabets), s30 Part 2A (per-alphabet 41-page widths, v1
   estimator; ZL3b reproduces s15), s30 Part 2B (three space conventions motivated by o1's gap sizes). o1 emits
   no token stream or sidecar, so an ink-driven segmentation row does not exist and is not commissioned here.
3. **Hash ledger facts.** n5 and n6_ab_split stubs each carry a FAILED original line and an OK amendment line
   (post-crash amendments; results match the amended hash). p1_bifolio has no stub of its own; its script hash
   is recorded only in n3b's stub. results_n4.txt prints no hash. All other stubs verify.
4. **Phase 2 compute is about 12 minutes on one CPU.** No GPU, no NMF, no board-scale job.
5. **Peer activity to record, not adopt:** `results_s31_null_glyph_charwin.txt` (peer, 20:24) is a Phase 3
   entrant pre-test (null-glyph cipher + m5 line draws). It is not the Phase 3 "scored once" run under the
   20:02 stop rule and is filed as a pre-test only.

## Decisions taken (from the investigation's six)

1. s30 accepted as the filed A/B stratified null; s20 does not re-run it.
2. s20 real-line L range: the decision uses pooled rows (cremma_all, cremma_c15, cremma_prose15, and the four
   s17 verse/epic texts); per-manuscript rows at ≥5k tokens are reported beside (10 rows).
3. s22 files from disk (s2 3A, p2, s30 2A–2B); an o1 token stream is deferred to OPEN.
4. Currier-A rule: option B, drop m_final_enrich for A rows (A's enrichment widths are 14–19× at 11k tokens;
   A-derived bands would be bands from a target half, the REDTEAM #4 defect again).
5. BH family: the p-values Phase 2 prints (m ≈ 6), computed in s23 and written as a fixed P-VALUE LEDGER block;
   earlier p-values are listed in the ledger unranked with their floor flags.
6. p1_bifolio: n3b's stub entry accepted as its hash record; a retro stub is not "before the run" and is not
   written. s23 states this.

## Steps (done-when in brackets)

### s20 — Currier A/B on the coupling metrics vs s15 widths and real-line ranges
- `s20_ab_coupling_v2.py` (stub hashed first): six `run_v2.py` calls (`--voynich` and the RF1b/IT2a sidecars,
  `--lang A|B`, `--ranges s15_ranges.json`, `--out results_s20_<translit>_<half>.txt`), then a reader over
  `results_s17_*.json` and `results_s18_cremma_*.json` building the real-line L range for cross_excess_eva and
  x_edge_mi_word from the pooled rows, with per-manuscript ≥5k rows beside. Pre-registered reading: B is
  outside every real-line row on both metrics and A is inside the real-line range → "coupling anomaly is a
  B-text property"; if A is also outside → "whole-text property"; if B is inside → the coupling claim is
  withdrawn. Prints s30 Part 1 survival beside as the stratification record.
- [done when results_s20.txt holds the six rows, the real-line range, and the printed reading]

### s21 — Daybreak's within-line Moran I on real-line gibberish and CREMMA (reassigned prefix; Timm's bound is c-309)
- `s21_moran_realline.py` (stub hashed first): the within-line lag-1 word-length Moran I exactly as defined in
  the Codex lab `moran_ablation.py` (definition copied into the docstring with its path and sha256; the script
  is not imported from the external tree), with the line-shuffle null (999 draws, seed 20261017), on
  gib_realline_pooled, cremma_prose15, cremma_c15, cremma_all, the four s17 verse/epic sidecars, and ZL3b as the
  reproduction check (must reproduce 0.157 to three decimals or stop). Pre-registered reading: if real-line
  gibberish reaches ≥0.129 (Daybreak's control maximum) the "no meaningless model reproduces it" clause is
  withdrawn and O-043 narrows to human meaningless production; if it stays below, the gibberish row joins the
  control set and the clause stands.
- [done when results_s21.txt exists with the ZL3b reproduction line and the nine rows]

### s22 — fixed-unit filing
- No compute. CLAIMS rows from s2 Part 3A, results_p2.txt and s30 Parts 2A–2B; registry U3 line updated;
  OPEN row for an o1-derived token stream. [done when the rows exist and U3 reads "verified as a table"]

### s23 — power refile, hash ledger, m1 × 10 seeds, P-VALUE LEDGER
- `s23_power_hash_ledger.py` (stub hashed first): (a) sha256sum -c over every prereg stub on disk and a table
  (file, stub, status, amendment lines, missing-stub note for p1_bifolio and results_n4.txt); (b) m1 column
  test over seeds 0–9 via the pw_m1_column.py pattern, median and range of P, written to results_s23.txt;
  (c) power statements pulled from C-constraints §1 for c1 hand 2, m6 Lc/Ls, a3/d6, written as refiled rows;
  (d) the P-VALUE LEDGER with BH q=0.05 over the Phase 2 family and floor-bound entries marked.
- [done when results_s23.txt has the four blocks; LEARNINGS/CLAIMS rows updated; the five negatives read
  "underpowered" in the D-list]

### v2.1 — dated amendment
- `PREREG-v2.1.md` + `scoreboard/PREREG-v2.1.sha256` (covering PREREG-v2.1.md, run_v2.py unchanged
  7dfdc9f7…, s15_ranges.json, n7_gibberish_ranges.json, results_m4_phase1_board.json). Items: (1) ranges file
  = s15_ranges.json; (2) within-manuscript widths are the stated margins; (3) X family present, the eight
  jackknife extras no-weight; (4) U1 HOLDS recorded with the O-047 caveat; (5) Currier-A rule: m_final_enrich
  dropped for A rows; (6) BH q=0.05 reporting and a power statement with every negative; (7) s20's reading as
  the stated exception for A on the coupling metrics; (8) Phase 3 entrants scored once, all/A/B, with the
  handed-table metrics (cross_excess_eva, x_edge_mi_word) carrying no family weight and the pair judged on
  types, h2, line-edge vocabulary, CHARWIN, Moran I, F1 residual and NMI-h1.
- [done when both files exist and `sha256sum -c` passes]

## Order, concurrency, prefixes

s20, s21 and s23 are independent single-CPU runs of 1–10 minutes; run s23 first (ledger), then s20, then s21;
v2.1 last. No scoreboard.json writes. Prefixes s20–s23 are this session's (claimed 19:47); s21 is reassigned
from "Timm bound (done as c-309)" to the Moran cross-check, recorded in the PLAN prefix table.

## Roadmap deltas

- Phase 3 gains a constraint: the pair is judged on what the handed table does not fix (v2.1 item 8), and
  Moran I / CHARWIN now have a gibberish reference row (s21). The peer's s31 pre-test is recorded, not counted.
- Phase 4 unchanged.
