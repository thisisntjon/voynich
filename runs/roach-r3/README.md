# r3: independent re-implementation of R3a–R3c (voynich-91, host Roach)

This answers brief `<team-comms>`. The lead's values were not given to me, and I have not read the lead's tree. After the freeze there were no edits, no FAILED lines and no amendments.

## Timeline, freeze and data

| Item | Value | Source |
|---|---|---|
| README written | 2026-10-18 02:38 PDT | `date` |
| Fixture run 1 | 02:35:46 PDT, r3.py 2cb399ea…; R3c false positive on the no-chain control | R3_PREREG_LOG.txt |
| Fixture run 2 | 02:36:45 PDT, r3.py 06e88402…; no-chain control clean | R3_PREREG_LOG.txt |
| Freeze | 2026-10-18 02:37:16 PDT; r3.py sha256 06e88402c27707541cc0cc636953ea4fc27997b99ce20d5889ebf0a3d46908fe | R3_PREREG_LOG.txt, r3.prereg.sha256 |
| Real run | 02:37:16 to 02:37:52 PDT, exit 0, stub match YES | R3_PREREG_LOG.txt, results_r3.txt |
| ZL3b-n.txt sha256 | bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc | https://www.voynich.nu/data/ZL3b-n.txt |
| Latin reference: Caesar, *De Bello Gallico* V–VIII | sha256 8bae4d88747b318b58ea193f981766fed337ddf613df452c1a06d72c9af75ffd; 255,543 bytes | https://www.gutenberg.org/cache/epub/18837/pg18837.txt |
| Italian reference: Manzoni, *I promessi sposi*, first 60,000 words used | sha256 4cdd962f1910a49091b945eff4233798b8c13f74b011cee75a8cccc7467d3612; 1,472,526 bytes | https://www.gutenberg.org/cache/epub/45334/pg45334.txt |
| ZL pages with paragraph text | 207, as the brief expects | results_r3.txt |
| ZL lines / words after cleaning | 4,130 / 35,075 | results_r3.txt |
```
cat R3_PREREG_LOG.txt r3.prereg.sha256; head -12 results_r3.txt; sha256sum ../dl_ZL/ZL3b-n.txt dl_PG18837/pg18837.txt dl_PG45334/pg45334.txt
```

## Segmentation rule (fixed before any real-data run; the brief's suggestion, unchanged)

- **prefix:** the longest match at the word start from {qo, q, o, y, d, s, l, r, ch, sh}, else empty.
- **suffix:** the longest match at the end of the remainder (the word with the prefix removed), from {aiin, ain, iin, in, dy, edy, eey, ey, y, ol, al, or, ar, am, m, g, l, r, s}, else empty.
- **core:** whatever is left, possibly empty.
- The empty prefix and the empty suffix are ordinary symbols.

The code is `PREFIXES`, `SUFFIXES` and `make_seg` in `r3.py`.

## Calls (Voynich ZL; R3a and R3b on held-out pages)

| Claim | Estimate | 95 % interval (brief: 80 % page subsample, 500 draws) | Rescaled interval (secondary) | Call | Source |
|---|---|---|---|---|---|
| R3a prefix-stream gain | +0.0457 bits/prefix, n = 4,865 | [+0.0390, +0.0520] | [+0.0314, +0.0577] | **FAIL**: below the 0.05 threshold, although the interval is above 0 | results_r3.txt |
| R3b (prefix, suffix) given core | +1.3795 bits/word, n = 5,557 | [+1.3382, +1.4090] | [+1.2898, +1.4336] | **PASS** | results_r3.txt |
| R3c within-line Moran I excess, all pages | +0.0888 (obs +0.1598, null +0.0710) | [+0.0823, +0.0944] | [+0.0750, +0.0994] | permutation p = 0.005, the smallest value 200 shuffles can give | results_r3.txt |
| R3c cross-line excess, all pages | −0.0221 (obs +0.0153, null +0.0374) | [−0.0379, −0.0072] | [−0.0565, +0.0052] | permutation p = 0.17, two-sided | results_r3.txt |
| R3c, held-out pages only | within +0.0888, cross −0.0505 | see file | see file | within-line only | results_r3.txt |
| R3c call | | | | **within-line only**, on both intervals | results_r3.txt |
```
python -I r3.py real ../dl_ZL/ZL3b-n.txt dl_PG18837/pg18837.txt dl_PG45334/pg45334.txt results_r3.txt; grep -A9 '== VOYNICH' results_r3.txt
```

