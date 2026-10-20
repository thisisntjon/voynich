# PREREG v2.1 — dated amendment to PREREG-v2.md

## 0. Status

Amendment to `PREREG-v2.md` (frozen 2026-10-17 19:27 PDT, sha256
`f8c42d76a3e7651bebc766f6ab1e726a98a9a11442387dbfe87a8a10bba49208`, recorded in
`scoreboard/PREREG-v2.sha256`); v2.1 drafted 2026-10-17 20:54 PDT (system clock, `date`); frozen when
`scoreboard/PREREG-v2.1.sha256` exists.

`PREREG-v2.md` is not edited and remains the record for every run scored before the v2.1 freeze
(results_m4, n6, n7, s15, s17, s18, s20, s21, s23 and the peer's s31 pre-test). v2.1 governs
Phase 3 (the entrant pair, PLAN.md Phase 3 block) and every run scored after the freeze.
Everything in v2 not amended below stands unchanged: §2 board transliteration and the three-file
robustness rule, §3 band values, §5 nulls, §6 A/B rule (as tightened in item 4), §8 sidecar
format, §9 stub rule. Nothing here touches `scoreboard/score.py` (v1 scorer), `PREREG.md` (v1),
`scoreboard/run_v2.py` (unchanged, hash in item 8) or any results file.

## 1. Ranges file: `s15_ranges.json` replaces `results_m4_phase1_board.json`

- The ranges file for every v2.1 run is **`s15_ranges.json`**, sha256
  `b995aba64e5baa22524565963d67880287e43e98220a7c3cdd2d136eac6b3fef` (printed in the
  results_s20.txt header; re-hashed from disk while drafting this amendment: matches).
- Its family ranges L/C/G/X are copied unchanged from `n7_gibberish_ranges.json`
  (`ac281dfd53a6a59622ecc1a149bf1461bce5bb0638aead8dd46f548ba29c6bd3`;
  `s15_ranges.json` → `provenance.ranges_source_sha256`), whose L/C/G in turn are the m4 ranges
  of `results_m4_phase1_board.json` (`bb86177034d324c9d9f6412b7b7925373b475c1e8a1f8b15d91a478adba5a769`;
  `provenance.n7.note` "L/C/G = m4 ranges unchanged; X per n7 prereg"). No band value and no
  family range moves under v2.1.
- The v2 §9 commands read `--ranges s15_ranges.json`. Every results file prints the ranges-file
  sha256 on its first lines beside the script hash (results_s20.txt lines 3–4 are the format).
- The `within_manuscript` block of `s15_ranges.json` is the **stated margin** for every in/out
  call: 200 random 41-page subsets of ZL3b (seeds 1000..1199, `run_v2.score_one`,
  results_s15.txt header), lo95/hi95 = 2.5/97.5 percentiles. A manuscript value or an entrant
  value is reported with this margin beside it; a band or range whose edge lies inside the
  margin is "within the manuscript's own width", not a pass or a fail. The ten weighted metrics
  (the `ranges` keys of `s15_ranges.json` not listed in its `no_weight`; `sd_len` is no-weight
  there and stays a v2 §3 band only):

| metric | median | lo95 | hi95 | full ZL3b | source |
|---|---|---|---|---|---|
| h2 | 2.1030 | 2.0540 | 2.1523 | 2.1262 | results_s15.txt widths table |
| jsd_first_fg | 0.1777 | 0.1447 | 0.2156 | 0.1759 | " |
| p_init_enrich | 18.11 | 12.30 | 26.35 | 17.89 | " |
| m_final_enrich | 16.23 | 10.18 | 27.41 | 16.31 | " |
| cross_excess_eva | 0.1801 | 0.1477 | 0.2085 | 0.1809 | " |
| redup_pct (%) | 0.8455 | 0.6623 | 1.0598 | 0.896 | " |
| x_edge_mi_word | 0.1890 | 0.1568 | 0.2208 | 0.1882 | " |
| types_25k | 2283 | 1911 | 2654 | 5417 (34.9k tok.) | " (41-page subset = raw type count at 4.9–8.8k tokens; not on the 25k scale) |
| x_position_entropy | 1.6569 | 1.6284 | 1.6912 | 1.6607 | " |
| x_ltr_minus_rtl | 0.0077 | 0.0026 | 0.0137 | 0.0049 | " |

  Caveat carried from results_s15.txt lines 52–53: the s15 estimator reconciles with
  s2 Part 3B on 6/7 v1 bands; the `redup_pct` CI differs beyond tolerance (s15 0.662–1.060 vs
  s2 0.714–1.192). The s15 width is the one used; the difference is reported, not gated.
  Subset token counts: median 6,898 (range 4,885–8,787), so the widths are at ~7k tokens and
  are wider than a 25k-token margin would be (results_s15.txt header).

## 2. X (gibberish) family present; eight jackknife extras carry no weight

- `s15_ranges.json` carries `"x_family": "gibberish"`, so `run_v2.py` prints X as a family (v2
  §7). The X ranges are n7's: per-writer min/max over the 38 Gaskell–Bowern files for the seven
  v1 bands and `x_position_entropy`; pooled 10,023-token corpus plus 38-writer jackknife for the
  extras (`provenance.n7.x_source`). `types_25k` has no X range (undefined at 25k).
- The eight X-jackknife extras are **no-weight** under v2.1, keys exactly as
  `s15_ranges.json` → `no_weight_reasons`: `x_moran_I`, `lex_beta`, `lex_rate_late_early`,
  `lex_edit1_excess`, `slot_occupancy_pc`, `slot_table_likeness`, `slot_core_crowding`,
  `bake_char3_minus_unigram`; reason string for each: "X range is a 10k-token pooled jackknife
  sliver (n7; O-046)". They are reported in every row and never counted. The gibberish family is
  scored on the weighted set like any family and is never favoured on those eight.
- Remaining `no_weight` entries of `s15_ranges.json` are carried over from v2 §4 (`sd_len`,
  `info_mi_adjacent`, `info_samecol_minus_othercol`, `x_hapax_10k`, `info_mi_page`,
  `info_bpe_adjacent`, `bake_winner`).
- n7's verdict on this file (results_n7.txt lines 348–353): PRIMARY FAVOURED G (all/A/B agree),
  kill-precondition met by all four families on all three subsets, parameter-change clause
  untested; the X-vs-L count is SIZE-DEPENDENT (full LEAN L, matched MIXED). Under v2 §7 the G
  "in" on h2/redup/position entropy is partly by construction, and that caveat travels.

## 3. U1 HOLDS recorded; edge bands keep full weight

- results_s18.txt lines 294–303 (pre-registered rule, `s18_cremma_v2.prereg.sha256`): primary
  statistic E = pooled cremma_prose15 `jsd_first_fg` excess over the within-line null;
  null_level 0.0055, T_hold 0.0945, T_inval 0.1392 (lower bound 0.1447 = s15 lo95);
  **E = 0.0078** (raw 0.0236, null 0.0158 ± 0.0031, 773 lines, 6,890 tokens); pooling guard not
  triggered; kill-rule token minima met (prose15 6,890 ≥ 5,000; c15 10,190 ≥ 8,000).
  **VERDICT: U1 HOLDS.** Sensitivity on the `_marks` family: E = 0.0085, same verdict (line 304,
  not the decision). Re-wrap clause (line 307): prose15 native − relined8 `jsd_first_fg` =
  0.0172, within the s15 half-width 0.0355.
- Consequence: the three line-edge bands (`jsd_first_fg`, `p_init_enrich`, `m_final_enrich`) and
  `x_edge_mi_word` keep full weight. Scribal prose lines do not produce the Voynich line-initial
  profile.
- **O-047 caveat (carried with every edge-band verdict):** verse and formulaic Latin
  manuscripts in s18 (Priapea, Sortes sanctorum) reach a line-initial excess of +0.10–0.14 at
  114–201 lines against Voynich +0.173 at 773 lines; Voynich was matched only at 773 and 1,398
  lines, and raw rows at ~100 lines are inflated even after the null (audit item 4). The edge
  bands are therefore a prose-vs-Voynich result, not a verse-vs-Voynich result, until O-047's
  matched-line-count draws are run. Other s18 caveats carried (line 308): prose15 column count
  unverified; paragraph proxy = ALTO TextBlock; abbreviations unresolved so Latin h2/types rows
  carry no weight.
- **Named secondary range "real-line L" for the two edge metrics.** Beside the m4-derived L
  range, every v2.1 row for `cross_excess_eva` and `x_edge_mi_word` reports position against the
  pooled real-line rows of results_s20.txt (from `results_s17_*.json` and
  `results_s18_cremma_*.json`, native line breaks): cremma_all (25,002 tok.) 0.0491 / 0.0643;
  cremma_c15 (10,190) 0.0390 / 0.0524; cremma_prose15 (6,890) 0.0239 / 0.0414;
  gib_realline_pooled (10,023) 0.0127 / 0.0298; mhg_nibelungenlied 0.0792 / 0.0832;
  oldfrench_roland 0.0911 / 0.0971; occitan_croisade 0.1084 / 0.1123; italian_dante 0.1615 /
  0.1672. Real-line L range: `cross_excess_eva` 0.0127..0.1615, `x_edge_mi_word`
  0.0298..0.1672 (n = 8 of 8). Per-manuscript CREMMA rows at ≥ 5k tokens (BIS-193 0.0974,
  CLM13027 0.0680 on cross; edge NA) are reported beside, not in the range. This secondary range
  is a reference, not a kill/favour range: it is the "inside / above" column of item 5.

## 4. Currier-A rule: `m_final_enrich` carries no weight for A rows

- Fact (results_n6_ab_split.txt line 17): Currier A fails the v1 joint pass on exactly
  `m_final_enrich` on all three transliterations (ZL3b, RF1b, IT2a: "joint FAIL missed
  m_final_enrich"); A's value is ×6.21 against the ≥ ×8 band (results_n6_ab_split.txt line 26;
  v2 §3 and §10 record the same ×6.21 from run_v2 on A). B and "all" pass 7/7 on all three
  files (line 18–19).
- **Rule:** for Currier-A rows (`--lang A`) `m_final_enrich` is reported and carries no weight;
  the A joint pass is over the other six v1 bands, and an A row that passes those six is written
  "A: joint PASS (6/6 under the v2.1 A-rule; m_final ×<value>, no weight)". B and "all" rows keep
  all seven. A-only / B-only verdict wording of v2 §6 is unchanged.
- **Rejected alternative:** re-deriving A-specific bands from an A-only 41-page bootstrap.
  Rejected because the enrichment ratios are the noisy bands (width 14–19× at 8–11k tokens,
  5–6× at 35k, workflow/research/C-constraints.md line 62; A is 11,231 tokens) and bands fitted
  to one target half would be bands from a target half (the REDTEAM #4 defect; phase-2.md
  "Decisions taken" 4). Reporting against the n6 matched-size A11k ranges stays a sensitivity
  row (results_n6_ab_split.txt section 2b), never the decision.
- Every verdict in Phase 3 is reported all / A / B (v2 §6), with the A row under this rule.
  n6's own verdict on the split is "SAME (size-fragile)" (full-size SAME, matched-size SPLIT;
  results_n6_ab_split.txt lines 80–88), and A vs B stays confounded with scribe and section
  (n6 header caveat): the A-rule is a scoring accommodation, not a two-language claim.

