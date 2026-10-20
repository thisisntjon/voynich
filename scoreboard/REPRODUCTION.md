# Reproduction record for scoreboard/score.py v2

Stamped 2026-10-17 16:25 PDT (system clock). Environment: Python 3.11.9,
numpy 2.4.6, scipy 1.17.0, scikit-learn 1.8.0. Test run:
`python -m unittest tests.test_score -v` -> 18 tests, all OK (26-33 s).

Checked against: results_a1.txt, results_a2.txt, results_a4b.txt,
results_a7.txt, results_b1.txt (T2), results_b3.txt (C3, C4),
results_b4.txt (VOYNICH and CTRL_dante rows), results_b5.txt (VOYNICH ZL3b
block, CTRL italian_dante and latin_augustine rows).

## Bit-exact (to the printed precision)

| file | rows | numbers checked |
|---|---|---|
| results_a1 | VMS eva, VMS glyph, VMS glyph+, latin_caesar, italian_dante | 12 + 6 + 6 + 12 + 12 |
| results_a2 | VMS (3 features), italian_dante (3 features), 20 enrichment ratios, page gallows (raw corpus) | 36 + 20 + 4 |
| results_a4b | VMS matched W=10, W=40; latin_caesar, italian_dante W=10 | 18 + 6 |
| results_a7 | VMS eva, VMS glyph+, latin_caesar, italian_dante | 16 |
| results_b1 T2 | all counts and rates | 3 + 8 |
| results_b3 C3 | voynich_eva, latin_caesar, italian_dante | 3 x 7 |
| results_b3 C4 | voynich_eva | 5 |
| results_b4 | VOYNICH row; CTRL_dante row | 10 + 8 |
| results_b5 | VOYNICH ZL3b: illus/hand/lang + within hand 1, 2; CTRL rows NMI and rotation null | 30 + 8 |

## Discrepancies and tolerances (none fudged)

1. **a2 page-first gallows share.** a2_position.py computed this block on
   `vparse.paragraph_text(vparse.load())`, i.e. with words containing `?`
   kept, while every other a/b metric (and the Corpus) drops them. On the
   standard corpus the scorer gives 85.02 % / 18.58 % (gallows) and
   47.34 % / 7.93 % (p/f) versus the filed 85.99 % / 18.61 % and
   48.31 % / 7.93 %. The test reproduces the filed values exactly on
   `Corpus.from_voynich(drop_unclear=False)` and checks the standard corpus
   to +-1.5 pp. Diagnosis (counted): 15 of 207 page-first lines begin
   with a `?`-word in the raw records (e.g. f8v `c?hod`, f36r `pcha?dan`);
   dropping that word makes the next word line-initial, and the net
   gallows count moves from 178/207 (85.99 %) to 176/207 (85.02 %) because
   the swaps gain and lose gallows status in both directions. The raw
   corpus reproduces the filed values exactly.

2. **b3 C4 shuffle deltas for controls.** b3_slot_claims.py used one
   `random.Random(7)` for every corpus in sequence (voynich_eva first),
   so only the Voynich row can be bit-exact when each corpus is scored on
   its own. Scorer vs filed: latin_caesar char-shuffle delta +0.633 vs
   +0.633; italian_dante +0.636 vs +0.635 (char-shuffled h2 3.744 vs
   3.742). Tolerance +-0.01. The word-shuffle delta is 0.000 either way
   (h2 with a space symbol is invariant to word order).

3. **b5 permutation null for the CTRL rows.** b5_nmf_topics.py shared one
   `np.random.default_rng(0)` across all six Voynich-layout blocks before
   the controls, so the 200 permutations differ. Scorer vs filed:
   italian_dante perm mean 0.002 / p99 0.004 vs 0.002 / 0.004;
   latin_augustine 0.015 / 0.022 vs 0.015 / 0.020. Tolerance +-0.005.
   Observed NMI and the deterministic rotation null match exactly
   (0.017, 0.011, 0.017, p 0.022; 0.155, 0.181, 0.273, p 0.575).

4. **b4 CTRL_dante.** b4 ran `report(lines=verse_lines)` on all verse
   lines with the 20-draw null; that is `position_all` with
   `null20_*`, not `position_body` (which drops the first line of each
   30-line pseudo-page). Matched exactly through `position_all`.
   `position_body` on the same corpus gives JSDfirst 0.0340 (not tested).

5. **a4b control rows** were produced by a4_selfcite.measure (unmatched,
   N=12000, far window >=2000 away), not by the matched a4b sampler; the
   scorer reports both (`near_copy.unmatched_*` reproduces the control
   rows; `near_copy.matched_*` reproduces the VMS rows). On a corpus
   without metadata the matched sampler runs on one group.

6. **Within-hand NMF selection.** b5 hard-coded hand 1 -> {H,P}, hand 2 ->
   {B,H,T}. The scorer selects sections with >=30 chunks within each hand
   and needs >=2 of them; on ZL3b this yields the same sets (hand 1: T has
   5 chunks, excluded; hand 2: C has 11, excluded; hands 3/4/5/? have one
   or no qualifying section) and the same k (4, 5). Any other corpus with
   hand labels is treated by the same rule.

## Frozen v1 scorer

`scoreboard/score.py` before this work (sha256
3a7b7c3efea13b884362f9f7f07551835bab8ca158ecdb43b946c96a8b3fbf1d, the hash
recorded in `scoreboard/PREREG.sha256`) is preserved byte-identical as
`scoreboard/score_v1.py`; `score.py` now imports and re-exports it, so
`g0_score_filed.py` (loads score.py by path, calls `score_corpus`) still
runs and gives h2 = 2.1262 on the Voynich lines. `PREREG.sha256` itself was
not edited; its `scoreboard/score.py` line now matches `score_v1.py`.
`scoreboard.json` keeps `entrants` / `reproduction_pass` untouched; v2
entries live under the new `v2` key.
