# r12: word-length rhythm, two ways (voynich-91, Roach; blind)

This is queue item r12 (<team-comms>). It replicates F-04 and a Voynich Ninja claim independently, on my own code (frozen r11 and r7 imported).

**VERDICT: "Voynich-specific positive in-line rhythm" does NOT HOLD.** The Voynich rhythm replicates, but one natural text (Finnish metrical verse) also shows it. Both controls behaved as required.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture | 2026-10-18 14:18:10 PDT, revision 0: OK. Planted AR(0.3) is positive on L1_POOLED in ≥ 8 blocks; the within-line-shuffled copy is not. | R12_PREREG_LOG.txt, results_fixture.txt |
| Freeze | 14:20:00 PDT; r12.py 980ded572901f3f2cd181a08459d351412af294af3b1e2d052f68b3e6fc759bc. The stub has 138 entries: r12.py, r11.py, r7.py and every data file. | r12.prereg.sha256 |
| Real run | 14:20:00 to 14:23:53 PDT, exit 0, stub match YES, r11 and r7 entries YES | R12_PREREG_LOG.txt, results_r12.txt |
| Texts | Voynich ZL and IT; Caesar; the 11 r11 texts (same sources and start markers as r11) | https://www.voynich.nu/data/ZL3b-n.txt, r11/README.md |
```
grep -v "^#" r12.prereg.sha256 | tr -d '\r' | sha256sum -c - | grep -c ': OK' ; cat R12_PREREG_LOG.txt ; grep "^#" r12.prereg.sha256
```

## Definitions (2,000 shuffles each; positive = excess > 0 and p_up < 0.05)

| Statistic | Measure | Null | Source |
|---|---|---|---|
| L1_POOLED (primary) | Pearson lag-1 word-length correlation over in-line pairs | within-line shuffles | r12.py docstring |
| L1_LINE | mean per-line lag-1 autocorrelation (lines with ≥ 4 words) | within-line shuffles | r12.py docstring |
| PARA | lag-1 inside paragraphs, including pairs across line breaks | within-paragraph shuffles | r12.py docstring |
| XLINE | (last word of a line, first word of the next) | within-line shuffles | r12.py docstring |
| Call | ZL positive on L1_POOLED in ≥ 8/15 blocks AND no natural text positive in ≥ 8/15 | | stub header |
```
grep "^#" r12.prereg.sha256
```

## Calls (positive blocks of 15)

| Text | L1_POOLED | L1_LINE | PARA | XLINE | Source |
|---|---|---|---|---|---|
| Voynich ZL | **12** | 12 | 11 | 0 | results_r12.txt "CALLS" |
| Voynich IT | 11 | 11 | 12 | 0 | results_r12.txt |
| Planted AR (positive) | 15 | 15 | 15 | 2 | results_r12.txt |
| Shuffled copy (negative) | 1 | 1 | 12 (see note) | 1 | results_r12.txt |
| **Kalevala (Finnish verse)** | **15** | 15 | 14 | 1 | results_r12.txt |
| Roget (synonym list) | 4 | 4 | 15 | 7 | results_r12.txt |
| Caesar | 3 | 3 | 0 | 1 | results_r12.txt |
| Apicius | 1 | 2 | 0 | 0 | results_r12.txt |
| CREMMA abbreviated Latin | 1 | 1 | 1 | 0 | results_r12.txt |
| Hebrew unvowelled | 0 | 0 | 3 | 0 | results_r12.txt |
| Medieval prayers | 0 | 0 | 2 | 0 | results_r12.txt |
| Digby, Culpeper, Ballads, Catholic litanies, Dante | 0 | 0 | 0 | 0 or 1 | results_r12.txt |
```
sed -n '/^CALLS/,$p' results_r12.txt
```

Whole-text L1_POOLED (all blocks pooled; same command, "whole text" lines):

| Text | Obs | Null | Excess | p_up | Source |
|---|---|---|---|---|---|
| Voynich ZL | +0.1630 | +0.0708 | +0.0922 | 0.0005 | results_r12.txt |
| Voynich IT | +0.1623 | +0.0705 | +0.0918 | 0.0005 | results_r12.txt |
| Kalevala | +0.2838 | +0.0484 | +0.2354 | 0.0005 | results_r12.txt |
| Caesar | −0.0142 | −0.0167 | +0.0026 | 0.32 | results_r12.txt |
| Dante | −0.0056 | +0.0221 | −0.0277 | 1.00 | results_r12.txt |
| Hebrew | −0.1491 | −0.0573 | −0.0918 | 1.00 | results_r12.txt |
```
grep 'whole text' results_r12.txt
```

## Reading (qualitative; the figures are in the tables above)

- **F-04's in-line rhythm replicates independently on both transliterations.** Adjacent words in a Voynich line have positively correlated lengths beyond what a shuffle of the same line gives. The relation does not continue across line breaks.
- **It is not unique to the Voynich in this reference class.** Finnish Kalevala verse, in strict trochaic metre, shows a stronger version. Every prose, list, liturgical and Semitic text does not; Dante and the Hebrew go the other way.
- **The pre-registered call is therefore NOT HOLDS.** The fair summary is that the Voynich behaves like metrically constrained verse on this measure and unlike prose.
- **Note on PARA:** the within-line-shuffled control is positive on PARA. Lines differ in mean word length, and a paragraph shuffle mixes lines. So PARA mixes order with line-level heterogeneity, which is why the call uses L1_POOLED.

## Deviations and notes

1. Paragraphs are defined per text type (docstring). CREMMA uses one page file and Hebrew one chapter per paragraph.
2. Word length is in transcribed characters: EVA glyph characters for the Voynich, letters for the others, consonants for Hebrew.
3. No revisions. The fixture passed at revision 0.

No decipherment was attempted.

## Files

`results_r12.txt`, `r12.py` (frozen), `r12.prereg.sha256`, `R12_PREREG_LOG.txt`, `results_fixture.txt`, `README.md`, `MANIFEST.sha256`.
