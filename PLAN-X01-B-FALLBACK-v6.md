# PLAN-X01-B-FALLBACK-v4: Part B on true unsegmented whole words (DRAFT for IV review; NOTHING frozen or run)
Date 2026-10-19 (PDT). Author: Voynich Analyst for Jon. Plan id PLAN-X01-B-FALLBACK, version 4. Supersedes B-FALLBACK-v3 (55bd50b6cb8615998c1713eb120b0b0e266eaa3db7f46796cc1341d742e37861), v2 (7abab496...), v1 (b3d5ab3c...) and v0 (ec030526...); all kept unchanged.
Base: PLAN-X01-v5.1 (af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393), sections 3, 3a, 5 and 5b. This file expands 5b. Where it differs from 5b or adds to it, the difference is listed in section 10 ("Differences from v5.1 5b"). Everything in v5.1 not listed there applies as written. It does not depend on v5.2.
Answers IV-REVIEW-X01-B-FALLBACK-v3.md (e24d053acb36d43e4b14c2592b6a9f76eb9921282c7575694805a07cd65dd29b; 1 must-fix) with Eve's calls of 2026-10-19, on top of the v2 (8438e85b...), v1 (393aa60a...) and v0 (d2ab5f40...) reviews. DEVIATION_1 (B2 dropped, 20c5de2b...) was accepted by IV. v4 changes only what section 15 lists.
Every result later filed from this plan is UNVERIFIED until the Independent Verifier signs.

## 0. Hard limits
- No A1 rule, threshold, seed, row or label is changed here.
- The Zattera-hybrid dependency is NOT changed. This plan runs only because A1 found Zattera-hybrid not ADEQUATE ON PLANTED BOOKS in at least one of the 9 cells (v5.1:155). It failed 9 of 9 (IV-RESCORE-X01-A1.md, e7be4afc...). Had it passed all 9, this plan would be void and section 5 would apply.
- Freeze, seed-guard and log rules are v5.1 section 3 rules 1-8, unchanged: stub `<name>.prereg.sha256` citing v5.1 and this file's hash, per-gate-seed SHA256 (already in frozen `vx01_common.py`), one hash-chained dev log per script (head fixed in the stub), a separate gate log not in the stub, one-shot gate, max 2 code-only revisions, the counts 10/15 and 4/15, at most 2 BelowNormal workers, running jobs untouched.
- New rule from the A1 record addendum (vx01_a1_RECORD_ADDENDUM_1_loaded_files.md): each stub lists EVERY file loaded at run time (spec loads included), found by a run-time trace at freeze (section 8).

