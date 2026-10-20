# r4: are adjacent word cores ordered? (voynich-91, host Roach; blind)

This answers brief `<team-comms>`. The lead's values were withheld, and I have not read the lead's tree. After the freeze there were no edits, no FAILED lines and no amendments.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| README written | 2026-10-18 03:08 PDT | `date` |
| Fixture run 1 | 03:04:28 PDT; on no-order fixtures the brief's interval sometimes excluded 0 | R4_PREREG_LOG.txt |
| Fixture run 2 | 03:05:52 PDT with the final script (sha256 f74f1ddc…); null sd and permutation p added | R4_PREREG_LOG.txt, results_fixture.txt |
| Freeze | 2026-10-18 03:06:37 PDT; r4.py sha256 f74f1ddcd7d34dfb5003ff867236d75f787e7f9cfbfe7cc4ddc0ab528b60735d | R4_PREREG_LOG.txt, r4.prereg.sha256 |
| Real run | 03:06:37 to 03:07:43 PDT, exit 0, stub match YES | R4_PREREG_LOG.txt, results_r4.txt |
| ZL3b-n.txt | sha256 bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc; 207 pages, 35,075 words | https://www.voynich.nu/data/ZL3b-n.txt |
| Latin plaintext (Caesar) | sha256 8bae4d88…; 30,880 words; 194,108 letters | https://www.gutenberg.org/cache/epub/18837/pg18837.txt |
| Italian plaintext (Manzoni, first 60,000 words) | sha256 4cdd962f…; 60,012 words; 275,636 letters | https://www.gutenberg.org/cache/epub/45334/pg45334.txt |
| Voynich held-out set | 41 pages, 5,557 words, 4,865 adjacent core pairs; 2,270 training core types | results_r4.txt |
```
cat R4_PREREG_LOG.txt r4.prereg.sha256; head -20 results_r4.txt
```

The split, segmentation and core definition are unchanged from r3. The class maps, statistic, controls and calls are exactly as written in the `r4.py` docstring.

## Pre-registered calls

