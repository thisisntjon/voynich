# r13: blind power audit of the F-23 / F-30 exclusions (voynich-91, Roach)

This answers brief <team-comms> The producers were built from the published descriptions only, on my own code (frozen r10 and r7 imported).

**VERDICT: copy-and-vary WEAK, table-and-grille UNINFORMATIVE.** The real-text failures are therefore not exclusions. This independently supports Argon's s101 claim (see the Calls table).

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture run 1 | 15:48:56 PDT, revision 0: NOT OK. Planted A refit 10/15; planted B refit 0/15, with every fold missing t5 order because the latent table is not recoverable. | R13_PREREG_LOG.txt, results_fixture_run1_rev0.txt |
| Revision 1 | ORACLE self-test added (copies from the true planted parameters); the fixture check moved to ORACLE. Run 2 at 15:50:02: NOT OK, because the A oracle used a refitted lexicon. | results_fixture_run2_rev1.txt |
| Revision 2 (2 of max 2) | The A oracle uses the true generating lexicon. Its first run (15:50:55) crashed before any result, on a pickling error. The same design was re-implemented by passing the generating lines (disclosed). Run 3 at 15:51:34: OK. ORACLE A 13, B 13; refit A 10, B 0. | results_fixture.txt, fixture_stdout_rev2_crash.txt |
| Freeze | 15:52:31 PDT; r13.py d3c91e27791781b3d047ca56a926ae6862a0b9b3c37fd38cc89b1bc0215b3d94. The stub covers r13.py, r10.py, r7.py and ZL3b-n. | r13.prereg.sha256 |
| Real run | 15:52:31 to 15:55:08 PDT, exit 0, stub match YES, r10 and r7 entries YES | R13_PREREG_LOG.txt, results_r13.txt |
| ZL3b-n | bf5b6d4a… | https://www.voynich.nu/data/ZL3b-n.txt |
```
grep -v "^#" r13.prereg.sha256 | tr -d '\r' | sha256sum -c - ; cat R13_PREREG_LOG.txt ; grep "^#" r13.prereg.sha256
```

## Design (frozen)

| Item | Rule | Source |
|---|---|---|
| (A) copy-and-vary | With probability q, copy one of the previous 10 words; with probability e, apply one edit (substitution, insertion or deletion); else a fresh lexicon draw. (q, e) are fitted by grid to the training rep/near rates. | r13.py docstring |
| (B) table-and-grille | R × 3 table from the S1 prefix/core/suffix distributions; grille offsets (0, d2, d3); random start per line; step 1–3 rows. R is fitted by grid to the training TTR and rep. | r13.py docstring |
| Quantities | r10 t1–t6 on whole words + t7 type/token + t8 mean word length | r13.py docstring |
| Match | all 8 inside the [0.5, 99.5] envelope of 200 copies of the producer refitted on the training quires | stub header |
| Call | POWERED planted ≥ 10/15; WEAK 5–9; UNINFORMATIVE ≤ 4; a real 0/15 is an exclusion only if POWERED | stub header |
```
grep "^#" r13.prereg.sha256
```

## Calls (folds matched of 15)

| Producer | Fitted on all of ZL | Planted, refitted (power) | Band | Planted ORACLE | Real ZL | Cross (negative control) | Source |
|---|---|---|---|---|---|---|---|
| A copy-and-vary | q 0.1, e 0.67 | 8 | **WEAK** | 13 | 1 | 1 (on planted B) | results_r13.txt "CALLS" |
| B table-and-grille | R 256 | 0 | **UNINFORMATIVE** | 14 | 0, not an exclusion | 0 (on planted A) | results_r13.txt |

| Test | Most-missed quantities (folds outside envelope) | Source |
|---|---|---|
| Planted A, refitted | t7 type/token 6, t6 locality 4 | results_r13.txt |
| Planted B, refitted | t5 order 15 | results_r13.txt |
| Real ZL, producer A | t6 11, t7 10, t8 8, t5 6 | results_r13.txt |
| Real ZL, producer B | t7 15, t3 13, t6 12, t2 9 | results_r13.txt |
```
grep -E 'folds matched|Producer parameters' results_r13.txt ; sed -n '/^CALLS/,$p' results_r13.txt
```

## Reading (qualitative; the figures are in the tables above)

- **The envelope test can recognise a producer when it has the producer's exact parameters**, on both producers.
- **The power is lost in the refitting step.**
  - **Copy-and-vary:** the refit recovers its two rates only roughly, and the planted text's type/token and quire-locality fall outside the refitted envelope on about half the folds, which leaves it WEAK.
  - **Table-and-grille:** the refit cannot recover the latent table alignment or the grille offsets. The planted text's strong word order is then outside the envelope on every fold, so the test is UNINFORMATIVE.
- **So the real-text failures do not exclude these producer families.** They show only that these particular refitted versions don't match.
- **The negative controls behave correctly:** each producer fails on the other's planted text. So the envelope discriminates; its weakness is parameter recovery, not a lack of sensitivity.
- **An informative exclusion of F-30-type producers would need a fitting procedure that infers the table and grille from the training text.**

## Deviations and notes

1. Both revisions were used, plus one disclosed implementation fix inside revision 2 (timeline table). The oracle is a reported addition; the call uses the refitted planted test, exactly as briefed.
2. The producers are my own constructions from the published descriptions; parameter grids are in the docstring.
3. B's fitted table size sits at the top of its grid (Calls table).
4. The first bridge copy went out before this README existed, with an incomplete manifest. That manifest is kept as MANIFEST.sha256.incomplete-no-readme; MANIFEST.sha256 is the complete one.

No decipherment was attempted.

## Files

`results_r13.txt`, `r13.py` (frozen), `r13.prereg.sha256`, `R13_PREREG_LOG.txt`, `results_fixture.txt` (run 3), `results_fixture_run1_rev0.txt`, `results_fixture_run2_rev1.txt`, `fixture_stdout_rev2_crash.txt`, `README.md`, `MANIFEST.sha256`, `MANIFEST.sha256.incomplete-no-readme`.