## 1. Units and scope
- True unsegmented whole words (EVA token strings as stored in the sidecar) for ALL tokens of every text, real and planted. Text loader: `S67.load_pages(path)` (s67_constrained_assembly_loqo.py:193-202), which returns (page id, quire, lines of words). No prefix/core/suffix split anywhere in SCORING (5b:156).
- Folds: the 15 quires of `S67.folds_of` on ZL3b (s67:579-581), i.e. A B C D E F G H I M N O Q S T (results_s101.txt:75). The same 15 labels are used for all 3 transliterations.
- Findings and producers in this plan (one row each, from results_s101.txt CALL lines):
| Finding | Producer(s) | Producer unit label (IV item 2; Eve call 2) | Source |
|---|---|---|---|
| F-23 | s57, s58, s61, s67 CA, s67 CA0 | built on Slot units | `seg_voy` passed, s101:684-710 |
| F-23 | r13 A (copy-and-vary) | no qualifier (no segmenter) | runs/roach-r13/r13.py:9-17, 132-154 |
| F-30 | s71 WTG global, WTG scribe | built on Slot units | `WTGProducer(tr_meta_voy, seg_voy, ...)`, s101:714 |
| F-30 | r13 B (table-and-grille) | built on S1 units (roach r7 prefix/suffix lists) | r13.py:18-19, 73, 118 |
| F-34 C1 | s81 line_sticky_fit, line_sticky75 (Latin plaintext) | no qualifier (no segmenter) | `S81.encipher`, s101:729; s81:218-256 |
| F-41 C2 | LP91 + s81 word stream | built on Slot units | `seg_voy` cores, s101:734-743 |
- Only s57, s58, s61, s67 (CA/CA0), WTG and LP91 are Slot-built. An EXCLUDED call for them reads "excluded as built on Slot units". For r13 B it reads "excluded as built on S1 units". For s81 and r13 A it has no qualifier. NOT EXCLUDED reads "survives the new whole-word criterion". v0 line 44 wrongly called the sticky battery and r13 A and B "built on Slot units". That was wrong.
- **F-41 C1 is NOT run under this plan (no claim).** It scores the LP91 core stream (`seg_voy.segment(w)[1]`, s101:734, 742; results_s101.txt:166), which 5b:156 forbids. Only F-41 C2 (the word stream) runs (Eve call 3).
- **B2 is dropped from this version** (Eve call 4). Its arms are segmented: F-44 is the Zattera arm and F-50 uses SQLite features (A3 N/A). See `vx01_bf_DEVIATION_1_B2_dropped.md`. The B2 seeds of 3a stay in `vx01_common.py`, unused.
- **WTG (global and scribe) and s81 line_sticky75 get NO EXCLUDED call under this plan.** They have no parameter grid (WTG_PARAMS fixed, s71:105-116; line_sticky75 p fixed at 0.75), so no MEI control can be built for them (v5.1:134). They can still be NOT EXCLUDED, MIXED or UNINFORMATIVE.
- **r13 A and B stay in.** They are loaded through the path-remap loader `vx01_bf_pathmap.py` (section 8a), because r13.py:66 and r10.py:61 point at `runs\r10\` and `runs\r7\`, which do not exist. The files live in `runs\roach-r10\` and `runs\roach-r7\` (IV v1 item 1). r13 is run on all 3 transliterations: each text is passed to r13 as its line tuples (quire, page id, words), the form `r13.Fit` and `gen_A/gen_B` take (r13.py:110-123, 132-174). r13's own IVTFF reader is not used.
- A14 and R(1) "report-only" analogues from v0 are dropped. No call ever rested on them, and they would add files (s80, s56) to the run.

## 2. The six statistics (fixed now; all per held-out QUIRE; codeable blind)
Notation: a "text" is a list of pages (pid, quire, lines). For a quire q of a text, `lines_q` = its lines in file order (lists of EVA words), `toks_q` = its tokens in reading order, and `gl(w) = corpora.to_glyphs(w, corpora.GLYPHS)` (corpora.py:11, 16-19, the same glyph rule as s113:136-137). Imports: `tools/vkb/features.py` as F, `m3_bakeoff_reconcile.py` as M3, `corpora`. `tools/s113_g2_envelope.py` is NOT imported (its `book_stats` fits SlotSegmenter, s113:143-146). `s57.Measured` is NOT used (it fits SlotSegmenter, s57:494, and imports g1_edge_joint, which spec-loads score.py).
Each text or copy has a tag string `tag`: `"vx01_bf|real|<T>"` for real text, and `"vx01_bf|<seed>"` for a generated text, where `<seed>` is that text's derived seed (section 6).
| k | Name | Exact definition (value for quire q) | Function (file:line) |
|---|---|---|---|
| 1 | Rw1_line | `F.rw1(lines_q)[1]`: adjacent same-word pairs inside lines over the exact within-line-shuffle expectation (empty words excluded by the function) | features.py:56-80 |
| 2 | h2 | `F.h1_h2([gl(w) for w in toks_q])[1]`: glyph conditional entropy H(next \| prev), with word-boundary padding | features.py:39-53 |
| 3 | rhythm | For each page p of quire q: `_, exc, n = F.rhythm([[len(gl(w)) for w in l] for l in lines_p if l], np.random.default_rng(F.seed(tag, pid, "rhythm")))`. Quire value = sum(exc*n) / sum(n) over pages with exc not None (pair-weighted, the same formula as s113:150-156, written out here). None if no page qualifies. | features.py:30-31, 83-112 |
| 4 | TTR_300 | TTR at matched token count. N = 300 tokens, R = 50 subsamples. rng = `np.random.default_rng(F.seed(tag, q, "ttr"))`. For r = 1..50: `idx = rng.choice(len(toks_q), 300, replace=False)`, ttr_r = (#distinct words among those 300) / 300. Value = mean of the 50 ttr_r. | own code (10 lines) |
| 5 | mean_len_eva | mean of `len(w)` over toks_q, in **EVA characters** | own code; = r13 t8 (r13.py:206) |
| 6 | CHARWIN_w | `pages = [dict(id=pid, lines=ls) for train pages] + [dict(id=pid, lines=ls) for pages of quire q]`; `acc = M3.score_folds(pages, [list(range(n_train, len(pages)))])`; value = `acc["unigram-GT-renorm"]["bits"]/acc["unigram-GT-renorm"]["tok"] - acc["char3-WB"]["bits"]/acc["char3-WB"]["tok"]`. Train pages = all pages of the TEXT UNDER TEST (real text in B1 and r_k; the planted book in B0) whose quire != q. The same train pages are used for the copies' quire q. Raw words, no Slot input. | m3_bakeoff_reconcile.py:87-97, 100-111, 118-140; same arithmetic as s57:519-523 |
- **Why N = 300 for TTR.** It is a round number below the smallest fold quire: quire I has 367 / 359 / 353 tokens on ZL3b / RF1b / IT2a (a token count read from the sidecars, not a statistic value). So TTR_300 is defined on every fold quire of every transliteration, and copies use the same layout. v0 cited r13 t7 as "matched", but t7 is the raw quire TTR (r13.py:205), so it was not matched. That was wrong.
- **Why EVA characters for word length.** It is r13 t8 exactly (r13.py:206), and glyph length already enters through rhythm (k=3) and h2 (k=2). Using EVA characters keeps statistic 5 distinct from those, and it needs no glyph rule.
- **Old statistics not defined on whole words:** M1 gain, b_pos and M7 need affixes or cores. They are replaced by k = 2, 3, 4 and 5 (as v0).
- **Undefined values and the match rule (IV v1 ruling 2; Eve call 2).** If statistic k is None or NaN on the scored quire, k is undefined for that fold. If it is undefined on >10% of the 200 copies, k is also undefined for that fold. **A fold MATCHES if and only if at least 5 statistics are both defined AND inside the band.** So with 6 defined, at most 1 may miss. With 5 defined, none may miss. With fewer than 5 defined, the fold is a NON-MATCH, reported as UNDEFINED. This replaces v1's rule (">= 5 defined, <= 1 miss"), which let a fold match with only 4 inside, below 5b:157's ">= 5/6 inside".
- **Level.** All six are measured per held-out quire: real value, copies and band. Nothing is measured at book level, except the fit loss (section 4), which pools training quires.

## 3. Nuisance spread r_k (measured FIRST by `vx01_bf_rk_c2.py`, at quire level)
- For each fold quire q and statistic k: r_k,q = max - min over ZL3b / RF1b / IT2a of statistic k (section 2) on real quire q, with tag `vx01_bf|real|<T>` and CHARWIN train = the other real quires of the same transliteration. 15 x 6 numbers. Also reported, but not used: the median over q of r_k,q.
- This is quire level, to match the band (IV item 5e). 5b:158's "max - min over ZL3b/RF1b/IT2a on the real whole-word text" is applied per quire. A pooled whole-book r_k is not used.
- Inputs: the 3 sidecars (section 8 D-rows), features.py, m3_bakeoff_reconcile.py and corpora.py (plus their imports, section 8). No model, no hypothesis, no random seed except the fixed `F.seed` tags.
- `vx01_bf_rk_c2.py` is frozen, run once, and its output table's SHA256 goes into the B0 stub before any producer is planted or scored.

## 4. Fit loss, fitter, band
- **Loss (IV item 6; IV v1 item 9).** For fold q, Qtr = the 14 OTHER FOLD QUIRES (the 15 fold quires minus q). Quire J and any other non-fold quire are never in Qtr. For a text X, s_k(X) = mean of statistic k over the quires in Qtr where k is defined, for k = 1..5. d_k is taken over the same defined quires. If k is defined on fewer than 10 of the 14, k is undefined for X at that fold, and its L term = 25. CHARWIN (k = 6) is NOT in the loss, because inside the fit it would need an inner leave-one-quire-out on every evaluation. It is still scored in the band. d_k = max(SD over those defined quires in Qtr of statistic k on the REAL-or-planted text under test, 1e-9). The copy's g_k uses the same rule (mean over its defined quires of Qtr; undefined if fewer than 10 of 14). For one candidate parameter set θ, the producer makes 1 simulated copy of the training layout (the same as the original fitters, e.g. s57:409), with seed rule control `fit|<fold>|<eval index>`. Then g_k = s_k(copy) and **L(θ) = Σ_{k=1..5} ((g_k − s_k(X)) / d_k)²**. Undefined g_k or s_k: that term = 25 (a 5-SD miss). Note: producer TRAINING input (below) and CHARWIN train pages are still "all pages with quire != q" (J included); only the loss uses Qtr.
- **Fitter (named; one per producer; frozen in the B0 stub).** The search schedule (stages and grids) of each producer's OWN frozen fit, re-implemented in `vx01_b0_fitter_recovery_c2.py` with L in place of the original loss. Grid constants are imported by name from the module (not copied by hand):
  - s57: stage A GRID_P x GRID_TAU x GRID_A with q = 0.25; stage B q_pre, q_suf, q_core on tenths with sum <= 1; stage C local refine (s57:141-143, 397-445).
  - s58: s58:114, 273-320 (same pattern, q_core GRID_QC).
  - s61: s61:120-121, 295-end of fit (stage A0 p_new, then A, ...).
  - s67 CA: s67:135-138, 414-467, with `CAProducer(..., use_class=True)`, all stages (A, B, refine).
  - s67 CA0 (IV v1 item 4): CA0 is the CA producer with `use_class=True` and gamma = 0 (rho moot = 0), i.e. CA's stage A only (s67:41, 55, 443-447; `"CA0": F["p0"]` at s67:518; s101:424-425). Its fit = stage A only: GRID_PREP x GRID_TAU with gamma = 0, rho = 0, scored by L, on `CAProducer(..., use_class=True)`. v1 wrongly said CA0 is `use_class=False`; that is CA-ind (s67:515-518, 532-534), which is not in this plan.
  - s81 line_sticky_fit: 1-D search over GRID_P (s81:122). line_sticky75: p fixed 0.75, nothing to fit.
  - LP91: GRID, STARTS, SWEEP, MAX_SWEEPS (s91:162-173), with STICKY_P 0.75 fixed (s91:179).
  - r13 A: QGRID x EGRID; r13 B: RGRID (r13.py:71, 177-193).
  - WTG: no free-parameter fit in s71. Params stay `S71.WTG_PARAMS` (s71:105-116, as s101:714). **"Refit" for WTG means: rebuild `WTGProducer` on the training pages of the text under test, with the fixed WTG_PARAMS** (s71:420-425). Its L is still computed, for the hardness check. **So WTG's Power test only tests the rebuild:** it is close to its oracle and says nothing about parameter recovery (IV v1 ruling 4).
  - The exact end line of each fit() is cited in the stub when the code is written. If any schedule cannot be reproduced exactly, that producer is UNINFORMATIVE (no call).
- **Page meta (IV v1 item 6).** Every text (real, planted book or copy) carries for each page: id, quire, hand, section and para, taken from `S71.load_translit_meta(T)` (s71:983-1004) for the layout page it occupies. Planted books and copies inherit them page by page from T's layout. WTG is rebuilt (its "refit") on that meta for whatever text is under test (s71:420-425, 462; WTG_scribe uses the page hand, s71:947; s101:718-722). Line counts and words-per-line come from `S67.load_pages(T)` (s101:685-686), except for WTG, whose line lengths come from the meta lines, as in s101:718-722. `--build-params` checks that page ids agree between the two loaders and writes the result into the params file. If they disagree, that is reported and no freeze happens until IV rules.
- **Producer training input.** Built exactly as s101:683-743, with the real text replaced by the training quires of the text under test (and `seg_voy` = SlotSegmenter fitted on those training words, for the Slot-built producers only).
- **Band.** For fold q: 200 copies of the refitted producer, each generated on the layout of quire q (pages, lines, words per line) of the text under test. Seed rule control `<control>|copy|<r>`. Band per statistic = `np.percentile(defined copy values, [0.5, 99.5])` (numpy default linear). Frozen procedure; the same procedure in B0 and B1 (the B1 stub hashes the B0 stub).

## 5. Planting parameters and MEI map (IV item 9; Eve call 9)
- **Planting rule (written, not by eye).** θ_plant(P, T) = the parameters the ORIGINAL frozen producer scripts fitted on the real training quires of T, read by the s101 rule `load_voynich_fitted_params` (s101:285-310), unchanged:
  - s57 / s58 / s61: `runs/s5x/fit_<T>.json` "params" (s61: "JW").
  - s67 CA: median over the 15 folds of `runs/s67/cells.json`.
  - s81: median p of `line_sticky_fit|latin_cremma` in `runs/s81/cells.json`.
  - LP91: median over `runs/s91/folds/<T>_*.json`.
  - WTG: `S71.WTG_PARAMS`.
  - s67 CA0 is not in s101's loader: its θ_plant = the median over the 15 folds of T of `runs/s67/cells.json` `params["CA0"]` (the key exists; 45 cells = 3 x 15), the same median rule as CA (accepted by IV, v1 ruling 3). The planting producer is `CAProducer(tr_voy, seg_voy, use_class=True)` (s101:707).
  - r13 A / B: `r13.fit_params(kind, Fit(all pages of T with quire != 'A'), same)` (r13.py:177-193), a deterministic grid fit with fixed seeds 13001 / 13002.
  - Planted books: producer trained on the real quires != 'A' of T (s101:683, 713, 734), generated on T's full layout (s101:685-686).
  - These values were fitted before this plan existed, by frozen code, so the plan author does not choose them. The real text enters this plan only through: (i) those fitted parameters and the producers' training quires; (ii) `vx01_bf_rk_c2.py`; (iii) B1.
- **Params file.** `vx01_b0_fitter_recovery_c2.py --build-params` (no seed, no planting) writes `vx01_bf_plant_params.json`: θ_plant for every (P, T), each value's source file and SHA256, and the fitter grids/schedules (by module constant name and value).
- **MEI map rule** (`--calibrate-mei`, dev seeds only).
  - All MEI books are generated by the PLANTING producer object (same training input, seg_voy and tables; section 7 oracle rule) with parameters reset to the candidate. Only the RNG seed differs.
  - For each (P, T), on the dev book (master 20261101), make the oracle band at θ_plant for each fold (200 copies at θ_plant, no refit), giving lo_k,q, hi_k,q and the copy SD sd_k,q.
  - Candidates: θ_plant with exactly ONE parameter set to another value of that parameter's grid in the table below (IV v1 item 7). Grids and key order (the key order is used for ties):
| Producer | Key order | Grid per key |
|---|---|---|
| s57 | p_copy, tau, a, q_pre, q_suf, q_core (the order of s57:405) | GRID_P, GRID_TAU, GRID_A (s57:141-143); each q on tenths 0.0-1.0 (s57:427-430); a move that makes q_pre + q_suf + q_core > 1 is not a candidate |
| s58 | p_copy, tau, a, q_core (the order of s58:281) | GRID_P, GRID_TAU, GRID_A as used at s58:293-295; q_core GRID_QC (s58:114) |
| s61 | `KEYS` = p_copy, tau, a, q_edit, p_new (s61:292) | GRID_P, GRID_TAU, GRID_A (s61:119); q_edit GRID_QE (s61:120); p_new GRID_PN (s61:121) |
| s67 CA | `KEYS` = p_rep, tau, gamma, rho (s67:399) | GRID_PREP, GRID_TAU, GRID_G, GRID_RHO (s67:135-138) |
| s67 CA0 | p_rep, tau (gamma = rho = 0 fixed) | GRID_PREP, GRID_TAU (s67:135-136) |
| LP91 | `KEYS` = conc, alpha, rho, lam, pen (s91:162) | `GRID` (s91:163-167) |
| s81 line_sticky_fit | p | GRID_P (s81:122) |
| r13 A | q, e | QGRID, EGRID (r13.py:71) |
| r13 B | R | RGRID (r13.py:71); a new R draws a new table and offsets from the SAME planting `Fit` object, with seed control `meitable\|<cand>` |
| WTG global / scribe | none | none: no MEI control, so no EXCLUDED call |
| s81 line_sticky75 | none | none: no MEI control, so no EXCLUDED call |
  - The s57, s58, s81 and r13 key orders are fixed here (those modules define no KEYS). For s61, s67 and s91 the module KEYS are used.
  - For each candidate: 4 full books (master 20261102, control `meimap|<cand>|<r>`). For each k, m_k,q = mean of the 4 books' quire-q values. Outward distances: up_k = median_q (m_k,q − hi_k,q)/sd_k,q and dn_k = median_q (lo_k,q − m_k,q)/sd_k,q; side_k = the larger of the two.
  - Pair (i, j) is "reached" by the candidate if side_i >= 0.5 and side_j >= 0.5. The 15 pairs are in lexicographic order of (k1, k2), k1 < k2.
  - θ_MEI(P, T, pair) = the reaching candidate chosen by these rules, in order (IV v2 items 3, 4):
    1. smallest max(|side_i − 0.5|, |side_j − 0.5|);
    2. then the smallest step count. For the moved key, build the list S = sorted(set(grid of that key) ∪ {θ_plant value of that key}). Step = |index in S of the candidate value − index in S of the θ_plant value|. So when θ_plant is off its grid, both neighbours are 1 step away: e.g. q_core 0.25 on tenths gives S = [..., 0.2, 0.25, 0.3, ...], and 0.2 and 0.3 are both 1 step;
    3. then the first key in the key order of the table above;
    4. then the LOWER value (an up move and a down move on the same key with the same step: take the lower value).
    These rules give one candidate for every pair, so the map is unique. Comparisons in rule 1 use the computed floats as they are; an exact float tie goes to rules 2-4.
  - Off-grid θ_plant values on disk now (IV v2 item 3): s58 IT2a q_core = 0.25 (runs/s58/fit_IT2a.json; GRID_QC tenths, s58:114; 0.25 = the stage-A start, s58:296); s61 RF1b and IT2a q_edit = 0.25 (runs/s61/fit_RF1b.json, fit_IT2a.json; GRID_QE tenths, s61:120). Rule 2 covers them. The θ_plant value itself is not a candidate (a candidate must change the value).
  - If no candidate reaches a pair, the MEI control cannot be built and no EXCLUDED call is filed for P (v5.1:134).
  - Output: `vx01_b0_mei_map.json`.
- **Freeze order.** The params file, MEI map and fitter (the `vx01_b0_fitter_recovery_c2.py` script itself) are all hashed in the B0-F stub BEFORE any gate-seed book exists. The script refuses `--gate` until the stub verifies (v5.1 rule 3).

## 6. Seeds (Eve call 1: v5.1 3a only; no new seeds)
- B0 dev 20261101, 20261102, 20261103; B0 gate 20261201, 20261202, 20261203 (v5.1:77-78). Their gate hashes are already in frozen `vx01_common.py` GATE_SEED_SHA256 (v5.1:95). B1 uses the B0 gate seeds (v5.1:95). B2 seeds: unused (B2 dropped).
- Derived seeds: the 3a rule unchanged (v5.1:94), first 8 bytes of SHA256("master|transliteration|family|control|fold"). The control field holds the sub-use: `power`, `wrongfam`, `mei`, `nuisance`, `oracle-power`, `oracle-mei`, `fit|<eval>`, `copy|<r>`, `meimap|<cand>|<r>`, `sign|<k>`. Nothing else adds randomness.
- No `vx01_bf_common.py`. The 12 v0 seeds (20265101-20265403) are DROPPED and never used.

## 7. Controls and calls
Cells: 3 transliterations x 3 gate masters = 9; 15 folds each.
| Control | Books | Required in EACH of 9 cells |
|---|---|---|
| Power | 1 planted book of P at θ_plant(P, T); refit per fold; all 15 folds scored | >= 10/15 |
| Wrong-family (hard negative) | 1 planted book of family W at θ_plant(W, T), scored with P's refit band | <= 4/15 |
| MEI | 15 books; book i at θ_MEI(P, T, pair i), scored at fold i only, with P's refit band | <= 4/15 |
| Nuisance | 1 planted book of P at θ_plant (control `nuisance`). At fold q, each statistic k of the scored quire gets value + σ·r_k,q added before comparison with the refit band. σ = +1 if the first byte of SHA256("master\|T\|P\|sign\|k\|q") is even, else −1. All six at once. Additive, on the measured value of the scored quire only; copies are not shifted. | >= 10/15 |
- **Hardness (wrong family).** W is fitted with the same L and its own schedule on the same training quires as P. In each cell: median over folds of L_W(θ̂_W) <= 1.5 x median over folds of L_P(θ̂_P), in all 9 cells. Otherwise use the next pairing (v5.1:145 list, unchanged; r13 A <-> r13 B). If no pairing is hard, P is UNINFORMATIVE. Why the sticky battery is a different family from s57: v5.1:146, unchanged.
- **Oracle control (IV item 7; Eve call 7; dev seeds only; BEFORE any gate).**
  - On dev masters 20261101-103 x 3 transliterations (9 dev cells).
  - **Oracle-power (IV v1 item 5).** The planted book is scored with bands made from copies generated by the SAME producer OBJECT that planted the book: the same training input (real quires != 'A'), the same seg_voy, lexicon, classes and tables, and for r13 the same `Fit`, table and offsets (r13.py:41-54; the rev-2 lesson at r13.py:44-46), at the TRUE θ_plant. No refit and no rebuild. Only the RNG seed differs (control `oracle-power|copy|<r>`). It must be >= 10/15 in each of the 9 dev cells.
  - Oracle-MEI: the MEI books (made by the same planting object at θ_MEI) are scored with the same oracle bands. It must be <= 4/15 in each of the 9 dev cells. Producers without an MEI control (WTG, line_sticky75) run oracle-power only.
  - If either fails, P is UNINFORMATIVE BY FIXTURE and no gate run is made for P.
  - The result file's SHA256 goes into the B0-F stub.
  - Note: the dev seeds 20261101 and 20261102 are also used by the MEI calibration, and dev seed 20261103 is also used for the single-process timing run (section 9). All three B0 dev seeds 20261101, 20261102 and 20261103 are used by the oracle fixture. This is a dev-only reuse, disclosed. 20261103 is a B0 dev seed (v5.1:77; `vx01_common.DEV_SEEDS["B0"]`, vx01_common.py:248-250) and is not a gate seed (IV-REVIEW v3 (d)).
- **B1-F (`vx01_b1_exclusions_rerun.py`).** H_P: P generates held-out quires like Voynich. Each of the 15 folds of real T is scored with P's refit band (section 4), so r_t = 0-15. The B1 table is v5.1:148-153 verbatim:
  - r_t <= 4 on all 3 -> EXCLUDED (needs Power + MEI + Nuisance).
  - r_t >= 10 on >= 2 of 3 -> NOT EXCLUDED (needs Power + Wrong-family).
  - Anything else -> MIXED, no claim.
  - A side whose B0 controls failed -> UNINFORMATIVE.
  - Labels as in section 1.
- Old s101/r13 numbers are NOT evidence about this criterion (5b:157).

## 8. Files loaded at run time (IV item 8; Eve call 8)
How found: a static, read-only scan of import statements (ast) from the roots m3_bakeoff_reconcile, features, corpora, vx01_common, s57, s58, s61, s67, s71, s81, s91, r13 (+ spec loads r10, r7) and score.py, plus the data files named in s101:106-126 and :285-310. Nothing was run. Spec-load edges: r13.py:66-68 -> r10; r10.py:61-62 -> r7; g1_edge_joint.py:46-49 -> scoreboard/score.py. Function-level imports are included (e.g. features.py:208 -> evidence -> findings_graph; these are only reached by build_folio_features, which this plan does not call).
**Rule (IV v1 item 3; a hard stop).** These are today's bytes, a check list, not a freeze.
- (a) At freeze, a run-time trace (open AND process-creation events, rule d) runs EVERY mode of each script (`vx01_bf_rk_c2.py`; `vx01_b0_fitter_recovery_c2.py --build-params`, `--calibrate-mei`, `--oracle`, `--dev`; `vx01_b1_exclusions_rerun.py --dev`) for EVERY producer and all 3 transliterations, on dev seeds only. Method: `sys.addaudithook` on "open" events plus every `sys.modules` `__file__` under the root. A `__pycache__/*.pyc` read is mapped to its `.py`. Entries whose `__file__` is relative (torch registers `torch.ops` as `_ops.py` and `torch.classes` as `_classes.py`) are filtered out, as are standard-library and site-packages paths. Lazy loads are caught because the trace calls every code path: openpyxl in `S64.load_greshko` (s64:151-153), the IVTFF reads of `S69.voynich_pages` (s69:283-290), and r13's spec loads through `vx01_bf_pathmap.py`.
- (b) If any file is loaded that is NOT in the list below, or any listed hash differs from disk, then **NO freeze**. The plan list is updated in a new plan version, and IV rechecks it before any freeze.
- (c) `--gate` (B0 and B1) installs the same audit hook. If any file under the project root is opened for reading that is not in the stub, the run is VOID. The hook allows writes only to the script's declared outputs (its run folder, results file and its own dev/gate logs). On a void, the hook writes a final gate-log line `GATE-VOID <path>`. It counts as the one gate run, so a rerun needs a new script version and IV OK (the same rule as compute condition iii, section 9).
- (d) **Process creation (IV v3 must-fix 1).** The same hook, in `--gate` (B0 and B1) and in the freeze trace, also watches these CPython audit events. Names are exact, from the Python "Audit events table" (docs.python.org/3.11/library/audit_events.html; the same names on the 3.13 page, checked 2026-10-19):

| Audit event | Raised by | Arguments |
|---|---|---|
| `subprocess.Popen` | subprocess.Popen (also run/call/check_output, os.popen) | executable, args, cwd, env |
| `_winapi.CreateProcess` | Windows process creation (internal event) | application_name, command_line, current_directory |
| `os.system` | os.system | command |
| `os.spawn` | os.spawn* | mode, path, args, env |
| `os.exec` | os.exec* | path, args, env |
| `os.posix_spawn` | os.posix_spawn, os.posix_spawnp | path, argv, env |
| `os.startfile` and `os.startfile/2` | os.startfile | path, operation (/2 adds arguments, cwd, show_cmd) |
| `os.fork` | os.fork | (none) |
| `os.forkpty` | os.forkpty | (none) |
| `pty.spawn` | pty.spawn | argv |

  - ANY one of these events, at any time after the hook is installed, means **GATE-VOID**: the hook writes the final gate-log line `GATE-VOID PROC <event> <exe or path> <args>` and stops the process. In the freeze trace the same event means NO freeze (rule b). There is **no allow-list**.
  - The last three events (`os.forkpty`, `pty.spawn`, `os.startfile/2`) are not in Eve's list. They are added because they also create a process.
  - Interpreter: the gate and the trace run on the same CPython as A1 and the IV traces: `<home>/AppData/Local/Programs/Python/Python311/python.exe`, 3.11.9. The project `.venv` is 3.13.12; it is NOT used (it also has no torch, IV-REVIEW v4 (b)). The audit event names above are the same in both versions.
  - **Environment pin (IV v4 must-fix 1).** The B0-F and B1-F stubs record the whole environment, and `--gate` refuses (exit, no gate-log GATE-START) on ANY mismatch with the running process. Values below were re-checked read-only on Skynet, 2026-10-19 ~01:00 PDT (Get-FileHash; `python -VV`; `importlib.metadata.version`; no install or upgrade). They are today's values; the stub takes them at freeze.
    - `sys.executable` = the path above; SHA256 5f7b89a612c9b8af1d6456cdfcd1dbe5ca630849e79aebced9bee9a6694952ec.
    - Full `sys.version` (= `python -VV`): `3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]`.
    - `Lib\site-packages\sitecustomize.py` SHA256 14bae2b6c8862fa98f4fa0396014c545c8daefdb871a2911203cc56be630e113. It runs at every interpreter start.
    - `importlib.metadata.version` of every site-packages distribution imported on the run path. The freeze trace lists them. Today: numpy 2.4.6, scipy 1.17.0, torch 2.11.0.dev20260115+cu128, openpyxl 3.1.5, scikit-learn 1.8.0, joblib 1.5.3, threadpoolctl 3.6.0, pandas 2.3.3, pyarrow 22.0.0, Pillow 12.1.0, lxml 6.0.2, psutil 7.2.1, defusedxml 0.7.1, python-dateutil 2.9.0.post0, pytz 2025.2, six 1.17.0, tqdm 4.67.1, typing_extensions 4.15.0, colorama 0.4.6, charset-normalizer 3.4.4, pywin32 311.
    - Versions are read by DISTRIBUTION name. The module `torchgen` belongs to the distribution `torch` (`packages_distributions()["torchgen"] = ["torch"]`), so it is pinned by torch's version. The module `pywin32_bootstrap` maps to no distribution, so it is pinned through pywin32 311, and the freeze trace hashes its file as well.
    - setuptools 65.5.0 (added in v6): the module `_distutils_hack` is imported at every interpreter start by `distutils-precedence.pth` and belongs to the distribution `setuptools` (`packages_distributions()["_distutils_hack"] = ["setuptools"]`), so it is pinned by setuptools' version.
    - If the freeze trace finds a distribution that is not in this list, that is "a file not in the list" under rule (b): NO freeze until a new plan version lists it.
  - Limit (stated, not fixed): a process started through raw ctypes/Win32 calls raises no Python audit event. No load-listed module does this (static scan, rule e).
- (e) **The scipy `cmd /c ver` spawn (Eve call).** Importing s57's chain imports scipy, which runs `numpy.testing` -> `platform.machine()` -> `platform._syscmd_ver` -> `cmd.exe /c ver` once (IV-REVIEW v3, spawn_who.txt). Rule: **the script calls `platform.uname()` before it installs the hook, with NO allow-list.** That call caches the result, so the later `platform.machine()` call spawns nothing. If any spawn happens after the hook is in, including this one, the run is VOID.
- (f) **Forbidden helpers (Eve call; IV v3 must-fix 1).** Plan code must never call any of these, or any function that calls them. I found them by a static ast scan (read-only, 2026-10-19 ~00:45 PDT) of all 48 load-listed .py files, looking for subprocess.*, os.system/popen/spawn*/exec*/startfile/fork/posix_spawn calls:

| File:line | Helper | What it spawns |
|---|---|---|
| s57_local_memory_model.py:159 | `clock()` | `subprocess.run(["date"])` |
| s67_constrained_assembly_loqo.py:155 | `clock()` | same |
| s69_prefix_stream_memory.py:169 | `clock()` | same |
| s55_code_vs_generator.py:150 | `clock()` | same |
| s87_core_layer_genre.py:195 | `clock()` | same |
| s80_a14_size_matched.py:176 | `clock()` | same |
| s34_morphology_syntax_geography.py:95 | `clock()` | same |
| s76_segmenter_independence.py:180 | `clock()` | same |
| s56_core_repetition_lag.py:95 | `clock()` | same |
| p4d1_core_order.py:244 | inside `main()` | `subprocess.run(["date"])` |
| tools/vkb/common.py:22 | `now()` | `subprocess.check_output(["date", ...])` |
| tools/findings_graph.py:187 | `stamp()` | `subprocess.check_output(["date", ...])` |
| tools/vkb/evidence.py:512, 514, 516 | `stub_check()` | `subprocess.Popen` (grep, tr, sha256sum) |

  - **Import-time blocker: NONE.** No load-listed module calls one of these helpers, or any spawn, at import time: module level, class bodies, and outside `if __name__ == "__main__"`. They are reached only through functions the plan does not call.
  - The plan's code takes clock time from `vx01_common.utc_now()` only (no spawn).
  - The worker-pool functions IV listed (s67 `main`, s71 `main`, s81 `main`, s91 `run_pool`, s80 `run_all`, r13 `match_test`, r10 `fold_test`) are also never called (single-process rule, section 9). A call to them would trip rule (d).