## 5. Coupling per Currier language (s20): a B-text property, and no family weight in Phase 3

- results_s20.txt (script `s20_ab_coupling_v2.py` 0c6f0edd…, stub match True, ranges
  s15_ranges.json b995aba6…), six rows: `cross_excess_eva` / `x_edge_mi_word`
  ZL3b A 0.1203 / 0.1265, B 0.2321 / 0.2404; RF1b A 0.1071 / 0.1126, B 0.2259 / 0.2332;
  IT2a A 0.0968 / 0.1023, B 0.2181 / 0.2262. |A − B| is 3.6–4.0 s15 half-widths on both metrics
  and all three files (half-widths 0.0304 and 0.0320).
- Pre-registered reading (results_s20.txt "READING"): on every file A is **inside** the pooled
  real-line L range of item 3 and B is **above** it on both metrics → **the coupling anomaly is
  a B-text property.** This is a stated exception recorded in v2 §6 terms, not a verdict on the
  manuscript: A is inside the real-line language range on the two coupling metrics; B is not.
- Stratification record (results_s30_phase2_deltas.txt lines 3–14, copied into
  results_s20.txt): both A and B coupling survive the position-stratified null (survival
  103.0–105.4 %), and non-Voynich syllable/prose edge tables mechanically drive coupling in both
  halves (Part 1B: LA_Herbal_Syllable +0.6741 / +0.6371, IT_Dante_Rank +0.2530 / +0.2111, all
  ≥ +0.09). s2 Part 2B (results_s2_u123_controls.txt line 30): the edge table "TRANSFERS
  OUT-OF-SAMPLE (A<->B, 166->41, and rank-mapped Dante table all clear >=+0.09)".
