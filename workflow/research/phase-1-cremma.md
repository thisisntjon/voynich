# Phase 1 s18 investigation — CREMMA Medii Aevi as the real-line control

Stamped 2026-10-17 20:00 PDT (from `date`). Read-only; nothing downloaded into the project. Evidence: GitHub tree/compare/release APIs via `gh`, raw fetches of 3 ALTO files (scratchpad only, read with `python -I`), the JOHD data paper (doi 10.5334/johd.97), Zenodo API, RN-Top PR #5 files at head 59bd149.

## 1. Repository layout and XML format

- Repo: https://github.com/HTR-United/CREMMA-Medieval-LAT (redirect target of htr-united/cremma-medieval-lat), default branch `main`, head 2925259 (2024-07-12). Releases: v0.1.2 (tag commit 9439fe3, 2023-10-04), 0.1.1, 0.1.0, 0.0.1a. `compare/v0.1.2...main` = 1 commit, only `README.md` changed; the 242 XML paths and byte sizes are identical in both trees (checked).
- Tree (recursive, not truncated, 662 blobs): 242 `.xml`, 121 `.txt`, 227 images (jpg/jpeg/png), plus root files `README.md`, `data-registry.csv` (per-manuscript metadata), `table.csv` (chocomufin character-normalisation table), `htr-united.yml`, `compiletxt.py`, `datapaper.pdf/.tex`, `CITATION.cff`, `JunicodeTwoBeta.ttf`.
- `data/<Manuscript>/` holds one page = one triplet `<page>.xml` (eScriptorium ALTO export), `<page>.chocomufin.xml` (same text after `chocomufin -n NFD convert table.csv`), `<page>.jpg`, `<page>.txt` (one CONTENT line per physical line, compiled by `compiletxt.py`). So the "242 XML files" are **121 pages x 2 variants**: plain 121 files / 6,952,796 B; chocomufin 121 files / 5,375,487 B; the 121 `.txt` are 376,823 B in total.
- Format: **ALTO v4** (`xmlns="http://www.loc.gov/standards/alto/ns-v4#"`), schema alto-4-2. Structure per file: `Description` > `Tags` (`OtherTag` ids for SegmOnto block types MainZone, RunningTitleZone, DropCapitalZone, NumberingZone, QuireMarksZone and line types DefaultLine, HeadingLine, DropCapitalLine) > `Layout/Page/PrintSpace` > `TextBlock TAGREFS=BTnnn` > `TextLine TAGREFS=LTnnn BASELINE=…` > exactly **one `String CONTENT="…"` per TextLine** (whole line as one attribute; no `SP`, no `HYP`, no word-level `String`). The large file sizes are polygon coordinates.
- Region boundaries: `TextBlock` = SegmOnto zone (a column is a MainZone; Arras-861 056r has MainZone, RunningTitleZone, MainZone = two columns of 35+35 lines; Latin8236 f142 has 3 blocks with 44 lines). **Paragraph boundaries are not marked**: no paragraph element, no line type for paragraph-first/last lines; only HeadingLine/DropCapitalLine types (README line table: 59 HeadingLine, 1 DropCapitalLine in the whole corpus) and in-text `¶`/`⁋` characters (in the character inventory of `htr-united.yml`). Tag ids differ per file (BT2715 vs BT1941), so parse by LABEL not by id.
- Lines per manuscript (README "Lines count", total 7,274 = yml volume): Arras-861 358, BGO-511 56, BIS-193 889, CCCC-MSS-165 151, CCCC-MSS-236 192, CLM13027 616, Egerton821 114, H318 427, Latin16195 449, Latin6395 681, Latin8236 214, LaurPlut33.31 204, LaurPlut39.34 135, LaurPlut53.08 245, LaurPlut53.09 158, Mazarine915 528, PalLat373 453, Phi_10a135 142, SBB_PK_Hdschr25 237, UBL758 570, WettF0015 455. 441 regions, 263,222 characters.
- Sample files: Arras-861/056r.xml: 71 lines, 475 space-split tokens, 156 combining marks; Latin8236/f142.xml: 44 lines, 293 tokens, 2 combining marks (humanist hand, nearly unabbreviated, verse: one hexameter per line). Plain vs chocomufin CONTENT differ on 41/71 Arras lines but only in character normalisation (e.g. `eᷤ` -> `eᷤᷤ`: `table.csv` maps COMBINING SMALL S to a doubled mark, which looks like a table bug); token counts 475 vs 474 (one spacing change).