**Added in v2 (IV v1 item 2): two IVTFF sources read by `S71.load_translit_meta` -> `S69.voynich_pages` (s71:985; s69:283-290; used for the WTG meta, s101:654). ZL3b's source, `data/ZL3b-n.txt`, is already listed.**
| # | SHA256 | Data file | Used for |
|---|---|---|---|
| D | eb857a1f353b18983fbc25b954e1bbce227a26d99cefabfda9206ff9b57644d2 | `data/external/voynich-nu-ivtff/RF1b-er.txt` | IVTFF source of RF1b sidecar (page meta, gaps, para) |
| D | 7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5 | `data/external/voynich-nu-ivtff/IT2a-n.txt` | IVTFF source of IT2a sidecar (page meta, gaps, para) |
| C | 5629800d5e0dd27d69a426b269a47c648c10b0e635cf136c804d3754965c6fe4 | `vx01_bf_pathmap.py` (new, written 2026-10-19 00:18 PDT; NOT frozen; section 8a) | r13 spec-load remap |
Hashes of the two IVTFF files are the IV's (IV-REVIEW-X01-B-FALLBACK-v1, "Missing file" table). I did not re-hash them in this round; the freeze trace (rule b) checks them. Totals: 47 + 1 code files, 63 + 2 data files. IV re-hashed the two IVTFF files on Skynet: both match (IV-REVIEW v2, point 2).

