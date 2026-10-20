# r5: second implementation of F-06 (core residual) and F-13 (core repetition) (voynich-91, Roach; blind)

This answers brief `<team-comms>`. The lead's values were withheld, and I have not read the lead's tree. After the freeze there were no edits, no FAILED lines and no amendments.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture run 1 | 2026-10-18 03:26:48 PDT; raw Witten–Bell gains negative even on the IID fixture | R5_PREREG_LOG.txt |
| Calibration probes | 03:27–03:28 PDT; 12 IID fixtures, 4.4 % of 180 fold p-values below 0.05 | R5_PREREG_LOG.txt |
| Fixture run 2 (final script) | 03:29:18 PDT, r5.py sha256 0a9bbaab…; excess descriptor added | R5_PREREG_LOG.txt, results_fixture.txt |
| Freeze | 03:30:06 PDT; 0a9bbaab8630d4897405963b8f0916bbbfb221596004978728ab0f4acad45715 | r5.prereg.sha256 |
| Real run | 03:30:06 to 03:31:18 PDT, exit 0, stub match YES | R5_PREREG_LOG.txt, results_r5.txt |
| ZL3b-n.txt | bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc | https://www.voynich.nu/data/ZL3b-n.txt |
| IT2a-n.txt (second transliteration) | 7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5 | https://www.voynich.nu/data/IT2a-n.txt |
| Latin control: Caesar BG V–VIII | 8bae4d88747b318b58ea193f981766fed337ddf613df452c1a06d72c9af75ffd | https://www.gutenberg.org/cache/epub/18837/pg18837.txt |
| Folds | 15 quires with ≥ 50 paragraph lines: A B C D E F G H I M N O Q S T. Quire J (18 lines) always stays in training. | results_r5.txt |
```
cat R5_PREREG_LOG.txt r5.prereg.sha256; head -10 results_r5.txt
```

Segmentation and core definition are unchanged from r3/r4. All definitions are in the `r5.py` docstring.

## Calls (ZL)

| Call | Result | Source |
|---|---|---|
| **R5a**: core stream p < 0.05 on ≥ 8 of 15 folds, AND neither affix stream reaches 8 | **FAIL**: core 13 folds, **prefix 15, suffix 15** | results_r5.txt |
| **R5b**: R_within(1) > 1 with p < 0.05, AND above Latin | **PASS**: R_within(1) = 1.323, p = 0.005, Latin 0.134 | results_r5.txt |
```
sed -n '/^CALLS/,$p' results_r5.txt
```

## R5a: next-word residual per stream

The fold columns count folds with p < 0.05 out of 15. The last column is the 166/41-split excess in bits per token.

| Corpus | prefix folds | core folds | suffix folds | 166/41 excess: prefix / core / suffix | Source |
|---|---|---|---|---|---|
| Voynich ZL | 15 | 13 (misses: O p 0.07, S p 0.14) | 15 | +0.054 / +0.107 / +0.059 (all p = 0.005) | results_r5.txt |
| Voynich ZL, per-fold excess range | +0.017 to +0.082 | +0.024 to +0.105 | +0.030 to +0.073 | | results_r5.txt |
| Voynich IT | 14 | 13 | 15 | +0.052 / +0.107 / +0.058 (all p = 0.005) | results_r5.txt |
| Latin (context) | 14 | 15 | 15 | +0.017 / +0.568 / +0.167 | results_r5.txt |
| Planted core bigram (positive) | 1 | 15 | 0 | −0.001 / +1.717 / −0.002 | results_r5.txt |
| Planted copy-recent | 2 | 8 | 0 | −0.002 / +0.054 / −0.000 | results_r5.txt |
| Negative: cores shuffled across the whole book | 15 | **0** | 15 | +0.054 / −0.003 (p = 0.60) / +0.059 | results_r5.txt |
```
grep -E '^R5a|folds with|secondary' results_r5.txt; grep -A19 '^R5a VOYNICH_ZL' results_r5.txt
```

**Reading of R5a** (qualitative; the figures are in the table above)
- **First half of F-06 replicates.** The core stream carries a held-out next-word residual on most quires, and it vanishes when cores are shuffled across the book.
- **Second half does not.** Both affix streams carry residuals on every fold, of the same order as the core's. Affix order survives in the negative control because only the cores were shuffled there.
- The planted control shows the test can separate the streams: a core bigram with iid affixes gives core-only signal.
- **Unverified possibilities.** Some of the affix residual may be the across-space coupling seen in R2, or line-position effects picked up by the bigram history. I did not test either.

