# Phase 3 investigation — entrant pair on the v2.1 board (read-only, just-in-time)

Written: Sat Oct 17 21:03:25 PDT 2026 (`date`). Governing rule: PREREG-v2.1.md item 7 (frozen 20:55, sha256 87e09ce3…). Scope: PLAN.md Phase 3 block (lines 149–155), 20:05 change note (line 150), s24 approval (line 155), stop rule (line 169). Nothing was run; `python -I` used only to read JSON sidecars.

## 1. s10 — period-plausible cipher twin

**Code that exists.**
- Naibbe re-encryption with flow choice: `f3_flow_choice.py:55-73` `naibbe_chunks()` reads the Zenodo workbook `data/naibbe_zenodo_17219445/Naibbe_Cipher.xlsx` (`c4_naibbe_lines.py:38`), sheet `encrypter`, rows ≥15: chunk letters + the six-table homophone pieces per letter and role (u/p/s). `f3_flow_choice.py:75-90` `cipher_stream()` re-encrypts the chunk sequence choosing among prefix×suffix pieces with weight `count × R(last,first)^beta`. `k1_joint_producer.py:121` `cipher_pages()` adds the M5 line layer (para-initial null word, Q_init/Q_end reweight, d-gradient; all rates measured on Voynich, k1 docstring lines 13-24). `k5_export_entrants.py:43` exported it as `data/controls_synthetic/flow_cipher_layer.meta.json` (meta `source`: "k1 CIPHER +layer: Naibbe tables (Zenodo 17219445), flow beta 1.5, M5 layer; tables measured on Voynich"; 159 pages, 21,292 tokens per results_n5.txt line 12).
- Random Naibbe-like key on Latin herbal: `ctl_naibbe.py:24-48` (26+676 units → 1–4 symbols from an 18-symbol core, p=0.5 bigram split, six tables; plaintext Macer+Pliny; output `data/controls_synthetic/naibbe_like`). Period-free random key; useful only as a second reference row.
- s31 pilot (peer, pre-registered 20:23, hashes OK): `s31_null_glyph_charwin_pilot.py:227-296` `gen_s31_cipher_null_affix()`: per plaintext stem k=3 homophones sampled from n6's word-internal order-2 glyph model (`n6_habit7k_glyph.py:117 sample_word_m2`), null-pad with prob `p_null_pad` (an M2 word replaces the homophone; lists `null_prefixes/null_suffixes` at lines 241-242 are declared but not used in the body — unverified beyond lines 227-296), reduplication 0.0085, line edges drawn directly from Voynich word pools (`build_m5_edge_pools`, lines 109-129: para-initial, ordinary line-initial, line-final tokens with counts; draw rates 0.55 line-initial, 0.48 line-final, lines 265/270), flow weight `R_la_syll^1.5` with `R_la_syll` = `f3.ratio_table` over Latin Macer syllables rank-mapped to EVA characters (lines 91-106; same construction as s30 Part 1B `s30_phase2_u2_u3_deltas.py:301-321`). Plaintext streams: `k2_nomenclator.py:45-53` (Caesar/Augustine alternating per (hand, illus) key). The "150-entry section name list" of the docstring (line 228) has no code in the generator body (unverified: not found in lines 227-296).

