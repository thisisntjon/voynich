# Independent replication of R1 and R2 (voynich-91, host Roach)

Written 2026-10-18 02:29 PDT (09:29Z, from `date`). Runs took place 2026-10-17 22:29-22:31 PDT.
This session did not read or adopt anything from the lead session's tree. Its only contact with the lead is listed in section 8, and all of it came after the results were hashed and filed.

## 1. Bottom line

| | Call against the fixed prediction | Robust? |
|---|---|---|
| **R1** line-initial profile | **PASS**: ZL 773-line 2.5 % bound +0.155 vs max prose +0.017 | Yes. IT and RF agree. All three side predictions about Voynich and prose matched. |
| **R2** across-space coupling | **PASS by the letter of the rule on ZL (margin +0.007)** | **No.** IT fails. The single control that ZL B beats (Priapea verse, 116 lines) falls inside Voynich B's own size-matched interval. "Controls below +0.13" did not reproduce. |

## 2. Data sources

All are public, text only, and each download sits in its own folder. No code from a download was executed, and every Python run used `-I`.

| Source | URL | Bytes | sha256 |
|---|---|---|---|
| ZL transliteration v3b (13/05/2025) | https://www.voynich.nu/data/ZL3b-n.txt | 411,671 | bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc |
| IT (Takahashi) v2a | https://www.voynich.nu/data/IT2a-n.txt | 342,104 | 7f27a8b0feed8f6de0a99900df6bf912dd1d295c38e5f830bac8b41c3f536fb5 |
| RF (Reeds/Friedman) v1b, EVA "full" | https://www.voynich.nu/data/RF1b-e.txt | 362,373 | e7d3238e35743e06c63367a933909ec37b1e2de7ada3a1b449447eafa1918782 |
| CREMMA Medii Aevi (CREMMA-Medieval-LAT) v0.1.2 | Zenodo record 8407213; files fetched from https://github.com/HTR-United/CREMMA-Medieval-LAT at tag v0.1.2 = commit 9439fe33a07eeb2814fa4b94b65c280f20aa6ec1 (the commit the Zenodo record cites as isSupplementTo) | 12,358,778 (XML and metadata only) | manifest of the 47 files used: `CREMMA_used_manifest.sha256` (c3222ed9...); data-registry.csv f5938151... |
| Dante, *La Divina Commedia* | https://www.gutenberg.org/cache/epub/1000/pg1000.txt (Project Gutenberg #1000) | 597,903 | 4669dcc00ee61ceffe92d871e61ea430cec87b35cbab24f19a4c0b1c7da521b2 |

- **CREMMA:** the official Zenodo zip is 356,673,369 bytes, mostly images. That is above the 200 MB per-source limit, so it was **not** downloaded. Only the XML and metadata (12 MB) were taken, from the exact tagged commit of the release. This is the same content as the release, but it was not checked byte-for-byte against the zip. **Unverified.**
- **Dante:** this is a modern edition with one verse per line, not a manuscript.

## 3. Selection and cleaning rules

The full text of these rules is in the `scripts/prep.py` docstring.

**Voynich (IVTFF, EVA). The same rules apply to all three files.**
- Comment lines (`#`) are dropped.
- From the page headers, `$L` (Currier language) and `$H` (hand) are kept.
- The primary corpus uses **paragraph loci (type P) only**. A secondary corpus `ALLLOCI` adds labels, circular and radial loci.
- Markup:
  - `<!...>` comments and the markers `<%>`, `<$>` and `<@..>` are removed.
  - `<->` and `<~>` become word breaks.
  - `[a:b]` becomes `a` (the first reading).
  - `{..}` braces are removed and their content kept. `'` is removed.
  - Each `@NNN;` code becomes one private character per code. `?` is kept as a character.
- Word separators: `.` always. `,` (uncertain space) also counts as a separator in the primary corpus. A secondary corpus `ZL_NOCOMMA` deletes `,` instead.
- Nothing else was deleted except leading spaces.
- One locus line is one manuscript line.
- Pages without `$L` (95 P-lines) are counted in "all" but not in A or B.
- Size of ZL after cleaning: 4,130 P-lines (A 1,557, B 2,478); 4,045 have at least 3 words.