### 8a. `vx01_bf_pathmap.py` (written in v3; Eve call 1; IV v1 item 1, v2 item 1)
- File: voynich root `vx01_bf_pathmap.py`, SHA256 5629800d5e0dd27d69a426b269a47c648c10b0e635cf136c804d3754965c6fe4 (copy for IV: box /workspace/team/voynich/vx01_bf_pathmap.py). NOT frozen. It freezes with the B0/B1 stubs, after IV checks it.
- API: `r13 = vx01_bf_pathmap.load_r13(log, expected=None)`. `log` is the calling script's chained-log function: one dict per remap, appended to that script's dev or gate log. `expected` = {relative target path: SHA256} from the caller's stub.
- What it does: for ONE spec import of `runs/roach-r13/r13.py`, it wraps `importlib.util.spec_from_file_location`. The wrapper remaps exactly two normalised absolute paths (constant `REMAP`) and passes every other call through unchanged. Afterwards it restores the original in a `finally`.
  - `<root>\runs\r10\r10.py` -> `<root>\runs\roach-r10\r10.py` (asked for by r13.py:66-68)
  - `<root>\runs\r7\r7.py` -> `<root>\runs\roach-r7\r7.py` (asked for by r10.py:61-63)
- Stops (RuntimeError):
  - the source path exists, or the target is missing;
  - a target hash differs from `expected`;
  - not exactly 2 remaps happened.
- Each remap logs `event=PATHMAP, module, src, dst, dst_sha256`.
- It edits, copies or creates no file. It opens files only to hash them, and writes only through the caller's log.
- `r10.R7PATH` and r13's `R10PATH` keep the unremapped strings. They are read only by r13/r10 `main()` (r13.py:260; r10.py:282-301), which this plan never calls.
- **Single process only.** The r13 module is not in `sys.modules`, so it cannot be pickled to workers (IV v2 item 2). Under section 9, no worker is ever started.
- **Smoke test (dev, done 2026-10-19 00:18:20 PDT; UNVERIFIED).** On Skynet, in the voynich root, I ran `python -B vx01_bf_pathmap.py --smoke`, one process, set to BelowNormal right after start; exit 0; under 1 s.
  - The smoke mode only imports r13 through `load_r13` and reads the grid constants QGRID, EGRID and RGRID plus the module file paths. It calls no r13 function: no Fit, no generation, no scoring, no producer.
  - Result: two PATHMAP records, r10 -> runs/roach-r10/r10.py (ada3231f...) and r7 -> runs/roach-r7/r7.py (0d5e65db...). r13 = d3c91e27.... The function was restored. `runs\r10` and `runs\r7` still do not exist afterwards.
  - Log: `vx01_bf_pathmap_dev_runs.log`, 4 chained records (SMOKE-START, PATHMAP x2, SMOKE-END). Chain head (SHA256 of the last line) 2ab8f2b5fea1ff63dbe745e49e567a9b2cc0688879af5f704835ed58ee76b409; file SHA256 3ec6d6b3e3d0f268fef190e897f3769e9ec16b8f49f58f7ca8444c6b1ff43fd9.

The s110 chain: NOT loaded. This plan does not import s113 or s110. If a later version needs them, they are added then.

| # | SHA256 (2026-10-18 ~23:55 PDT bytes) | File | Reached via |
|---|---|---|---|
| C1 | 598472b8b6e2e08186241a0e44e23860d933e4c0c8e42653c5222a9335b2b299 | `m3_bakeoff_reconcile.py` | root/spec |
| C2 | 2f2b3d4af32a054a63f4c90492e56dd0e2e76d7157de1317a0d62aeb40223518 | `corpora.py` | m3_bakeoff_reconcile.py:41 |
| C3 | 0e317c9a762e77c2f9002a1b95af367911a6714a7585803ab8715178a95a91c1 | `vparse.py` | corpora.py:6 |
| C4 | 4b9a400be433c2429864c638e823c742d6a54899e36597c0e6a2269eaf24c06f | `scoreboard/__init__.py` | m3_bakeoff_reconcile.py:42 |
| C5 | a59c9c17f8abe4cc8e29347854b02304eaa6a13c90b32f1890c1b1a60e7b23ed | `scoreboard/metrics_new.py` | m3_bakeoff_reconcile.py:42 |
| C6 | 0a1f266fa7798448eb3791ba61752d9ab7aa8b3b52092d8e9dc9184a46493017 | `tools/vkb/features.py` | root/spec |
| C7 | 0d47dd5579cdd397f87f744f1ca422919fa6c170457c51355b9cd3449800d56b | `tools/vkb/common.py` | tools/vkb/features.py:17 |
| C8 | b70b99f3efa52931d7400cb72d5230b7b7394660276adf809cfb2c309fdb791d | `tools/vkb/evidence.py` | tools/vkb/features.py:208 |
| C9 | afbed346288544232eaf31d97d954e383e27632dcdb8e81428513f8e2509e925 | `tools/findings_graph.py` | tools/vkb/evidence.py:264 |
| C10 | cd4e5960f6e4058fd75f63478be58acf3b27ac54c6168a818c2d19a89325360a | `vx01_common.py` | root/spec |
| C11 | 4adc4796938b68f97d69e9d0b3b35fba6cb40ae68576538445352dfeb6063155 | `s57_local_memory_model.py` | root/spec |
| C12 | 426b7b649361a8776a2152b95ddde4380d23af73f2e5096ed70891abee7937b3 | `a2_position.py` | s57_local_memory_model.py:120 |
| C13 | 4f955d34794293725c0063020ff00b1c5ed401aa38ee361cd2e4b345eca57ba7 | `g1_edge_joint.py` | s57_local_memory_model.py:121 |
| C14 | a40137f5ea2b8ef54d8829cf4bdecefa43f393cb53d0e7a526afe8010489afc1 | `n1_habit_table.py` | s57_local_memory_model.py:123 |
| C15 | 0b20e37ec2254d277a7ed8e1bf73e03c9fbfd15f92c4289496dd0ee07392f3b2 | `a1_profile.py` | n1_habit_table.py:67 |
| C16 | f21281d9fe41d309823117ab2517af5fddae6aead7ae84b5fec6114ea7c78c0a | `c2_section_generator.py` | n1_habit_table.py:68 |
| C17 | 5fcdfdeb5e819ad33bbb1641cf2c5ce850b61b7fb9c85ec4bc21933caaf69d5a | `b4_selfcite_sim.py` | c2_section_generator.py:35 |
| C18 | 0f1722dea55b3cceda5e6f622e6cedc99c779506b160862ad2c41e5168d41007 | `b5_nmf_topics.py` | c2_section_generator.py:36 |
| C19 | 30b6ba47c9de4a36379ea0fea92a39a10da5ec6da4f4488266d4b3f68a827ffb | `c3_edge_coupling.py` | n1_habit_table.py:69 |
| C20 | 5bd3e11f07c7231d37efbedb644aa0d5644a4678b33ca030065fa9241c26ab76 | `f1_residual_order.py` | n1_habit_table.py:70 |
| C21 | 46b5e002aee66f6ee95f43c8f4edccffb68629e3a526416333eb8e552465260b | `c4_naibbe_lines.py` | f1_residual_order.py:49 |
| C22 | e0ac0ac62d6de16da094501a3fff26afd0551de681421ba66e6b8383d121e0ca | `f3_flow_choice.py` | n1_habit_table.py:71 |
| C23 | 440ff45dee9087abe9a6aa77976bbe46b369790cb113416bf5779658f49008bd | `f2_syllable_control.py` | f3_flow_choice.py:38 |
| C24 | 634e2534941bc1fc0b0942f2e6b331049835d8c61a4be8efe43e358ef6f5c0e3 | `s58_two_layer_heldout.py` | root/spec |
| C25 | 059a218127de9fbbde080dc78c658e6b31dec3ecae33be7c5b8b511b81266622 | `s61_joint_word_producer.py` | root/spec |
| C26 | 8e5299212a84ec552ec00d34aaa9871333e65e98c2bacc7ae45ebf12cc8cc354 | `s67_constrained_assembly_loqo.py` | root/spec |
| C27 | 9b4f024792c778ae300fd14d7d1e85f03243d50964b1f7f61ba09f1553c11a18 | `s71_weakened_grille_and_sticky_naibbe_loqo.py` | root/spec |
| C28 | 56485b42c5c928c908a04be1a9b888a06c85088bc0b49589ef340d69ca220cec | `s55_code_vs_generator.py` | s71_weakened_grille_and_sticky_naibbe_loqo.py:87 |
| C29 | 6af7dbf59486209a8f5d0fac79850a9130a6d56797662e89a9e2a90111e30fe3 | `s64_naibbe_taxonomy.py` | s71_weakened_grille_and_sticky_naibbe_loqo.py:89 |
| C30 | 11e722d4a0391d34228637da8b9c1872a6dc4ddd5dc1f2ff4e94f8c6a903c458 | `s69_prefix_stream_memory.py` | s71_weakened_grille_and_sticky_naibbe_loqo.py:91 |
| C31 | 418515ad0ecd7544fb4bba2fb0efcce1ecdbe198809c6bf830cbf31b57cd5063 | `s81_sticky_table_loqo.py` | root/spec |
| C32 | 92dba656c9d74dfb972837d3bba070bb945c3ed59ef444448d5bd7aafcdee21a | `s91_line_pool_producer_loqo.py` | root/spec |
| C33 | d5ed585681670bc9e9eaf76449b7497a43bb33d6d4e689b0f0c337387f49d8db | `s87_core_layer_genre.py` | s91_line_pool_producer_loqo.py:140 |
| C34 | 196cf61f3ca5af440e03fa5e1550d1ac7ee25ad32b35de3ec61d1965d6485a5b | `s80_a14_size_matched.py` | s87_core_layer_genre.py:146 |
| C35 | 5a400968081214ba5f38bbe29bdabe42ddcfe6f949f491e5f579ce3f0e8b7a39 | `p4d1_core_order.py` | s80_a14_size_matched.py:131 |
| C36 | 406b6d9fd5cfafc8830dec85ddb05cf6743a49024220bbc7429c9d303aba8625 | `s34_morphology_syntax_geography.py` | p4d1_core_order.py:98 |
| C37 | 9f0bb9a84f8b104804ced4743ae0a85d29b4428ad7982474f56b1090fb1d3f57 | `c1_quire_null.py` | s34_morphology_syntax_geography.py:60 |
| C38 | 3aba99a6cdd124a50d6dba5636fb5c37e1bbec25a5568600ca07b9bfcd342dea | `p1_bifolio_null.py` | s34_morphology_syntax_geography.py:61 |
| C39 | 0ddc1eaafd22eb852b46f0fe2023b6cefaae3c3cbc9d59c47efc57a74e01626b | `m1_coordinates.py` | p1_bifolio_null.py:81 |
| C40 | 8b4d2fdb08aa01f4b3402386b3ff1ccbc2041f662e10e8a440cae5d784874a65 | `tools/boxes.py` | m1_coordinates.py:29 |
| C41 | 5676bd92ae940c63c7a55ba468558fb9119692bd6fe144fb9e56e07a2b730c02 | `s29_q1_label_controls.py` | s34_morphology_syntax_geography.py:62 |
| C42 | 43f7aab7ad8c2bfa12e9d020f4749eb11281d51d7262c898cb499452c0184a29 | `s76_segmenter_independence.py` | s80_a14_size_matched.py:133 |
| C43 | 1e5987dfee74c819b1f1c11abe0d386ce19f1ca730c39a30d45d4a534391b6a7 | `s56_core_repetition_lag.py` | s76_segmenter_independence.py:131 |
| C44 | d3c91e27791781b3d047ca56a926ae6862a0b9b3c37fd38cc89b1bc0215b3d94 | `runs/roach-r13/r13.py` | root/spec |
| C45 | ada3231f0b6b0992767c7bd98fb206a4b1f138dcdb11d190cfc521ddaff4f69b | `runs/roach-r10/r10.py` | root/spec |
| C46 | 0d5e65db45b3c410bfbcab5b56d45adaab09b09c9af007b3546538a5b9f69b96 | `runs/roach-r7/r7.py` | root/spec |
| C47 | 3a7b7c3efea13b884362f9f7f07551835bab8ca158ecdb43b946c96a8b3fbf1d | `scoreboard/score.py` | root/spec |

