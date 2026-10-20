# r10: what makes cores repeat inside lines? (voynich-91, Roach; blind)

This is queue item r10 (<team-comms>), run on my own code (frozen r7 imported). **VERDICT: no generator matches under both segmenters.** The fold counts are in the Calls table, and both controls behaved as required.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture run 1 | 13:49:12 PDT, revision 0: NOT OK. The planted pool was also matched by copy-recent with a 3-word window (8/15). | R10_PREREG_LOG.txt, results_fixture_run1_rev0.txt |
| Revision 1 | Copy window narrowed to distance 1. Fixture run 2, 13:50:47: NOT OK (the same). | results_fixture_run2_rev1.txt |
| Revision 2 (2 of max 2) | R_w(d) baseline changed to the exact within-PAGE expectation. The within-line baseline is invariant for an exchangeable line pool (R = 1 at every d). Fixture run 3, 13:52:33: OK. Copy text: copy 15, pool 0, drift 0. Pool text: pool 13, copy 0, drift 0. | results_fixture.txt |
| Freeze | 13:54:09 PDT; r10.py ada3231f0b6b0992767c7bd98fb206a4b1f138dcdb11d190cfc521ddaff4f69b. The stub covers r10.py, ../r7/r7.py and ZL3b-n. | r10.prereg.sha256 |
| Real run | 13:54:09 to 13:58:33 PDT, exit 0, stub match YES, r7 entry match YES | R10_PREREG_LOG.txt, results_r10.txt |
| ZL3b-n | bf5b6d4a… | https://www.voynich.nu/data/ZL3b-n.txt |
```
grep -v "^#" r10.prereg.sha256 | tr -d '\r' | sha256sum -c - ; cat R10_PREREG_LOG.txt ; grep "^#" r10.prereg.sha256
```

## Definitions

| Item | Rule | Source |
|---|---|---|
| t1–t3 | R_w(1), R_w(2), mean R_w(3..6): in-line identity / exact page expectation | r10.py docstring |
| t4 | R_x′(1): cross-line identity / page expectation | r10.py docstring |
| t5 | order: Miller–Madow MI at K = 100 minus within-line-shuffle mean (real 200 shuffles; copies 20) | r10.py docstring |
| t6 | quire locality L_q against the training book | r10.py docstring |
| Generators | (i) per-line Pólya pool; (ii) drifting recency urn across lines; (iii) copy the previous word with probability c, all fitted on training quires | r10.py docstring |
| Match | all 6 quantities inside the [0.5, 99.5] envelope of 200 copies; a generator matches a segmenter if ≥ 8 of 15 folds | stub header |
```
grep "^#" r10.prereg.sha256
```

## Calls (folds matched out of 15)

| Corpus | (i) pool | (ii) drift | (iii) copy | Source |
|---|---|---|---|---|
| ZL, S1 cores | 1 | 3 | 2 | results_r10.txt "CALLS" |
| ZL, S2 cores (MDL) | 1 | 3 | 3 | results_r10.txt |
| Planted copy (positive) | 0 | 0 | 13 (required ≥ 8) | results_r10.txt |
| Planted pool (negative) | 14 | 0 | 0 (required < 8) | results_r10.txt |
```
sed -n '/^CALLS/,$p' results_r10.txt
```

## Which property each generator misses (count of folds outside the envelope)

| Generator | S1 most-missed | S2 most-missed | Source |
|---|---|---|---|
| (i) per-line pool | t6 locality 12, t3 decay 8, t2 4 | t6 10, t3 9, t5 4 | results_r10.txt |
| (ii) drifting pool | t6 9, t4 cross-line 5, t3 4 | t6 8, t3 6, t4 6 | results_r10.txt |
| (iii) copy-recent | t6 13, t2 distance-2 repeats 5, t3 2 | t6 10, t2 6, t1 5 | results_r10.txt |
```
grep -E '^== |folds matched|most-missed' results_r10.txt ; grep -A17 '== VOYNICH_ZL S1' results_r10.txt
```

## Reading (qualitative; the figures are in the tables above)

- **Quire locality defeats all three generators.** They draw cores from one book-wide lexicon, but real quires are much more or much less self-repetitive than that (the same finding as r7 (d)).
- **Beyond locality, each generator lacks something different:**
  - A per-line pool repeats at every distance equally; the real repetition decays with distance.
  - Copying the previous word gives distance-1 repeats only; the real text also repeats at distance 2.
  - A drifting pool shares too much across line breaks; the real text drops at the break.
- **The fitted copy rate is tiny (c ≈ 0.02 on every fold)**, so the in-line excess is not mainly immediate reduplication.
- **The likely mechanism is quire-local vocabulary with within-line reuse over a few positions that resets at the line break.** That is a reading only; no generator tested it.

## Deviations and notes

1. Two revisions before the freeze, the maximum (timeline table). Revision 2 changed the R_w baseline to the page level, because the brief's quantity is only meaningful against a baseline that an exchangeable line does not absorb. This is the same R_within as r5.
2. Generator copies use 20 shuffles for t5 (the real data uses 200), for run time.
3. Generators draw only training-lexicon types, so the novel cores of a held-out quire cannot appear. This is part of why t6 is missed.

No decipherment was attempted.

## Files

`results_r10.txt`, `r10.py` (frozen), `r10.prereg.sha256`, `R10_PREREG_LOG.txt`, `results_fixture.txt` (run 3), `results_fixture_run1_rev0.txt`, `results_fixture_run2_rev1.txt`, `README.md`, `MANIFEST.sha256`.