**CREMMA Latin**
- Fifteenth-century rule: notBefore ≥ 1400 and notAfter ≤ 1499 in `data-registry.csv`. This selects 7 manuscripts.
- Genre classes were fixed before any run:

| MS | Registry date | Genre (fixed in advance) | Lines (≥3 words) |
|---|---|---|---|
| PalLat373 (Plaoul, *De Fide*) | 1400-1499 | prose | 427 |
| Laur. Plut. 53.08 (Donatus on Terence) | 1459 | prose | 216 |
| Laur. Plut. 53.09 (Donatus on Terence) | 1400-1499 | prose | 125 |
| SBB-PK Hdschr. 25 (Book of Hours) | 1400-1499 | formulaic | 212 |
| Berlin Germ. Oct. 511 (penitential psalms) | 1400-1499 | formulaic | 39 |
| Laur. Plut. 39.34 (Priapea) | 1400-1499 | verse | 116 |
| BnF Latin 8236 (Prudentius, Tibullus) | 1471-1499 | verse | 204 |

- Pools: `LAT15_PROSE` is the three prose manuscripts (768 lines with at least 3 words). `LAT15_ALL` is all seven.
- Source files: the release's normalised `*.chocomufin.xml` (ALTO).
- Lines kept: lines in a `MainZone` block whose line type is `DefaultLine` or absent. Headings, interlinear lines, drop capitals, margins and numbering are excluded.
- Text normalisation:
  - Unicode NFD, then combining marks deleted (so abbreviation marks are lost), then lowercased.
  - Kept: letters, plus the word signs ⁊, ÷, ∻ and &. Punctuation and digits are **deleted, not replaced by a space**.
  - Split on whitespace.

**Dante**
- Start at the first `Canto I`.
- Drop blank lines, cantica headings and canto headings.
- Apply the same normalisation as the Latin.
- 14,233 lines.

## 4. Definitions

- **R1:** take lines with at least 3 words. P is the distribution of first characters of line-initial words; Q is the distribution of first characters of all non-initial words. The statistic is JSD(P, Q) in bits (log2, plug-in).
  - Null: shuffle the words within each line, 30 times, and take the mean.
  - Excess = observed − null mean.
  - Matched size: 773 lines drawn without replacement from the Voynich lines with at least 3 words, 200 draws. Each draw gets its own 30-shuffle null. Report the median and the 2.5 / 97.5 percentiles.
- **R2:** take every within-line adjacent pair (lines with at least 2 words). X is the last character of the left word, Y the first character of the right word. The statistic is plug-in MI(X;Y) in bits. The null and excess are as in R1.
- **Seeds:** fixed in the scripts (20261017 + corpus index; 773; 7732).

## 5. Results

### R1 (from `results_r1.txt`)

| Corpus | Lines | JSD obs | Null mean | **Excess** |
|---|---|---|---|---|
| Voynich ZL, all | 4,045 | 0.1775 | 0.0028 | **+0.1748** |
| ZL Currier A / B | 1,515 / 2,449 | | | +0.1369 / +0.2205 |
| IT, all (A / B) | 4,033 | | | +0.1731 (+0.1323 / +0.2212) |
| RF, all (A / B) | 4,037 | | | +0.1847 (+0.1449 / +0.2319) |
| ZL_ALLLOCI / ZL_NOCOMMA | | | | +0.1681 / +0.1754 |
| Prose: PalLat373 | 427 | 0.0246 | 0.0172 | +0.0074 |
| Prose: Laur. 53.08 | 216 | 0.0308 | 0.0260 | +0.0048 |
| Prose: Laur. 53.09 | 125 | 0.0533 | 0.0361 | +0.0172 |
| **LAT15_PROSE pool** | 768 | 0.0166 | 0.0115 | **+0.0050** |
| Formulaic: SBB Hdschr. 25 / BGO-511 | 212 / 39 | | | +0.0009 / +0.0645 |
| Verse: Laur. 39.34 / Latin 8236 | 116 / 204 | | | +0.0659 / +0.0502 |
| LAT15_ALL pool | 1,339 | | | +0.0065 |
| Dante | 14,233 | | | +0.0299 |