| # | SHA256 | Data file | Used for |
|---|---|---|---|
| D | ce233477803a865365e53418f5e2b78c324fa0ea124b0aa46a9eb6a5189f7ef0 | `data/translit/ZL3b_eva.meta.json` | real text T=ZL3b (S67.load_pages, s67:193-202) |
| D | c7d9bccba99b2610b9d80b4ce5f26f7d1ab54c12ec2364d0423d6b89f51da9df | `data/translit/RF1b.meta.json` | real text T=RF1b |
| D | 0d0d3e758d1e308b0aee4b4d006f90cbc8090c081e0fcb3327de6734ac5e5fdf | `data/translit/IT2a.meta.json` | real text T=IT2a |
| D | 890835df665d33b96228d4a587030fee2bc1637783dc627b4e6aa584186cadcd | `data/naibbe_zenodo_17219445/Naibbe_Cipher.xlsx` | Naibbe key tables (S81.key_tables -> S64.load_greshko, s81:205-208, s64:98,152-153) |
| D | 2f63d4beabdbc1b84821a74ce462eb3dcc80d43117ec33db6a5f8eb5aa7da3fc | `runs/s49/lang_latin_cremma.meta.json` | Latin plaintext letters_lat (S81.plain_letters, s81:211-215; s64:99) |
| D | f329b589b20090096ff97df8fa61cda0eb826a7aec9d7b04a7fc3798024d96d6 | `runs/s57/fit_ZL3b.json` | planting params s57 (s101:291-293) |
| D | 2291e6669f97965dc16cd8109f916e9f08f9abd3b58b4e81e54a30086484f096 | `runs/s57/fit_RF1b.json` | planting params s57 (s101:291-293) |
| D | 2187b06b94db4e5b8f79c8575adfba7f7aea1408c0e05f831ad4035c22a221bb | `runs/s57/fit_IT2a.json` | planting params s57 (s101:291-293) |
| D | 90c32cda1b0f932ac600d655a0360d5632e45ad6df9aeb282899685c86de4ff8 | `runs/s58/fit_ZL3b.json` | planting params s58 (s101:291-293) |
| D | 43e4e0e41bd359594b0756b6614ae8a607e6219c17589476ad095d75b020903b | `runs/s58/fit_RF1b.json` | planting params s58 (s101:291-293) |
| D | 0eadf610f64a5481d8cae184f83d30abd9010ab6591ab570568aaed481353a95 | `runs/s58/fit_IT2a.json` | planting params s58 (s101:291-293) |
| D | c2a194731811c7f4a1bfaffa3fe7c8f4483fc6164028a1068f0a7dc792bb85c1 | `runs/s61/fit_ZL3b.json` | planting params s61 (s101:291-293) |
| D | 945eb987cdc8720795a357df9a4f7770447d2223d611b3a136e418306b15d7b8 | `runs/s61/fit_RF1b.json` | planting params s61 (s101:291-293) |
| D | 5312811de64e508de6929522b6adc4dadb23a70477dda33b53b7f2ec1de0e6e4 | `runs/s61/fit_IT2a.json` | planting params s61 (s101:291-293) |
| D | 607fa9d91d5f3b359324f1cb42ae45b6a360684fc273b2f6bd58fcd57856d8b8 | `runs/s67/cells.json` | planting params s67 CA (s101:287,295-296) |
| D | 297f598ed396d3c0ce511c185dec5e010fae8fe86cac6704d396fc1f01f23b1d | `runs/s81/cells.json` | planting param s81 p (s101:288,298-303) |
| D | bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc | `data/ZL3b-n.txt` | vparse default path (vparse.py:10); listed in case it is read |
| D | bd9961f3510c7f4ae50f45a693ff73b143447f89fdc1c10d7ed95cfb1068a3dd | `vx01_gate_seeds.json` | gate seed list (hash in stub key line) |
| D | 002a50c97cab5a0050d675876d12f367f494fb5d8b84aa08772aafc2313ed3a2 | `runs/s91/folds/IT2a_A.json` | planting params LP91 (median over folds, s101:304-309) |
| D | eb4b9ec51415456e4ae47163146f9d5f88451ffb2840f1cd687a27a366ff8100 | `runs/s91/folds/IT2a_B.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 4b0980611ebf8962c1c3a7c9481415c7309e6e0e3f69bc0d4b1ae4bc6f84496f | `runs/s91/folds/IT2a_C.json` | planting params LP91 (median over folds, s101:304-309) |
| D | eeef211231d9535070999ce21582b8d648ea0bd312fd3375516ddc4cb3372e00 | `runs/s91/folds/IT2a_D.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 94f17130822ec0c5063ed78506303dbf742068483ad9188478e5cc594fb21a4a | `runs/s91/folds/IT2a_E.json` | planting params LP91 (median over folds, s101:304-309) |
| D | fcf488a1d87b0dd9861fc31ab46f09700b522fe24ec81597a2ddb38358d508d2 | `runs/s91/folds/IT2a_F.json` | planting params LP91 (median over folds, s101:304-309) |
| D | c82d71a85a0256558508a2f590b818ec5c52d8226fe105b974e29585eec00459 | `runs/s91/folds/IT2a_G.json` | planting params LP91 (median over folds, s101:304-309) |
| D | ca208092b278fb448a11b327ca95ee3dcc98d4f3d35554e3ce95b367a5e1e392 | `runs/s91/folds/IT2a_H.json` | planting params LP91 (median over folds, s101:304-309) |
| D | ce773d52dbcbd86f871ac9c98b64d38a60cfb6ec04bd93452eb5773a4005b95f | `runs/s91/folds/IT2a_I.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 890db08e956b9e1173ac954b82af779f7408fc85d41275058b17933937e36519 | `runs/s91/folds/IT2a_M.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 3dfebe76f50fe1f6d12878fca64dd13d76c32fbd028d4a07ee98c5a1f36d777f | `runs/s91/folds/IT2a_N.json` | planting params LP91 (median over folds, s101:304-309) |
| D | eeec4faa6b649638842a29b7dd6999581676922ec7ef51c70945412a589757ac | `runs/s91/folds/IT2a_O.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 4af7b6b9027d20ae66736a2a18bbde070fdf292efc7578998fc16b07ce246aac | `runs/s91/folds/IT2a_Q.json` | planting params LP91 (median over folds, s101:304-309) |
| D | dacda0b5bfc9236dbd65dc435c8799746a3daeb5c869f5dd1dac3c2e27d4335c | `runs/s91/folds/IT2a_S.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 1f4a4b89d2d75b372bdec20b9a556f0ff4cc138e5092f5e2c2d787bf7ba9a0b0 | `runs/s91/folds/IT2a_T.json` | planting params LP91 (median over folds, s101:304-309) |
| D | fa0f366e99d067cb507a3129061a5062518017cd483205bc969c67bb7242bbab | `runs/s91/folds/RF1b_A.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 18273cc47515e1132cc6842f47c10a5fbe344da05cd1be56b932628defbca137 | `runs/s91/folds/RF1b_B.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 52510de8620bb777819cb62a2a9a3fac55defdb383e1fcfc198c99ffcd624059 | `runs/s91/folds/RF1b_C.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 532932473a7074dda7be186cac69dac4223149b174c11dff4944c8c9310be34b | `runs/s91/folds/RF1b_D.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 60bd9f399531fb7e625a4e902d8e295fe7285d3a59a0e947f2b1db24d6e2fadd | `runs/s91/folds/RF1b_E.json` | planting params LP91 (median over folds, s101:304-309) |
| D | b02ee6c15fb07acbb6a3df1884f9555c43d2978f87ed3160414c575402bcf347 | `runs/s91/folds/RF1b_F.json` | planting params LP91 (median over folds, s101:304-309) |
| D | ff728e2c0a4d4980e855d0d5f45afbd5a907dc865eaab6933ed6f66cd6884a44 | `runs/s91/folds/RF1b_G.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 51cfe4a6b6f1df6bd6b51a32907022b8f0d9e365b27b8c29611921d8713c4bbb | `runs/s91/folds/RF1b_H.json` | planting params LP91 (median over folds, s101:304-309) |
| D | f0f0f70a4caa4cb322d8c7e6baaab95ec9dd839fd17162bf8793867bafb8066f | `runs/s91/folds/RF1b_I.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 0820fdcedf534ea9f36557bbbdee55f7c4dae582bcb50977c34ae9a284f16491 | `runs/s91/folds/RF1b_M.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 72662746548d7e9049542459e813f5e46e585f5b30d6af1d5ab7a93972c30efc | `runs/s91/folds/RF1b_N.json` | planting params LP91 (median over folds, s101:304-309) |
| D | e482fb1cd0e34bdd1ffa4c7f78af87912a8c7d41dfdd7838198335a9f7c4edac | `runs/s91/folds/RF1b_O.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 5d16372dcf05adad831267297e891d2dd0baef6de112797347f58f9d2b264c81 | `runs/s91/folds/RF1b_Q.json` | planting params LP91 (median over folds, s101:304-309) |
| D | a22c43627db8c028105a8423d85cae43b3808387d97e91f851f21e35de58e496 | `runs/s91/folds/RF1b_S.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 7420f0f53a04bde38f550dba8fa39d30f94b43758ffccdf497bee450e97f769a | `runs/s91/folds/RF1b_T.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 7d1d88baf53eec15233b971e60828387baef06aaf6e73806562e56a42ea1ccc0 | `runs/s91/folds/ZL3b_A.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 49e2a666cb2e534e74091e875b070c04bb9e661cf91312e8a6a4699687ac60b3 | `runs/s91/folds/ZL3b_B.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 35c9b382246c45f44c8c4adf86c3515831690407af0b79201331b2790ab31499 | `runs/s91/folds/ZL3b_C.json` | planting params LP91 (median over folds, s101:304-309) |
| D | bcedd6986d5844b226306b80c5eb9b4079ff42b4a67b9f103363086393f66a4b | `runs/s91/folds/ZL3b_D.json` | planting params LP91 (median over folds, s101:304-309) |
| D | b5e8fccb08cef267b893d3a7baeb0380e843212c80cc07133acedd13e2df0c96 | `runs/s91/folds/ZL3b_E.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 65dbf71bbf9e81f3b976e2fd53b9be902c58dd2f05bfe30b935e1abc90583f65 | `runs/s91/folds/ZL3b_F.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 911146dc81f836ad1532528a9ae6690d9ecd6eadec1b3074ecf20a7b74aa2bf6 | `runs/s91/folds/ZL3b_G.json` | planting params LP91 (median over folds, s101:304-309) |
| D | cd5d0f1a2ec8a12bd6ac660a77734d6b09953500e34c6972d0170352cf6beada | `runs/s91/folds/ZL3b_H.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 4e94bf414ade34c0df22976687fcf577305aa3504812047af7cb68220fe63f6c | `runs/s91/folds/ZL3b_I.json` | planting params LP91 (median over folds, s101:304-309) |
| D | f6dcdd58f02600d78546d0aec73a032a2eed405e8b12f2b365a6712149629cfd | `runs/s91/folds/ZL3b_M.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 11e4a84d3d14f9efa655dc4c9a51a64904126c7002d3ea5ef07a0b9b5b8e3862 | `runs/s91/folds/ZL3b_N.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 9f71834af67c53df98dfc23b75c4a5654e1ed7b6a2d02c2420b797dd2aca4f16 | `runs/s91/folds/ZL3b_O.json` | planting params LP91 (median over folds, s101:304-309) |
| D | a024bd5a6bb07f432f1c5a761dd41e412d0e0742c2d90ec64504043012a9324b | `runs/s91/folds/ZL3b_Q.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 0f3139a0e0a122c6dbf34e5c73050060fdd8940653900fa46efca3d464b2d82c | `runs/s91/folds/ZL3b_S.json` | planting params LP91 (median over folds, s101:304-309) |
| D | 15524a438cb85e6d46e4cacae58f77ecdbc164f9f92fa1cab7662f8bb36f3975 | `runs/s91/folds/ZL3b_T.json` | planting params LP91 (median over folds, s101:304-309) |

