# r6: line-held affix table test (voynich-91, Roach; blind, first independent implementation)

This answers brief `<team-comms>`. The lead's values were withheld, and I have not read the lead's tree. **VERDICT: FAIL.** The line-held generator matched 0 of 15 folds.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture run | 2026-10-18 12:23:00 PDT, revision 0 (no revisions). Planted line-held: PASS, with (i) 13/15, (ii) 0, (iii) 0, fitted alpha about 3.0–3.15 against 3 planted. Chain: FAIL, with (iii) 14/15. | R6_PREREG_LOG.txt, results_fixture.txt |
| Freeze | 12:32:29 PDT; r6.py sha256 6e6ee178b4ef0c9ffab438e0aa1a197f377d27eaeb5de41d98613a32eaf036c4. The prereg covers r6.py (which has no local imports) and all three data files, with the thresholds and the call in its header. | r6.prereg.sha256 |
| Real run | 12:32:29 to 12:50:42 PDT, exit 0, stub match YES; single process at below-normal priority | R6_PREREG_LOG.txt, results_r6.txt |
| ZL3b-n.txt | bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc | https://www.voynich.nu/data/ZL3b-n.txt |
| IT2a-n.txt | 7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5 | https://www.voynich.nu/data/IT2a-n.txt |
| Latin (Caesar BG V–VIII) | 8bae4d88747b318b58ea193f981766fed337ddf613df452c1a06d72c9af75ffd | https://www.gutenberg.org/cache/epub/18837/pg18837.txt |
```
grep -v "^#" r6.prereg.sha256 | tr -d '\r' | sha256sum -c - ; cat R6_PREREG_LOG.txt ; head -7 results_r6.txt
```

The definitions are in the r6.py docstring and the r6.prereg.sha256 header.
- **Profile per stream:** q1 = R_w(1); q2 = R_w(1) − R_w(3) (decay); q3 = C, within-line clustering against the page; q4 = X, adjacent-line sharing against the page, where X ≈ 1 means a reset. All are computed on line positions ≥ 2, with exact closed-form shuffle expectations.
- **Match:** all 8 quantities of the held-out quire fall inside the generator's [0.5, 99.5] percentile envelope over 200 copies.
- **Call:** (i) ≥ 8/15 AND (ii) < 8 AND (iii) < 8.

## Calls

| Item | Result | Source |
|---|---|---|
| ZL call | (i) line-held **0/15**, (ii) per-word 4/15, (iii) Markov 1/15, threshold 8 → **FAIL** | results_r6.txt, "CALLS" |
| IT (second transliteration) | (i) 0/15, (ii) 2/15, (iii) 0/15 → FAIL | results_r6.txt |
| Positive control: planted line-held (alpha = 3) on the ZL layout | (i) 13/15, (ii) 0, (iii) 0 → PASS, as required. Line-held signature YES on both streams. | results_r6.txt |
| Negative control: Latin | Line-held signature NO on both streams, as required. Fold call FAIL: (i) 5, (ii) 4, (iii) 11. | results_r6.txt |
| VERDICT | **FAIL** (controls as required) | results_r6.txt |
```
sed -n '/^CALLS/,$p' results_r6.txt
```

## R6a: whole-text profile, exact permutation p from 200 shuffles