## R5b: core repetition R(d) = identical-core rate / within-page-shuffle rate

| Corpus | R_within(1) (perm p) | R_cross(1) | d* (R_reading first ≤ 1) | R_within(1) common / rare cores | Source |
|---|---|---|---|---|---|
| Voynich ZL | 1.323 (0.005) | 0.522 | 26 | 1.244 / 1.910 | results_r5.txt |
| Voynich IT | 1.335 (0.005) | 0.539 | 20 | 1.255 / 2.029 | results_r5.txt |
| Latin prose (positive, < 1 expected) | 0.134 (1.000) | 0.000 | 1 | 0.147 / 0.000 | results_r5.txt |
| Copy-recent (positive, > 1 expected) | 3.162 (0.005) | 1.058 | 8 | 2.088 / 22.997 | results_r5.txt |
| Planted core bigram | 0.996 (0.50) | 1.217 | 3 | 0.962 / 2.206 | results_r5.txt |
| Negative (null expected) | 0.992 (0.61) | 1.119 | 7 | 0.996 / 1.110 | results_r5.txt |
```
grep -E '^R5b|R_within\(1\) =|by left' results_r5.txt
```

| ZL, d | 1 | 2 | 3 | 4 | 5 | 6 | 8 | 10 | 20 | 30 | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R within | 1.323 | 1.385 | 1.268 | 1.167 | 1.074 | 0.995 | 0.797 | 0.627 | 1.949 (few pairs) | n/a | results_r5.txt |
| R cross | 0.522 | 0.748 | 0.822 | 0.923 | 1.078 | 1.116 | 1.085 | 1.134 | 1.052 | 0.986 | results_r5.txt |
| R reading | 1.229 | 1.244 | 1.119 | 1.058 | 1.076 | 1.073 | 1.033 | 1.105 | 1.053 | 0.986 | results_r5.txt |
```
grep -A16 '^R5b VOYNICH_ZL' results_r5.txt
```

**Reading of R5b** (qualitative; the figures are in the tables above)
- **F-13 replicates, on both transliterations.**
  - The same core recurs inside a line more often than a within-page shuffle predicts.
  - The effect peaks at the first two distances and falls to the shuffle level within a few tokens.
  - It is stronger for rare cores than for common ones.
- **Latin prose is the opposite**, as the brief predicted.
- **Across a line break the pattern reverses:** the last core of a line rarely repeats as the first core of the next. In reading order R stays slightly above 1 out to about the brief's 20-token range; the long tail is a small effect.

## Deviations and choices left open by the brief

1. **Excess descriptor**, added after the first fixture run and before the freeze. Witten–Bell halves the back-off mass on rarely seen histories, so raw gains are negative even with no order. The permutation p (the decision statistic) is unaffected.
2. **Folds.** The brief says 15 folds; ZL has 16 quires with paragraph text. The pre-registered rule (≥ 50 lines) drops the smallest quire, J.
3. **R5a scoring.** In-line pairs only, so line-initial tokens are not scored. Unseen held-out tokens share one UNK symbol. Only the tested stream is shuffled.
4. **R5b.**
   - Empty cores are excluded from pairs.
   - The rare/common split uses the r3 training pages.
   - The cross-line series counts any same-page pair spanning a line break.
   - Whole-book, because R5b fits no model.
5. **Latin cores** use r3-style frequency affixes. Pages are 30-line blocks; quires are contiguous pseudo-quires.
6. **Planted generators** use the ZL layout and a Zipf core vocabulary. Parameters are in the docstring.
7. **Fold-count spread.** On iid streams the per-realisation count of significant folds varies. The calibration check (timeline table) shows fold p-values are uniform overall, and the 8-of-15 threshold is far beyond that spread.

No generators were built beyond the controls, and no decipherment was attempted.

## Files

`results_r5.txt`, `r5.py` (frozen), `r5.prereg.sha256`, `R5_PREREG_LOG.txt`, `results_fixture.txt` (run by the frozen script), `README.md` (this file), `MANIFEST.sha256`.