**What s31 reached and missed** (results_s31_null_glyph_charwin.txt line 4, verbatim):
`s31_cipher_null_affix (C) | tok=34857 typ=6427 typ25k=5190 hap=0.643 | h2=2.112 sd=1.702 JSDf=0.100 p=x14.51 m=x 3.19 ex=+0.598 rep=1.13% | v1=5/7 v2=7/9 | CHARWIN=+0.057 POSLOCK=1.611 MORAN=-0.017`
Against v2.1 item 1 margins: h2 in (2.054–2.152); p_init in (12.30–26.35); jsd_first_fg OUT (0.100 < lo95 0.1447); m_final OUT (×3.19 vs 10.18–27.41); cross_excess +0.598 is 12 half-widths above the B value 0.232 ("not reached" by overshoot, item 5b); redup 1.13 % OUT (0.662–1.060); CHARWIN +0.057 vs +0.094 (no s15 width exists); Moran −0.017 (n5 whole-stream estimator, not s21's within-line I). One seed, full book, v2 ranges, Voynich-measured edge pools. It is recorded, not counted (PLAN.md Phase 2 close-out, line 141).

**Positive control.** v2.1 item 7 and PLAN line 152 name "the Zenodo workbook key on `flow_cipher_layer`": the real Naibbe tables re-encrypting Greshko's own sampled plaintext (`f3.naibbe_chunks`), scored as a row on the same board. In Phase 3 there is no decode step, so this row is a cipher-family anchor (a decipherable text with a known key) and not a solver check; it scores CHARWIN −0.182, Moran −0.021 (results_n5.txt line 12) and its tables are Voynich-measured, so it can reach nothing the entrant is judged on (decision 2).

**Smallest build that satisfies item 7.** One script `s10_cipher_twin.py`, one output `results_s10.txt`, sidecars under `runs/s10/` (not `data/controls_synthetic/`), stub frozen with sha256 before the run. Generation per transliteration T ∈ {ZL3b, RF1b, IT2a} (n6 pattern, `n6_habit7k_glyph.py:213-240`): seed 0 = calibration only, seeds 1–3 = measurement. Scoring: `scoreboard/run_v2.py score_one` with `--ranges s15_ranges.json`, rows all/A/B (`--lang`, sidecar page field `lang`, `s1_v2_joint_producers.py:116 layout_with_lang`), full sidecar for the 25k-scale `types_25k`, and the 41 held-out pages (`g1_edge_joint.py:79-85 split_names`, `Random(20261017)` shuffle, 80/20 of 207 → 41; `s15_band_widths.py:65` `subset_ids(g1=True)`) for the margin comparison against `s15_ranges.json → g1_heldout_41`. Extras: CHARWIN via `n5_signature_discrimination.py:118 score()` (m3.page_split seed 20261017, 80/20); within-line Moran I + 999-draw line-shuffle null via `s21_moran_realline.py`; F1 via `N.residual(by,"quires")` and NMI-h1 via `n3.nmi_tests` + `n4.nmi_bifolio` exactly as `n4_habit7k.py:336-364`.

**Free parameters and how each is fixed before scoring** (no value chosen by looking at the board):
| parameter | fixed how | source |
|---|---|---|
| homophones per unit | 3 (vowels) / 2 (consonants) if letter-level; 3 per stem if s31 design | period profile `research_notes/External anchors/period_nomenclators.md:30`; s31:248 |
| null rate `p_null_pad` | one seed-0 bisection to T's type count (14 steps, the s1 "one parameter" budget) | `s1_v2_joint_producers.py:3`, `s31:400-410` |
| flow beta, M_CAND | 1.5, 8 inherited constants | `s31:72-73`, `n4_habit7k.py` docstring |
| edge table | `R_la_syll` (real-line-derived Latin syllable), identical object handed to s28 | `s30:321`, `s31:91-106` |
| line-edge draw rates | inherit s31's 0.55 / 0.48 verbatim (pre-registered) or derive from results_m5_line_anatomy.txt line 100 (0.717 attested mid-line) — decision 4 | `s31:265,270` |
| plaintext | k2 Caesar/Augustine per (hand, illus) | `k2_nomenclator.py:45-53` |
| names list | 150 per section (docstring) — needs code | `s31:228` |
| reduplication | 0.0085 | `s31:276` |
| seeds / pages | 0 calibrate; 1,2,3 measure; g1 41 pages | v2.1 item 7 |

## 2. s28 — matched generator

Generator: `s31:298-370` `gen_s31_generator_m5_direct()` = c2 `Gen` (`c2_section_generator.py:66`, copy/lexicon/mutate, p_seed 0.6, p_mut 0.6) + N2 habit table p=0.04 (`n4_habit7k.py:163 habit_table_over`) + V2_glyph 7k lexicon (`n6.synth_glyph_forms`, lam by seed-0 bisection, `n6:156-180`) + the same `R_la_syll` + the same M5 pools. The edge table is handed as the `f3.ratio_table` closure (`f3:49-52`), the same object s2 fitted on A/B/166 pages (`s2_u1_u2_u3_controls.py:387-414`, verdict results_s2 line 30) and s30 used in Part 1B (`s30:333-342`). Matching = same R, same pools, same M2 glyph model, same calibration target and seeds, so the pair differs only in the word stream (Latin plaintext through a key vs copy-mutate). s31 row (line 5): `typ=6794 … h2=2.127 JSDf=0.111 p=x21.85 m=x3.54 ex=+0.627 rep=0.73% | v1=6/7 | CHARWIN=-0.021 MORAN=+0.053`. TEAM-HANDOFF.md line 70 attributes the m_final miss to M2 trained on all words; training M2 on `ws[1:-1]` is a design change that must go into both stubs (matched) and be frozen before the run.

`c2_s1_joint` (`s1_v2_joint_producers.py:332-370`; sidecar `data/controls_synthetic/c2_s1_joint.meta.json`, 19:40) cannot be reused as s28: it uses Voynich's own table `R = f3.ratio_table(by)` (s1:302) and k1 Q_init/Q_end measured on Voynich, one seed, full book, v2 ranges, no held-out split; it missed p_init ×6.37 and m_final ×4.07 (results_s1_v2_joint.txt lines 22, 39). It is a reference row at most. s28 must be rebuilt as a fresh script; the s31 sidecar `runs/s31/s31_gen_m5_direct.meta.json` is the nearest ancestor and is also not the scored-once run.

## 3. s27 — K4 as a bound only

Reported: one v2.1 row set (all/A/B, 3 seeds, 41 pages, RF1b/IT2a) at K4's middle setting k=6 w=180 β=1.8 (`k4_lossy_nomenclator.py:143-146`), with its shuffled-plaintext null (k4:155-160). results_k4.txt lines 5-9 already show the ceiling: types 5,076–5,613, hapax 0.31–0.33, h2 2.23–2.31, m-final ×2.6–4.5, crossMI +0.215–0.693, residual +0.038–0.050, NMI h1 0.17–0.32. Why it cannot be favoured: (i) PLAN.md line 78: "K4 is a bound, not a hypothesis" (B-prior-art §5: no period nomenclator near 7k; L-107); (ii) it is circular twice — `R = f3.ratio_table(by)` on Voynich (k4:133) and a codeword pool of Voynich types ranked by frequency (k4:40-45) — so edge/coupling are reached mechanically (v2.1 item 5); (iii) types and hapax fail the margin. Its use: a "reached / not reached" line per target metric showing what even a circular word-code reaches (F1 +0.047, NMI-h1 0.27), entering no count.

## 4. Judged target set (v2.1 item 7) and predicted separation

| metric | Voynich | margin / rule | s10 predicted | s28 predicted | separates? |
|---|---|---|---|---|---|
| types_25k | 5417 full; 2535 g1_41 | s15 1911–2654 (41 p.) | in (calibrated) | in (calibrated) | no |
| h2 | 2.126 | 2.054–2.152 | in (s31 2.112) | in (2.127) | no |
| jsd_first_fg | 0.176 | 0.1447–0.2156 | out (0.100) | out (0.111) | no |
| p_init_enrich | ×17.9 | 12.30–26.35 | in (×14.5) | in (×21.9) | no |
| m_final_enrich | ×16.3 (B ×32; A no weight) | 10.18–27.41 | out (×3.2) unless M2 mid-line fix | out (×3.5) same | no |
| CHARWIN | +0.094 | none on file (n5: G max +0.038, E max −0.147) | positive (+0.057, s31 H2) | negative (−0.021) | **yes** (sign) |
| Moran I within-line | 0.157 | Δ = entrant I − Voynich I with page-bootstrap 95 % interval (see rule below) | missed (Latin word lengths give I<0: prose15 −0.033) | missed (G max 0.129, c-320) | sign differs; both predicted "missed" |
| F1 residual | +0.046 (CI 0.036–0.056) | Δ with bootstrap interval (n6 gives per-run CIs) | reached if letter-level (Naibbe +0.04, f3 docstring line 5; K4 +0.047) | missed (n6 +0.027, CI 0.016–0.039) | **yes**, design-dependent |
| NMI-h1 | 0.275 (bar 0.206) | ≥0.206, 1/55 floor | letter-level: no (k2 docstring lines 3-5: K1 cipher shows no section NMI); stem-level: yes (nomen 0.366) | no (n6 0.087) | **only if stem-level** |
| cross_excess / edge MI (B) | 0.232 / 0.240 | reached = within ±0.030/0.032 of B; no weight | overshoot +0.598 | overshoot +0.627 | no |

**Effect-size rule for the three unbanded metrics (coordinator addendum, 20:58).** A per-dataset p-value (entrant beats its own line-shuffle q99) tests the entrant against its own null, not against Voynich, so it is not the reached/missed rule. Rule: Δ = entrant value − Voynich value with a page-bootstrap 95 % interval (Daybreak's REPORT.md uses a page bootstrap; `s21_moran_realline.py` has the within-line estimator and the per-corpus values in results_s21.txt; `N.residual` already returns a page/quire bootstrap CI for F1, results_n6.txt lines 5-18; CHARWIN gets the same page bootstrap over m3's 80/20 fold). "Reached" = the interval includes zero or lies above it; "missed" = the interval lies entirely below zero. The own-null q99 line is still printed (the O-043 clause "no tested meaningless model reproduces it", results_s21.txt line 36) but does not decide. No entrant parameter may be tuned to the Moran, CHARWIN or F1 value: each is fixed from the mechanism (table §1) before the stub is frozen, and what counts is the prediction holding on untouched material — the 41 held-out pages for the board metrics and the seeds never used in calibration for the whole-book ones.

Plainly: of ten judged quantities, seven are predicted ties (five by shared construction: same M2, same pools, same table, same calibration). The separators are CHARWIN (one pilot seed; no stated margin) and F1, plus NMI-h1 only if s10 is a stem-level code — which B §5 closes historically. Under the v2 §7 arithmetic both entrants are expected kill-candidates (jsd_first, m_final, redup tight-outs), so the pair cannot deliver a Tier-2 "favoured" verdict; the best deliverable is a registered two-metric lean (CHARWIN, F1) with BH over the round's p-values. The gate should hear this before the stubs are frozen.

## 5. s24 — bounded musical/hybrid notation check

**What is on disk.** No edge-transition matrix or slot table is saved anywhere (no `np.save`/matrix dump in any script; results_*.json are metric rows). What exists: sidecars with lines (`data/translit/{ZL3b_eva,RF1b,IT2a}.meta.json`; `data/controls_synthetic/` c2_best, flow_cipher_layer, flow_gen_layer, markov1, naibbe_like, nomen_*, c2_s1_joint, nomen_s1_joint; `data/controls_realline/`; `data/external/cremma/` 54 sidecars; `results_s17_*.json`/`results_s18_cremma_*.json` are rows, not matrices) and in-memory builders: `f3.ratio_table` (ratio R), `g1_edge_joint.py:87-100 fit_table` (count table last→first, MIN_COUNT), `c3_edge_coupling.py:45 edge_pairs` (EVA chars and glyph+ units), `d1_edge_coupling.py:61-68 cross_pairs/within_pairs`, slots via `scoreboard/metrics_new.py:341 slot_structure` (SlotSegmenter prefix×core×suffix occupancy, top 2000 types) and `d2_slot_bakeoff.py:81 fit_slots`. Shapes: EVA ~23×23 (last glyph × first glyph), glyph+ ~30×30 (`corpora.GLYPHS_PLUS`). The cap's "existing edge matrices and slot tables only" must therefore mean "built at run time from existing sidecars with existing builders; no new generator" (decision 6).

**Statistic.** T = within-line last→first glyph count matrix. Order both axes by one permutation π; score MAD(π) = Σ T_ij |π(i)−π(j)| / Σ T_ij. Search: spectral (Fiedler vector of the Laplacian of T+Tᵀ) then 2-opt sweeps, fixed 200 sweeps, seed 20261017; report MAD and band mass |π(i)−π(j)| ≤ 2. Same search for every control.

**Controls, same search.** (a) 200 within-line token-shuffle nulls of each Voynich transliteration (preserves line marginals); (b) 200 independent row/column permutation nulls of T (same margins); (c) real-line language tables: cremma_prose15, cremma_c15, mhg_nibelungenlied, italian_dante (s17/s18 sidecars, native lines); (d) generator tables: c2_best, flow_gen_layer, markov1, timm_schinner (sidecars scored by n6, `results_n6_timm_schinner.json` → its sidecar under data/controls_synthetic; unverified name).

**Fixed predictions as pass/fail.**
1. Seriation: PASS iff Voynich MAD < 1st percentile of both null families on all three transliterations AND below the minimum MAD of every language and generator table by more than the spread of the three Voynich transliterations. Otherwise FAIL.
2. Line-end reset: ratio = MI excess(last glyph of line n, first glyph of line n+1) / within-line excess (d1 `cross_pairs`/`within_pairs`, 20-rep nulls). PASS iff Voynich ratio < the minimum ratio over the four language tables on all three transliterations. FAIL otherwise.
3. Pitch-slot removal: strip the SlotSegmenter core from every token; PASS iff the residual (prefix+suffix) stream has ≤ 100 types covering ≥ 90 % of tokens AND its h2 lies inside the L family h2 range of `s15_ranges.json`. FAIL otherwise (Latin h2 rows carry no weight, v2.1 item 3, so this reads against the m4 L range only).
Verdict: musical/hybrid framing "not excluded" only if all three PASS; any FAIL retires it for the pair.

**Runtime vs cap.** Matrix build <1 s per corpus; a 23×23 search ~50 ms; (200+200)×3 + 8 control searches ≈ 1,208 searches ≈ 1 min; prediction 2 ~20 s; prediction 3 ≈ 3 × 20 s (`slot_structure` is part of run_v2's 19–23 s full-book score, results_s15.txt lines 40-42). Expected 2–3 min, one CPU, no GPU; wall-clock guard at 15 min writes a STOPPED line to `results_s24.txt`.

## 6. Costs and hazards

Runtime evidence: 41-page `score_one` 4.5 s mean (results_s15.txt line 7); full-book 19–23 s (lines 40-42); s1 (2 entrants × 1 seed × 3 subsets, full book, v2) 4 min (prereg 19:39:39 → results 19:43:40); s31 (2 calibrations + 2 generators + n5 signatures) 73 s (20:23:45 → 20:24:58); n6 (3 T × 6 runs with F1 bootstrap and NMI nulls) ~6 min (19:36:07 → 19:42:18); n5 CHARWIN ~5 min for ~30 rows; s21 12 Moran rows with 999 draws 66 s.

Hazards: (1) `scoreboard/run.py` files into `scoreboard/scoreboard.json` (run.py:1,34); use `run_v2.score_one` only (run_v2.py:23 "does not touch scoreboard.json"). (2) Sidecars in `data/controls_synthetic/` are picked up by any script that lists that directory (s31 avoided it with `runs/s31/`; s1 did not); write to `runs/s10|s28|s27|s24/`. (3) Prefix collisions: files changed since 20:45 are only s20/s21/s23, PREREG-v2.1.md, scoreboard/PREREG-v2.1.sha256, PLAN.md and the registers; no new s*/t* script or result from peers; TEAM-HANDOFF.md line 266 reserves s27/s28/s5/s10 and s20–s24 for voynich-08, "s32 onward" free. (4) F1, NMI-h1, CHARWIN are whole-book/page-split statistics (quire split, 80/20 page split); they cannot be scored on 41 pages; n5's m3 split and the g1 split both use Random(20261017) 80/20 but identity of the page sets is unverified. (5) The M5 edge pools are Voynich tokens: jsd_first/p_init are reached by construction for both entrants, so they are "fixed by the handed pools" exactly as coupling is fixed by the table. (6) Three transliterations × 3 seeds × calibration = the generator runs 3× (n6 pattern); the board-scale slot is the full-book score_one (~20 s × 27 rows per entrant).

## Decisions needed before the Phase 3 plan
1. s10 design: letter-level verbose homophonic (period-plausible, L-107; predicted no NMI-h1) or s31's stem-level homophones (predicted NMI-h1, but a codebook by another name, B §5). Decides whether NMI-h1 separates.
2. Role of the positive control: `flow_cipher_layer` (Voynich-measured tables, known key) as a reference row only; no decode step in Phase 3.
3. Scoring unit per metric: board metrics on the 41 held-out pages, F1/NMI-h1/CHARWIN on the full book with their own nulls, declared in the stub.
4. Line-edge pools: inherit s31's Voynich pools and declare jsd_first/p_init "fixed by the pools, no weight", or build the edges from m5 rates only (then both entrants likely miss them as s1 did).
5. Confirm the Δ-with-page-bootstrap rule (§4) for Moran I, CHARWIN and F1 (interval below zero = missed), and NMI-h1 ≥ 0.206 with the 1/55 floor; bootstrap B and block unit (pages for Moran/CHARWIN, quires for F1 as n6) fixed in the stub.
6. s24 cap reading: matrices built at run time from existing sidecars; the three pass rules above adopted verbatim; the M2 mid-line (`ws[1:-1]`) fix applied to both entrants or neither.

## Cost table (one CPU, sequential)
| step | what | minutes | board-scale slot |
|---|---|---|---|
| s24 | matrices + 1,208 searches + 2 predictions | 2–3 (cap 15) | no |
| s27 | K4 one setting × 3 T × 3 seeds, v2.1 rows, extras | ~20 | yes (27 full-book rows) |
| s28 | calibrate + generate 3 T × 3 seeds, v2.1 all/A/B full + 41 p., CHARWIN, Moran, F1, NMI | ~25 | yes |
| s10 | same as s28 | ~25 | yes |
| ledger | BH block, power lines, hash checks, results assembly | ~5 | no |
| total | | ~80 | one NMF-class job at a time (PLAN line 147) |