## 9. Scripts (none written or frozen; order; v5.1:160 and :174 names)
| # | Script | Modes | Stub holds |
|---|---|---|---|
| 6b | `vx01_bf_rk_c2.py` | single run (real text only) | script + all loaded files (trace) + sidecars; output table hash goes to the B0 stub |
| 7 | `vx01_b0_fitter_recovery_c2.py` | `--build-params` (no seed) -> `--calibrate-mei` (dev) -> `--oracle` (dev) -> `--dev` (dev) -> `--gate` | script SHA256 TBD; all loaded files (trace); vx01_bf_rk output hash; `vx01_bf_plant_params.json` hash; `vx01_b0_mei_map.json` hash; oracle-result hash; dev-log chain head; gate_seeds_sha256; this file's and v5.1's hashes; the decision rules of sections 2, 4, 5 and 7 copied in |
| 8 | `vx01_b1_exclusions_rerun.py` | `--dev` (dev, on planted books only) -> `--gate` (real text) | script SHA256 TBD; B0 stub hash; B0 gate result hash; all loaded files; B1 table copied in |
No `vx01_b2_*` in this version. No `vx01_bf_common.py`. The script table numbers are v5.1:174-177.
**Compute rule.** IV v1 ruling 6, four conditions, copied word for word:
"(i) The estimate is a written formula from the `--dev` wall times, e.g. 2 x Σ over producers of (dev seconds per cell x 9), and its value goes into the B0-F stub before `--gate`. (ii) The cap is checked only between producers, in the fixed order F-34 C1, F-41 C2, F-23, F-30. A stop leaves the producers already done standing; the rest are "not run, no call". (iii) A cap stop writes a final gate-log line that counts as GATE-COMPLETE, so the same script can't be rerun to finish with a bigger cap; a bigger cap needs a new script version and IV OK. (iv) ≤2 BelowNormal workers, the free-RAM check as in v5.1 rule 8, and other jobs are never touched."
**Single process (Eve call, 2026-10-19; IV v2 item 2, option (a)).** r13 and EVERY step of `--gate` (B0 and B1) run in ONE process with NO spawned workers. So the audit hook (section 8 rule c) and the pathmap stay in force for every file read. All dev modes run single-process too, so the dev timing is the gate timing. This replaces "<=2 BelowNormal workers" in IV condition (iv) with "1 BelowNormal process", which is stricter. The rest of (iv) (the free-RAM check, never touch other jobs) holds as written.
Eve's compute rule: estimate hours from SINGLE-PROCESS dev timing, cap at 2x that estimate, run at BelowNormal, stop if over the cap, never kill other jobs. Where Eve's rule and IV's wording differ, IV's wording rules.
**How the timing is measured (none exists yet).**
- After the oracle fixture passes and before the B0-F stub is written: `vx01_b0_fitter_recovery_c2.py --dev`, single process, BelowNormal, DEV seed 20261103 only.
- It runs one full cell (ZL3b; all 4 controls; 15 folds; fit + 200 copies) for each producer still in the run. Wall seconds per producer are logged in its dev log.
- Estimate E = Σ over producers of (dev seconds for that cell x 9). Cap = 2 x E. Both numbers go into the B0-F stub.
- `--gate` checks elapsed time against the cap only between producers (condition ii).
- B1 is timed the same way, by `vx01_b1_exclusions_rerun.py --dev` on planted books, before its stub.
- If the dev timing makes the cap impractical, that is reported to Eve before any stub. The cap is never changed after the stub.
Size, for scale only: up to 13 producers x 4 controls x 9 cells x 15 folds x (fit + 200 copies), all in one process. s101 took 7,811 s for one seed-set, with workers and without refit-per-fold envelopes, so expect many times that. A producer that fails its oracle fixture costs no gate compute.
WTG note: WTG's Power test only tests the rebuild (section 4), not parameter recovery.

