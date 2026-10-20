# r7: line-scoped core signature under two independent segmenters (voynich-91, Roach; blind)

This is the task relayed from Skynet (reply thread: the r6 brief). It was run on my own code only (the r3–r6 lineage), with no Skynet code.

**VERDICT: on ZL, the signature does NOT HOLD under either segmenter.** The fold counts are in the Calls table, and both controls behaved as required.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| Fixture | 2026-10-18 12:59:14 PDT, revision 0. Planted HOLDS 15/15 (S1, S2); word-Markov NOT HOLDS under S0/S1/S2. FIXTURE CHECK OK. | R7_PREREG_LOG.txt, results_fixture.txt |
| Freeze | 13:01:13 PDT; r7.py 0d5e65db45b3c410bfbcab5b56d45adaab09b09c9af007b3546538a5b9f69b96. The stub covers r7.py and all 6 data files, with every threshold and the call in its header. | r7.prereg.sha256 |
| Real run | 13:01:13 to 13:05:06 PDT, exit 0, stub match YES | R7_PREREG_LOG.txt, results_r7.txt |
| ZL3b / IT2a | bf5b6d4a… / 7f27a8b0… | https://www.voynich.nu/data/ZL3b-n.txt, https://www.voynich.nu/data/IT2a-n.txt |
| Latin (negative control) | Caesar BG V–VIII, 30,880 words, 8bae4d88… | https://www.gutenberg.org/cache/epub/18837/pg18837.txt |
| Recipe reference | Forme of Cury (c. 1390), recipe text only: 16,207 words. This is the whole recipe section, below the 35,075 target. 87d1a281… | https://www.gutenberg.org/cache/epub/8102/pg8102.txt |
| Repetition reference | Book of Common Prayer from "THE LITANY" on (litany and psalter): 35,076 words; ca675286… | https://www.gutenberg.org/cache/epub/29622/pg29622.txt |
| Prose reference | Manzoni, I promessi sposi: 35,081 words; 4cdd962f… | https://www.gutenberg.org/cache/epub/45334/pg45334.txt |
```
grep -v "^#" r7.prereg.sha256 | tr -d '\r' | sha256sum -c - ; cat R7_PREREG_LOG.txt ; head -10 results_r7.txt
```

## Definitions (frozen before the real run)

| Item | Rule | Source |
|---|---|---|
| S0 | the whole word | r7.prereg.sha256 header, r7.py docstring |
| S1 | r3 affix lists (Voynich-type text); r3 frequency affixes (references) | r7.prereg.sha256 header |
| S2 (new) | greedy minimum-description-length affix inducer: 25 + 25 candidates, at most 15 per side, fitted unsupervised on each text | r7.prereg.sha256 header |
| (a) | Miller–Madow MI excess at K = 100 classes > 0 and p_up < 0.05 (200 within-line shuffles) | r7.prereg.sha256 header |
| (b) | R_within(1) > 1 and p_up < 0.05 (200 within-line shuffles, exact expectation) | r7.prereg.sha256 header |
| (c) | Rw′ − Rx′ > 0 and p_up < 0.05 (200 within-page shuffles) | r7.prereg.sha256 header |
| (d) | quire locality 0.8 ≤ L_q ≤ 1.25; shuffle band over 200 whole-book shuffles reported | r7.prereg.sha256 header |
| Call | signature HOLDS if all four pass on ≥ 8 of 15 LOQO folds | r7.prereg.sha256 header |
```
grep "^#" r7.prereg.sha256
```

## Calls (folds passing all four, out of 15)

| Corpus | S0 | S1 | S2 | Source |
|---|---|---|---|---|
| Voynich ZL | 0, NOT HOLDS | 1, NOT HOLDS | 1, NOT HOLDS | results_r7.txt |
| Voynich IT | 2, NOT HOLDS | 2, NOT HOLDS | 2, NOT HOLDS | results_r7.txt |
| Planted (positive) | 2 | 13, HOLDS (required) | 13, HOLDS | results_r7.txt |
| Word-Markov (negative) | 0 | 0 | 0 (required NOT HOLDS) | results_r7.txt |
| Latin (negative) | 0 | 0 | 0 (required NOT HOLDS) | results_r7.txt |
| Forme of Cury | 0 | 0 | 0 | results_r7.txt |
| BCP litany | 0 | 0 | 0 | results_r7.txt |
| Manzoni | 0 | 0 | 0 | results_r7.txt |
| Any reference with (b)&(c) together on ≥ 8 folds | none (0 folds for every reference and definition) | | | results_r7.txt |
```
sed -n '/^CALLS/,$p' results_r7.txt
```

## Components on Voynich (folds passing out of 15)

| Corpus / definition | (a) order | (b) R_within(1) | (c) within > cross | (d) quire locality | (b)&(c) | Source |
|---|---|---|---|---|---|---|
| ZL S0 | 10 | 1 | 6 | 5 | 0 | results_r7.txt |
| ZL S1 | 2 | 9 | 9 | 5 | 7 | results_r7.txt |
| ZL S2 | 5 | 4 | 9 | 8 | 2 | results_r7.txt |
| IT S0 | 8 | 4 | 6 | 3 | 3 | results_r7.txt |
| IT S1 | 3 | 9 | 10 | 6 | 7 | results_r7.txt |
| IT S2 | 6 | 3 | 9 | 7 | 3 | results_r7.txt |
```
grep -E '^== |folds passing' results_r7.txt
```

| ZL S1 quire | A | B | C | D | E | F | G | H | I | M | N | O | Q | S | T | Source |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| L_q | 0.589 | 0.936 | 0.775 | 0.553 | 1.210 | 0.782 | 0.829 | 0.730 | 0.288 | 2.040 | 1.244 | 0.579 | 0.753 | 0.727 | 1.169 | results_r7.txt |
| (d) pass | no | yes | no | no | yes | no | yes | no | no | no | yes | no | no | no | yes | results_r7.txt |
```
awk '/VOYNICH_ZL S1: 15 folds/,/folds passing/' results_r7.txt
```

## Reading (qualitative; the figures are in the tables above)

- **(b) and (c) are partly supported, under S1 only.** Within-line same-core repetition and the drop across line breaks each hold on more than half of the quires, but together they fall just short of the bar, on both transliterations. Under S2 (MDL cores), (b) mostly disappears.
- **(a), per quire at K = 100, is rarely significant under S1 or S2**, consistent with r4's weak order. It is more often significant on whole words.
- **(d) fails on most quires, in both directions.** Some quires are far more self-repetitive than the book, many far less. The shuffle bands are much narrower than the pre-registered 0.8–1.25 window.
- **S1 and S2 agree on the overall call but disagree on the components.** The MDL inducer finds different affixes on ZL (for example cho/che/she/ol, ody/eedy/o) and almost no suffixes on IT, so the two core definitions really do differ.
- **No natural-language reference** (recipe, litany or prose) shows within-line same-core repetition above shuffle. That property appears only in the Voynich and the planted control.

## Deviations and notes

1. The Forme of Cury recipe section is smaller than the matched size, so it was used in full (timeline table).
2. S1 for the references is the r3 frequency-affix segmenter, since the Voynich lists don't apply. S2 is fitted on each whole text without labels.
3. Empty cores (possible under S1) are dropped from each line's core sequence.
4. (d) is defined per held-out quire against the whole book, with the numeric window written down before running.

No decipherment was attempted.

## Files

`results_r7.txt`, `r7.py` (frozen), `r7.prereg.sha256`, `R7_PREREG_LOG.txt`, `results_fixture.txt`, `README.md`, `MANIFEST.sha256`.