**Notes on the calls**
- **R3a** is a near miss. The order effect is real, since the interval is above 0, but it is smaller than the brief's bar.
- **R3c:** the primary cross-line interval lies below 0, which the brief's rule counts as "within-line only". On the rescaled interval it includes 0.

## References (context only, no pass/fail)

| Corpus | R3a gain | R3b gain | R3c within excess | R3c cross excess | Source |
|---|---|---|---|---|---|
| Voynich ZL | +0.046 | +1.38 | +0.089 | −0.022 | results_r3.txt |
| Latin (Caesar) | +0.009 | +3.42 | +0.003 (perm p 0.30) | −0.001 | results_r3.txt |
| Italian (Manzoni) | +0.020 | +2.66 | −0.176 | −0.155 | results_r3.txt |
```
grep -E '^(==|R3a|R3b|R3c \[all pages\] (within|cross)|LATIN|ITALIAN)' results_r3.txt
```

**What the references show**
- R3b passes far more strongly on both natural-language references than on the Voynich. So "affixes depend on the core" is not distinctive of the Voynich under this definition.
- R3a: the Voynich prefix-order gain is several times the references', but still under the threshold.
- R3c: within-line word-length correlation is positive for the Voynich, about zero for Latin and strongly negative for Italian. The Italian result is probably a short/long alternation of function words; that reading is unverified.
- Affixes are frequency-defined on each text's training pages; the lists are in `results_r3.txt`.

## Synthetic fixture (the check behind deviation 1)

| Fixture | R3a gain | R3b gain | R3c within excess, all pages | Brief-interval call | Rescaled call / perm p | Source |
|---|---|---|---|---|---|---|
| Planted prefix chain | +1.2898 | +1.6811 | +0.0273 | within-line only | within-line only / 0.005 | results_fixture.txt |
| No-chain control | −0.0042 | −0.0462 | +0.0082, interval [+0.0036, +0.0128] | **within-line only (false positive)** | no excess / 0.065 | results_fixture.txt |
```
python -I r3.py fixture fixture_out; grep -E '^(==|R3a|R3b|R3c \[all pages\])' fixture_out/results_fixture.txt
```

## Deviations from the brief and choices it left open

1. **Secondary interval and permutation test, added after the fixture run and before the freeze.**
   - With the brief's interval, the no-chain control gave a false "within-line" result (table above).
   - The cause: 80 % subsamples drawn without replacement overlap heavily, so their spread understates the full-sample uncertainty by about half, √(0.2/0.8).
   - I added a rescaled interval, est + √(k/(n−k)) · (quantile − median of draws), plus a permutation p over the shuffles.
   - Primary calls still follow the brief. On the real data the primary and secondary calls agree for every claim.
2. **R3a population.** Only prefixes with a previous prefix in the same line (position ≥ 2) are scored. The unigram model is fitted on the same population of training tokens, which keeps line-initial effects out of the gain.
   - **Models:** Witten-Bell interpolation. The unigram backs off to uniform over the prefix alphabet; the R3b unconditional model backs off to uniform over all (prefix, suffix) pairs.
3. **R3c sample.** The brief does not say which pages to use for R3c. The primary uses all pages; held-out only is reported too.
   - **Cross pairs:** consecutive paragraph lines on the same page in file order, including across paragraph boundaries.
   - **Null:** within-line shuffles drawn once, so each subsample uses the same shuffles restricted to its pages.
4. **Word length** is counted in transcribed EVA characters, so `ch` counts 2, and each `@NNN;` code and `?` counts 1.
5. **IVTFF markup** follows the r1/r2 rules V1–V14, because the brief does not specify them:
   - `[a:b]` becomes `a`.
   - Braces and `'` are removed.
   - `<->` and `<~>` become word breaks.
   - Each `@NNN;` code becomes one character.
6. **Page sort** is a plain Python string sort, followed by the brief's seeded shuffle.
7. **References:**
   - These are Gutenberg typeset lines, not manuscript lines, so their line effects are artificial.
   - Pseudo-pages are fixed blocks of lines, with the training share matching the brief's ratio.
   - Normalisation: NFD, combining marks dropped, lowercased, non-letters turned into spaces.
   - The Italian text is cut at a fixed word count, and its opening includes front matter and an introductory essay by another author.
   - The suffix counts give each word each of its final strings once.
   - The exact parameters are in the `r3.py` docstring.
8. **Seeds** are listed in the `r3.py` docstring ("SEEDS").

No generators were built and no decipherment was attempted.

## Files

`results_r3.txt` (the real run), `r3.py` (the frozen script), `r3.prereg.sha256`, `R3_PREREG_LOG.txt`, `results_fixture.txt`, and this README.