## 10. Differences from v5.1 5b (complete list)
| # | 5b says | v1 does | Why / authority |
|---|---|---|---|
| a | B0, B1, B2 run (5b:155, :160) | B2 dropped | Its arms are segmented (Eve call 4; DEVIATION_1) |
| b | Power, wrong-family, MEI, nuisance controls | adds an oracle fixture gate (dev seeds) before any gate run | IV item 7; Eve call 7; stricter, so it can only remove calls |
| c | Producers built on Slot units: s57, s58, s61, s67, LP91 (5b:159) | adds WTG (Slot), r13 B (S1 units); s81 and r13 A carry no qualifier | Code facts (s101:714; r13.py:18-19); Eve call 2 |
| d | F-41 C1 and C2 touched (section 5) | F-41 C1 not run | 5b:156 forbids core scoring; Eve call 3 |
| e | TTR "at matched token count", mean word length (5b:157) | TTR_300 (50 subsamples); mean length in EVA chars | Definitions that 5b left open; Eve call 5 |
| f | r_k "on the real whole-word text" (5b:158) | r_k per quire (r_k,q) | Matches the band level; IV item 5e |
| g | loss, MEI map, shift form not written (v5.1:127, 133-134) | defined in sections 4, 5 and 7; CHARWIN not in the loss | IV item 6; Eve call 6; CHARWIN-out accepted (IV v1 ruling 1) |
| h | ">= 5/6 inside" (5b:157) | match iff >= 5 statistics are defined AND inside; fewer than 5 defined = NON-MATCH (UNDEFINED) | IV v1 ruling 2, accepted by Eve; same strictness as 5b, plus an undefined rule |
| i | an EXCLUDED call is possible for every producer | WTG and line_sticky75: no EXCLUDED call (no MEI control) | v5.1:134; IV v1 item 7; Eve call 7 |
| j | (not in 5b) | r13 loaded via `vx01_bf_pathmap.py`; `--gate` audit hook voids a run that reads an unlisted file | IV v1 items 1 and 3; Eve call 1 |
| k | (not in 5b) | compute cap rule (section 9); one process, no workers, for r13 and all gate steps | IV v1 ruling 6; IV v2 item 2; Eve |
Seeds and script names: as 5b:160 (no change), plus the helper module `vx01_bf_pathmap.py` (not a run script).

## 11. Changes from B-FALLBACK-v0
| IV item | Fix | v1 section |
|---|---|---|
| 1 Seeds/scripts differ from 5b; false "changes nothing" line | 3a B0 seeds only; 12 new seeds and vx01_bf_common.py dropped; v5.1 names; header line replaced by a true statement plus section 10 | header, 6, 9, 10 |
| 2 Wrong unit labels | per-producer labels; v0 error stated | 1 |
| 3 F-41 C1 scores Slot cores | F-41 C1 not run; only C2 | 1, 7, 9 |
| 4 B2 undefined | B2 dropped; deviation note | 1, 9, 10a; vx01_bf_DEVIATION_1_B2_dropped.md |
| 5a TTR matching | TTR_300, 50 subsamples, seed tag | 2 |
| 5b EVA vs glyph length | EVA chars, reason given | 2 |
| 5c CHARWIN | `M3.score_folds` called directly on raw words; train/test pages fixed; no S57.Measured | 2 |
| 5d no s113.book_stats | features.rw1/h1_h2/rhythm called directly; rhythm seed tag fixed | 2 |
| 5e level | all per quire; r_k per quire | 2, 3 |
| 6 Loss and shift | L defined; additive signed shift on the scored quire | 4, 7 |
| 7 Oracle control | oracle-power >= 10/15 and oracle-MEI <= 4/15 on 9 dev cells before any gate | 7 |
| 8 File hashes | 47 code + 63 data files listed with SHA256; run-time trace rule; s110 not loaded | 8 |
| 9 Planting-author leak | θ_plant by the written s101 rule from pre-existing frozen fits; params file, MEI map and fitter hashed in the B0-F stub before any gate book | 5, 9 |
Left for later (A3 is not running): the call-map fixes for F-15 / F-43 and the recheck against graph ecca41ab.

## 12. Rulings on v1 section 12 (closed)
- **Choices 1, 3, 4 and 5 are ACCEPTED by IV (v1 rulings).** Choice 2 was OVERRULED by IV, and IV's rule is accepted by Eve and written in section 2. Choice 6 is ACCEPTED with IV's 4 conditions (section 9).
  1. CHARWIN is not in the fit loss; it is scored in the band. ACCEPTED.
  2. Match rule: REPLACED by "match iff >= 5 statistics defined AND inside" (section 2). The ">10% of copies undefined -> not counted" and "undefined L term = 25" parts are kept.
  3. **s67 CA0's θ_plant = the median over the 15 folds of T of `runs/s67/cells.json` `params["CA0"]`, the same median rule as s101 uses for CA.** ACCEPTED. Its fitter is CA's stage A (section 4).
  4. **WTG "refit" = rebuild `WTGProducer` on the training pages and their page meta, with fixed WTG_PARAMS. No parameter is fitted.** ACCEPTED. Its Power test only tests the rebuild.
  5. MEI by one-parameter moves only. ACCEPTED. This can only remove EXCLUDED calls.
  6. Compute: ACCEPTED with conditions (section 9).
- No open choice remains in this version that I am aware of. IV checks it.

## 13b. Note
The v1 table "Changes from B-FALLBACK-v1" (section 13) is kept as history.

## 13. Changes from B-FALLBACK-v1
| IV v1 item | Fix | v2 section |
|---|---|---|
| 1 r13 path break | `vx01_bf_pathmap.py`: hashed, logged remap of 2 spec-load paths; no file edited; r13 A/B stay | 1, 8 (table), 8a, 10j |
| 2 two IVTFF files missing | RF1b-er.txt and IT2a-n.txt added with SHA256 | 8 |
| 3 trace not a hard stop | trace runs all modes, all producers and all 3 transliterations; unlisted file or hash change = no freeze until a new plan list and IV recheck; `--gate` audit hook voids the run; torch `_ops.py`/`_classes.py` filtered | 8 |
| 4 CA0 cite wrong | CA0 = use_class=True, gamma 0, stage A only; v1 error stated; CA-ind not in plan | 4, 5 |
| 5 oracle must reuse planting object | oracle and MEI books come from the planting producer object (same tables, seg_voy, r13 Fit/table/offsets); only the seed differs | 5, 7 |
| 6 WTG page meta | all texts inherit id, quire, hand, section and para from `S71.load_translit_meta`; WTG rebuilt on it; loader-agreement check | 4 |
| 7 MEI not codeable | grid and key order per producer (module KEYS for s61, s67, s91; fixed here for s57, s58, s81, r13); WTG and line_sticky75: no MEI, so no EXCLUDED call | 1, 5, 10i |
| 8 match rule loosens 5b | ">= 5 defined AND inside" | 2, 10h, 12 |
| 9 Qtr undefined | Qtr = 14 other fold quires; mean/SD over defined quires; undefined if < 10 of 14 | 4 |
| 10 compute rule | IV's 4 conditions word for word, plus Eve's rule (IV rules where they differ); written estimate formula; WTG note | 9 |
Left for later (A3 is not running): the call-map fixes for F-15 / F-43 and the recheck against graph ecca41ab.

## 14. Changes from B-FALLBACK-v2
| IV v2 item | Fix | v3 section |
|---|---|---|
| 1 pathmap file missing | `vx01_bf_pathmap.py` written (SHA256 5629800d...), NOT frozen; added to the load list; smoke test logged in its own dev log | 8 (table), 8a |
| 2 workers break r13, pathmap and audit hook | Eve: r13 and all `--gate` steps in one process, no workers (IV option a); dev modes too; compute rule and timing method updated | 8a, 9, 10k |
| 3 MEI tie rule when θ_plant is off its grid | θ_plant's value put into the sorted grid; steps counted in that list; the 3 off-grid cases named | 5 |
| 4 tie-break not total | last rule: an up/down tie takes the lower value | 5 |

## 15. Changes from B-FALLBACK-v3
| Item | Fix | v4 section |
|---|---|---|
| IV v3 must-fix 1 (a) | hook and freeze trace also watch the process-creation audit events (exact names cited); any one = GATE-VOID or no freeze; no allow-list; interpreter pinned to 3.11.9 | 8 rules (a), (d) |
| IV v3 must-fix 1 (b) / Eve | scipy `cmd /c ver`: call `platform.uname()` before the hook goes in; no allow-list | 8 rule (e) |
| IV v3 must-fix 1 (c) / Eve | every spawning helper in the 48 load-listed .py files listed with file:line and forbidden; no import-time blocker | 8 rule (f) |
| IV v3 note (d) | dev seed 20261103 added to the dev-reuse note | 7 (oracle note) |
Separate file: `vx01_bf_DISCLOSURE_1_incoming_slip.md` (the .incoming slip of 2026-10-19 00:18 PDT).

## 16. Changes from B-FALLBACK-v4
| Item | Fix | v5 section |
|---|---|---|
| IV v4 must-fix 1 | whole environment pinned in the stub (exe SHA256, full `python -VV`, all run-path distribution versions incl. torch 2.11.0.dev20260115+cu128, sitecustomize.py SHA256); `--gate` refuses on any mismatch. Nothing else changed: the title and header lines above are left as in v4 on purpose, so the v4->v5 diff touches only this; this file is v5 by its name and this row. | 8 rule (d), "Environment pin" |


## 17. Changes from B-FALLBACK-v5
Base: B-FALLBACK sha256 4ed0314a7c8aef4d925dee4fbab3ef8eca3a005352062563e3708a0273e63f3e. Authority: IV-REVIEW-X01-B0F-CODE-1 (sha256 d5a8d86ad73b5b4ca69061c6345ac505a440899f67f44fd363e5f365da7dba13) and Eve's ruling of 2026-10-19.
| Item | Fix | v6 section |
|---|---|---|
| IV code-1 must-fix 3 | setuptools 65.5.0 added to the environment pin (`_distutils_hack` maps to setuptools) | 8 rule (d), "Environment pin" |
| Eve ruling | script names changed mechanically to the code-2 files `vx01_bf_rk_c2.py` and `vx01_b0_fitter_recovery_c2.py` in the 10 places that named the scripts (the bare "vx01_b0" in sections 4 and 5 included); the code-1 files stay as the record of what IV reviewed | 3, 4, 5, 8 (a), 9 |
Nothing else changed. The title and header lines are left as they were on purpose; this file is v6 by its name and this section.
