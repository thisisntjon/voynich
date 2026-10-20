# Audit: explorediscussion.txt (external chat transcript)

Stamp: Mon Oct 19 00:02:44 PDT 2026 (from `date`). This is a read-only audit. This report is the only file written, and nothing is filed to the graph.
Input: `explorediscussion.txt` (4,893 lines), read in line ranges. Our records: FINDINGS-MAP/GRAPH, D-066, LEARNINGS, CLAIMS, research_notes, `data/external/intake-phase1/`, and VKB (`tokens`, `loci`, `folios`, `quires`, `sources`, `external_items`), all on ZL3b unless stated. Web: two searches (Greshko disclaimer, Tucker/O'Neill).

## Verdict (top)

1. The closing claim (L4805-4890) is not supported: "almost certainly" a table-based verbose homophonic cipher over abbreviated 15th-c. Southern German/Latin, with labels as table coordinates.
2. Our own tests count against it. H-03 (verbose homophonic) is *disfavoured as built*, and H-04 (Naibbe, per word) is *excluded at default settings* (F-24, F-25, L-006, L-159).
3. Period ciphers over real Latin, Venetian and southern German recipe text fail 0/12 cells (F-45, s102). Spec-built verbose table encodings fail 0/9 (F-47, s104).
4. Greshko himself disclaims it. He does not assert that Naibbe is how the MS was made, or even that the MS is a ciphertext, and he says the cipher "fails in several major ways" (web, Wild Hunt and press, quoted secondhand). The main text is not on disk (VKB `fake-greshko-2025-pdf`).
5. Brewer & Lewis 2024 is real (SHM 37(3):559-582, Crossref-verified in BREWER-LEWIS-CHECK.md). It is a history and iconography paper, though. It gives a motive (Hartlieb's call for "secret letters"), not a mechanism, and Hartlieb's call is from the 1450s, after the vellum window.
6. The "labels as coordinates" evidence is mostly fabricated. Most EVA tokens the transcript quotes for f84r, f73v, f68r1, f78r, f88r and f100r are not in ZL3b (table B).
7. The "otedy otedy" adjacent pairs (f84r Arch 4, f73v nymphs) do not exist in ZL3b. Corpus-wide, `otedy otedy` occurs once.
8. Its zodiac anchors are wrong. f73v's month is *decebre*, not "Novembr". f72r3 is Cancer, not Leo, and f72v1 is Libra, not Virgo.
9. The parts that stand are standard background. Vellum C-14 is 1404-1438. Labels lack qo-. Currier A = hand 1. Top-word frequencies are roughly right. Zipf is uninformative.
10. Net: the transcript is a fluent mix of real background, confabulated transcriptions and overclaimed synthesis. Nothing in it moves the scoreboard.

**Five most important errors or overclaims**

1. **Fabricated EVA readings used as evidence.** These include f84r "otedy otedy", "otolor", "otokcho" and "dail or chy"; f73v "otaly/otedy/otedy" atop the wheel; the f68r1 Sun/Moon both "oky" and "okeody ×3"; the f78r lane stacks dly/oly, daly/dal, daldy; and the f100r okechol→qokechol. ZL3b has none of these at those loci (table B). The "labels are table coordinates" conclusion (L4332-4344, L4879-4880) rests on them.
2. **"Naibbe proves the mechanism"** (L2290 fact 32, L3587, L4875). Our rebuild from Greshko's own tables gives an orderless prefix stream (F-24, s64/s81/s85, 0/15 LOQO). Its h2 matches, but it misses the line-edge and coupling profile (L-006) and the repeat rate. Greshko disclaims the claim.
3. **"Brewer & Lewis proved Bavarian physicians mandated gynaecological ciphers, and the Rosettes = seven-chambered uterus"** (L67-71, L131, L3620). The paper's abstract claims a culture of self-censorship around Hartlieb (c.1410-68) and proposes the Rosettes as coitus and conception. It makes no claim about the Voynich text, its mechanism or its language. The full text is unread (paywall).
4. **Material and provenance overstatements.** "Ink applied when the parchment was fresh" and "pigments authentic": McCrone reports only "consistent with" and finds the text and drawing inks "most likely created contemporaneously". Zandbergen calls the 2009 fresh-ink statement incorrect. C-14 dates the skin, not the writing. The f1r erased columns are given as a 15th-c. decryption key, but Davis 2024 and Zandbergen attribute them to Marci, 1660s. f116v and f66r are read as clean German, where Davis's own draft calls f116v "pseudo-Germanic" and possibly late 15th c., and the f66r "mus/del" is a forum reading.
5. **Structural claims stated as proven but contradicted or untested by us.** "Labels encode states / humoral degrees": the zodiac positional crib is closed (L-152, z=−1.4), and F-28 finds no zodiac order. The "pharma labels match herbal title words / internal pointers" claim: F-20, no internal crib (s53/s54, control 13/13). "Root shape tracks label suffix", "o- top / d- bottom" and "9-slot line columns" are untested and built on fabricated tokens.

## A. Claims, line ranges, class and verdict

Class: H = historical fact, S = statistical claim about the text, I = interpretation, C = citation. Ids: F-/H-/L-/c- refer to our registers.

| # | Lines | Claim (deduplicated) | Class | Verdict |
|---|---|---|---|---|
| 1 | 7, 104, 1915-1920 | Zipf's law shows language; hoaxes also pass it | S | SUPPORTED-BY-OUR-DATA for "Zipf is non-diagnostic" (L-046: Markov-1 pseudo-text fits Zipf R² 0.99) |
| 2 | 46-65, 1903-1914 | Conditional character entropy h2 ≈ 2 bits vs 3.3-4 for European languages | S | SUPPORTED-BY-OUR-DATA (h2 2.11 ZL3b, L-074; Latin 3.295, L-089). "Sukhotin, Schinner 2007, Bowern & Lindemann 2021" are real. "Giampaolo Bennett 1976" is FACTUALLY-WRONG: the author is William Ralph Bennett (1976 book); name from memory, unverified |
| 3 | 49, 54 | "Proves it cannot be simple 1:1 substitution of a European language" | I | SUPPORTED-BY-OUR-DATA in direction (L-002, F-35, F-45) |
| 4 | 54, 85, 1897-1902 | Currier A/B (1970s) are distinct profiles; Scribe 1 = A only, Scribes 2-5 = B | S/H | Mostly SUPPORTED (F-16, L-138: hand 1 = A, hands 2-3 = B). Hand 4 pages (astro/zodiac) carry no Currier tag in VKB `folios`, so "2-5 all B" is overstated. Davis's assignments themselves are X-08 (unverified) |
| 5 | 48, 76, 1887 | Davis 2020 (*Manuscript Studies* 5.1) "proved" ≥5 scribes | C/H | CITATION real (VKB `physi-davis-s-5-scribe-assignments`, PDF on disk). "Proved" overstates: X-08 is unverified by us. ZL3b $H pages 113/46/33/27/7 |
| 6 | 1898 (fact 17) | Scribes 1 and 2 alternate within Quires 4 and 7 and share bifolios | H | UNTESTED-BY-US (not checked against $H; unverified) |
| 7 | 42, 1863, 1881 | 2009 Arizona AMS: four samples (f8, f26, f47, f68), 1404-1438 at 95% | H/C | SUPPORTED (physical_provenance.md Q1; hodgins-2009.pdf on disk). The transcript's "the parchment is 100% early 15th c." is fine, but the test dates skin, not writing |
| 8 | 9, 44-45, 1866-1870, 1880 | McCrone: inks and pigments "authentic"; ink applied to fresh parchment; codicologists "confirmed" no aged-skin writing | H/C | FACTUALLY-WRONG as phrased. McCrone (MA47613, 1 Apr 2009) says text and drawing inks are iron-gall and "most likely created contemporaneously", and materials are "consistent with" the period. Nothing shows ink on fresh skin; Zandbergen calls the 2009 press statement incorrect (physical_codicology.md, physical_provenance.md). Titanium-compound particles appear on f70v and f1r in McCrone Table I, and the transcript's "zero titanium" is not what the table says. Egg glair: McCrone says "possibly eggwhite" for one sample |
| 9 | 1864, 1870 | ZooMS/peptide proved calfskin (Yale 2014-16) | H | Partly SUPPORTED: York 2014 protein analysis found calf (via Zandbergen; primary unread, unverified). The attribution to "Zyats & Yale" is CITATION-UNVERIFIED |
| 10 | 1865, 1871, 404 | 14-15 calves; "second-grade utility vellum"; stitched tears pre-date text | H | UNTESTED-BY-US (unverified; the calf count is not in our notes) |
| 11 | 47, 1897 | Layfield & Davis 2026 (*Digital Medievalist*): singulions mis-nested at binding | C | CITATION real (DOI resolves, bigpicture-historical.md; PDF on disk). Our F-51 agrees in direction only. "Proved", and "the quire numbers were written after mis-nesting" (113), are unverified |
| 12 | 371-379, 1891-1892 | 116 folios, 14 missing (12, 59-64, 74, 91-92, 97-98, 109-110); 20 quires; "Quires 12 and 16 completely missing" | H | Missing folios SUPPORTED (VKB `quires`). FACTUALLY-WRONG on quires: VKB quire L (12) holds f73. The wholly absent quires are P and R (16 and 18; f91-92, f97-98) |
| 13 | 375-377 | ~37,900 tokens, ~170,000 glyphs, 8,105 types, ~5,400 hapax | S | Roughly SUPPORTED. ZL3b gives 39,020 tokens, 8,295 types, 5,796 hapax and 194,646 EVA chars. Figures depend on the transliteration |
| 14 | 2620-2640 | Top-15 word counts (daiin 863, ol 537, chedy 501 ...) | S | Roughly SUPPORTED. ZL3b: daiin 848, ol 561, chedy 507, aiin 504, shedy 434. The order differs after rank 5 (ar 402, s 350 omitted) |
| 15 | 2645-2675 | Three seed families make up ~80% of tokens; all words are within edit 1-2 of daiin, ol or chedy | S | UNTESTED-BY-US as stated (unverified). Related: F-13, F-22 |
| 16 | 1478 | d is 8.5-9.5% of glyphs; dd < 0.05% | S | d share: CONTRADICTED-BY-OUR-DATA (ZL3b 6.8% of EVA chars). dd: SUPPORTED (25 tokens contain dd) |
| 17 | 55, 1904, 3559 | Line as a functional unit; line-initial and line-final vocab; no hyphenation | S | SUPPORTED-BY-OUR-DATA (F-01, F-02, F-04, TRIANGULATED) |
| 18 | 56, 1906, 3582 | Rigid prefix-core-suffix slot grammar (Stolfi 2000) | S | SUPPORTED (F-11; X-01 at-risk) |
| 19 | 1658-1690, 1905, 3563 | Plant-interruption "reset": the word after `<->` takes gallows, line-start forms | S | Partly CONTRADICTED. L-156/s35: a drawing gap is a *weak* edge; post-drawing o/y/d/s are enriched, but gallows stay at mid-line rates. F-18 |
| 20 | 1716-1745 | Leaves on a herbal page split words (ol+dy, d+ees) | S | UNTESTED-BY-US. Folio unnamed; unverified. F-19 says the word unit is physical |
| 21 | 870-890, 1907 | Paragraph-initial gallows are a marker; stripping them leaves a valid word >75% of the time | S | UNTESTED-BY-US (F-02 covers paragraph gallows as a line-start effect; the 75% figure is unverified) |
| 22 | 491-495, 1908, 3555 | qo- ~13% of B paragraph words, near zero in labels; labels are o- forms | S | SUPPORTED for qo-: ZL3b labels 10/1199 (0.8%); B paragraphs 4082/23182 (17.6%); L-033, L-084. The "o- enrichment is real" part is CONTESTED: a frequency-matched test gives OR 1.29, p 0.93 (F-43 data line, s109) |
| 23 | 491-495, 4333-4344 | qo- is a case marker; o- is the nominative or label column | I | UNTESTED-BY-US (no meaning test; F-15 says the prefix is chosen jointly with the core) |
| 24 | 1909, 2270 | Adjacent repeats and minimal pairs are "orders of magnitude" above prose (Schinner 2007; Timm & Schinner) | S/C | SUPPORTED in direction (F-13; L-083: repeats 0.896% vs 0-0.16%). Citations real (Greshko supplement bibliography lists both) |
| 25 | 1131-1150, 1910, 3598 | LDA/TF-IDF clusters vocabulary by section (Montemurro & Zanette 2013; "Sterneck ACL 2021") | S/C | Partly SUPPORTED: F-07 (Hand-1 section vocabulary at the permutation floor). L-029 shows hand-2 topic signal is not separable from quire drift. "Sterneck et al., ACL 2021" is CITATION-UNVERIFIED (an arXiv 2021 topic-model paper by Sterneck, Polish & Bowern exists; venue unverified) |
| 26 | 1146-1150, 3598, 4855 | Starred recipes blend Herbal and Bath vocabulary | S | UNTESTED-BY-US (no run found; see section C) |
| 27 | 1085-1090, 1912, 3546 | Pharma root labels match unique herbal-page words (internal pointers) | S | CONTRADICTED-BY-OUR-DATA: F-20 (s53, s54; planted link recovered 13/13; db-s114 null), L-140, L-149 |
| 28 | 1100-1110 | Plant colour vs vocabulary correlation is zero | S | Consistent with F-33 (no core-picture link; only strong links excluded). Colour itself is UNTESTED-BY-US |
| 29 | 1090-1095 | First word on herbal pages is unique ("title") | S | UNTESTED-BY-US (unverified) |
| 30 | 2000-2060 | ~9-10 words per full line; each line is a ~9-step cycle | S | Mean words per line 8.49 (ZL3b P loci): roughly right. The "9-slot cycle" is UNTESTED; F-04 (rhythm) covers the line structure |
| 31 | 2090-2140 | f88r is Currier A, Scribe 1 | H | SUPPORTED (VKB `folios`: f88r hand 1, A) |
| 32 | 2010-2060, 2120-2130 | f88r paragraph text ("pchedy okeody daiin pchey koldy ..."; "qokol chol okol cheey chody cheol daiin okeoly daiin chey") and root labels (oald, alody, choky, okchody, qokold ...) | S | FACTUALLY-WRONG. ZL3b f88r P lines and labels differ entirely (labels: otorchety, osal, orald, oldar, otoky, otaly ...) |
| 33 | 2150-2270 | f100r label grid (kolold, chold, saralol, qokeechedy, qokchedy, dchdy, daldy, okechol, qokechol, dalkar) | S | FACTUALLY-WRONG. ZL3b f100r labels: chosaroshol, sochorcfhy, otear, chofary, ... okols. `qokechol` occurs 0 times in the corpus and `okechol` once (f104r P) |
| 34 | 423-475 | f84r canopy labels (otolor, or shekar, qokdy, otedy loly, dail or chy, otedy otedy, otokcho, otaly, dchedy); "otedy 17× in the page paragraphs" | S | Mostly FACTUALLY-WRONG. ZL3b f84r L: ololal, or.shekar, ydy, okedy, loly, doiir, olshy, otedy, lkol, okolshy, otoly, dshedy, otaly. otedy is 1 label + 6 paragraph tokens. No otedy otedy pair |
| 35 | 580-620, 3849 | f73v nymph labels (otaly, otedy, otedy at the top; okedy, okeey, otar ...) and inner ring text | S | FACTUALLY-WRONG. ZL3b f73v L includes otedy once and oky once, with no otaly and no adjacent duplicate. The ring texts (f73v.5/.22/.33) do not match |
| 36 | 3275-3380 | f68r1: Sun and Moon both open with "oky"; okeody ×3; otaly; okor | S | Mostly FACTUALLY-WRONG. ZL3b f68r1 has one circular text "oky okchdy okardy ..." and 29 labels with no okeody, otaly or okor |
| 37 | 3972-4082, 4341 | f78r lane stacks dly/oly, daly/dal, daldy/qokld between the pipes | S | FACTUALLY-WRONG. ZL3b f78r labels: okchdldlo, okchdy, dar aloifhy, dchedaly, otarodlay orory, okaral. dal and oly occur only inside paragraph lines; dly is not on f78r (f28r, f75v) |
| 38 | 3445-3492 | f70v: 29 labels, zero qo-, >80% o-initial | S | Direction SUPPORTED (ZL3b f70v1/f70v2 labels are almost all ot-/ok-, with no qo-). The listed tokens are only partly real |
| 39 | 3726-3790 | f72r3 is Leo/"Agost"; f72v1 is Virgo/"Septembr"; their ring texts | H/S | FACTUALLY-WRONG. f72r3 is Cancer (iollet) and f72v1 is Libra (octe(m)bre) (zodiac_months.md, after Zandbergen). Ring texts do not match ZL3b |
| 40 | 101-102, 560-570, 3452, 3825 | Month names in "Franco-Provençal/Alpine": Mars ... Novembr, Decembr; f73v reads "Novembr" | H | FACTUALLY-WRONG. f73v reads decebre (one Stolfi file reads "possibly oct", unverified). The spellings are aberil, jong, iollet, augst, octembre ... The language is Northern French or Occitan (Zandbergen; Pelling), and the hand is a later one |
| 41 | 103, 1889, 3539 | f1r MSI reveals a 15th-c. owner's cipher-key attempt | H | FACTUALLY-WRONG per our notes. Davis 2024 (Zandbergen agreeing) attributes the hand to Marci, 1662-65; it is "not in any obvious order" (multispectral_marginalia.md) |
| 42 | 101, 2780-2830, 4365 | f116v: "pox leber ... anchiton oladabas ... six marix morix ... oror sheey valsch vbren so nim gas mich o"; written in the main scribes' ink; "100% proves" a native MHG writer | H | Readings partly SUPPORTED: Davis's Jan 2026 draft has pox leber, anchiton oladabas, ma+ria, oror sheey ... so nim gas mich, but she calls it "pseudo-Germanic" and possibly late 15th c. The ink matching the scribes is unverified (McCrone sample 16 is iron-gall only). "100% proves" is overclaim. f116v is hand 3 in ZL3b $H |
| 43 | 2990-3030, 3535, 4362 | f66r labels in German: "mus", "del/oel" | H | CITATION-UNVERIFIED: only a forum reading "und den muss des" (multispectral_marginalia.md; f66r was not imaged) |
| 44 | 104 | f17r margin in German, "mal/mar" | H | Partly: Davis's draft reads "Mallier aller ... otaiol oim"; Pelling reads it as Occitan. Language disputed |
| 45 | 46, 94-97, 1913 | Swallowtail merlons restrict origin to N. Italy c.1420 | H | UNTESTED-BY-US (secondary; unverified) |
| 46 | 108, 3801-3823 | Crossbow Sagittarius = S. German/Bohemian convention; costume dates to 1410-1440 | H | UNTESTED-BY-US (unverified art-historical claims) |
| 47 | 117, 1924 | 1599 payment of 600 florins to Widemann | H/C | SUPPORTED as a candidate only. Guzy 2022 (on disk) says it "seems to present a way" and does not identify the MS |
| 48 | 76, 1925-1930 | Tepenecz on f1r; Baresch 1639; Marci letter 1665; Beckx; Voynich 1912; Kraus 1961/1969; Newbold/Manly | H | SUPPORTED where our notes cover them (bigpicture-historical.md; neal-marci-1665 dateline 19 Aug 1665). The Kraus prices are unverified |
| 49 | 7 | Sunflower and capsicum claims "from Tucker & Talbert (2014)", and the Mesoamerican theory is "thoroughly debunked" | C | FACTUALLY-WRONG on attribution. The sunflower and capsicum IDs are O'Neill 1944; Tucker & Talbert published in *HerbalGram* 100 (2013) (web). "Debunked" is an overstatement: our notes call it "effectively ruled out on combined evidence" (C-14 plus a European ownership chain) |
| 50 | 11 | Bax 2014; Cheshire 2019 (Romance Studies) and the Bristol distancing | H | Consistent with common record; not checked by us (unverified) |
| 51 | 67, 1913 | Toresella "proved" the alchemical-herbal parallel | C | CITATION-UNVERIFIED; "proved" overstated |
| 52 | 20, 68-71, 131, 3620 | Brewer & Lewis 2024: Hartlieb mandated ciphers; the Rosettes match a seven-chambered uterus; they decoded other German ciphers | C/H | Partly SUPPORTED. The paper is real (Crossref) and Hartlieb's "secret letters" call is in the abstract. The comparator ciphers are said to be N. Italian (secondary, unverified), not German. "Proved" and "mandated across Bavaria" are overclaims, and the seven-chamber/Rosettes mapping is the authors' proposal |
| 53 | 4887 | Hartlieb wrote in the 1450s | H | Consistent with BREWER-LEWIS-CHECK (c.1450s). It contradicts the transcript's own "1420s workshop" motive (date tension) |
| 54 | 1915, 3587, 4875 | Greshko 2025 (Cryptologia): Naibbe reproduces h2, Zipf and slot grammar "simultaneously"; this is the mechanism | C/I | CITATION real (DOI 10.1080/01611194.2025.2566408, from the supplement on disk). The mechanism claim is CONTRADICTED-BY-OUR-DATA: F-24, L-006, L-159; supplement p.5 repeats 0.18% "lower than observed VMS rates". The author disclaims it (web, secondhand) |
| 55 | 700-760, 4874-4880 | Verbose table cipher explains A/B as two tables, low h2, labels and qo- | I | CONTRADICTED-BY-OUR-DATA: H-03 disfavoured (F-25, F-45, F-47); H-14 narrowed (D-067); A/B = scribe, not a table (F-16) |
| 56 | 1151-1160, 4332-4344, 4879 | Labels encode states or coordinates (4 humours × 4 degrees = 16, or 30 zodiac steps) | I | CONTRADICTED in its testable part: zodiac same-position repeats at the permuted rate (L-152 z=−1.4); no zodiac order (F-28). Labels do repeat within an illustration unit (L-152 z=+13.9), which is compatible with a class-specific register but not with coordinates |
| 57 | 4870 | "Not random gibberish because of the qo-/o- split and topic clustering" | I | Overclaim. H-08 is disfavoured on other grounds (F-04, F-26). The qo- split alone does not decide it (L-033: "labels are a habit register") |
| 58 | 3640-3698 | Collaborative copy from an exemplar, yet scribes adapt spelling to obstacles (live encoding) | I | Mixed. F-21 (errors look like composition) is SINGLE and at-risk. L-187: R_P1 cannot separate copied from composed text at quire size |
| 59 | 1180-1250, 3438 | Compass pinpricks, drypoint; physician authorship "95% match" | H/I | UNTESTED-BY-US. "Raking-light Yale 2014" is CITATION-UNVERIFIED; the 95% figure is invented |
| 60 | 1265-1500, 4226-4290 | Roots as mnemonics, cross-sections, the toxic-look-alike rationale | I | UNTESTED-BY-US (interpretation; no data) |
| 61 | 2575-2610 | 8 foldouts; no ruling (Clemens & Harkness 2016) | H/C | CITATION-UNVERIFIED |
| 62 | 2580 | Hand-drawn gallows show "tremor" (Stolfi & R...) | C | CITATION-UNVERIFIED |
| 63 | 3606-3612 | 10 wheels × 30 nymphs = 300 degrees | H | UNTESTED-BY-US. Counts vary by wheel, and f70v alone is given as 29 + 1 star (L3460). Unverified |
| 64 | 29-31, 50-52 | "October 2026 binding study" and "September 2026 WitchTok trend" | H | Binding study real (item 11). WitchTok unverified |

### B. Label-token check (ZL3b, VKB `loci` and `tokens`)

| Folio | Transcript says | ZL3b has |
|---|---|---|
| f84r (hand 2, B) | otolor, or shekar, qokdy, otedy loly, dail or chy, **otedy otedy**, otokcho, otaly, dchedy | ololal, or.shekar, ydy, okedy, loly, doiir, olshy, otedy, lkol, okolshy, otoly, dshedy, otaly; otedy is 1 label + 6 paragraph (not 17) |
| f73v (hand 4) | otaly, **otedy, otedy**, chedy atop; okedy, okeey, otar, oky ... | okol, oteody, oteedy, eeeody, okeody, ..., otedy, eeed, oky, ...; no otaly; no adjacent pair |
| f70v1/2 (hand 4) | otaly, otal, otedy, okedy ... | otaly, otal, okaly-type forms present; zero qo- (direction right) |
| f68r1 (hand 4) | Sun "oky..." and Moon "oky oeeody okody okeey ldy"; okeody ×3; otaly; okor ×2 | circular text "oky okchdy okardy q?ear oygy"; 29 labels; no okeody, otaly or okor |
| f78r (hand 2, B) | lanes dal chd / qokal / dly oly / oky lshy / daly dal / daldy qokld / skal qokedy / olkeec okoly | labels okchdldlo, okchdy, dar aloifhy, dchedaly, otarodlay orory, okaral; dal (×3) and oly (×1) only in paragraphs; dly absent |
| f100r (hand 1, A) | kolold, chold, okeol, chody, saralol, qokeechedy, qokchedy, dchdy, daldy, okechol, qokechol, dalkar, chol okol | chosaroshol, sochorcfhy, otear, chofary, sar char daiindy, oraro, chalsain, soity, sosam, dakocth, sofam, okeeos, shockhey, orol, olcheom, oteol, okols |
| f88r (hand 1, A) | oald, alody, oaral, choky, oky, okchody, qokold, shokchey | otorchety, osal, orald, oldar, otoky, otaly, otaldy, oram, dary, okol, sorory, otyda, ofyskydal, otor am, ofaldo |
| Corpus | otedy otedy "dozens" of times-type claims; daiin daiin "dozens" | otedy otedy 1; daiin daiin 11 (adjacent, same line) |

Refutation check: these are ZL3b only. RF1b and IT2a were not checked (unverified). A different transliteration could carry a few of the forms, but not the f100r/f88r sets wholesale.

## C. What is new and testable (candidates), and what already covers it

Rule D-066(v) applies: real-language controls and shuffled Voynich come first. Nothing here is pre-registered.

1. **Labels as coordinates in a 16- or 30-state alphabet** (L3602, L4879). Already covered: L-152/q1 (zodiac position crib closed, z=−1.4); F-28 (no circular-zodiac or month order, planted orders recovered); L-033 (no list order; o-initial is a register). The residual is a *state-count* test: does the zodiac label inventory per wheel collapse to K≈16-30 recurring classes beyond a frequency-matched draw? It would need L-152's within-illustration shuffle plus a class-conditioned generator (O-044 is still open). Marginal value, since the coordinate story's evidence was fabricated.
2. **Starred recipes (f103-f116) draw vocabulary from Herbal plus Bath** (L1146, L4855). No dedicated run found. Nearby: F-07 and L-029 (section topic; quire-drift confound), F-17 and F-42 (quire-local pools), L-084 (S -edy 13.68% sits between B 25.98% and H 4.12%, which a pure hand or section mixture would also give). Any test must control hand (f103-f116 are mostly hand 3) and quire, with a shuffled-Voynich and real-language section-mixture control. It is likely confounded by hand.
3. **"Adjacent minimal pairs in label rows" (X then qX)**. Covered by L-152 (within-illustration repetition z=+13.9) and F-13 (short-range core recurrence). The specific okechol/qokechol case does not exist.
4. **Word after `<->` drawing gaps takes gallows**. Covered by L-156 and s35 (weak edge; gallows at mid-line rates) and F-18.
5. **Root shape vs label suffix; o-/top vs d-/bottom on plant labels**. Partly covered by F-33/s78/s86 (affix frames associate with pictures; cores do not) and F-44 (label position). A suffix-by-root-class test would be retrospective (D-066 e) and needs an image-derived root taxonomy first.
6. **9-column line alignment (mutual information by position)**. Covered by F-04 and F-14 (rhythm and prefix memory restart per line).
7. **f86v4 adjacent-quadrant shared vocabulary** (L1066-1075). Untested. It is a single page (~20 lines) and underpowered, so not worth a run id.

The only real lead the transcript gestures at, period encipherment motive in women's-secrets medicine, is already on file. See BREWER-LEWIS-CHECK.md, F-45/s102 and L-209: Jon's recipe-cipher hypothesis has 0/12 cells.

## D. Not checked (unverified)

- RF1b and IT2a label forms.
- Davis 2020 quire-sharing detail.
- The calf count.
- Merlon and costume art history.
- Toresella, Clemens & Harkness, and the Sterneck venue.
- The main text of the Greshko paper, where the disclaimer is quoted secondhand from the press.
- The full text of Brewer & Lewis (paywalled).
- WitchTok.
- The image-level claims (pinpricks, paint order, f79v creature, women counts).
