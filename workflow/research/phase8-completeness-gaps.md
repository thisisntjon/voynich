# Phase 8 angle: completeness gaps (what we do not hold, and whether we can get it)

Date: 2026-10-19 09:31 PDT (read with `date`). Author: Phase 8 investigator, completeness-gaps angle. Read-only investigation: this is the only file written. The scratch work (`coverage.tsv`, scripts) is in the session scratchpad and is not project data.

Question: what does a complete triangulation need that we do not hold, and can we get it?

Short answer: the text layer is nearly complete. The gaps are in three places: (a) images beyond the Yale RGB set (MSI for 7 more folios, the inside front cover, comparison-manuscript images); (b) about 15 named literature items that are open access but simply not pulled, plus a paywalled core (Timm & Schinner 2019/2023, Rugg, Brewer & Lewis, O'Neill, Clemens 2016) that cannot be pulled by an agent; (c) registers that lag the disk. The VKB `sources` table still says MSI is MISSING and Davis 2020 is not on disk, and 5 of the 8 held transliterations are not loaded into the VKB.

---

## 1. What I found

### 1.1 Per-page coverage (227 VKB folios)

Built from `data/vkb/vkb.sqlite` (opened read-only), the IVTFF files in `data/external/voynich-nu-ivtff/`, and `data/atlas/objects.tsv`.

| Layer | Folios covered (of 227) | Note |
|---|---|---|
| ZL3b loci (VKB) | 227 | primary |
| RF1b loci (VKB) | 227 | |
| IT2a loci (VKB) | 225 | missing `fRos`, `f116v` |
| GC2a (file only, not in VKB) | 225 | missing `fRos`, `f116v`; v101 alphabet |
| LSI 0d (file only) | 226 | multi-transcriber |
| FG2a / FSG (file only) | 202 | no circular or radial text |
| CD2a / Currier (file only) | 131 | herbal-heavy: H 110, B 19, T 2 |
| Yale scan (one-to-one or panel) | 227 | `panel_images` covers 50 folios that have no own `image_path` (shared or partial canvases and foldout panels) |
| MSI held | 3 | f1r (C:\, `data/msi/f1r`), f17r and f116v (`<local-path>`) |
| MSI publicly available | 10 | adds f8r, f26r, f47r, f70v1, f71r, f93r, f102v1 (from `data/msi/SOURCE_LISTING.tsv`) |
| Hand (Davis) | 227 | 1:113, 2:46, 3:34, 4:27, 5:7. Single source; Timm 2026 "One Hand, Five Labels" (VL00769) contests it. No second hand assignment is held per folio |
| Currier language | 197 | 30 blank. These are source-native blanks, mostly A, C, Z |
| page_facts | 227 | 10,161 rows, 50 attributes. Per folio: colour 207, illustration 191, description 160, plant-id 134, damage 80, later-addition 60 |
| ZL label loci | per section | Z 299, P 234, C 172, A 116, B 116, T 60, H 32, **S 0** |
| Atlas objects | 222 (184 own) | 975 objects. Every `kind` and `caption` comes from `qwen2.5vl` (machine); 96 have linked labels. None: f58r, f76r, f106v, f107r, f113r |

By section (FG = FSG coverage; CD = Currier coverage; plant-id/colour/desc = page_facts folios; nattr = mean distinct page_fact attributes):

| sec | folios | FG | CD | plant-id | colour | desc | nattr |
|---|---|---|---|---|---|---|---|
| H herbal | 129 | 127 | 110 | 128 | 129 | 92 | 21.4 |
| S stars/recipes | 25 | 24 | 0 | 0 | 25 | **3** | 17.3 |
| B biological | 19 | 19 | 19 | 0 | 0 (!) | 15 | 16.8 |
| P pharma | 16 | 16 | 0 | 6 | 16 | 13 | 21.9 |
| Z zodiac | 12 | 0 | 0 | 0 | 12 | 12 | 26.5 |
| C cosmo | 11 | 5 | 0 | 0 | 11 | 11 | 21.4 |
| A astro | 8 | 5 | 0 | 0 | 8 | 8 | 20.9 |
| T text | 7 | 6 | 2 | 0 | 6 | 6 | 20.9 |

**Weakest section: S (recipes, f103r–f116r).** It holds 11,646 tokens, the most text of any section, yet has 0 label loci, no Currier-transliteration coverage, page_fact descriptions on only 3/25 folios, and the three folios with no atlas objects (f106v, f107r, f113r). **B has no `colour` page_facts at all** (0/19), although the s123/s126 water-colour runs need them. Their colour evidence comes from the scans, not from a curated fact.

**Weakest pages** (low on independent layers): f106v, f107r, f113r (S, no atlas, ~17 attributes); f113v, f115v, f103v–f105v, f107v, f111v, f112v, f114v (S); f75r, f75v, f81v, f82v, f83r (B: only 14–17 attributes, 1–4 atlas objects); f94r, f94v, f21v, f38v (H, small text); f58v (S-type, no FSG/Currier); fRos (only ZL/RF; no IT or GC, though it has 315 page_facts); f116v (no IT or GC, but MSI held).

### 1.2 Images

- **Yale RGB scans are the full IIIF resolution.** All 204 files in `data/external/yale_scans/pages/` match the manifest width and height (0 mismatches). The IIIF `info.json` for f1r (`/iiif/2/1006076/info.json`) lists a largest size of 2972x3766 with maxArea 11,192,552, so there is no larger IIIF master. Widths run from 2559 to 9078 px (foldouts). The "full TIFF at `/download/tiff/<id>`" route in `data/external/README.md` §6 returned **HTTP 404** for id 1006076 on a HEAD request. It may need the child-object id, or GET; that part is unverified.
- **The inside front cover (canvas 2, IIIF 1006075) is held nowhere.** See Surprise 1.
- **MSI:** 3 of 10 folios are held. The other 7 folios total about 33 GB raw (3.8–4.8 GB each). The processed images, Lab true-colour TIFFs and RGB JPEGs for all 10 folios come to about 1.3 GB. D:\ has 199 GB free; C:\ has 35 GB free.
- **Raking light:** none exists publicly (VKB `sources`).
- **Glyph-level segmentation:** none exists publicly.

### 1.3 Literature and sources (named list)

What exists to check against: `data/external/library/` (lib01). It holds `catalogue_v2.tsv` (2,979 rows), 587 legally open PDFs in `fulltext/`, `primary_sources.tsv` (59 rows), a full voynich.nu crawl (586 files), 2,825 voynich.ninja thread titles, 1,243 blog posts and `GAPS.md`. Also the VKB `sources` table (97 rows: 58 HAVE, 27 PARTIAL, 9 MISSING, 3 FAKE) and `external_items` (87 rows).

Columns: Held = full text or the data itself is on disk; OA = obtainable openly; Value = value for triangulation.

| Item | Held? where | OA | URL | Value |
|---|---|---|---|---|
| D'Imperio 1978 | YES `data/external/meaning-visual-programme/dimperio-1978-elegant-enigma.pdf` (+ .txt) | yes (DTIC; NSA URL 403) | https://apps.dtic.mil/dtic/tr/fulltext/u2/a070618.pdf | high |
| Currier 1976 papers | PARTIAL: transliteration CD2a held; paper text only as voynich.nu crawl `library/web/voynich_nu/raw/www.voynich.nu/extra/curr_main.html` | yes (voynich.nu transcription) | https://www.voynich.nu/extra/curr_main.html | high (A/B and hands definitions) |
| Tiltman 1951/1967 | NO (catalogue only: VL01312, VL01351) | partly. NSA 403; IA has Friedman–Tiltman correspondence (`41775189081427`, `41774749081383`); `nsa_technical_journal_nd_1974_02` matched the search but its content is unverified | https://www.voynich.nu/refs.html#tilt | medium |
| Stolfi (notes, grammar, interlinear) | PARTIAL: `data/external/cribs/stolfi_*`, LSI, `text16e6.evt` (via the Bowern repo), page_facts (Stolfi page notes ~3,700 rows). The 2000 word grammar and Notes 017/045 are not held as files | yes (ic.unicamp.br partly 404; Wayback) | https://www.ic.unicamp.br/~stolfi/voynich/ | high |
| Zandbergen (voynich.nu) | YES text crawl (586 files); **0 of 1,165 referenced images held** | yes | https://www.voynich.nu/ | high |
| Davis 2020 | YES `data/external/intake-phase1/davis-2020.pdf` | yes (MUSE) | https://doi.org/10.1353/mns.2020.0011 | high |
| Bowern & Lindemann 2021 | YES `data/external/bowern-lindemann-entropy/` (paper + corpora + CSVs) | Annual Review closed; Yale copy held | https://doi.org/10.1146/annurev-linguistics-011619-030613 | high |
| Hodgins radiocarbon 2009 | YES `data/external/intake-phase1/hodgins-2009.pdf`. The internal Arizona report is unpublished | letter yes | voynich.nu/extra/carbon.html | high |
| McCrone report 2009 | YES but **image-only scan, no text layer** (`intake-phase1/mccrone-2009.pdf`). page_facts carries 26 rows from Table I | yes | (Beinecke, link in VL01565) | high |
| Janick & Tucker 2018 | PARTIAL: reading samples only, `data/external/page-facts/plants/raw/janick_tucker_2018_*`, `tucker_janick_2019_*` | no (Springer) | https://doi.org/10.1007/978-3-319-77294-3 | medium (plant IDs; Tucker & Talbert 2013 is in page_facts, 36 rows) |
| O'Neill 1944 | NO | no (Speculum/JSTOR) | https://doi.org/10.2307/2856859 | low–medium (sunflower claim; dating context) |
| Montemurro & Zanette 2013 | YES `data/external/papers/montemurro_zanette_2013_plosone.*` | yes CC BY | https://doi.org/10.1371/journal.pone.0066344 | high |
| Amancio et al. 2013 | **NO** (VL02973, no local path) | **yes, PLOS ONE CC BY (HTTP 200 checked)** | https://doi.org/10.1371/journal.pone.0067310 | medium–high |
| Reddy & Knight 2011 | **NO** (VKB `liter-reddy-knight-2011` MISSING) | **yes, ACL (HTTP 200 checked)** | https://aclanthology.org/W11-1511.pdf | medium |
| Timm & Schinner 2019 | PARTIAL: generator code + Timm 2014 arXiv held (`timm-schinner-generator/`); the Cryptologia paper and the 2021/2023 papers are not | no | https://doi.org/10.1080/01611194.2019.1596999 | high |
| Rugg 2004 | NO paper; producer reimplemented (`data/controls_synthetic/rugg_grille.*`) | no (Cryptologia; SciAm) | https://doi.org/10.1080/0161-110491892755 | medium |
| Greshko 2025 | PARTIAL: Zenodo supplement held (`naibbe-greshko/`, `data/naibbe_zenodo_17219445`); **paper PDF is a FAKE** (Cloudflare page, `lit-20261018/greshko-tandf-pdf/NOTE-greshko.pdf.txt`) | yes per OpenAlex (publisher OA), but behind a Cloudflare challenge | https://doi.org/10.1080/01611194.2025.2566408 | high |
| Brewer & Lewis 2024 | NO | **no** (OpenAlex `is_oa: False`, checked) | https://doi.org/10.1093/shm/hkad099 | medium (f86v Rosettes reading; testable label claim) |
| Taiz & Taiz 2011 | NO: `taiz-*.pdf.txt` is **0 bytes**; only the landing page is held | gated (ISHS member PDF) | https://ishs.org/chronica-horticulturae/vol51nr2/ | low–medium |
| Pelling 2006 | NO (book); blog posts indexed | no | (book) | medium (Averlino / Milan hypothesis) |
| Beasley 2024 (MA thesis, Oklahoma) | YES `data/external/wave5-beasley-2024/` | yes | — | high (alchemical-herbal family, 38 MSS) |
| Layfield & Davis 2026 (two papers) | YES `intake-phase1/layfield-davis-2026-pdf.pdf` (+ html) | yes (diamond) | https://doi.org/10.4000/16k0a | high |
| Bax 2014 | PARTIAL: star-label posts (Wayback) in `cribs/`; the main paper is not held | yes, IA copy (VL02912) | https://archive.org/details/Stephen_Bax_provisional_partial_decoding_V... | low–medium (crib-check control) |
| Velinska (blog) | NO | **not found**: Wayback `available` API gives no snapshot for velinska.wordpress.com; site not located (unverified which domain it used) | — | low |
| Knowles' match list | NO | **not located**; Mark Knowles started voynich.ninja thread 2740 "Labelese Analysis" (title only held) | https://www.voynich.ninja/thread-2740.html | low–medium (label crib candidates) |
| Yale facsimile essays (Clemens ed. 2016) | NO (catalogue VL00143, VL01661) | no (book) | (Yale UP) | high: the only published source for the Yale 2014 forensic / codicology details (`GAPS.md`) |
| Voynich Ninja key threads | 1 thread (5081) held; 2,825 titles indexed | guest view is partial (O-033) | https://www.voynich.ninja/ | medium |
| voynich.nu pages not pulled | text complete; **images 0/1,165** (342 in `img/`, 99 in `extra/`, 49 in `q20/` …); about 49 linked docs missing (`extra/xc/*`, `extra/dimperio92c.html`, `extra/hmm_ent.html`, `extra/sol_class.html`, `hist/stolfi/*`; several are probably dead links) | yes | https://www.voynich.nu/ | high (colour and annotation figures, letter tables) |
| Reeds' codes | PARTIAL: 288 Reeds colour-code rows (via Stolfi) in page_facts, 127 folios; Reeds bibliography crawled; Reeds 1995 Friedman paper on IA (`jimreedsfriedman`), not held. **I could not identify a specific "h/c/a/p" scheme**: unverified | yes | https://archive.org/details/jimreedsfriedman | medium |
| Friedman group notes | PARTIAL: FSG transliteration held; 3 IA letters in the library corpus (VL01162/65/66); group minutes 1944–45 are catalogue only | partly (IA) | archive.org (Friedman collection ids 417…) | medium |
| Brumbaugh / Newbold | NO full text. Newbold 1928 appears on IA (`bwb_P8-BYE-831`, `isbn_9781169318861`) and is **US public domain since 2024** (1928 + 95), so `GAPS.md` "copyright / not open" is likely stale. Whether IA lends it or shows full view is unverified. Brumbaugh is JSTOR, closed | Newbold: likely; Brumbaugh: no | https://archive.org/details/bwb_P8-BYE-831 | low–medium (history / failed-decipherment controls) |

Controls and comparanda:

| Item | Held? where | OA | Value |
|---|---|---|---|
| Egerton 747 | TEI text YES (`data/external/ventura_egerton747/`, Ventura 2009, licence not stated); **page images NOT held** (only crop pairs in `data/egerton_caption_gate/*.zip`). BL viewer: Wayback snapshot 2023-03-30 exists; the live viewer redirects (307). Image availability after the BL cyberattack is unverified | text yes; images uncertain | high (known-answer caption control, D-072/D-073 track) |
| Fontana (BSB Cod.icon. 242 + Schulte 1910 transcription) | YES 249 JPEGs at 1600 px (`data/external/daybreak-intake-20261019/fontana_*`; image location per its manifest) | yes BSB IIIF | high (cipher known-answer). 1600 px, not full resolution |
| BnF lat. 9333 (Tacuinum) | YES as machine-readable table: `data/controls_tabular/raw_tacuinum_medimanus` | yes | medium |
| BL Add MS 41623 | YES 331 images `data/herbals_alchemical/bl_add41623` | yes | medium (outside the Segre family per VKB) |
| Bodleian Canon. Misc. 408 | YES 166 images `data/anchor_A0/bodleian_canon_misc_408` (+ manifest in `herbals_alchemical`) | yes | high (A0 anchor) |
| Sloane 4016 | YES 235 images `data/herbals_period/sloane4016` (captions unverified) | yes | medium |
| LJS 419 | YES 209 images + TEI `data/herbals_period/ljs419` | yes | medium |
| CREMMA | YES `data/external/cremma/` (121 ALTO) + earlier partial copy | yes (CC BY / CC0 conflict noted) | high (real-line control) |
| BnF lat. 17844 / 17848 | NO (Gallica 403 / 520; `herbals_alchemical/bnf_lat17844/`) | PD but blocked | high for s105 (Segre P1/P2 family) |
| Sloane MS 3188 (Boxer 2022) | NO | yes, CEUR 3313 paper 1, CC BY | high (the only real-manuscript gibberish comparator) |
| CEUR 3313 (VOY 2022) papers | 3 of 16 held (4, 6, 10) | yes CC BY | medium–high |

### 1.4 Other transliterations

All 8 current voynich.nu files are held, every one with a hash matching the remote (`primary_sources.tsv`): ZL3b, RF1b-e/er, IT2a, VT0e, GC2a + voyn_101, FG2a, CD2a, LSI 0d, plus 13 superseded versions. **Only ZL3b, RF1b and IT2a are loaded into VKB `loci`.** GC (v101), FSG, Currier, VT and LSI exist only as files. Not held: Stolfi's majority-vote `only-m.zip` (Note 045), the original `takahashi.evt` (low value), and a standalone STA alphabet file.

---

## 2. Verified vs inferred

Verified (command or check named):
- Coverage counts: a read-only `sqlite3` script against `vkb.sqlite` (`folios`, `loci`, `page_facts`, `panel_images`), IVTFF page tags parsed with `re`, and `objects.tsv` parsed. Output in scratchpad `p8cg/coverage.tsv`.
- Scan resolution: PIL dimensions of all 204 files against `pages_index.json` (0 mismatches); `curl .../iiif/2/1006076/info.json` (max 2972x3766).
- The TIFF route: `curl -I .../download/tiff/1006076` gave 404.
- MSI availability: parsed `data/msi/SOURCE_LISTING.tsv` (479 Drive files, 10 folios); `ls /d/voynich-msi`; `df -h`.
- The facsimile_full off-by-one (Surprise 1): read `s127_facsimile_manifest.py` lines 8–30; compared `data/facsimile_full/MANIFEST.tsv` rows 2, 3, 205, 206; `sha256sum` shows `extra/206_116v.jpg` = `yale_scans/pages/205_116v.jpg`.
- Literature: regex lookup over `catalogue_v2.tsv` and `FULLTEXT-MANIFEST.tsv`; `find` over `data/`; `curl -I` gave 200 for ACL W11-1511 and PLOS 0067310; OpenAlex `open_access` for 10.1093/shm/hkad099 = closed; Wayback availability API for velinska.wordpress.com (none) and stephenbax.net (yes); IA advancedsearch for Friedman, Tiltman and Newbold.
- voynich.nu crawl: a link-extraction script over the 586 crawled files (49 missing linked docs, 1,165 image refs, 0 image files held).

Inferred / unverified:
- That Yale has no higher-resolution master beyond IIIF. The IIIF limit is verified; the TIFF/PDF routes were not tested with a GET or child-object ids.
- Newbold 1928 being US public domain (copyright arithmetic only; IA access mode not checked).
- That Velinska's blog is unarchived (one domain guess checked); Knowles' "match list" not located; the meaning of "Reeds' h/c/a/p codes" not identified.
- Egerton 747 image availability at the BL now.
- Section-weakness judgments use my own composite score (transliteration count, atlas, page_fact presence). That score is a heuristic, not a project measure.

Process note: one metadata lookup (Unpaywall, `api.unpaywall.org/v2/10.1093/shm/hkad099?email=...`) sent the user's email as the API's contact parameter. That should not have happened. The OpenAlex call that replaced it needs no email.

---

## 3. Surprises

1. **`data/facsimile_full/MANIFEST.tsv` is shifted by one canvas for 204 rows.** `s127_facsimile_manifest.py` enumerates canvases from 1 (`enumerate(man["items"], 1)`), but the s45 file prefixes are 0-based (`002_1r.jpg` is canvas index 2 of 0..212, i.e. the 3rd canvas). Effects:
   - every `s45_reuse` row pairs the label and IIIF id of canvas N with the image of canvas N+1 (row "1r" → `003_1v.jpg`);
   - the inside front cover (1006075) is labelled onto the f1r image and was **never downloaded**;
   - 116v appears twice (row 205 "116r" and `extra/206_116v.jpg`, same sha256).

   s127 is parked and the script is not named in any `*.prereg.sha256` stub (grep found none), so no filed result rests on it. Any future picture work must not use that manifest as-is. Under the no-overwrite rule the fix is a new manifest under a new run id.
2. **The VKB `sources` table lags the disk:**
   - MSI is marked MISSING, but 3 folios are held;
   - Davis 2020 is marked "on disk: No", but it is held;
   - voynich.nu history/quire pages are marked "on disk: No", but they were crawled;
   - `physi-f116v/f1r/f17r` say "MSI missing".

   The library (lib01, 2,979 rows) is not linked into the VKB at all.
3. **McCrone 2009, the only pigment and ink source, has no text layer** (an image scan). Taiz 2011's `.pdf.txt` is a 0-byte file next to a download-gate HTML page.
4. **The S section is the largest text block and the thinnest everywhere else** (0 labels, 3/25 descriptions, no Currier coverage). B has 0 `colour` page_facts.
5. **The atlas is 100% machine-captioned** (qwen2.5vl). No object has a human-checked or source-cited kind, so it is a lead layer, not an evidence layer.
6. Hand assignment has one source (Davis). The project holds the direct rebuttal (Timm 2026, VL00769) but no alternative per-folio hand table.

---

## 4. Assumption candidates (the cleanup plan would rest on these)

| # | Assumption | How to verify |
|---|---|---|
| A1 | "We hold the full-resolution scans." True for IIIF; the TIFF/PDF masters are untested | GET `https://collections.library.yale.edu/download/tiff/<child oid>` for one folio (HEAD only), and compare its pixel size with the IIIF size |
| A2 | "data/facsimile_full is a correct whole-book manifest." **False** (Surprise 1) | Rebuild from `pages_index.json` (which maps file→label correctly) and diff |
| A3 | "VKB `sources` is the gap register." Stale | Join `sources.local_path` against the filesystem and `library/primary_sources.tsv`; count HAVE/MISSING flips |
| A4 | "All transliterations are in the VKB." Only 3 of 8 | `SELECT DISTINCT translit FROM loci` |
| A5 | "Paywalled items cannot be obtained." Some are OA through a Cloudflare challenge (Greshko), lending-only (Newbold), or have a publisher OA flag | Per-DOI OpenAlex `open_access` + a browser fetch |
| A6 | "MSI beyond 3 folios needs a request." **False**: the Drive folder is public, with 10 folios | `data/msi/SOURCE_LISTING.tsv` |
| A7 | "voynich.nu is fully held." Text only; 0/1,165 images | Rerun the link-extraction script |

---

## 5. Prioritized acquisition list

Effort and risk in brackets [effort / risk]. "Risk" means risk to project integrity (licence, overwrite, live work), not download risk.

| P | Pull | From | Expected effort | Why |
|---|---|---|---|---|
| 1 | Correct whole-book facsimile manifest (new run id, new file) + the one missing image, inside front cover (IIIF 1006075, ~2.5 MB) | `pages_index.json`; `https://collections.library.yale.edu/iiif/2/1006075/full/full/0/default.jpg` | [low / low] ~15 min | Blocks any s127-style picture work; closes the last Yale canvas |
| 2 | MSI processed, Lab true-colour TIFF and RGB JPEG for the 7 missing folios (~1.3 GB), then the raw stacks for f8r, f26r, f47r (radiocarbon leaves), f70v1, f71r, f93r, f102v1 (~33 GB) | Drive folder in `data/msi/README.md`; put on `<local-path>` (199 GB free; C:\ has only 35 GB) | [medium / low] hours of transfer, existing downloader; credit line required; no redistribution | MSI on the C14-sampled leaves and a zodiac page triangulates erasures, later additions and ink layers |
| 3 | Open papers not yet held: Reddy & Knight 2011; Amancio et al. 2013; the 13 missing CEUR 3313 (VOY 2022) papers incl. Boxer 2022 Sloane 3188; Bax 2014 (IA); Reeds 1995 Friedman transcription (IA `jimreedsfriedman`) | URLs in §1.3 | [low / low] < 1 h | Cheap; two are direct comparators (Sloane 3188 gibberish, Amancio unknown-text stats) |
| 4 | OCR the McCrone 2009 scan into a sidecar `.txt` (new file, PDF untouched) | local `intake-phase1/mccrone-2009.pdf` | [low / low] | Makes the only pigment source searchable and checkable against page_facts Table I rows |
| 5 | Load GC2a, FG2a, CD2a, VT0e and LSI (split by transcriber) into VKB `loci` with their `translit` tags | files already held | [medium / low] VKB rebuild; alphabet maps needed for GC/CD/FSG (STA bridge) | Gives independent-transcriber triangulation per locus inside the one database |
| 6 | Greshko 2025 PDF | the DOI, through a real browser session (claude-in-chrome) | [low / low] | OA per OpenAlex; replaces the FAKE file (O-018) |
| 7 | voynich.nu images (1,165 refs: annotation, colour and letter figures) + the ~49 missing linked pages (incl. `extra/dimperio92c.html`, `extra/hmm_ent.html`, `extra/sol_class.html`) | voynich.nu, polite crawl into the lib01 tree | [medium / low] research-use only, credit Zandbergen | Figures carry information the text crawl lacks (colour annotations, glyph tables) |
| 8 | Newbold 1928 (US PD) and the Friedman/Tiltman IA items (`41775189081427`, `41774749081383`, minutes if found) | archive.org / HathiTrust | [low–medium / low] | History controls; Friedman's synthetic-language hypothesis source |
| 9 | Egerton 747 page images | BL Digitised Manuscripts (status unverified), Wayback 2023 viewer, or the 2002 facsimile | [medium / low] may be blocked | Needed for the image side of the Egerton caption gate |
| 10 | BnF lat. 17844 / 17848 retry | Gallica IIIF (403/520 on 2026-10-18) | [low per try / low] | s105 data gate (O-062) |
| 11 | voynich.ninja key threads (statistics, Labelese/Knowles, MSI, f116v) | voynich.ninja (guest limits, O-033) | [medium / low] | Unpublished analyses, crib lists |
| 12 | Paywalled core: Timm & Schinner 2019/2021/2023, Rugg 2004 + Rugg & Taylor 2016, Brewer & Lewis 2024, O'Neill 1944, Brumbaugh 1974/76, Clemens 2016 essays, Janick & Tucker 2018, Pelling 2006, Taiz 2011 | need institutional or library access; cannot be pulled by an agent | [high / low] | Clemens 2016 is the only route to the Yale 2014 forensic details; Timm & Schinner is the main rival producer |
| — | Not obtainable now: raking light, a glyph-level segmentation, the Arizona internal C14 report, the Kircher carteggio scans, Velinska (unarchived), Knowles' list (not located) | — | — | Record them as gaps, not tasks |

Register recommendations (no new files; edits belong to whoever owns the registers):
- Refresh the VKB `sources` HAVE/MISSING flags from disk (A3) and link `library/catalogue_v2.tsv` into the VKB as one external table rather than a parallel catalogue. [medium / low]
- Mark `data/facsimile_full/MANIFEST.tsv` as defective in INVENTORY (label only, no move) until the replacement exists. [low / low]
- Add an S-section and B-colour page_facts pull: voynich.nu q19/q20 page descriptions are already crawled and only need parsing. [medium / low]
