# r15: quire drift beyond hand and section (voynich-91b, Roach; blind)

This answers <team-comms> Own code. voynich-91 was already running r14, so this process did not start a second r14. The core ratio is the r10 definition of R_within(1). The prefix and suffix list is this run's own.

**CALL: Test A NO DRIFT.** ZL p = 0.000900 and IT p = 0.000600 meet their thresholds. RF p = 0.054495 does not (threshold 0.05). The call needs all three.

Test B has no pre-registered call. On ZL, IT and RF the omnibus p-values are 0.452, 0.463 and 0.345. The minimum detectable quire offset at 80% power (p < 0.01 on at least 8 of 10 synthetic books) is 1.00, 0.75 and 1.00 noise-SD.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Self-test and fixture | 2026-10-18 20:43:47 PDT, revision 0: PASS. Sanity offset 5 on all features, p = 0.000100. Planted 10/10. Null 0/10. | results_fixture.txt |
| Freeze | 20:44:03 PDT. r15b.py d45b3b3c3f15515d87a299766964143cfbd87f39346f8291071591966ef341be. | r15b.prereg.sha256, R15B_PREREG_LOG.txt |
| Real run | 20:44:16 to 20:44:28 PDT, exit 0, stub match YES | results_r15b.txt |
| ZL3b-n | bf5b6d4a… | https://www.voynich.nu/data/ZL3b-n.txt |
| IT2a-n | 7f27a8b0… | https://www.voynich.nu/data/IT2a-n.txt |
| RF1b-e | e7d3238e… | https://www.voynich.nu/data/RF1b-e.txt |

```
grep -v "^#" r15b.prereg.sha256 | tr -d '\r' | sha256sum -c -
```

The stub paths are relative to this run directory. On the bridge, `../dl_ZL/ZL3b-n.txt`, `../dl_IT/IT2a-n.txt` and `../dl_RF/RF1b-e.txt` are the same bytes as `corpora/dl_ZL/ZL3b-n.txt`, `corpora/dl_IT/IT2a-n.txt` and `corpora/dl_RF/RF1b-e.txt`.

## Design (frozen)

| Item | Rule | Source |
|---|---|---|
| Layout | IVTFF page variables in the transliteration: quire `$Q`, Davis hand `$H` in 1–5, section `$I` in A B C H P S T Z | r15b.py docstring |
| Unit | Folio with at least 100 locus-type-P word tokens | r15b.py docstring |
| Features | 19 most common initial glyphs, 19 most common final glyphs, mean glyph length, unigram entropy. 40 features. | r15b.py docstring |
| Test A | Sum of eta-squared of quire on residuals after hand × section cell means. 10,000 within-cell permutations of the quire labels. | r15b.py docstring |
| DRIFT | p < 0.01 on ZL and p < 0.05 on both IT and RF | stub header |
| Test B | Same omnibus on R_within(1) and cadence excess (200 within-line shuffles). Report p. No DRIFT call. | stub header |
| MDE | Smallest delta in {0.25, 0.50, 0.75, 1, 1.5, 2, 3} with p < 0.01 on at least 8 of 10 synthetic books. Offset is N(0, delta) on both quantities. | r15b.py docstring |
| Workers | 4 processes at below-normal priority | r15b.py docstring |

```
grep "^#" r15b.prereg.sha256
```

## Fixture

| Book | DRIFT at p < 0.01 | Required | Source |
|---|---|---|---|
| Sanity, offset 5 on all 40 features | p = 0.000100 | must call | results_fixture.txt |
| Planted, offset 0.8 on features 0–12, 10 books | 10 | at least 8 | results_fixture.txt |
| Null, 10 books | 0 | at most 1 | results_fixture.txt |

ZL layout used for the fixture: 94 folios, 15 quires, 13 hand × section cells, 6 of those cells contain more than one quire (67 folios).

## Calls

| Transliteration | Folios | Test A obs | Test A p | Threshold | Test A | Test B MDE | Test B p | Source |
|---|---|---|---|---|---|---|---|---|
| ZL3b | 94 | 6.572585 | 0.000900 | 0.01 | HIT | 1.00 | 0.451955 | results_r15b.txt |
| IT2a | 95 | 6.630288 | 0.000600 | 0.05 | HIT | 0.75 | 0.463454 | results_r15b.txt |
| RF1b-e | 79 | 7.633512 | 0.054495 | 0.05 | MISS | 1.00 | 0.345265 | results_r15b.txt |

Test A call: **NO DRIFT**.

## Reading

The fixture separates a planted quire offset from noise. Every planted book is past the permutation floor (p = 0.000100, no null draw reached the observed omnibus). No null book reaches p < 0.01. The smallest null p in the ten is 0.091.

On the real glyph shares, ZL and IT each put the quire omnibus past their own threshold after hand and section are removed. RF does not. The pre-registered call is the conjunction, so the call is NO DRIFT. RF's omnibus is the largest of the three (7.63 against 6.57 and 6.63) and its p is the largest, which is what a smaller folio set does to the null.

Test B is powered for a quire offset of about one noise-SD on both quantities together. The real p-values sit near the middle of the null. In-line core reuse and within-line length rhythm do not add a quire difference beyond hand and section, on these three transliterations, at an effect this test can see.

## Deviations and notes

1. No revision. The fixture passed at revision 0.
2. Four workers, not twelve. voynich-91 already had twelve workers on the r14 fixture. This run set its own priority below normal.
3. R_within(1) uses this run's prefix and suffix list. The ratio matches the r10 definition: adjacent in-line core matches divided by the exact within-folio coincidence.
4. A post-run count, not a re-analysis: locus-P dot/comma slots are 35,075 (ZL), 34,491 (IT) and 34,659 (RF). The parser keeps 34,054, 33,614 and 30,326 of those. RF has 3,484 slots that contain an `@nnn;` code; those words are dropped because `@` is not a glyph. That is why RF contributes 79 folios rather than 94 or 95. The frozen rule did that. The call was not recomputed.
5. An IVTFF `<->` gap is removed as a tag, so the words on either side can join.

No decipherment was attempted.

## Files

`results_r15b.txt`, `r15b.py` (frozen), `r15b.prereg.sha256`, `R15B_PREREG_LOG.txt`, `results_fixture.txt`, `README.md`, `MANIFEST.sha256`.
