# Phase 1 plan — real-line control (retire U1)

Stamped 2026-10-17 20:05 PDT from `date`. Linked from `workflow/PLAN.md` Phase 1. Investigation files:
`workflow/research/phase-1-instrument.md`, `workflow/research/phase-1-cremma.md`. Prior work folded in:
`results_s2_u123_controls.txt` (peer, pre-registered 19:48, hash 28adb12e…; identical copy `results_s26_u123_controls.txt`).

## What the investigation changed

1. **The on-disk pre-test is already done.** s2 Part 1 scored native vs 8-word re-lined lines with the v1
   estimator: Voynich JSDf 0.176 native / 0.001 re-lined; gibberish 0.0075; Nibelungenlied 0.092; Old French
   Roland 0.020; Occitan 0.076; Dante 0.032. Verdict: outcome A, max non-Voynich native 0.092 < 0.10. The
   RN-Top -am odds ratio reproduces (21.3 native). So s17 becomes a v2 re-score of the same corpora plus a
   real-line gibberish sidecar, not a new design.
2. **U2 is largely retired by s2 Parts 2A–2B.** 102.7–102.9 % of the cross-space MI excess survives a
   (hand, section, slot) stratified null on three transliterations; an edge table fitted on Currier A
   generates +0.153 on B, B on A +0.252, 166 pages → 41 held-out +0.229, and a rank-mapped Dante table
   +0.230, all ≥ +0.09. Reading: the coupling is adjacent ordering, not position; but *any* skewed edge
   table reproduces it, so a producer handed a table proves nothing (REDTEAM #1 confirmed mechanical).
   Registry: U2 verified as ordering; "producer reached the coupling" is withdrawn as evidence.
3. **U3 has a table and seven band widths** (s2 Parts 3A–3B): h2 25k 2.126 EVA / 2.397 glyph+ / 2.540
   GC2a; 200-split 41-page 95 % CIs: h2 [2.054, 2.152], jsd_first [0.145, 0.216], cross_excess
   [0.148, 0.209], m_final [10.2, 27.4]. These are the provisional s15 widths; s15 must still cover every v2
   metric with the n7 X ranges attached.
4. **The pooled gibberish sidecar is 8×20 wrapped** (`tools/gibberish_to_meta.py`), so it cannot serve as
   a real-line corpus; the 38 source files keep the volunteers' lines (1,617 lines). New sidecar needed.
5. **CREMMA facts.** 242 XML = 121 pages × 2 variants (plain 6.95 MB; chocomufin 5.38 MB, has a
   combining-mark bug); ALTO v4, one String per TextLine, SegmOnto zones (MainZone, RunningTitle,
   DropCapital, QuireMarks, Numbering); no paragraph marks; columns are separate MainZone blocks;
   abbreviations unresolved (MUFI + NFD marks); punctuation attached to words; line-end word breaks
   unmarked. 21 manuscripts, 57,412 words total; only two exceed 5k words (CLM13027 6,499; BIS-193 7,370).
   15th-century: 7 manuscripts, 9,933 words; prose15 candidates PalLat373 (2,258), LaurPlut53.08 (2,985),
   LaurPlut53.09 (1,300) = 6,543 pooled; column count unverified. Licence stated inconsistently (CC-BY 4.0
   in yml, CC0 in the paper). Zenodo and GitHub zips include images (357 MB, over the stop); raw per-file
   fetch at tag v0.1.2 (sha 9439fe33…) is 6.95 MB plain-only.
6. **Instrument.** `run_v2.py` `load_meta` keeps sidecar lines verbatim (id or page dialect) and nothing
   re-wraps; edge metrics see real lines; Moran I runs on the concatenated stream; CHARWIN is not a run_v2
   key (nearest is `bake_char3_minus_unigram`, a different estimator); `jsd_last_lg` lands only in the
   `.json`. Ranges format: `ranges[metric][L|C|G|X]={min,max}` plus `tight`/`no_weight`; X read only with
   `x_family: gibberish`; other keys ignored. `--out results_s15.txt` would also write `results_s15.json`,
   so the ranges file is `s15_ranges.json`. Run with `python -I scoreboard/run_v2.py` (the `-m` form
   fails under -I).

## Steps (done-when in brackets)

### s15 — within-manuscript widths for every v2 metric
- Script `s15_band_widths.py` (new, prefix claimed). Reuse `workflow/research/C-helpers/floors_v1_bands.py`'s
  41-page subsetting, replace its metric call with `run_v2.score_one`, 200 splits (seeds 1000–1199, l1's
  convention), edge-null nrep 20, ZL3b plus RF1b and IT2a rows at full size. Write incrementally.
- Output `results_s15.txt` (table: median, 95 % CI, min..max per metric per transliteration) and
  `s15_ranges.json` = n7's L/C/G/X ranges and `tight`/`no_weight` copied verbatim, plus a top-level
  `within_manuscript` block, plus `no_weight` extended to the eight X jackknife-artefact extras (O-046)
  with the reason string.
- Check against s2 Part 3B: the seven v1 medians must match within 0.01 / 1 ×; if not, stop and report.
- Runtime estimate 20–30 min (5–8 s per split), one corpus in memory; takes the single board-scale slot.
- [done when results_s15.txt and s15_ranges.json exist, 200 splits each, seven v1 rows reconciled with s2]

### s17 — real-line corpora on the v2 scorer
- `tools/realline_to_meta.py` (new): builds `data/controls_realline/` sidecars in the `id` dialect with real
  lines: `gib_realline_pooled` from the 38 Gaskell–Bowern source files (keep volunteers' lines, drop `_____`
  page rules, join trailing `-`), `mhg_nibelungenlied` (long-lines; `## Aventiure` headers as page/paragraph
  breaks), `italian_dante` (verse lines; canto breaks as pages), and the two s2 corpora if their sources are
  on disk (Old French Roland, Occitan Croisade). Line-preservation check: per-line token counts out of
  `load_meta`+`subsample` equal the sidecar's.
- `s17_realline_v2.py`: `run_v2.py --meta <each> --family L --ranges s15_ranges.json --out results_s17_<name>.txt`,
  then a summary `results_s17.txt` with jsd_first, jsd_last (from the .json), p_init, m_final, cross_excess,
  x_edge_mi_word, x_position_entropy, x_moran_I, and n5's CHARWIN (imported from
  `n5_signature_discrimination.py`, same estimator) per corpus, native vs 8-word re-lined, beside s2 Part 1's
  v1 numbers.