## 2. Per-manuscript metadata (data-registry.csv + README + data paper Table 6/9)

Dates are notBefore–notAfter from `data-registry.csv` (the README/paper give the same at century level, except LaurPlut33.31: registry 1330–1340, paper 1300–1310). Words = data paper Table 9 (space-delimited words of the transcription). Text type from the "Content" column plus my identification of the work; column count is **unverified** for every manuscript (the paper only says "two kinds of layout: multi-columns and singular columns … lines are most often long, except for the Psalms and Book of Hours"); it can be read off at parse time as the number of MainZone TextBlocks per page.

| Folder | Date | Script | Genre | Work | Prose/verse | Words | Lines |
|---|---|---|---|---|---|---|---|
| Egerton821 | 1100–1199 | Praegothica | Medic. | Sortes sanctorum, charms | prose | 981 | 114 |
| H318 | 1100–1299 | Semitextualis Libraria | Medic. | De urinis, recipes, De coitu | prose | 4,456 | 427 |
| CCCC-MSS-236 | 1200–1225 | Textualis Libraria | Lit. | Martial, Epigrams I | verse | 1,239 | 192 |
| CLM13027 | 1250–1299 | S. Textualis Libraria | Medic. | Liber minor de coitu; Galen | prose | 6,499 | 616 |
| Latin16195 | 1250–1299 | Semitextualis Currens | Medic. | Questiones de coitu | prose | 4,135 | 449 |
| WettF0015 | 1270–1280 | Textualis Libraria | Schol. | Rothwell, Sentences comm. | prose | 3,574 | 455 |
| LaurentianusPluteus33.31 | 1330–1340 | Textualis Meridionalis | Lit. | Priapea 12–45 (Boccaccio's hand) | verse | 1,278 | 204 |
| Arras-861 | 1300–1399 | Textualis Formata | Lit. | Seneca, Ad Lucilium 121–122 | prose, 2 cols (sample) | 2,416 | 358 |
| BIS-193 | 1300–1399 | Textualis currens | Schol. | Wodeham, Ordinatio IV | prose | 7,370 | 889 |
| Phi_10a135 | 1300–1399 | Cursiva recentior | Medic. | Tractatus de sterilitate | prose | 1,487 | 142 |
| Mazarine915 | 1300–1399 | Textualis Meridionalis | Schol. | Wodeham, Ordinatio | prose | 4,751 | 528 |
| UBL758 | 1320–1340 | Textualis Libraria | Eccl. | In annuntiatione Mariae (sermon) | prose | 4,468 | 570 |
| Latin6395 | 1325–1399 | Semitextualis Libraria | Lit. | Seneca, Medea 284– | verse | 3,304 | 681 |
| LaurentianusPluteus39.34 | **1400–1499** | Humanistica Cursiva | Lit. | Priapea 1–16 | verse | 783 | 135 |
| PalLat373 | **1400–1499** | Hybrida Currens | Schol. | Plaoul, De fide, lect. 1–2 | prose | 2,258 | 453 |
| LaurentianusPluteus53.08 | **1459** | Personal Humanistica | Gramm. | Donatus, In Phormionem | prose | 2,985 | 245 |
| LaurentianusPluteus53.09 | **1400–1499** | Humanistica Rotunda | Gramm. | Donatus, In Phormionem | prose | 1,300 | 158 |
| SBB_PK_Hdschr25 | **1400–1499** | Textualis Formata | Eccl. | Book of Hours (Bruges) | liturgical, short lines | 961 | 237 |
| BGO-511 | **1400–1499** | Hybrida formata | Eccl. | Psalm 6 (Latin psalm in a German ms) | psalm, short lines | 171 | 56 |
| Latin8236 | **1471–1499** | Humanistica Cursiva | Lit. | Prudentius; Tibullus | verse (1 line = 1 verse) | 1,475 | 214 |
| CCCC-MSS-165 | 1500–1599 | Personal Cursive | Schol. | Abelard, Sic et non | prose | 1,521 | 151 |

- **1400–1500 at all:** 7 manuscripts (the bold rows): 9,933 words, 1,498 lines in total.
- **prose15 candidates** (15th-century, prose, running text): **PalLat373, LaurentianusPluteus53.08, LaurentianusPluteus53.09** = 6,543 words / 856 lines pooled. This clears the stub's ">=5k tokens pooled" bar but no single prose15 manuscript reaches 5k. Single-column status of the three is unverified (PalLat373 at 453 lines on 4 pages = ~113 lines/page strongly suggests two columns; the Donatus commentaries at ~40–60 lines/page could be either).
- **Kill rule as written** ("≥3 manuscripts with ≥5k tokens each") **fails on this corpus whatever the parser does**: only CLM13027 (6,499) and BIS-193 (7,370) exceed 5k words; next are Mazarine915 4,751, UBL758 4,468, H318 4,456, Latin16195 4,135. The whole corpus is 57,412 words (Table 7). The rule needs rewording before the pre-registration is frozen (see Decisions).
- Verse manuscripts to exclude from prose rows: CCCC-MSS-236, LaurPlut33.31, Latin6395, LaurPlut39.34, Latin8236; short-line liturgical: SBB_PK_Hdschr25, BGO-511. My prose/verse assignments come from the named works (Priapea, Martial, Medea, Prudentius, Tibullus are verse), not from the paper, which does not state them: unverified against the images.
- HTR-United catalog page (https://htr-united.github.io/catalog.html) is JavaScript-rendered and returned no entry text; `htr-united.yml` in the repo is its source: format Alto-XML, time 1100–1599, language lat, 1 hand per folder, **licence CC-BY 4.0** in the yml vs CC0 in the data paper vs "other-open" on Zenodo (conflict; record it in `data/external/README.md`).

## 3. Transcription conventions and token-count hazards

- Graphematic: abbreviations **not resolved**; abbreviation signs kept as MUFI/Unicode characters (ꝑ ꝓ ꝙ ꝗ ꝯ ꝰ ⁊ ꝵ ꝭ ẜ ħ ł đ and NFD combining marks U+0303 tilde, U+033E vertical tilde, U+1DD1 ur, U+0363–U+036F superscript letters, U+0335 stroke, PUA U+F1AC "abbreviation sign semicolon"). yml: "ligatures are reduced to their component letters … spaces between letters reproduce the original (e.g. in the case of a semicontinuous script)". Paper: no u/v or i/j normalisation.
- Punctuation simplified: two-part signs -> `:`; single punctus -> `.`; also `,` `;` `/` `¶` `⁋`. Punctuation is **attached to words without spaces** in the samples (`facit.aliud`, `ꝑtinet.aliud`): a naive `split()` undercounts; strip `.:;,` before tokenising.
- Line-end hyphenation: paper says marked with `-` (U+002D); `table.csv` also folds `_` and en dash to `-`. In the 3 sample files 0/159 lines end in `-` (the Arras lines break mid-word with no sign: `mor|tale`, `ex̾cendũ`), so broken words at line ends are mostly **unmarked**; a line-final token is often a word fragment. Count of `-` across the corpus unverified until fetched.
- No confidence field: no `WC`, no `CC`, no `SP`/`HYP` elements (checked in all 3 files; the schema allows them but eScriptorium ground-truth exports omit them).
- `&` is XML-escaped (`&amp;`), parse with an XML parser, not regex. Capitals are kept (sentence/verse initials). Digits, `℥`, `=`, `+`, `^`, `*`, `'` occur (yml inventory). The chocomufin variant doubles some combining marks (table bug), so character-level metrics must pick one variant and say which.
- Heading/drop-capital lines carry TAGREFS to HeadingLine/DropCapitalLine; running titles and quire marks are separate TextBlocks (RunningTitleZone, QuireMarksZone, NumberingZone) and must be dropped from the line stream.

## 4. Cheapest faithful fetch (scope: official release, XML only, no images, hard stop 200 MB)

| Option | Content | Bytes | Verdict |
|---|---|---|---|
| (b) Zenodo 10.5281/zenodo.7013436 -> latest 8407213 (v0.1.2, 2023-10-04) | one file `HTR-United/CREMMA-Medieval-LAT-v0.1.2.zip` (whole repo incl. images) | **356,673,369** | over the 200 MB stop; no per-file access |
| GitHub zipball/tarball of tag v0.1.2 | whole repo | ~355 MB (repo size 355,198 KB) | same |
| (c) `git clone --filter=blob:none --sparse` + non-cone sparse-checkout `data/*/*.xml` | 242 XML blobs + commits/trees (small) | ~12.3 MB blobs + a few hundred KB metadata; `.git` keeps the blob pack (~x2 on disk) | works, but git on Windows with a 50-char filename containing commas and spaces (PalLat373) and the repo's history in `.git`; needs cleanup |
| (a) tree API at tag sha 9439fe3 + raw per-file at `v0.1.2` | 242 XML (or 121 plain XML, or 121 txt) | 12,328,283 B all XML; 6,952,796 B plain XML only; 376,823 B txt only | **recommended**: pinned to the release commit, exact size known before download, no images, no git state |

Recommended commands (PowerShell, from the project root; `tools/fetch_cremma.py` (as built; the proposed .ps1 was never kept), script outside `data/external/`):

```
$sha = "9439fe33a07eeb2814fa4b94b65c280f20aa6ec1"   # tag v0.1.2 == main for data/
gh api "repos/HTR-United/CREMMA-Medieval-LAT/git/trees/$sha?recursive=1" > data\external\cremma\tree_v0.1.2.json
# size check (expect 12,328,283 for */*.xml; abort if > 200_000_000), then for each path:
curl.exe -sSL "https://raw.githubusercontent.com/HTR-United/CREMMA-Medieval-LAT/v0.1.2/<path>" -o "data\external\cremma\<path>"
```
also fetch `README.md`, `data-registry.csv`, `table.csv`, `htr-united.yml`, `CITATION.cff` (~30 KB) for provenance, and write the per-file sha256 (the tree API gives git blob SHA-1s: `sha1("blob <size>\0"+bytes)`, which lets the fetch be verified without a second download). Expected byte count: **12,328,283 B** for all 242 XML, 12.36 MB with the five metadata files. If only one variant is wanted, the plain `.xml` (6,952,796 B) is the eScriptorium export; the chocomufin variant is derived from it by `table.csv`.

## 5. RN-Top/Voynich PR #5 method (LLM-generated, unreviewed)

PR merged 2026-10-01T04:42Z, head 59bd149, body ends "Generated with Claude Code"; every commit "Co-Authored-By: Claude Opus 5.5". Files: `analyses/m_abbreviation_prereg.md`, `analyses/m_abbreviation_test.py`, `analyses/comparison_fingerprint.py`, `output/*`, `parser.py` (+1 line). Text: `data/ZL3b-n.txt` (IVTFF, voynich.nu ZL3b-n via matthewdgreen/cipher_benchmark mirror), `parse_zl3b()` one row per token, reading = first alternative of `[a:b]`, `,` (uncertain space) treated as a word break, `clean` = EVA token; restricted to **locus type P** (`,@P` in the locus header) and lines with ≥2 tokens. Lines keyed by `(folio, header)`.

- **8.5 % vs 16.1 %** (`m_abbreviation_test.py` P2): `is_para_end` = the IVTFF line text contains `<$>` (paragraph end marker). `m_final` = `structural_validation.ending_of(last token) in {"am","m"}` where `ending_of` returns "am" if the token ends in `am`, "m" if it ends in `m` but not `im`/`am`. Statistic = mean(m_final | para_end) − mean(m_final | not para_end) over lines: 729 paragraph-final lines (8.5 %) vs 3,375 other lines (16.1 %). Null: shuffle the para_end flag among lines **within each folio**, 10,000 permutations, seed 20261001; two-sided p = (#|null−mean| ≥ |obs−mean| + 1)/(N+1) = 0.0001. Decision rule pre-registered in commit c2443e6; P1 (m-final lines fuller than folio median) failed p = 0.38; P3 (line-final −0.36 glyphs vs stem's mid-line forms) p = 0.0001.
- **OR 22.9 native vs 1.8 re-lined** (`comparison_fingerprint.py`, exploratory, generic pipeline): tokens lower-cased; `ending(w)` = last 2 letters if len > 2 else the word; for every line with ≥2 tokens the last token goes to `end`, all other tokens (including line-initial) to `mid`. For each ending e with end+mid ≥ 30: **OR = ((end_e+0.5)/(end_tot−end_e+0.5)) / ((mid_e+0.5)/(mid_tot−mid_e+0.5))** (Haldane-corrected odds of ending e at line-final vs non-final). Reported value = **the maximum OR over all endings** and its ending (native: `am` 22.9; re-lined: `ld` 1.8; shuffled words in native line lengths: `d` 2.2; Latin Apicius/Albertanus/Bede re-lined: 2.8/2.1/1.7). No p-value. Note the max-over-endings is a selection statistic, and `am` as a 2-letter ending counts `dam`, `kam` … but not bare `-m`.
- **Re-lining**: `widths` = for each native line (≥2 tokens) the character width `sum(len(w)) + len(line) − 1`; `reflow(words, widths, rng)` walks the P-locus tokens in corpus order, draws a target width for each new line with replacement from `widths` (`np.random.default_rng(20261001)`), greedy-fills until adding the next word (+1 space) would exceed the target, then starts a new line (first word always placed). The same word sequence, so word statistics are identical and only line positions move. The fingerprint word measures are capped at 35,000 tokens; `line_end_effect` uses all lines.
- To reproduce on ZL3b in s17: same P-locus filter, `<$>` paragraph flag, folio-stratified permutation for P2; for the OR use the formula above on 2-letter endings and report both the `am`-specific OR and the max; re-line with the width-sampling rule above and a stated seed. Their count of 38,958 tokens (all locus types) and 4,104 line-final tokens in P lines are the checkpoints.

## Decisions needed before s18

1. **Kill rule rewording**: "≥3 manuscripts with ≥5k tokens each" is unreachable (2 manuscripts qualify, max 7,370 words). Options: ≥3 prose manuscripts with ≥2k tokens plus a pooled prose15 row ≥5k (6,543 available), or keep the rule and record U1 as unverified now.
2. **prose15 definition**: accept PalLat373 + LaurPlut53.08 + LaurPlut53.09 as the pooled prose15 row (6.5k words, ~856 lines) given that single-column status is unverified, or require single-column by MainZone count and risk dropping PalLat373 (then 4.3k words, below the bar).
3. **Paragraph marks**: ALTO has none; choose a proxy for paragraph-initial lines (pilcrow `¶`/`⁋` in the line, capital after `.`, HeadingLine/DropCapitalLine, first line of a MainZone) or run the edge metrics without the paragraph split and say so.
4. **Which XML variant and which token rule**: plain `.xml` (recommended) vs `.chocomufin.xml`; tokeniser = split on whitespace after stripping `.:;,` and keeping combining marks attached; treat unmarked line-end word breaks as tokens (they are, for the layout question) and record how many lines end in `-`.
5. **Fetch**: approve option (a) raw-per-file at tag v0.1.2 (12.33 MB) with git-blob SHA-1 verification, into `data/external/cremma/`, logged with the licence conflict (CC-BY 4.0 yml / CC0 paper / other-open Zenodo).
