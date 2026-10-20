# r9: regional affix drift (voynich-91, Roach; blind)

This is queue item r9 (<team-comms>). It tests my own r6 reading, on my own code only. **VERDICT: FAIL.** The drift generator matches no ZL fold, but the decay itself is measured and significant. Both controls behaved as required.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture run 1 | 2026-10-18 13:28:05 PDT, revision 0: OK, but the fitted scale was 10 against a planted 5 | R9_PREREG_LOG.txt |
| Revision 1 (1 of max 2) | The share between lines 3 apart (r_x3) was added to the drift fit | r9.py docstring |
| Fixture run 2 | 13:31:56 PDT: OK. Planted drift PASS, drift 12/15, scale 5.0 (planted 5); planted line-held not PASS, line-held 13 | results_fixture.txt |
| Freeze | 13:35:47 PDT; r9.py b5a62a57c65a52004c35881c27073dc51e426b45c40954c4571e13f97f51567b. The stub covers r9.py and the 3 data files. | r9.prereg.sha256 |
| Real run | 13:35:47 to 13:47:44 PDT, exit 0, stub match YES; 12 workers at below-normal priority | R9_PREREG_LOG.txt, results_r9.txt |
| Data | ZL3b bf5b6d4a…, IT2a 7f27a8b0…, Caesar 8bae4d88… | https://www.voynich.nu/data/ZL3b-n.txt, https://www.voynich.nu/data/IT2a-n.txt, https://www.gutenberg.org/cache/epub/18837/pg18837.txt |
```
grep -v "^#" r9.prereg.sha256 | tr -d '\r' | sha256sum -c - ; cat R9_PREREG_LOG.txt ; grep "^#" r9.prereg.sha256
```

## R9a: affix-share decay with line distance (mean over quires; exact p from 200 quire shuffles)

S(D) is the share for lines D apart on the same page, relative to the quire level. SX(1) is the share for the last line of a page against the first line of the next.

| Text / stream | S(1) (p) | S(2–4) (p) | SX(1) cross-page (p) | S(D), D = 1..4 | Source |
|---|---|---|---|---|---|
| ZL prefix | 1.148 (0.005) | 1.102 (0.005) | 1.046 (0.194) | 1.148 1.118 1.126 1.061 | results_r9.txt |
| ZL suffix | 1.224 (0.005) | 1.184 (0.005) | 1.069 (0.109) | 1.224 1.206 1.197 1.150 | results_r9.txt |
| IT prefix | 1.165 (0.005) | 1.105 (0.005) | 1.065 (0.050) | 1.165 1.117 1.130 1.068 | results_r9.txt |
| IT suffix | 1.230 (0.005) | 1.190 (0.005) | 1.081 (0.095) | 1.230 1.213 1.198 1.160 | results_r9.txt |
```
grep -E '^R9a|S\(1\)|S\(2-4\)|SX\(1\)|S\(D\)' results_r9.txt
```

## Calls (folds matched out of 15; MATCH = all 14 quantities inside the 99 % envelope of 200 copies)

| Text | (i) drift | (ii) line-held | (iii) per-word | (iv) chain | Median fitted drift scale | Call | Source |
|---|---|---|---|---|---|---|---|
| ZL | 0 | 0 | 0 | 0 | 10.0 lines | **FAIL** | results_r9.txt "CALLS" |
| IT | 0 | 0 | 0 | 0 | 5.0 lines | FAIL | results_r9.txt |
| Planted drift (positive) | 10 | 4 | 0 | 1 | 5.0 (planted 5) | PASS (required) | results_r9.txt |
| Planted line-held (negative) | 1 | 11 | 0 | 0 | 1.0 | not PASS (required) | results_r9.txt |
| Latin (reference) | 9 | 3 | 0 | 6 | 3.3 | PASS | results_r9.txt |
```
sed -n '/^CALLS/,$p' results_r9.txt ; grep -A17 '^R9b VOYNICH_ZL' results_r9.txt
```

## Reading (qualitative; the figures are in the tables above)

- **Regional affix drift is real in the measurement.** Affix sharing between lines of a page is well above the quire level and decays with line distance, for both streams and both transliterations.
- **The drift does not clearly carry across page breaks.** The cross-page share is lower and not significant at 0.05 (borderline for IT prefixes).
- **But my simple drifting-table generator does not reproduce the full profile on any fold.** Its fitted concentration sits at the grid edge (β = 1, the most concentrated tables allowed), which is a sign of misfit.
- The r6 profile already showed short-range within-line suffix order. A drifting table, like a line-held table, is exchangeable within a line and cannot produce that. Which quantities fail per fold was not recorded by this script; that is a limitation.
- **The verdict is therefore that the drift is confirmed as a property, but the pure drifting-table mechanism is rejected.** Some within-line ordering component is still needed.
- **Latin is matched by drift** on most folds, with its chain generator second. So a drifting topical vocabulary is an ordinary language property, not a Voynich peculiarity.

## Deviations and notes

1. One revision before the freeze (timeline table).
2. The β grid's lower edge was hit on Voynich, so a wider grid might fit better. That was not tested after the freeze.
3. The cross-page quantity uses consecutive pages within the same quire.

No decipherment was attempted.

## Files

`results_r9.txt`, `r9.py` (frozen), `r9.prereg.sha256`, `R9_PREREG_LOG.txt`, `results_fixture.txt` (fixture run 2), `results_fixture_run1_rev0.txt`, `README.md`, `MANIFEST.sha256`.
