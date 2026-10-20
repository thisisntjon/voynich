# r8: homophonic cipher under a per-line affix table versus Voynich core statistics (voynich-91, Roach; blind)

This is the task relayed from Skynet (reply thread: the r6 brief). It was run on my own code only, reusing frozen r7 through an explicit local import that the stub also covers.

**VERDICT: the segmenters DISAGREE. Under S1 the claim HOLDS; under S2 it does NOT HOLD.** The settings counts are in the Calls table.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture run 1 | 2026-10-18 13:02:31 PDT, revision 0: NOT OK. The WEAK stand-in (r7 planted) had core order of about +0.3, stronger than ciphers B and C, so it was not weak. | R8_PREREG_LOG.txt, fixture_out (run 1) |
| Revision 1 (1 of max 2) | The WEAK stand-in was given truly weak order (copy 0.15, chain 0.05). The fixture pass check uses ORACLE cores, the generator's boundaries, in the fixture only. S1/S2 fixture outcomes are reported, not required. | r8.py docstring, R8_PREREG_LOG.txt |
| Fixture run 2 | 13:07:58 PDT: FIXTURE CHECK OK. ORACLE: WEAK HOLDS (2/3 settings), STRONG NOT HOLDS (1/3). Info: WEAK S1 HOLDS, S2 NOT HOLDS. | results_fixture.txt |
| Freeze | 13:13:45 PDT; r8.py d5fe0de371e44576ab4e2caeb76cc9ce617ba0b4b640c5d54a226fbe63a722c6. The stub covers r8.py, ../r7/r7.py and both data files. | r8.prereg.sha256 |
| Real run | 13:13:45 to 13:15:46 PDT, exit 0, stub match YES, r7 entry match YES | R8_PREREG_LOG.txt, results_r8.txt |
| ZL3b-n | bf5b6d4a… | https://www.voynich.nu/data/ZL3b-n.txt |
| Plaintext: Caesar BG V–VIII as a letter stream (194,108 letters) | 8bae4d88… | https://www.gutenberg.org/cache/epub/18837/pg18837.txt |
```
grep -v "^#" r8.prereg.sha256 | tr -d '\r' | sha256sum -c - ; cat R8_PREREG_LOG.txt ; head -8 results_r8.txt
```

## Design (frozen)

| Item | Rule | Source |
|---|---|---|
| Cipher | Core glyphs {k,t,p,f,e,o,a,i,d}; homophone classes of codewords; one table of 3 (prefix, suffix) pairs per line from the r3 lists + empty; the ZL layout filled with the first 35,075 cipher words | r8.py docstring, stub header |
| Settings | A: letter, h = 3, length 2–3 ; B: letter, h = 6, length 2–3 ; C: 2-letter chunk, h = 2, length 3–4 | stub header |
| Segmentation | S1 (r3 lists) and S2 (r7 MDL, fitted on each text); generator boundaries never used | stub header |
| Measures per LOQO fold | (a) Miller–Madow MI excess at K = 100 over 200 within-line shuffles; (b) R_within(1) against the exact within-line expectation | stub header |
| Call | A setting supports if cipher (a) > Voynich (a) AND cipher (b) < Voynich (b) on ≥ 8/15 folds; the claim HOLDS under a segmenter if ≥ 2 of 3 settings support | stub header |
```
grep "^#" r8.prereg.sha256
```

## Calls

| Segmenter | Setting A | Setting B | Setting C | Settings supporting | Claim | Source |
|---|---|---|---|---|---|---|
| S1 | 15/15 SUPPORTS | 15/15 SUPPORTS | 14/15 SUPPORTS | 3 of 3 | **HOLDS** | results_r8.txt |
| S2 | 0/15 | 1/15 | 9/15 SUPPORTS | 1 of 3 | **NOT HOLDS** | results_r8.txt |
```
grep -E 'folds supporting|^CALL|VERDICT' results_r8.txt
```

## The two halves of each comparison

This descriptive split is computed from the frozen per-fold lines in results_r8.txt; it is not a new test.

| Setting / segmenter | cipher order > Voynich (folds) | cipher R_within(1) < Voynich (folds) | Source |
|---|---|---|---|
| A / S1 | 15 | 15 | results_r8.txt |
| A / S2 | 0 | 15 | results_r8.txt |
| B / S1 | 15 | 15 | results_r8.txt |
| B / S2 | 1 | 14 | results_r8.txt |
| C / S1 | 14 | 15 | results_r8.txt |
| C / S2 | 10 | 14 | results_r8.txt |
```
grep -A16 -E '^   [ABC]/S[12] +fold' results_r8.txt
```

## Reading (qualitative; the figures are in the tables above)

- **The "less same-core recurrence" half holds under both segmenters, in every setting.** Every cipher has lower R_within(1) than the Voynich on almost every fold.
- **The "more core order" half depends on the segmenter.** S1 strips the line-table affixes, and the homophone cores then carry clearly more order than the Voynich.
- **On ciphers A and B, the MDL inducer (S2) finds prefixes but no suffixes** (results_r8.txt "cipher S2 MDL affixes"). Each S2 core therefore keeps its line-table suffix. The line table makes those core+suffix strings cluster within lines, and the order excess turns negative. With 2-letter units (C) S2 does find suffixes, and order exceeds the Voynich on most folds.
- **So F-39's "wrong core statistics" conclusion is robust for recurrence, but for order it is contingent on segmentation.** A segmenter that fails to strip a per-line suffix table hides the cipher's order. This is the disagreement the brief asked to be reported.

## Deviations and notes

1. One revision before the freeze (timeline table). The fixture's WEAK stand-in was not weak in run 1, and the pass check was moved to oracle cores, because S2's behaviour on the cipher is what the real run measures.
2. The cipher core alphabet deliberately overlaps Voynich affix glyphs (o, d, a, i), so S1 can mis-strip. That is part of the test.
3. The plaintext is Latin only. The three settings were fixed before the run.

No decipherment was attempted.

## Files

`results_r8.txt`, `r8.py` (frozen), `r8.prereg.sha256`, `R8_PREREG_LOG.txt`, `results_fixture.txt` (fixture run 2, from the frozen script), `results_fixture_run1_rev0.txt` (fixture run 1, superseded), `README.md`, `MANIFEST.sha256`.
