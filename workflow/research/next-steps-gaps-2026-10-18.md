# Next experiments, ranked by the gaps in the map (2026-10-18 12:08 PDT, clock read with `date`)

Written by a voynich-08 subagent, read-only over the project except this file. Inputs: `workflow/FINDINGS-MAP.md`
(generated 11:24), `workflow/TRIANGULATION.md`, `workflow/PLAN.md`, `.inventory/registers/LEARNINGS.md` (L-160..L-187,
L-300..L-316), `DECISIONS.md` (D-056..D-063), `OPEN.md`, and the result/script files cited inline. This is a
proposal list, not a synthesis: the canonical homes stay the graph, CLAIMS and PLAN (D-058). If a number here
disagrees with a `results_*.txt`, the result file wins.

## 0. Do first: two filings that need no compute

**0a. s93's CALL_1 does not hold under its own written rule (checked).** The frozen docstring
(`s93_unified_line_producer_and_f09_f16_triangulation.py` line 39-41) requires `C2_legacy >= 5/6` on `>= 8/15` folds per
transliteration. The code (line 1151) tests `>= 4`, and the result prints `C2_legacy 5 / 6 / 4` folds
(`results_s93.txt` line 136). As written, CALL_1 is False. This is the D-063 failure mode again. The F-41 [method] line
that cites s93 should be re-read against the written rule before it carries any weight. Parts 2 and 3 (F-09, X-08) were
not re-checked here (unverified).

**0b. s96 Part 1 has already printed** `CALL_1A_F26_X06_DISCHARGED: True` and `CALL_1B_F37_X06_DISCHARGED: True` with
"Written Rule == Coded Rule" headers (`results_s96.txt` lines 110-174). The run started 12:03 and is still writing. When
it finishes, gate it (stub check, printed call vs docstring rule) and file it. If Part 1 stands, F-26 and F-37 leave
CONTESTED at no further cost. Do not design anything that duplicates P-28.

## 1. Where the map is thin

### 1.1 Load-bearing (◆) and pointing findings below TRIANGULATED, or at risk

| F | grade | rests on | has | cheapest missing independent axis | who is already on it |
|---|---|---|---|---|---|
| F-34 ◆ | CORROBORATED, at risk | X-01 | data, method, split | **impl** (roach blind run of the line-held affix table on LOQO); physical | physical and X-01: s96 (P-28) |
| F-39 ◆ | CONTESTED | X-01 | data, impl, method, order, seg, split | resolve the contested seg line (excess order under Zattera/Seg_Affix2); then physical | s96 (native-segmenter synthesis, s45 ink) |
| F-40 ◆ | TRIANGULATED, at risk | X-01 | data, impl, method, order, split | X-01 discharge (counted seg line); physical line is resolved "partial" at 127 pages | s96 (5 segmenters, training-split bands) |
| F-41 | CORROBORATED, at risk | X-01 | data, method, split | **seg** (re-fit under Zattera/Seg_Affix2/RawWord); impl | s94 (core producer, same segmenter); s93 (needs 0a) |
| F-26 | CONTESTED | X-06 | data, method | resolution only | s96 Part 1 (0b) |
| F-37 | CONTESTED | X-06 | data, impl | resolution only | s96 Part 1 (0b) |
| F-21 | SINGLE, at risk | — | impl | a powered statistic first (L-187); then data/seg | nobody |
| F-10 | SINGLE | — | external | low priority: compatibility link only (weak) | nobody |

X-01 (SlotSegmenter units) is the single assumption that halves four load-bearing findings (F-34, F-39, F-40, F-41).
s96 is the run that can discharge it. Nothing proposed below re-tests X-01.

### 1.2 The top of the scoreboard and what moves it

The map's weights, recomputed by hand from its rule (strength × grade, halved for an undischarged at-risk assumption;
weak links count 0):

- **H-14 (line-held table cipher):** for 2.7 = F-14 moderate × 1.0 + F-34 moderate × 0.67 × ½. Against 1.0 = F-34
  strong × 0.67 × ½. F-39 counts 0 while it is CONTESTED. Net **+1.7**.
- **H-05 (table-and-grille, meaningless):** for 3.0 = F-14 2.0 + F-40 moderate × 1.0 × ½. Against 3.0 = F-30 strong.
  Net **0**.
