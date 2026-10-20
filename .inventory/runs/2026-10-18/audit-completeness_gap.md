# Voynich completeness gap map

Written 2026-10-18 15:55 PDT (clock read with `date`). This was a read-only pass over `.`. Web checks were made by search and fetch only; nothing was downloaded.

Status key:
- **HAVE** (path) means the data is on disk and usable.
- **PARTIAL** means part of it is on disk or registered; the entry says what is missing.
- **MISSING** means it is not on disk; the entry gives the best public source.

"Unverified" means I did not open the primary source.

## Defects found in the tree during this pass (fix before trusting these items)

- `data/external/voynich-nu-ivtff/ivtff_format.pdf` is 355 bytes. It is an HTML **404 page**, not the IVTFF spec. Its `.pdf.txt` is the same error text. The spec is therefore not on disk; `ivtff.xlsx` is.
- `data/external/lit-20261018/meister-1902-pelling-zip/Meister1902.zip` is an HTML 404 page. `literature-2026-10-18.md` §4 already says so.
- `data/external/lit-20261018/greshko-tandf-pdf/greshko.pdf` is 5,865 bytes and starts with `<!DOCTYPE`. It is an HTML page, not the paper. O-018 is still open.
- There is no `ZL3b-n.txt` copy under `data/external/voynich-nu-ivtff/`. ZL3b is held only at `data/ZL3b-n.txt` (frozen). That is fine, but the voynich.nu README was updated 24/03/2026. Whether a newer ZL release exists is unverified. `/data/beta/` lists no ZL file (checked).

---

## 1. Transliterations