| Call | Primary (plug-in, brief's interval) | Secondary (permutation p / rescaled interval) | Source |
|---|---|---|---|
| (i) K=100 freq: Voynich excess > 0 with interval above 0 | **NO**: +0.0072 [−0.0106, +0.0190] | **NO**: p_up 0.234 | results_r4.txt "calls" block |
| (i), Miller–Madow version | **NO**: +0.0127 [−0.0076, +0.0245] | **NO**: p_up 0.090 | results_r4.txt |
| (ii) Voynich below both ciphers with separation, K 50/100/200 × both methods × Latin and Italian | **YES**: all 24 comparisons separated | **YES** (rescaled) | results_r4.txt |
| (iii) negative control includes 0 at every K | **NO → controls failed**: 6 of 11 cells exclude 0 | **NO → controls failed**: freq K=25 p_two 0.025, freq K=200 p_two 0.035 | results_r4.txt |
```
sed -n '/--- calls/,$p' results_r4.txt
```

## Voynich and negative control, plug-in excess (bits)

| Map | K | Voynich excess [95 %] | Voynich perm p_up | Negative-control excess [95 %] | Negative perm p_two | Source |
|---|---|---|---|---|---|---|
| freq | 25 | +0.0126 [+0.0040, +0.0183] | 0.010 | +0.0082 [+0.0017, +0.0129] | 0.025 | results_r4.txt |
| freq | 50 | +0.0160 [+0.0029, +0.0280] | 0.010 | +0.0053 [−0.0036, +0.0122] | 0.328 | results_r4.txt |
| freq | 100 | +0.0072 [−0.0106, +0.0190] | 0.234 | +0.0103 [−0.0003, +0.0192] | 0.274 | results_r4.txt |
| freq | 200 | +0.0043 [−0.0143, +0.0204] | 0.383 | +0.0288 [+0.0119, +0.0414] | 0.035 | results_r4.txt |
| freq | 400 | −0.0185 [−0.0364, −0.0052] | 0.920 | +0.0239 [+0.0041, +0.0377] | 0.095 | results_r4.txt |
| freq | full (2,271 classes) | −0.0285 [−0.0546, −0.0190] | 0.975 | +0.0254 [+0.0045, +0.0390] | 0.134 | results_r4.txt |
| cluster | 25 | +0.0071 [−0.0006, +0.0117] | 0.015 | −0.0030 [−0.0067, +0.0003] | 0.303 | results_r4.txt |
| cluster | 50 | +0.0085 [−0.0034, +0.0133] | 0.025 | −0.0052 [−0.0098, −0.0017] | 0.134 | results_r4.txt |
| cluster | 100 | +0.0059 [−0.0066, +0.0121] | 0.229 | +0.0058 [−0.0028, +0.0123] | 0.333 | results_r4.txt |
| cluster | 200 | −0.0002 [−0.0217, +0.0074] | 0.542 | +0.0029 [−0.0098, +0.0127] | 0.701 | results_r4.txt |
| cluster | 400 (292 classes: only 291 cores have count ≥ 5) | −0.0158 [−0.0356, −0.0021] | 0.876 | +0.0237 [+0.0075, +0.0349] | 0.114 | results_r4.txt |
```
grep -A13 -E '== (VOYNICH|NEGATIVE)' results_r4.txt
```

## Positive controls: planted ciphers, size and layout matched (plug-in excess)

| Control | Plaintext symbols | K=50 freq / cluster | K=100 freq / cluster | K=200 freq / cluster | perm p | Source |
|---|---|---|---|---|---|---|
| Cipher (a) Latin, letter → core | 23 | +0.481 / +0.481 | +0.481 / +0.481 | +0.481 / +0.481 | 0.005 | results_r4.txt |
| Cipher (b) Latin, bigram → core | 362 | +0.236 / +0.139 | +0.472 / +0.291 | +0.639 / +0.509 | 0.005 | results_r4.txt |
| Cipher (a) Italian | 25 | +0.511 / +0.511 | +0.511 / +0.511 | +0.511 / +0.511 | 0.005 | results_r4.txt |
| Cipher (b) Italian | 381 | +0.160 / +0.187 | +0.329 / +0.259 | +0.444 / +0.435 | 0.005 | results_r4.txt |
| Fixture: 1,450 Zipf core types, chain on half the transitions (run by the frozen script) | n/a | +0.371 / +0.604 | +0.495 / +0.768 | +0.552 / +0.834 | 0.005 | fixture_out/results_fixture.txt |
```
for c in CIPHER_A_LAT CIPHER_B_LAT CIPHER_A_IT CIPHER_B_IT; do grep -A13 "== $c" results_r4.txt; done; grep -A13 'chain=True' fixture_out/results_fixture.txt
```

## What this says about the at-risk claim (interpretation; the source is the tables above)

- **The worry is not borne out for strong order.** At the Voynich's exact size and layout, the statistic finds the planted order in every cipher at every K, with p at its floor. It also finds it in a fixture with Voynich-like sparsity (about 1,450 types), at every K under both maps. Plug-in excess against a within-line shuffle is not blind at this sparsity.
- **Limitation:** the cipher inventories (22–352 types) are far smaller than the Voynich's 2,270. The sparse fixture is the stronger evidence on sparsity, but its order is synthetic.
- **The Voynich shows at most weak order.** The excess is small and positive at coarse K (freq 25/50: +0.013 to +0.016, permutation p 0.010; cluster 25/50: p 0.015 to 0.025). It is not distinguishable from zero at K ≥ 100, and it is negative at K ≥ 400.
  - This is about 4–40 times smaller than the planted ciphers at the same K. The closest is cipher (b) Italian at freq K = 25 (+0.047).
  - Strictly, "excess ≤ 0" is not supported at K = 25–50.
  - It is supported at the brief's K = 100, where call (i) is NO.
- **Controls failed (iii), as pre-registered.** The brief's subsample interval excludes 0 in 6 of 11 negative-control cells. The cause is the realisation-noise problem shown on the fixtures, so the primary interval cannot hold a 0-centred null to its nominal coverage.
  - Under the exact permutation test, 2 of 11 plug-in cells have p_two < 0.05. About 0.55 are expected by chance across 11 cells, and the chance of 2 or more is about 0.10.
  - Even so, the Voynich's coarse-K p ≈ 0.01 is of the same order as the negative control's worst cell (0.025). So the weak coarse-K order should be read as **not established**.

## Deviations and choices left open by the brief

1. **Secondary null sd and permutation p, added after the fixture run and before the freeze.**
   - Across fixture seeds the no-order excess is centred on 0 with |z| ≤ 2.3, but the brief's interval sometimes excluded 0.
   - Primary calls remain exactly as briefed.
2. **Interval draws use shuffles 1–20 for each draw's null mean.** The point estimates use all 200 shuffles. This was for run time and is declared in the docstring.
3. **Clustering method:** spherical k-means on left/right neighbour profiles. Only cores with training count ≥ 5 are clustered; rare and unseen cores go to one pooled class. "full" is identical under both maps.
4. **Ciphers:**
   - Each is laid out on the Voynich's exact pages, lines and line lengths, so it is the same size as the Voynich.
   - That uses only the first 35,075 cipher symbols: about 35k letters of Caesar for (a), about 70k for (b). Both source texts are at least 30,000 words.
   - Prefixes and suffixes are uniform random. Plaintext spaces and punctuation are dropped.
5. **Negative control:** cores are permuted across the whole book with prefixes, suffixes, lines and pages kept. Class maps are refitted on its own training pages.
6. **Calls:** primary uses plug-in; Miller–Madow is reported as secondary for every call.

## Files

`results_r4.txt` (the real run), `r4.py` (frozen), `r4.prereg.sha256`, `R4_PREREG_LOG.txt`, `results_fixture.txt` (fixture run by the frozen script), `README.md` (this file), `MANIFEST.sha256`.