- **H-06 (lexical system):** net −1.7.

**The order is fragile, and s96 alone can flip it.** If s96 discharges X-01 on F-34 and F-40 and resolves F-39 as
agreeing, the weights become H-14 3.3 / 4.0 (net −0.7) and H-05 4.0 / 3.0 (net +1.0). That flip comes from filing, not
from any new evidence about the mechanism.

**The decisive gap.** The largest single weight either hypothesis holds is the same line: F-14 (prefix memory, moderate,
TRIANGULATED). It counts for both. An experiment that tells which mechanism produces F-14's memory moves 2.0 between
them, the largest swing available. Experiment E1 is designed for that.

The second gap is wider. H-14 carries plaintext and H-05 does not. No experiment has asked whether the cores carry any
content that a fitted mechanical producer cannot. Since s93/s94, such a producer exists to compare against. E2 asks.

## 2. Our recurring failure modes, as design rules

| # | Failure (where) | Design rule for every experiment below |
|---|---|---|
| R1 | **Double sampling in fitted producers.** Regenerating from observed quire counts re-samples the vocabulary and over-localises it. s89 Arm B could not recover a planted copy of itself (FX1 4/15, D-062). s91 failed locality on 21/45 folds from the same source (L-185, L-316). s94 rewrote its lexicon rule twice (REVISION 1) | The generator must be identical in and out of sample, and must never re-draw the counts being scored. A fixture fitted LOQO on a planted instance of the producer must recover it (≥ 12/15) **before** the freeze. A failed fixture means the arm does not run (D-062 precedent). |
| R2 | **Plug-in MI over a large inventory.** Full-inventory core MI read negative for Dante and Old French, so A14 never measured order (s80, L-172, X-06 flipped). Inventory size also changed signs between segmenters (s76, L-166) | Every MI or order statistic is computed at matched K (50/100/200), with Miller-Madow. Real languages are scored at the same K as controls. Never compare MI across inventory sizes. |
| R3 | **Verdicts filed against the pre-registered rule.** s85 calls printed False were filed as discharges, s86 had no threshold, and s92's coded rule differed from its written rule (D-063, L-186). s93 coded `>= 4/15` where it wrote `>= 8/15` (0a). Earlier: s75 was edited after its run (D-059), and s71 prose contradicted its own table | The script asserts and prints `written threshold == coded threshold` for each call, quoting the docstring constant. Thresholds live in one constant block that both docstring and code read. The gate files the printed boolean. A battery swap (e.g. "de-aliased") needs an amendment file before the run. |
| R4 | **Underpowered per-quire statistics.** R_P1 at quire size could not separate copied Latin from composed Latin (control spread 0.15-1.3, s95, L-187). s78's positive control came in 17/20, one short | Before any per-quire count rule (≥ 8/15), run a size-matched positive and negative control at the same quire token counts. If they do not separate at the planned power, the per-quire rule is dropped for a pooled LOQO statistic with a permutation p. Absence claims need a powered positive control (TRIANGULATION). |
| R5 | **Intervals that miss realisation noise.** 80 % page-subsample intervals excluded 0 for shuffled controls in 6/11 cells (L-171). s70's intervals excluded their own point estimates (L-307) | The decision statistic is the within-line permutation p (≥ 200 shuffles). Intervals come from jackknife or LOQO block bootstrap and are descriptors only. |
| R6 | **Fitting the target and calling it reproduced.** The s67 cadence matched the rhythm because it was fitted to it (L-160). The s91 fit used in-sample locality | A property used in the fit loss cannot be a pass criterion. List the fit targets and the scored targets separately in the stub. |
| R7 | **Mislabelled independence axes.** Re-runs of our own code were filed as `impl` (L-186) | `impl` only from code that imports nothing of ours: roach, or Daybreak's codex_lab. Same code on another transliteration is `data`. |
| R8 | **Discriminators that the confusable class also passes.** The stem-graph solver scores letter-in-core ciphers as highly as stem codes (s84, L-179) | Every discriminator carries a planted control from the class it must reject, and the call requires that control to fail. |
| R9 | **Confounded labels and segmenter-dependent stories.** Hand vs section (L-303, L-305). Rare-core "origins" that were partly segmentation artefacts (L-304) | Stratify by section/quire/bifolio before a scribe or content claim. Every core-level statistic runs under ≥ 3 segmenters, including RawWord. |
| R10 | **Reading-order assumptions** (L-173, memory) | Prefer statistics that are symmetric in direction (lags in both directions, bags within a unit). If order is used, add the s79 T1-T3 transforms as an `order` line. |

