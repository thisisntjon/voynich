# r11: a bigger reference class for in-line reuse (b) and the cross-line drop (c) (voynich-91, Roach; blind)

This is queue item r11 (<team-comms>), run on my own code (frozen r7 imported) with 2,000 shuffles per test. **VERDICT: no reference text shows (b) and (c) together.** None of the 11 new texts passes (b) on a single block (Calls table). Both controls behaved as required.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture run 1 | 13:59:49 PDT, revision 0: OK. Planted shows under S1; word-Markov does not. | R11_PREREG_LOG.txt, results_fixture_run1_rev0.txt |
| Loader-only dry run | 14:00 PDT, no statistics computed: the ballads start marker (nth = 2) was not found | R11_PREREG_LOG.txt |
| Revision 1 (1 of max 2) | Ballads marker changed to nth = 1. The dry run at 14:01 had all 11 loaders OK. Fixture run 2 at 14:02: OK. | results_fixture.txt |
| Stub | First attempt at 14:02 broke on CREMMA file names with spaces; it is kept as r11.prereg.sha256.BROKEN-unquoted-paths-1402. The stub was rebuilt at 14:12:10 PDT: 136 entries, all OK. | r11.prereg.sha256 |
| Freeze / real run | r11.py 668037abf5c53d809de8a3d80bc07b7e915034a6d4a9335a2674b1259a2e7867; 14:12:10 to 14:16:05 PDT, exit 0, stub match YES, r7 entry match YES | R11_PREREG_LOG.txt, results_r11.txt |
```
grep -v "^#" r11.prereg.sha256 | tr -d '\r' | sha256sum -c - | grep -c ': OK' ; cat R11_PREREG_LOG.txt ; grep "^#" r11.prereg.sha256
```

## Texts (each cut to at most 35,075 words in 15 blocks; one source line = one line)

| Text | Kind | Words used | Source |
|---|---|---|---|
| Apicius, De re coquinaria (Latin, critical edition) | recipe collection | 31,205 | https://www.gutenberg.org/cache/epub/16439/pg16439.txt |
| Digby, The Closet … Opened (1669) | recipe collection | 35,082 | https://www.gutenberg.org/cache/epub/16441/pg16441.txt |
| Roget's Thesaurus | synonym list | 35,077 | https://www.gutenberg.org/cache/epub/10681/pg10681.txt |
| Culpeper, Complete Herbal | herbal | 35,076 | https://www.gutenberg.org/cache/epub/49513/pg49513.txt |
| Kalevala (Finnish) | verse with parallelism | 35,077 | https://www.gutenberg.org/cache/epub/7000/pg7000.txt |
| English and Scottish Popular Ballads, vol. 1 | verse with refrains | 35,081 | https://www.gutenberg.org/cache/epub/44969/pg44969.txt |
| Complete Manual of Catholic Piety, from the first litany | litanies | 35,083 | https://www.gutenberg.org/cache/epub/62988/pg62988.txt |
| Prayers of the Middle Ages | prayers and litanies | 14,527 (whole text) | https://www.gutenberg.org/cache/epub/48242/pg48242.txt |
| CREMMA Medii Aevi, raw ALTO (abbreviations kept) | abbreviated medieval Latin, real manuscript lines | 35,078 | https://github.com/HTR-United/CREMMA-Medieval-LAT (v0.1.2) |
| WLC Genesis + Exodus, points stripped | unvowelled Semitic (Hebrew), verse = line | 35,076 | https://github.com/openscriptures/morphhb |
| Dante, Commedia | Italian verse | 35,079 | https://www.gutenberg.org/cache/epub/1000/pg1000.txt |
| Caesar BG V–VIII (negative control) | Latin prose | (r7) | https://www.gutenberg.org/cache/epub/18837/pg18837.txt |
```
python -I r11dry.py r11.py <home>/voynich-replication   # the loader-only dry run; word counts as above
```

## Calls (blocks passing out of 15; threshold 8; 2,000 shuffles per test)

| Text | (b) S0 / S2 | (c) S0 / S2 | (b)&(c) S0 / S2 | Shows? | Source |
|---|---|---|---|---|---|
| Voynich ZL (also S1: (b) 8, (c) 9, (b)&(c) 6) | 1 / 3 | 6 / 9 | 0 / 2 | no, under all three | results_r11.txt |
| Planted (positive; 16 quires) | 2 / 16 | 5 / 16 | 2 / 16 (S1 16/16) | YES under S1 (required) | results_r11.txt |
| Caesar (negative) | 0 / 0 | 0 / 0 | 0 / 0 | no (required) | results_r11.txt |
| Apicius | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| Digby | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| Roget | 0 / 0 | 0 / 2 | 0 / 0 | no | results_r11.txt |
| Culpeper | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| Kalevala | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| Ballads | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| Catholic litanies | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| Medieval prayers | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| CREMMA abbreviated Latin | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| Hebrew unvowelled | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
| Dante | 0 / 0 | 0 / 0 | 0 / 0 | no | results_r11.txt |
```
grep -E 'blocks \(threshold' results_r11.txt ; sed -n '/^CALLS/,$p' results_r11.txt
```

## Reading (qualitative; the figures are in the table above)

- **In-line reuse is absent from every reference text.** This covers texts built on repetition (litanies, refrains, Kalevala parallelism), list texts (thesaurus, herbal, recipes), abbreviated manuscript Latin and consonantal Hebrew. Adjacent identical words or cores are never more frequent than a within-line shuffle predicts; natural texts avoid immediate repetition.
- **The Voynich is the only text with it.** Under S1 it is on the edge, at the bar for (b) and just under it for (b) and (c) together. Under MDL cores (S2) and whole words (S0) it is weaker.
- **So within-line core reuse is distinctive of the Voynich against a wide reference class.** It is strong only under the hand-made S1 segmentation, which matches the r7 result.

## Deviations and notes

1. The positive control used all 16 quires of the ZL layout, so its threshold scaled to 9 of 16. The Voynich itself uses the 15 quires with ≥ 50 lines.
2. Apicius includes the edition's apparatus and the Gutenberg producer credits, and Prayers of the Middle Ages has only 14,527 words; both were used whole.
3. One revision and one rebuilt stub before any real run (timeline table). r11.py did not change between fixture run 2 and the real run.

No decipherment was attempted.

## Files

`results_r11.txt`, `r11.py` (frozen), `r11.prereg.sha256`, `r11.prereg.sha256.BROKEN-unquoted-paths-1402` (superseded, kept), `R11_PREREG_LOG.txt`, `results_fixture.txt` (run 2), `results_fixture_run1_rev0.txt`, `r11dry.py` (loader-only dry-run script), `README.md`, `MANIFEST.sha256`.