- [done when results_s17.txt lists ≥4 real-line corpora native and re-lined on v2 metrics, with the
  gibberish row on real lines]

### s18 — CREMMA
- Fetch (approved scope): `tools/fetch_cremma.py` lists the tree at tag v0.1.2 via the GitHub API, sums
  the byte count of `data/*/*.xml` plain variant plus README/yml/csv metadata, aborts above 200 MB, then
  downloads raw per file into `data/external/cremma/` (new, empty), verifies each file's git blob SHA-1
  against the tree, writes a fetch log to `data/external/README.md`. Expected 6,952,796 B + metadata.
- `tools/cremma_to_meta.py` (outside the data folder, run with `python -I`): plain `.xml` variant; MainZone
  TextBlocks only (drop RunningTitle, Numbering, QuireMarks, DropCapital zones); each TextBlock is a
  paragraph proxy (first line of a block = "paragraph-initial"); each ALTO file is a page; tokens = NFD,
  strip combining marks, lowercase, split on whitespace, strip trailing `.:,;`; line-end breaks left as the
  scribe left them (unmarked). Sidecars per manuscript `cremma_<id>.meta.json`, a pooled `cremma_all`, a
  pooled `cremma_prose15` (PalLat373, LaurPlut53.08, LaurPlut53.09), and `cremma_c15` (all seven
  15th-century). Manuscript table with dates, script, text type and the `prose15` flag written to
  `data/controls_realline/CREMMA_MANIFEST.md`, with "column count unverified" where it is.
- `s18_cremma_v2.py`: score every sidecar as in s17; `results_s18.txt` with the decision block.
- [done when results_s18.txt holds the pooled prose15 row (≥5k tokens), cremma_c15, cremma_all, and
  per-manuscript rows, with the three-outcome verdict printed by the pre-registered rule]

### s19 — re-wrap
- Same CREMMA text wrapped 8×20 and 9-word; `results_s19.txt` reports the native-minus-wrapped difference
  per metric, flagged where it exceeds the s15 width.
- [done when results_s19.txt exists for prose15, c15 and all]

## Pre-registration stub (to freeze as `s18_cremma_v2.prereg.sha256` before s18 runs)

- Decision statistic: jsd_first on `cremma_prose15` (6,543 words pooled; if under 5k tokens after
  tokenisation, `cremma_c15` with a stated caveat). Secondary: jsd_last, and the s15 widths.
- Outcomes, exhaustive: **below 0.10** → U1 holds. **0.10 to below the s15 jsd_first lower bound
  (0.145 provisional from s2 3B)** → U1 partly invalidated; edge bands count as one Tier-3 constraint,
  cited only with the real-line comparison. **At or above the lower bound** → U1 invalidated; edge bands
  lose weight under v2's rule; "the only metric outside every family" withdrawn.