Matched size (773 lines, 200 draws), median [2.5 %, 97.5 %]:

| Transliteration | Excess |
|---|---|
| ZL | +0.1746 [+0.1551, +0.1975] |
| IT | +0.1732 [+0.1552, +0.1951] |
| RF | +0.1835 [+0.1615, +0.2045] |

**Call: PASS.** The ZL 2.5 % bound, +0.1551, is above every prose pool; the highest is Laur. 53.09 at +0.0172.

Side predictions:

| Prediction | Result | Status |
|---|---|---|
| Voynich excess ~+0.17 | +0.175 | matched |
| Pooled prose ~+0.01 | +0.005 | matched |
| No prose manuscript above +0.05 | all at or below +0.017 | matched |
| Verse or formulaic at 100-200 lines can reach +0.10 to +0.14 | at most +0.066 here | **not observed** |

The last prediction says "can reach", so failing to observe it here does not contradict it.

### R2 (from `results_r2.txt`)

| Corpus | Pairs | MI obs | Null mean | **Excess** |
|---|---|---|---|---|
| ZL, all | 30,945 | 0.2007 | 0.0196 | +0.1811 |
| **ZL Currier A** | 9,780 | 0.1557 | 0.0369 | **+0.1188** |
| **ZL Currier B** | 20,710 | 0.2533 | 0.0193 | **+0.2340** |
| IT all / A / B | | | | +0.1682 / +0.1013 / +0.2184 |
| RF all / A / B | | | | +0.1765 / +0.1084 / +0.2307 |
| ZL_ALLLOCI all / A / B | | | | +0.1784 / +0.1197 / +0.2315 |
| ZL_NOCOMMA all / A / B | | | | +0.1480 / +0.0808 / +0.1948 |
| Prose: PalLat373 / 53.08 / 53.09 | 1,753 / 2,725 / 1,141 | | | +0.0604 / +0.0255 / +0.0399 |
| LAT15_PROSE pool | 5,619 | 0.1416 | 0.1139 | +0.0277 |
| Formulaic: SBB Hdschr. 25 / BGO-511 | 705 / 114 | | | +0.0376 / −0.0847 |
| **Verse: Laur. 39.34 (Priapea)** | 636 | 0.6190 | 0.3921 | **+0.2269** |
| Verse: Latin 8236 | 1,196 | 0.4069 | 0.2376 | +0.1693 |
| LAT15_ALL pool | 8,270 | | | +0.0374 |
| Dante | 82,964 | 0.1038 | 0.0070 | +0.0968 |

- Control range: −0.0847 (BGO-511) to +0.2269 (Laur. 39.34).
- ZL B, +0.2340, is above the maximum (margin +0.0071). ZL A, +0.1188, is inside the range. **Call: PASS.**
- Robustness:
  - IT B, +0.2184, is **not** above the maximum, so IT fails.
  - RF passes (B +0.2307).
  - A is inside the range for all three transliterations.
- Matched size, 773 lines (pre-registered as secondary), median [2.5 %, 97.5 %]:
  - ZL A: +0.1178 [+0.1057, +0.1303]
  - ZL B: +0.2328 [+0.2169, +0.2500]
  - The B interval reaches below +0.2269.
- Post-hoc (`explore_r2.txt`; script hashed but written after seeing the results, so it is **not** pre-registered):
  - ZL B cut down to 116 lines gives +0.219 [+0.171, +0.260]. The Priapea control's +0.227 lies inside that interval.
  - A line bootstrap of the Latin controls was also run. It is biased upward by duplicated lines (e.g. Priapea median +0.397), so it was discarded.