## 3. Proposed experiments, ranked by (expected movement) / (compute hours)

Compute estimates are scaled from measured wall times: s69 4 min, s71 2 min, s81 53 min, s91 96 min (fitted LOQO
producer), s93 15 min, s92 4 min. These are prereg-stub to result-file times, an approximation. Budget: ≤ 4 low-priority
CPU workers, or the RTX 5080 (`torch.cuda.is_available()` = True, checked 12:07). All paths below were checked with `ls`.

### E1. Is the prefix memory a hidden line state or an observed one-step cursor? (H-14 vs H-05) — rank 1

- **Question.** F-14 says the prefix depends on the previous prefix and resets at the line. A line-held table (H-14)
  makes the prefixes in a line share a hidden state. Then P(t) and P(t+2) stay dependent given P(t+1), because a
  hidden-state chain is not first-order in what we observe. A grille or cursor procedure (H-05) is first-order in the
  observed prefix, so that conditional dependence is about 0. s69 reported "little further back" and a ~0.02-bit
  line residue, but it never ran planted controls for either mechanism (L-163).
- **Decides.** Which of H-05 and H-14 keeps F-14's moderate "for" link (a 2.0 swing). It also sharpens F-34.
- **Design.** Statistic: CMI2 = I(P_t ; P_t+2 | P_t+1, C_t, C_t+2), and the lag profile I(P_t ; P_t+d | C) for
  d = 1..4. Matched K on prefix classes, Miller-Madow (R2). Both directions are averaged (R10). The null is a within-line
  shuffle that holds each line's prefix multiset and core sequence fixed; decide by permutation p over 200 shuffles (R5).
  Producers are fitted on training quires to the lag-1 gain only (R6):
  - (i) s81 line-sticky Naibbe, `p_stay` fitted;
  - (ii) s71 weakened grille (WTG);
  - (iii) ULP93 (s93 M4).
  Each is scored on 15-quire LOQO.
- **Controls.** Positive: planted line-sticky text with `p_stay` 0.75 and 1.0 (s86 ST1 recovers it); CMI2 must exceed its
  null at Voynich token count. Negative: a planted first-order observed Markov prefix chain; CMI2 must sit at its null.
  Both must pass at quire-pooled LOQO size, or the run reports descriptively (R4).
- **Pre-registered call.**
  - "Hidden line state": Voynich CMI2 p < 0.05 on all 3 transliterations, and Voynich inside the fitted (i) band and
    outside the (ii) band.
  - "Observed cursor": the reverse.
  - Otherwise: not separable at this power.
  - Repeat under Zattera and Seg_Affix2 (R9).
- **Data.**
  - Transliterations: `data/translit/{ZL3b_eva,RF1b,IT2a}.meta.json`.
  - Code: `s69_prefix_stream_memory.py`, `s71_weakened_grille_and_sticky_naibbe_loqo.py`, `s81_sticky_table_loqo.py`,
    `s93_...py`, `s76_segmenter_independence.py` (Zattera).
- **Compute.** About 2-3 CPU-hours on 2 workers: the s81 fit dominates, and three segmenters roughly double one s81 run.
  No GPU needed.
- **Outcomes.**
  - Hidden line state: F-14 points for H-14 only, and the scoreboard leads with H-14 whatever s96 does.
  - Cursor: F-14 moves to H-05, and H-14 is left with F-34's moderate link alone.
  - Not separable: record F-14 as non-discriminating between the two; then E2 becomes the only separator.

### E2. Do the cores carry content that transfers across quires? (content vs mechanism) — rank 2