| Item | Status | Path / source | Known errors and caveats |
|---|---|---|---|
| ZL3b (EVA, IVTFF 2.0, 13/05/2025) | HAVE | `data/ZL3b-n.txt`; sidecars `data/translit/ZL3b_eva.meta.json`, `ZL3b_glyphplus.meta.json` | 740 `<%>` markers. These do not exhaust the physical entries: on f108v, f111r and f111v the scans show 16/17/19 stars where `<%>` gives 7/6/8 (L-216; 321 stars against about 285 paragraphs). The page variables carry $Q, $P, $F, $B, $I, $L, $H (Davis) and $C (Currier hands 1-5, X, Y). |
| RF1b (ZL+GC merged via STA1) | HAVE | `data/external/voynich-nu-ivtff/RF1b-e.txt` (extended EVA), `RF1b-er.txt` (basic); `data/translit/RF1b.meta.json` | 100% coverage. Extended `@nnn;` codes are lost in `-er`. |
| IT2a (Takahashi, 1999 state) | HAVE | `voynich-nu-ivtff/IT2a-n.txt`, `data/translit/IT2a.meta.json`; also `VT0e-n.txt` (voynichese.com auto version) | 96.8% coverage. VT0e is auto-generated and has fewer types (8,078 against 8,547). |
| Takahashi original EVT | PARTIAL | only via IT2a and LSI | the original `takahashi.evt` from Stolfi's mirror is not on disk (low value) |
| Currier / D'Imperio (CD2a) | HAVE | `voynich-nu-ivtff/CD2a-n.txt` | 40.8% coverage (herbal-heavy). Currier alphabet, so it needs an alphabet map; no meta sidecar. |
| FSG (FG2a) | HAVE | `voynich-nu-ivtff/FG2a-n.txt` | 75.4% coverage: no circular or radial text, only 98 labels; no sidecar |
| v101 (Glen Claston, GC2a + voyn_101) | HAVE | `GC2a-n.txt`, `voyn_101.txt`, `data/translit/GC2a.meta.json` | Not losslessly convertible to EVA. The h2 band is alphabet-specific (O-022: GC2a 2.540). |
| EVA variants (Eva-T basic, extended EVA, STA1, glyph+) | PARTIAL | basic and extended EVA via RF1b; glyph+ sidecar | No standalone STA-alphabet file. Zattera's SLA alphabet exists only as the paper (`papers/zattera_2022...`). The IVTFF spec PDF is a 404 page (see Defects). Source: https://www.voynich.nu/extra/sp_transcr.html (no licence; citation requested). |
| Stolfi / Landini interlinear | PARTIAL | `voynich-nu-ivtff/LSI_ivtff_0d.txt` (Zandbergen's IVTFF 1.5 beta conversion) | Stolfi's original release 1.6e6 (`tcmt16e6.evt`, per-page comment files, per-unit files) is not on disk. Source: https://ic.unicamp.br/~stolfi/voynich/98-12-28-interln16e6 (no licence stated; about 2-5 MB). Ghost duplicates: O-059 reports that 16 of 31 repeated label pairs may be interlinear duplicates in Stolfi's 1998 HTML (f89r2 under f89v2, f100v under f101v1). This is **unverified**, and db-s114 is blocked on it. LSI token counts sum over transcribers, so split by the transcriber letter first. |
| Per-locus transcriber disagreement table | MISSING (derivable) | from LSI + RF1b + IT2a + GC2a | No tool computes a per-locus disagreement or uncertainty weight. |

Totals for section 1: HAVE 6, PARTIAL 4, MISSING 1.

## 2. Images

| Item | Status | Path / source | Notes |
|---|---|---|---|
| Yale Beinecke full-resolution scans | HAVE | `data/external/yale_scans/pages/` (204 JPEGs, 523 MB, sha256 in MANIFEST.md); manifest `manifest_2002046.json` | Public domain (Yale catalogue). These are IIIF `full/full` JPEGs at native size (about 2700-3000 x 3700-3800 px). The TIFF masters (`/download/tiff/<id>`) were not fetched. Covers, flyleaves, spine and edges were skipped (9 canvases). |
| Foldouts | PARTIAL | composite canvases ("69v and 70r", "85r (part)", ...); `tools/segment_scans.py` lists them as unmatched | No per-panel crop or registration exists for f67r, f68r, f72v, f85/86, f90r or f95v. |
| Older facsimile cutouts | HAVE | `data/facsimile/` (6 folios) | — |
| Multispectral imaging (Lazarus Project / RIT 2014, released by Davis 2024; 10 folios: 1r, 8r, 17r, 26r, 47r, 70v1, 71r, 93r, 102v1, 116v) | MISSING | Google Drive folder https://drive.google.com/drive/folders/1mNQGKQDSCR4M_c2M2JrsU5soghvYwMig, linked from https://manuscriptroadtrip.wordpress.com/2024/09/08/multispectral-imaging-and-the-voynich-manuscript/ | No formal licence. The post says the images "may be viewed and freely downloaded", with credit to the Lazarus Project / RIT Carlson Center and the citation "Beinecke MS 408, folio n". The folder holds four subfolders: Raw 16-bit TIFF bands ("enormous"), processed pseudocolour, lab true-colour TIFFs, and RGB JPEGs. Size is not stated; expect tens of GB. This is O-060 (deferred by Jon). |
| Raking light | MISSING (no public source) | none found; the only public trace is a proposal on ciphermysteries (raking IR of f116v) | It would need a request to the Beinecke. A stand-in is the MSI lab true-colour set on the same 10 folios. |
| Covers, spine and binding images | PARTIAL | they are in the Yale manifest but were skipped by the fetch | small; same PD source |

Totals for section 2: HAVE 2, PARTIAL 2, MISSING 2.

## 3. Physical and codicological data

| Item | Status | Path / source | Notes |
|---|---|---|---|
| Quire collation and missing leaves | PARTIAL | $Q, $P, $F, $B in `data/ZL3b-n.txt`; `data/folio_evidence_inventory.tsv` (quire, page_in_quire, bifolio); prose list in `research_notes/.../physical_provenance.md` Q3 | There is no structured collation table with missing-leaf slots (f12 stub, ff59-64, f74 stub, ff91-92, ff97-98, ff109-110; 14 against 16 missing). Sources: https://www.voynich.nu/descr.html and Layfield & Davis 2026 Table 5. |
| Bifolio structure and conjugate pairs | HAVE | ZL $B / $F; used by `s35_physical_codicology_quire_network.py` and `p1_bifolio_null.py` | Not cross-checked against Layfield & Davis Table 5 (CC BY 4.0, https://journals.openedition.org/digitalmedievalist/2331). |
| Original foliation and quire marks | PARTIAL | prose only (physical_provenance.md) | No per-folio table records foliation hand, quire-mark presence, the trailing "9", or paint over numbers (f42r). Source: https://voynich.nu/extra/sp_origin.html. |
| Davis's 5-scribe assignments | PARTIAL | $H in ZL3b (113/46/33/27/7 pages) | The 2020 article (letterform criteria, ambiguous pages, f115r shared by scribes 2 and 3) is not on disk. It is open access on Project MUSE: https://muse.jhu.edu/article/754633; Penn: https://repository.upenn.edu/mss_sims/vol5/iss1/6. The model is contested (O-020). |
| Water stains and offsets (Layfield & Davis 2026) | MISSING | The article has **no catalogue** of stains or offsets (checked by fetch). It names only 10v/15r (splash), 33v/40r (blue), 58v/65r (green), 76v/83r (arm) and 78v/81r (streams). | No public dataset exists, so one would have to be built from the scans. |
| Stitching and binding history | PARTIAL | prose (physical_provenance.md Q3: single late-Gothic sewing, Zyats 2016) | No sewing-station or thread-hole data. Zyats et al. AIC 2011 paper: https://resources.culturalheritage.org/conservators-converse/?p=3447. |
| C14 dating (Arizona 2009) | PARTIAL | prose only (4 folios f8, f26, f47, f68; 1404-1438) | The per-sample table is on https://www.voynich.nu/extra/carbon.html (not saved). Hodgins' formal figures were not checked. |
| McCrone ink and pigment report (2009) | MISSING | text-only PDF: https://beinecke.library.yale.edu/sites/default/files/files/voynich_analysis.pdf (Toronto Omeka record; not confirmed live). Figures and spectra were never released. | Yale terms; small (under 1 MB). |
| Vellum (calf; goat cover, York 2014) | PARTIAL | prose | no source document on disk |
| f116v marginalia | PARTIAL | images, plus `data/external/cribs/stolfi_f116v.htm`, `stolfi_note016_f116v.txt`, ciphermysteries page | The MSI f116v stack is missing. |
| f1r key-like letters and Tepenec signature | PARTIAL | image `002_1r.jpg`; ZL comment (lines 5-20 of ZL3b) | MSI 1r (UV signature, erased text) is missing. |
| f17r marginalia | PARTIAL | image only | MSI 17r is missing and no reading is on disk. |
| Provenance documents (Marci 1665/66, Baresch 1637/1639, Kircher, Horczicky) | PARTIAL | secondary prose only | Transcriptions and translations: https://www.voynich.nu/letters.html (research use; the Kircher carteggio scan links died in 2025 per that page). Guzy 2022 on Rudolf II book transactions is CEUR 3313 paper 16 (CC BY 4.0). |

Totals for section 3: HAVE 1, PARTIAL 10, MISSING 2.

## 4. Layout data

| Item | Status | Path | Notes |
|---|---|---|---|
| Word bounding boxes (Rozanova / voynichese.com) | HAVE | `data/external/word-coordinates/lrozanova-voynich-units-main/.../voynichese_boxes/` (223 folios, MIT) | Snapped to a 3-px grid on a page about 600 px wide. Provenance is "incompletely documented" (O-019). Box gaps disagree with ink gaps at 26% of zero-gap sites. |
| Line boxes | PARTIAL | `runs/s47/lines.tsv`, `positions.tsv`; s45 `ink_lines_ZL3b.meta.json` | These come from scan segmentation aligned to ZL. There is no independent line-polygon ground truth (PAGE-XML). |
| Label loci | HAVE | `@L` loci in ZL3b; cribs for f67v2, f68r1-r3 and f70v-f73v (clock positions) | No x,y anchor of each label against its drawn object. |
| Ink-derived word gaps (s45, s47) | HAVE | `runs/s45/`, `runs/s47/`, `results_s45.txt`, `results_s47.txt` | κ 0.87 against ZL spaces; scope is agreement only (O-048) |
| Paragraph and star positions (s100) | HAVE | `runs/s100/star_classes.tsv` (321 stars: page x,y, nearest line, filled/tailed) | Paragraph starts beyond `<%>` are not re-encoded as loci (O-061). |
| Illustration and plant regions | PARTIAL | `runs/s48/` (crops, embeddings) via `tools/plant_regions.py` | No full-manuscript drawing/text mask and no text-over-paint order. |
| Glyph-level segmentation | MISSING | none public (README §6: "Not found") | must be built from the scans |

Totals for section 4: HAVE 4, PARTIAL 2, MISSING 1.

## 5. Comparanda corpora

| Item | Status | Path / source | Notes |
|---|---|---|---|
| Period herbals (images and plant identities) | PARTIAL | `data/herbals_period/ljs419` (205 images, PD), `sloane4016` (235); captions are agent transcriptions and **unverified** | No edition-sourced identities. Touwaide 2013 (Sloane 4016) is not open. Tucker & Talbert 2013 (HerbalGram) is not on disk. Sherwood lists are in `cribs/`. |
| Alchemical-herbal family (Beasley 2024, 38 MSS) | PARTIAL | `data/herbals_alchemical/` (BSB Clm 5905 and BL Add 41623 on disk but **outside** the family); BnF Lat. 17848/17844 were refused by Gallica | The thesis PDF is not on disk: https://shareok.org/items/76577e4f-2332-4974-b6ca-113704873aaf (ShareOK; licence unverified). Segre Rutz 2000 (identities) is not open. O-062. |
| Recipe texts | HAVE | `data/controls_period/raw_it`, `raw_de`; `external/genre-s87` (Forme of Cury and others) | — |
| Tabular medical texts | PARTIAL | `data/controls_tabular/` (MediManus Tacuinum BnF lat. 9333 is the **only machine-readable table** found; De gradibus; Lull Tabula); `controls_tabular_ruled/` (1531/1532 page images, OCR 39-53% token match, L-223) | No transcription of a ruled table exists (O-063). It would need HTR (CREMMA models) or manual keying. |
| Lullian works | HAVE | `controls_tabular/raw_lull*` (1515, 1596, 1617) | only the Tabula generalis is scored |
| Period ciphers (Florentine, Venetian, Milanese) and nomenclators | PARTIAL | `external/nomenclators/` (Meister 1906 PD; Pelling blogs); Megyesi 2022 and 2021 statistics in `research_notes/External anchors/period_nomenclators.md` | Missing: (a) the **DECODE database** (https://de-crypt.org; over 1,000 keys, about 41% transcribed; papers CC BY 4.0, data terms **unverified**); (b) Meister 1902 (HathiTrust `pdus`, hvd.hxub2m and uc1.b4177709, US IP only); (c) Tranchedino Cod. Vind. 2398 (no ÖNB digitisation found; ADEVA 1970 facsimile only). |
| Shorthand systems (Tironian) | MISSING | Schmitz 1893 *Commentarii notarum tironianarum*: https://archive.org/details/commentariinotar00schm (PD, OCR) | about 13,000 signs; no control file in `data/controls/` |
| Glossaries | PARTIAL | `genre-s89` (Promptorium parvulorum, Sinonoma Bartholomei, Alphita); Lingua Ignota is a 30-entry sample only (O-015) | — |
| Period Latin, Italian and German texts | HAVE | CREMMA (121 XML, CC BY/CC0 conflict), `data/controls/*`, `controls_period` | — |
| Real period gibberish manuscript (Sloane MS 3188, Boxer 2022) | MISSING | CEUR 3313 paper 1 (CC BY 4.0) https://ceur-ws.org/Vol-3313/ | the only real-manuscript meaningless-text comparator named in the literature |

Totals for section 5: HAVE 4, PARTIAL 5, MISSING 2.

## 6. Scholarly literature with measurable claims

| Work | On disk? | Claims tested or recorded? |
|---|---|---|
| Currier 1976 | No (https://voynich.nu/extra/curr_main.html, transcription by Guy and Reeds 1992) | PARTIAL. A/B and hands are used throughout via $L/$C. Parisel 2026b confirms them. His specific statistics (line-final and line-initial glyph rules, the hand 3/4/X/Y claims) are not tested as claims. |
| Stolfi (word grammar, page notes) | PARTIAL (cribs, LSI) | PARTIAL. Recorded in CONSTRAINTS-MAP; the 2000 grammar is not scored directly. |
| Reddy & Knight 2011 | No (https://aclanthology.org/W11-1511/, ACL CC BY) | Recorded only as "external, unverified" in FINDINGS-GRAPH line 162. Not tested. |
| Montemurro & Zanette 2013 | Yes (`papers/montemurro_zanette_2013_plosone.txt`, CC BY) | PARTIAL. Claim c-221 is VERIFIED-LITERATURE, but the information-vs-scale peak (M18) has **no code** (METHODS.md line 196). |
| Timm & Schinner | Yes (generator, arXiv 1407.6639) | HAVE. Scored as a producer (`ctl_timm_schinner.py`, n6/n7). The 2019/2020 Cryptologia paper is paywalled. |
| Rugg 2004 (grille) | No (Cryptologia, paywalled) | HAVE as a producer (`results_n6_rugg_grille`, s71) |
| Bowern & Lindemann 2021 | Yes (Yale PDF, corpora CSVs) | PARTIAL. The statistics CSVs are on disk, but O-031 says they were never put on the board. No `results_*` cites them. |
| Davis 2020 | No (MUSE open access) | PARTIAL ($H used; criteria not read) |
| Zandbergen voynich.nu (history, quire, illustration pages) | No (only IVTFF files and README) | PARTIAL. Prose notes cite descr.html, carbon.html and sp_origin.html. The per-quire pages and illustration-section pages are not saved or tabulated. |
| Ponzi | No | PARTIAL. Ponzi 2019 on line ends was extended by s35 Part 2 (TEAM-HANDOFF line 84). No Ponzi text is on disk. |
| HistoCrypt and the VOY 2022 papers | 3 of 16 CEUR 3313 papers on disk (4, 6, 10) | Missing: Farrugia, Layfield & van der Plas (scribes), Caruana et al. (word relations), Lindemann (MATTR), Painter & Bowern (glyph phylogeny), Feaster (rightward/downward grapheme distributions), Stafford (paragraph habits), Boxer (Sloane 3188), Katz and Guzy (ownership), Schmeh & Dunin, and the Zandbergen and Davis keynotes. All CC BY 4.0 at https://ceur-ws.org/Vol-3313/. HistoCrypt Megyesi keys papers: recorded. |
| Voynich Ninja statistics threads | 1 thread (5081, Naibbe) | MISSING. Guests cannot see links (O-033, human decision). |
| Schwartz 2026, Rozanova-Temerev 2026, Parisel, Steckley, Zattera, Greshko | Yes (the Greshko paper text is not) | HAVE: tested extensively |

Totals for section 6 (14 rows): HAVE 3, PARTIAL 8, MISSING 3. The three MISSING rows are Reddy & Knight, the VOY 2022 papers (only 3 of 16 on disk) and the Ninja threads.

---

## Grand totals

| Category | HAVE | PARTIAL | MISSING |
|---|---|---|---|
| 1 Transliterations | 6 | 4 | 1 |
| 2 Images | 2 | 2 | 2 |
| 3 Physical / codicological | 1 | 10 | 2 |
| 4 Layout | 4 | 2 | 1 |
| 5 Comparanda | 4 | 5 | 2 |
| 6 Literature | 3 | 8 | 3 |
| **All** | **20** | **31** | **11** |

## Top 15 gaps, ranked by the new analysis each unlocks

1. **Contact, offset and stain matrix for every leaf** (MISSING). Build it from the PD Yale scans plus the CC BY Layfield & Davis conjoint table. *Question:* what was the pre-binding page adjacency, read off the physical evidence and not the text? Do the order-dependent findings (F-32, recto/verso, quire locality) survive under that order? **[novel]**
2. **Transcriber-free glyph segmentation** (MISSING). Build it from the scans with the Rozanova boxes (MIT) as seeds, on the GPU. *Question:* are EVA's units (ch, sh, iin, gallows plus pedestal) real? This would discharge X-01 / O-056 and give a hand model from glyph shape alone. **[novel]**
3. **MSI raw 16-bit band stacks for 10 folios** (MISSING; Google Drive; attribution, no licence). *Questions:* recover the erased f1r text; separate the ink layers and the sequence of drawing, text and paint on f17r, f116v and f70v1; check whether text was written over finished drawings (Schwartz's claim). **[novel]**
4. **DECODE nomenclator ciphertexts and keys** (PARTIAL; de-crypt.org; data terms unverified). *Question:* do Voynich statistics fall inside the distribution of real 15th-century chancery ciphertexts at matched size? Today only synthetic nomenclators are scored.
5. **Davis 2020 criteria and ambiguous pages** (PARTIAL; MUSE open access). *Question:* do scribe boundaries match glyph-shape clusters (with gap 2)? This would settle O-020.
6. **CEUR 3313 (13 missing papers, CC BY)**. *Questions:* Boxer's Sloane 3188 as a real period-gibberish control; Feaster's directional distributions and Stafford's paragraph habits turned into testable claims.
7. **Beasley 2024 thesis plus BnF 17848/17844 and Segre identities** (PARTIAL). *Question:* does Herbal-A match the alchemical-herbal family in plant identity and sequence? This would unblock s105.
8. **Ruled medical tables transcribed** (PARTIAL; PD page images on disk). *Question:* the F-40 row-structure test against real tables.
9. **Structured codicology table** (PARTIAL): missing-leaf slots, foliation and quire-mark hands, paint transfers (voynich.nu). *Question:* test gap and edge effects at physical lacunae (for example the Quire 8 centre and Quire 20's ff109-110) against the star and paragraph cadence.
10. **Stolfi 16e6 original plus page notes** (PARTIAL; unicamp). *Questions:* verify the O-059 ghost duplicates; build per-locus reading-uncertainty weights.
11. **Foldout panel registration** (PARTIAL). *Question:* order-free reading of the rosettes and f67/f68 circular text by geometric position.
12. **McCrone report text** (MISSING; Beinecke PDF). *Question:* the per-sample ink and pigment sites as a constraint on the sequence of writing, drawing and paint.
13. **Montemurro & Zanette M18 curve and Bowern & Lindemann CSVs on the board** (PARTIAL; on disk). *Question:* where does Voynich's information-vs-scale peak sit against the habit generators?
14. **Tironian / shorthand control** (MISSING; Schmitz 1893, PD). *Question:* a sign-for-word shorthand as a producer family, not yet scored.
15. **Reddy & Knight 2011 and Currier 1976 claims** (MISSING / PARTIAL; ACL CC BY; voynich.nu). *Question:* replicate their page-topic and vowel/consonant claims and Currier's line-edge rules under the current nulls.