**Reading of R2.**
- Voynich B is far above every **prose** control (+0.03 to +0.06) and above Dante (+0.10).
- But the two fifteenth-century Latin **verse** manuscripts reach +0.17 and +0.23 at small n. So "B above every real-line control by a clear margin" and "controls below +0.13" are **not** reproduced.
- "A inside the control range" holds, but only because the range is very wide. A, at +0.12, is above every prose control.

## 6. What would refute each result, and whether it was checked

| Result | Would be refuted by | Checked? |
|---|---|---|
| R1 | ZL 773-line 2.5 % bound at or below some prose-pool excess | Yes: not refuted (+0.155 vs +0.017). |
| R1 | The result depends on the transliteration, the comma rule or the locus rule | Yes: IT, RF, ALLLOCI and NOCOMMA all at +0.168 to +0.185. |
| R1 | A real prose text with a large excess | Partly: only 3 fifteenth-century Latin prose manuscripts, plus Dante (verse, +0.030). No vernacular prose was tested. |
| R2 | ZL B at or below the top control | Yes: not refuted on ZL, by +0.007. **Refuted on IT.** |
| R2 | ZL A outside the control range | Yes: not refuted. |
| R2 | The B margin vanishes at matched size | Yes (secondary and post-hoc): at 116 and 773 lines the B interval includes the top control's value. In practice the "clear margin" claim does not survive. |
| R2 | Comma rule | Yes: with NOCOMMA, B drops to +0.195, which is below the Priapea control. |

## 7. Where my definitions may differ from the lead session's

1. **Comma (`,`) as a space.** R2 is sensitive to this (B +0.234 vs +0.195). The lead's choice is unknown to me.
2. **Paragraph loci only.** Little effect.
3. **`@NNN;` codes as one character per code.** They matter for RF (4,021 codes).
4. **Latin text:**
   - I used the `chocomufin` normalisation and stripped combining marks, so abbreviation marks are lost. This changes the last characters of words, which feeds R2.
   - Punctuation is deleted, not turned into a space, so a few words are joined (e.g. "tuus.Int" → "tuusint").
   - Headings, interlinear lines and drop-capital lines are excluded.
5. **Prose pool size.** Mine has 768 lines with at least 3 words; the lead's matched size is 773. That suggests the same three prose manuscripts with slightly different line filtering. **Unverified.**
6. **Control set for R2.** I included all seven fifteenth-century manuscripts (verse and formulaic too), both pools and Dante, as the brief says ("every Latin manuscript and pool and the verse control"). The lead's "controls below +0.13" suggests the lead's set did not include these two verse manuscripts, or treated them differently. **Unverified.**
7. **Plug-in MI.** Small controls have large null means (0.2 to 1.0 bits). The shuffle null corrects for the mean, but the variance of the excess is large at a few hundred pairs.
8. **Not verified:** whether RF1b-e, rather than RF1b-er, is the RF file the lead used, and whether the lead used raw or `chocomufin` XML.

## 8. Process record

- **Pre-registration** (`PREREG_LOG.txt`):
  - `prep.py`, `r1.py` and `r2.py` were hashed at 2026-10-17 22:29:02 PDT, before running.
  - One amendment, before any R1/R2 run: the page regex missed page `fRos`, so prep.py was fixed and re-hashed (288930c3...).
  - Final hashes: r1.py b0fb86ea..., r2.py 2bfe9279...
  - Both result files print "stub match: YES". corpora.json is b492cab1...
  - `explore_r2.py` was written and hashed after the results and is labelled post-hoc.
- **Contact with the lead:** after the results were filed, I read routing messages in `<team-comms>` to find the lead's address. These were voynich-08's registration (no R1/R2 numbers), the steward's acknowledgement and the steward's Fable routing handoff. I then exchanged check-in messages with voynich-08 (`20261018T092718Z-roach-voynich91-replication-checkin.md`, reply `<team-comms>`). The reply contained no R1/R2 lead values.
- **Files:** `results_r1.txt`, `results_r2.txt`, `explore_r2.txt`, `prep_log.txt`, `PREREG_LOG.txt`, `scripts/` and `CREMMA_used_manifest.sha256`, all in `<home>/voynich-replication/`.