- **Rules for Phase 3:** (a) entrants are judged on the **B** row for `cross_excess_eva` and
  `x_edge_mi_word`; an entrant may not be favoured for matching A on these two metrics, because
  A sits inside the real-line language range. (b) Because any fitted or handed edge table
  regenerates the coupling (s2 Part 2B; s30 Part 1B), these two metrics carry **no family
  weight** in Phase 3: they are reported per row as "reached / not reached" (reached = inside
  the s15 within-manuscript margin of the B value, item 1), and they enter no in/out count, no
  kill and no favour. The joint `types_25k` + `x_edge_mi_word` clause of v2 §4 (M19) survives as
  a type-range check only: an entrant that reaches the edge value by leaving the `types_25k`
  range is reported as "edge reached, types failed".

## 6. Reporting rules (new §11)

1. **Power statement with every negative.** A result reported as negative (p ≥ 0.05, "no
   effect", "does not reproduce") carries, in the same block, the smallest effect the test
   detects at power 0.8 or the words "power unverified", in the format of results_s23.txt
   block (c) (TEST / FILED / POWER / STATUS). A negative without a power line is a power
   statement, not a negative (s23: the five refiled Phase 2 negatives are UNDERPOWERED ×3,
   POWER UNVERIFIED ×2; none is a negative).
2. **Per-round Benjamini–Hochberg, q = 0.05.** One family per round = every p-value the round's
   result file prints; the ledger is written in that result file in the format of
   results_s23.txt block (d) (rank, raw_p, BH_cutoff, pass, floor, test, source), with m stated.
   Seed replicates enter as one p (the median; the rest are sensitivity). Any later file that
   prints a p-value appends its row to its own copy of the block and re-states m.
3. **Floor-bound p-values are marked, not ranked.** A p equal to its exact/permutation floor
   (1/55 for the hand-1 quire-block null, 1/105 for hand 2, 1/201 for 200-shuffle tests,
   1/1000 for 999-draw tests) is listed unranked with the words "floor, not ranked" and is
   excluded from m (s23 block (d) CONTEXT lines; C-constraints §5 pitfall 2).
4. The Phase 2 ledger (results_s23.txt block (d)): m = 7, BH survivors NONE (smallest ranked p
   0.0199 vs cutoff 0.0071); context base rate 291 of 582 printed p-values across results_*.txt
   are < 0.05, so any single sub-0.05 p cited without a pre-registered family is noise at ~50 %
   prior.

## 7. Phase 3 scoring rule

- **Entrants:** one per family, prefixes as in PLAN.md Phase 3: **s27** the K4 shared-codeword
  producer (C; a bound only, PLAN.md line 110), **s28** the matched edge-table generator
  (G; 7k budget, real-line-derived edge table, line 111), **s10** the period-plausible cipher
  twin (homophonic alphabet + nulls + small names list + m5 line-end draw, positive control the
  Zenodo workbook key, line 112). s5 (joint producer) only if s28 vs s10 do not tie. s24 is the
  approved family-framing check, not an entrant.
- **Procedure:** each entrant has a prereg stub (v2 §9) frozen before its run; the results file
  prints the script hash and the s15_ranges.json hash; each is scored **once** on v2.1,
  **all / A / B** (A under item 4), **3 seeds**, on the **41 held-out pages** (g1 split,
  `Random(20261017)`; the manuscript's own g1_41 row is in results_s15.txt and
  `s15_ranges.json` → `g1_heldout_41`), on ZL3b with the RF1b/IT2a re-score of v2 §2.
- **Target set (what the handed edge table does not fix; PLAN.md line 149):**
  1. `types_25k` (s15 margin; the 25k scale on the full sidecar, raw type count on the 41 pages);
  2. `h2` per unit (EVA character level, v2 §2; alphabet-specific);
  3. the line-edge vocabulary: `jsd_first_fg`, `p_init_enrich`, `m_final_enrich` (A-rule, item 4);
  4. CHARWIN (the d2 page-split char-win, results_n5.txt +0.094; reported with the s21 line-shuffle
     convention where applicable);
  5. `x_moran_I` / within-line lag-1 word-length Moran I, judged against the s21 reference, not
     the family range (the family range is no-weight, item 2):
     s21 (results_s21.txt, pre-registered, reproduces Daybreak's ZL3b within-line I 0.157244
     exactly): real-line human gibberish within-line I 0.098, p = 0.728 against its own
     line-shuffle null (not above it); real-line Latin pools −0.033 (prose15), −0.019 (c15),
     +0.037 (all); verse/epic −0.116 to −0.149; only the Voynich rows exceed their line-shuffle
     q99 (p = 0.001). Reference range for `x_moran_I` / within-line I in Phase 3: real-line
     language −0.149..+0.037, gibberish 0.098, G producers max 0.129, Voynich 0.157; **an entrant
     must exceed its own line-shuffle q99 to count as reaching it.** The O-043 clause "no tested
     meaningless model reproduces it" stands (results_s21.txt line 36);
  6. the F1 held-out word-order residual: manuscript +0.046 (quires, 95 % CI +0.036..+0.056;
     results_n6.txt line 5), reopened as a target by results_n6.txt (the 7k-type glyph-model
     generator does not reproduce it);
  7. hand-1 within-hand section NMI: manuscript 0.275 (quire-block p 0.018, bifolio p 0.000;
     results_n6.txt line 6), HOLDS against the powered 7k generator (seed-mean 0.087 vs the
     0.206 bar, results_n6.txt line 18); cited always with the 1/55-floor caveat (the quire-block
     p = 0.018 is the exact floor; "floor, not ranked", item 6.3). Hand-2 NMI is NOT EVIDENCE
     (results_n6.txt line 21) and is not a target.
- `cross_excess_eva` and `x_edge_mi_word`: reached / not reached only, B row (item 5).
  All other v2 §4 no-weight and item 2 no-weight metrics: reported, never counted.
- **Decision:** the v2 §7 kill/favoured arithmetic over the weighted set above, all / A / B
  (v2 §6), three EVA files (v2 §2), with the item 1 margins beside every in/out, and the item 6
  ledger in the Phase 3 results file (one BH family for the round).
- **Stop rule (Jon, 2026-10-17 20:02, PLAN.md line 167 and Phase 3 "Depends on"):** the pair is
  scored once; the effort stops after it regardless of outcome. No re-tuning, no second
  configuration, no re-score on a later ranges file. Phase 4 runs only on human-input evidence.

## 8. Hash list to freeze in `scoreboard/PREREG-v2.1.sha256`

`sha256sum` format, no BOM; `scoreboard/PREREG-v2.sha256` is kept unchanged as the v2 record.

| file | sha256 (as read while drafting) | note |
|---|---|---|
| PREREG-v2.1.md | (computed at the freeze) | this file |
| scoreboard/run_v2.py | 7dfdc9f75de5980adaa4b387df8ab272fd1d1c7a9ff452e94cac149012ff253e | unchanged from v2 |
| s15_ranges.json | b995aba64e5baa22524565963d67880287e43e98220a7c3cdd2d136eac6b3fef | the v2.1 ranges file (item 1) |
| n7_gibberish_ranges.json | ac281dfd53a6a59622ecc1a149bf1461bce5bb0638aead8dd46f548ba29c6bd3 | L/C/G/X source of s15_ranges.json |
| results_m4_phase1_board.json | bb86177034d324c9d9f6412b7b7925373b475c1e8a1f8b15d91a478adba5a769 | for the record of what v2 used |

`tools/gibberish_to_meta.py` (db1d131c…) stays hashed in `scoreboard/PREREG-v2.sha256` and is
not re-listed; the X sidecars it produced are unchanged. Frozen when the sha256 file exists and
`sha256sum -c scoreboard/PREREG-v2.1.sha256` passes.