| Corpus / stream | q1 R_w(1) (p_up, p_two) | q2 decay (p_two) | q3 C (p_up) | q4 X (p_up) | R_w(d), d = 1..6 | Source |
|---|---|---|---|---|---|---|
| ZL prefix | 0.978 (0.990, 0.035) | −0.049 (0.005) | 1.065 (0.005) | 1.050 (0.005) | 0.978 1.077 1.027 1.007 0.986 0.966 | results_r6.txt |
| ZL suffix | 1.128 (0.005, 0.005) | +0.117 (0.005) | 1.119 (0.005) | 1.069 (0.005) | 1.128 1.076 1.010 0.983 0.930 0.856 | results_r6.txt |
| IT prefix | 0.991 (0.796, 0.433) | −0.040 (0.035) | 1.068 (0.005) | 1.051 (0.005) | 0.991 1.072 1.031 0.995 0.981 0.950 | results_r6.txt |
| IT suffix | 1.089 (0.005, 0.005) | +0.086 (0.005) | 1.107 (0.005) | 1.072 (0.005) | 1.089 1.086 1.004 0.984 0.972 0.835 | results_r6.txt |
| Planted prefix | 1.000 (0.468) | +0.002 | 2.320 (0.005) | 0.956 (1.000) | about 1.0 flat | results_r6.txt |
| Planted suffix | 0.994 (0.856) | +0.006 | 3.546 (0.005) | 0.870 (1.000) | about 1.0 flat | results_r6.txt |
| Latin prefix | 0.998 (0.726) | −0.003 | 1.002 (0.244) | 0.998 (0.871) | about 1.0 flat | results_r6.txt |
| Latin suffix | 1.132 (0.005) | +0.214 (0.005) | 1.120 (0.005) | 1.040 (0.005) | 1.132 0.917 0.918 1.021 1.001 0.960 | results_r6.txt |
```
grep -E '^R6a|q1 R_w|q3 C|R_w\(d\)|signature' results_r6.txt
```

## R6b: per-fold matches (ZL)

| Fold | Lines | Fitted alpha prefix / suffix | (i) | (ii) | (iii) | Source |
|---|---|---|---|---|---|---|
| A B C D E F G H I M N O Q S T | 71–1,084 | about 21–23 / 18–23 | 0 of 15 | B, C, I, Q (4) | I (1) | results_r6.txt |
```
grep -A17 '^R6b VOYNICH_ZL' results_r6.txt
```

## What this says about the claim (qualitative; the figures are in the tables above)

- **The Voynich affix streams do cluster within lines.** C is above the page level for both streams with p at the floor, so there is a line-scale component.
- **But the clustering does not reset at the line break.** Adjacent lines share affixes above the page level, X > 1 with p at the floor. A line-held table predicts X ≈ 1 or below, as the planted control shows.
- **The suffix stream has within-line order that decays with distance.** R_w falls from above 1 at d = 1 to below 1 by d = 5–6. A line-held table is exchangeable within its line and predicts a flat R_w ≈ 1.
- **The prefix stream** shows a weak alternation instead: slightly below 1 at d = 1, above 1 at d = 2.
- **No generator reproduces the profile.** The fitted line-held tables are weak (alpha about 21, against 3 in the planted control). They match no fold because they cannot produce the cross-line sharing or the suffix order. The per-word and Markov generators fail on most folds too.
- **My reading:** a regional affix drift spanning several lines, plus short-range suffix order, fits better than one table per line. This is an interpretation and was not tested by a generator.
- **Latin suffixes show a similar pattern** (order, within-line clustering, X > 1). It is reproduced by the Markov generator on 11 of 15 folds. The pattern is therefore not unique to the Voynich, but the Voynich's version is not captured by a first-order chain.

## Deviations and choices left open by the brief

1. **Shuffle for q3 and q4.** The brief asks for permutation p against within-line shuffles for every quantity. q3 (within-line clustering) and q4 (adjacent-line sharing) are invariant under any within-line shuffle, because a line-held table is exchangeable within its line. So they use within-page shuffles (200), and q1/q2 use within-line shuffles (200). This is written in the frozen header.
2. **Line-initial words** are excluded from every profile quantity, which keeps the known line-initial effect out. All generators draw the line-initial affix from the training line-initial distribution.
3. **The line-held generator** is a Dirichlet-multinomial per line. Its single parameter alpha is solved in closed form from the training within-line identity rate.
4. **Folds:** quires with ≥ 50 paragraph lines, giving 15; quire J (18 lines) always stays in training. This is the same rule as r5.
5. **Brief versus prompt:** the brief only asks for a "README"; the relayed prompt asks for README.md, delivered here.

No decipherment was attempted, and nothing was built beyond the controls.

## Files

`results_r6.txt`, `r6.py` (frozen), `r6.prereg.sha256`, `R6_PREREG_LOG.txt`, `results_fixture.txt` (from the frozen script, which was not revised after the fixture), `README.md` (this file), `MANIFEST.sha256`.