- **Question.** Mechanical producers (ULP93, s94's LP94) draw cores independently from a lexicon with a quire tilt and a
  line pool. Any text with topics makes specific core pairs co-occur on the same page, and that association transfers to
  unseen pages. Does Voynich show held-out pair co-occurrence beyond what quire tilt and page length explain?
- **Decides.** H-06 and H-14 (content-bearing) against H-05 and H-07 (no content). It would be a new F with strong links,
  and the first content-side test since s78. Distinct from s78: no pictures are used, so its power is not capped by the
  number of herbal pages.
- **Design.** Order-free bag-of-cores per page and per paragraph (R10).
  1. On training quires, compute PMI for core pairs at matched K = 100/200 top cores (R2).
  2. On the held-out quire, compute the same pairs' co-occurrence and take the rank correlation ρ between training and
     held-out PMI.
  3. Null: cores permuted across pages within the held-out quire, preserving page lengths and quire marginals.
  4. Stratify by section, and run Hand 1 and Hands 2/3 separately (R9).
- **Controls.**
  - Positive: Latin herbal and recipe texts cut to Voynich page sizes and K-matched (`data/external/genre-s87`,
    `data/external/genre-s89`, CREMMA `data/external/cremma`). Also a planted H-14 HLT text with Latin plaintext (the s83
    producer).
  - Negative (R8): ULP93 and LP94 output and the s71 grille, each fitted LOQO. They must show ρ ≈ 0 beyond tilt. If a
    mechanical producer passes, the statistic cannot discriminate and the run is descriptive.
  - Power: the positive control must pass at Voynich page count, run under the s95 rule (R4).
- **Pre-registered call.** Transfer if pooled-LOQO ρ for Voynich exceeds the 95th percentile of every mechanical
  producer with p < 0.05 on all 3 transliterations and ≥ 2 of 3 segmenters. No transfer if it sits inside the producers'
  range while the positive control passes.
- **Data.** Paths above, plus the s87 loaders (`s87_core_layer_genre.py`).
- **Compute.** About 3-4 CPU-hours on 2 workers, mostly regenerating producer replicates. The PMI matrices fit the GPU if
  K is raised to 400.
- **Start condition.** After s94 files, so that LP94 can join the negative set (it is running; do not duplicate it).
- **Outcomes.**
  - Transfer: a strong link against H-05 and H-07, and for H-14 and H-06. This is the first positive content evidence,
    and it would justify reopening a word-level decoding discriminator (with R8).
  - No transfer with a powered control: a strong link for H-05 (meaningless procedure). It is the most consequential
    possible move on the board.

### E3. roach blind replication of the line-held affix table (F-34 impl) — rank 3

- **Question.** Does a line-held affix table, written by roach from the s81 prose spec and not its code, reproduce the s69
  prefix-memory call pattern on ≥ 13/15 held-out quires, while predicting 0/15?
- **Decides.** F-34 goes CORROBORATED → TRIANGULATED, and it is the §5 cheapest missing axis. Combined with s96's physical
  line, F-34's weight rises from 0.67 to 1.0 in both directions.
- **Controls.** As in s81: default, line-lock and page-lock variants as negatives; a planted sticky instance as positive.
  The call is s81's rule verbatim (R3, R7).
- **Data.** Public transliterations on roach. roach's tree is on that machine, and `<local-path>` is
  reachable (checked).
- **Compute.** 0 SKYNET hours; about 1-2 roach hours, plus a spec page.
- **Outcomes.**
  - Agrees: F-34 is the first TRIANGULATED mechanism finding.
  - Disagrees: F-34 goes CONTESTED. That removes H-14's "for" link and moves the board toward H-05.

### E4. Is the F-40 physical failure power or ink? — rank 4

- **Question.** In s92, the ink stream `ZL3b_ink_full_127` fails in-line reuse in 2 of 3 segmenter cells (Rw 1.056,
  p 0.066). Is that the 127-page sample size, or a real difference between ink and transcription?
- **Decides.** The contested-then-"partial" physical line on F-40, and the F-40 physical axis.
- **Design.** Score the same 127 pages from the transliteration (ZL3b restricted to the s45 page list) with the identical
  s92 code. Then score 127-page random subsets of all 207 pages (500 draws) to get the power at that size.
- **Pre-registered call.**
  - Power: if ≥ 80 % of the 127-page transliteration subsets pass, the ink failure is evidence of an ink effect.
  - Otherwise the physical line is underpowered and is filed as uninformative (the s95 precedent).
- **Data.** `runs/s45/ink_ZL3b.meta.json`, `runs/s45/ink_lines_ZL3b.meta.json`, `runs/s45/pages` (171 entries),
  `s92_f40_seg_order_physical_triangulation.py`.
- **Compute.** Under 0.5 CPU-hour, 1 worker.
- **Outcomes.** Low movement (F-40 is already TRIANGULATED), but it closes an open contested line cheaply.

### E5. ULP93 re-scored under its written rule, plus the seg axis for F-41 — rank 5

- **Question.** Under the frozen thresholds (C2_legacy ≥ 8/15, see 0a), and under Zattera, Seg_Affix2 and RawWord, does
  the line-scoped producer still reproduce the core signature and the slot battery?
- **Decides.** The F-41 seg axis (§5 gap), and whether s93 supports F-41 at all.
- **Design.** Re-freeze s93 Part 1 unchanged except for an assertion that the written and coded thresholds are equal
  (R3). Add segmenter cells. The fixture must recover a planted ULP93 (R1).
- **Start condition.** Hold until s94 files, so this does not duplicate the core-producer question. If LP94 passes C1,
  run this on LP94 + affix table instead of LP93.
- **Data.** `s93_unified_line_producer_and_f09_f16_triangulation.py`, `s91_line_pool_producer_loqo.py`, the
  transliterations above.
- **Compute.** About 1-1.5 CPU-hours on 2 workers (s93 took 15 min for one segmenter, with three parts).
- **Outcomes.** F-41 gains seg or goes CONTESTED. The F-41 "for H-05 (weak)" link is unaffected; the "against H-07
  (moderate)" link gains weight.

### E6. A powered copying-vs-composition statistic for F-21 — rank 6

- **Question.** L-187 found that R_P1 cannot separate copied Latin from composed Latin at quire size. Is there a
  statistic that can, and where does Voynich sit on it? Candidates are visual-confusion pairs (glyph pairs similar in
  shape, minimal-pair rate within a page vs across pages), and the 646 inline `[a:b]` alternations (L-302).
- **Decides.** F-21 (SINGLE, at risk) and H-10 (weak).
- **Design.** Choose the statistic only after it separates CREMMA copied manuscripts from composed Latin (Pliny) at
  Voynich quire size with a planted-error control (R4, R8). That validation is a separate stub; then score Voynich.
- **Data.** `data/external/cremma`, `data/controls_realline/cremma_*_marks.meta.json`, and
  `s53_p4a1_p4e1_anchors_and_errors.py`.
- **Compute.** About 1 CPU-hour.
- **Outcomes.** Low scoreboard movement: H-10 is already excluded on F-27 (strong).

### E7. External axis from the literature already on disk (F-34, F-40) — rank 7

- **Question.** Does any published study (Timm & Schinner, Rozanova & Temerev 2026, Bowern & Lindemann, Gaskell &
  Bowern) report within-line word reuse, cross-line avoidance, or line-held affix state in numbers we can compare?
- **Data.** `data/external/papers`, `data/external/timm-schinner-generator`,
  `data/external/bowern-lindemann-entropy`, `data/external/gaskell-bowern-gibberish`.
- **Compute.** 0; about 1 agent-hour of reading, kept inside a subagent.
- **Outcomes.** Adds `external` to F-40 and F-34 (the §5 missing axis). Whether any paper reports these statistics was
  not checked (unverified); if none does, record that so it is not re-searched.

### Not proposed, with reasons

- **New cipher producers:** blocked by D-061 until a core-layer reference class matches. E2 is the test that would lift it.
- **F-39 physical, X-01 discharges, F-26/F-37 re-scoring:** these are P-28 / s96 (running).
- **Core producer with a shared lexicon:** this is s94 (running).
- **Line pool plus affixes plus handshake:** this is s93 / P-25 (filed; see 0a).
- **Daybreak's s119:** not found anywhere in the project tree (grep for `s119`, checked). It is presumably in
  `lab/codex_lab`, which was not read, so its scope is unknown. Confirm its scope
  before starting E3: Daybreak is the other source of `impl` lines and could run E3 instead of roach.

## 4. Order of work

1. **Filing, about 30 min agent time, no compute.** Do 0a and 0b first: gate s93 against its written rule, and gate and
   file s96 when it finishes. Then rerun `render` and `sprawl`, and recheck §1.2: the H-05/H-14 order may flip on filing
   alone.
2. **Now, in parallel.** E1 on 2 workers (H-05 vs H-14). E3 handed to roach or Daybreak. E4 on one worker.
3. **After s94 files.** E2 and E5.
4. **Fill-in.** E6 and E7.