- Re-wrap clause: if s19's native-minus-wrapped jsd_first on prose15 exceeds the s15 width, report the
  real-line effect as that difference.
- Kill rule (reworded after the investigation): the pooled prose15 row cannot reach 5k tokens and
  cremma_c15 cannot reach 8k; then s17 stands alone and U1 stays unverified, recorded as such.
- Caveats carried: prose15 column count unverified; paragraph proxy is the ALTO TextBlock; abbreviations
  unresolved so Latin h2/types rows are reported but carry no weight.

## Amendments from the independent audit (Astra, `workflow/research/support-phase1-audit.md`, folded 2026-10-17 20:13)

1. **Pooling guard (audit item 1).** Pooled JSD can cancel opposite per-manuscript effects (exact
   counterexample: 1.0 in each of two manuscripts, 0.0 pooled). The pooled `cremma_prose15` row stays the
   primary statistic, but it is *not sufficient on its own*: s18 also reports (i) each manuscript's
   jsd_first as an excess over its own within-line permutation null (score.py nrep 20), (ii) the
   manuscript-weighted mean of those excesses, (iii) leave-one-manuscript-out pooled values, and (iv) a
   heterogeneity line (max minus min per-manuscript excess). Rule: if any single manuscript's calibrated
   excess reaches the Voynich matched-size excess (item 4), a low pooled value does not count as "U1 holds".
2. **Tokeniser (item 2).** Internal `. : , ;` are word boundaries (split), not deleted-and-joined;
   token counts and changed-line counts are reported per manuscript; unmarked line-end word breaks are
   never reconstructed.
3. **Abbreviation marks (item 3).** Base-letter rows are the board rows; a `_marks` sensitivity family
   keeps each base character with its attached combining marks as the glyph unit (first glyph = base[0]
   with its marks). Reported beside, never compared to an EVA band without that qualification.
4. **Calibration (item 4).** Raw JSD at 50–100 lines is biased upward (IID simulation: mean 0.126 at 50
   lines, 0.056 at 100, 0.0012 at 4,130). So the decision compares *excess over the within-line
   permutation null*, and s18 adds a matched-size Voynich reference: 200 random draws of ZL3b with the
   same number of lines as `cremma_prose15`, reporting median and 95 % range of the excess. Effect
   magnitude and uncertainty are reported, not only a p-value.
5. **Paragraph proxy (item 5).** MainZone blocks are often columns; the sidecar key is `block_first`
   and all paragraph-specific comparisons are labelled "block-initial (column proxy)".

Stub change: the three outcomes are decided on the pooled prose15 *excess* (not raw jsd_first), with the
pooling guard applied; the 0.10 / 0.145 thresholds stay as provisional and are restated in excess terms
once s15 reports the Voynich within-line null level (score.py's edge null on the 41-page draws).

## Order, concurrency, prefixes

s15 first (board-scale slot). s17 sidecar build in parallel (light). s18 fetch and sidecar build in
parallel with s15 (no scoring until s15_ranges.json exists). s18 scoring after the stub is hashed. s19 last.
No writes to `scoreboard/scoreboard.json`, `data/controls_synthetic/`, or `data/controls_gibberish/`.
Prefixes s15, s17, s18, s19 claimed in TEAM-HANDOFF.md at 19:47.

## Roadmap deltas (from this investigation)

- Phase 2 s20 (position-stratified null, A-fitted table, Latin table): **done by s2 Parts 2A–2B** on the
  v1 estimator; s20 shrinks to a language-stratified re-run on v2 (A inside L on the coupling, n6) and is
  no longer load-bearing for Phase 3.
- Phase 2 s21 (Timm bound): **done by s2 Part 2C** (53,261 implied letters for a 1.528 letters/token
  verbose cipher; 34,857 words for a word cipher). Dropped as a step; numbers go to CLAIMS.
- Phase 2 s22 (fixed unit): Part 3A supplies the table; s22 keeps only the o1 ink-split row and the
  within-manuscript widths per alphabet.
- Phase 3: a producer handed an edge table reaching the coupling is now *known* to be mechanical (U2b:
  even a Dante-rank table reaches +0.23). The entrant pair must be scored with the coupling metrics
  weighted only through what the table does *not* fix (types, h2, line-edge vocabulary), or the pair cannot
  separate. This is a roadmap change: the Phase 3 stub must say which metrics the handed table determines.
- The s1/s2 prefixes reserved for Phase 3 are already used by the peer's joint-producer and controls runs;
  the prefix table is amended (Phase 3 entrants move to s27 onward).
