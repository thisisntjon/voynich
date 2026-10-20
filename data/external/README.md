# data/external — untrusted downloads for the Voynich campaign (Phase 0, item 3)

Fetched 2026-10-17 16:15–16:30 PDT (clock read with `date`) by the data agent. Every directory here is an
untrusted download: never run code from inside them; read them only with `python -I` scripts that live in
`tools/`. Sizes are `du -sh` of the directory. Token counts come from `tools/ivtff_tokens.py`
(simple IVTFF tokeniser: `<...>` tags dropped, `[a:b]` takes a, `{...}` braces removed,
`. , - =` are breaks, `? ! *` uncertainty marks stripped). Our own data/ZL3b-n.txt gives
pages=227 loci=5385 tokens=38255 types=8708 with the same tool, so counts are comparable.

| # | Resource | Status | Local dir | Size |
|---|----------|--------|-----------|------|
| 1 | voynich.nu IVTFF transliterations (GC, FSG, CD, IT, VT, LSI, RF) | FOUND | voynich-nu-ivtff/ | 4.0 MB |
| 2 | Schwartz 2026 preprint + extracted text | FOUND | schwartz-2026-preprint/ | 8.1 MB |
| 3 | Timm & Schinner self-citation generator (Java source + jar, iOS app source, arXiv 1407.6639) | FOUND | timm-schinner-generator/ | 142 MB |
| 4 | Lindemann & Bowern entropy corpora + R/Python code (github chirila/Voynich-public) + papers | FOUND, slimmed 2026-10-17 18:10 | bowern-lindemann-entropy/ | 45 MB (was 992 MB) |
| 5 | Gaskell & Bowern gibberish corpus (github danielgaskell/voynich) + both CEUR papers | FOUND | gaskell-bowern-gibberish/ | 78 MB |
| 6 | Word bounding boxes: Rozanova–Temerev voynich-units repo (voynichese.com boxes, 223 folios) + Yale IIIF manifest | FOUND | word-coordinates/ | 24 MB |
| 7 | Cribs: f68r1–r3 star labels (voynich.nu + Stolfi + Bax), zodiac label files f70v1–f73v, Sherwood plant list (124 folios), f116v readings | FOUND (partial) | cribs/ | 2 MB |
| 8 | Period nomenclators: Meister 1906 (primary, archive.org), Domnina on Tranchedini, facsimile-publisher description of Cod. Vind. 2398, blog notes | PARTIAL | nomenclators/ | 37 MB |
| + | Naibbe cipher (Greshko 2025): Zenodo supplement (Voynichesque.xlsm macro workbook) + forum thread; Cryptologia HTML/PDF blocked (403) | PARTIAL | naibbe-greshko/ | 7.5 MB |
| + | Papers: Rozanova–Temerev 2608.17096 (+arXiv source/ancillary), Parisel 2604.19762, Zattera CEUR paper10, Bowern–Gaskell lingbuzz 005939, Montemurro–Zanette 2013, arXiv 2609.20835 | FOUND | papers/ | 33 MB |

---

## 1. voynich-nu-ivtff/  (https://www.voynich.nu/data/ ; index in 000_README.txt, format spec in ivtff.xlsx)

License: files carry voynich.nu headers; Zandbergen asks for citation; no formal license stated (treat as research-use).
All IVTFF 2.0 except LSI (IVTFF 1.5 beta). Header line `#=IVTFF <alphabet> <ver>` gives the alphabet.

| File | Transliteration | Version | Alphabet | pages | loci | tokens | types | Coverage |
|------|-----------------|---------|----------|-------|------|--------|-------|----------|
| GC2a-n.txt | Glen Claston | 2a (2023-02-05, mod 2025-06-25) | **v101** (not losslessly convertible to EVA) | 226 | 5367 | 40681 | 9688 | 99.7% of loci; labels often grouped per locus |
| voyn_101.txt | Claston original (non-IVTFF, `<1r.1>` tags, cp1252 chars) | — | v101 | — | — | — | — | source of GC2a |
| FG2a-n.txt | Friedman Study Group | 2a (2023-02-02) | **FSG** (upper-case) | 202 | 4060 | 33293 | 6734 | 75.4%: paragraph + 98 labels only, no circular/radial text |
| CD2a-n.txt | Currier / D'Imperio | 2a (2023-02-02) | **Currier** (upper-case) | 131 | 2196 | 15980 | 4200 | 40.8%: herbal-heavy, paragraphs + 21 labels |
| IT2a-n.txt | Takahashi (as in LSI, 1999 state) | 2a (2023-02-02, mod 2025-06-25) | **Eva-T** (basic EVA) | 225 | 5215 | 37026 | 8547 | 96.8%, full ms incl. circular/radial |
| VT0e-n.txt | Takahashi via voynichese.com (auto-generated) | 0e | Eva-T | 225 | 5207 | 37886 | 8078 | ~97% |
| LSI_ivtff_0d.txt | Landini–Stolfi Interlinear (all transcribers interleaved per locus) | 0d beta | Eva-T | 227 | 17344 | 119016 | 13019 | 99.2%; **token count is the sum over transcribers** — split by the transcriber letter in the locus tag before use |
| RF1b-e.txt | Reference transliteration = ZL+GC merged via STA1 alphabet, full extended EVA (@nnn; codes) | 1b | Eva (extended) | 227 | 5385 | 37756 | 9818 | 100% |
| RF1b-er.txt | same, basic EVA | 1b | Eva | 227 | 5385 | 37736 | 8846 | 100% |

Coverage figures from https://www.voynich.nu/extra/sp_transcr.html (fetched, not saved). The token
counts for CD/FG/GC are in different alphabets (one v101 char can be several EVA chars), so cross-file
comparisons need an alphabet map; ivtff.xlsx and the voynich.nu "sta" pages document the STA1 bridge.
Top-10 types agree across the EVA files (daiin, ol, chedy, aiin, shedy, chol, or, ar, chey ...).

Note 2026-10-18 16:07 PDT: `ivtff_format.pdf` (and its `.pdf.txt`) is a 355-byte HTML 404 page, not the spec; left in place (see `NOTE-ivtff_format.pdf.txt`). The real IVTFF format PDF is `ivtff_format.real.pdf` (https://www.voynich.nu/software/ivtt/IVTFF_format.pdf, 1,171,234 bytes, sha256 7ac9c4a8...6939d49).

## 2. schwartz-2026-preprint/  (https://bootloops.ai/voynich.pdf, 8.3 MB, 43 pp., dated 2026-10-01; text in text.txt)

Matthew D. Schwartz (Harvard Physics), "How the Voynich Manuscript was written". Preliminary; header says
"Some content remains AI-generated and is still being validated". No license stated (author preprint).

Summary (20 lines):
1. Thesis: turn every proposed reading and every proposed meaningless-text generator into a probability model and score it on withheld pages; readings fail, a keyless writing procedure fits.
2. Data: ZL transliteration, EVA, 227 text pages, ~38k tokens; "folded" parsing (iin, ii, ee, ch, sh as units) is primary; Currier A/B and Fagin Davis's five hands taken as given.
3. Method: Bayesian evidence computed exactly (closed forms/recursions, rational arithmetic) for multinomial/Markov/mixture models (Schwartz & Sen 2026).
4. Held-out design: every model is fitted on one half of a scribe's pages and scored on the other half; mechanism families, languages, statistics and thresholds fixed before any manuscript page was scored.
5. Validation: each solver first had to recover a known answer from real Latin/Hebrew/Arabic disguised by the mechanism under test; a family is excluded only where that recovery succeeded (Table 1 gives the power).
6. Reading criterion: the decode must (a) rank the hypothesised language first by character statistics and (b) cost bits/word within a window calibrated on comparison texts in that language; codebooks need a word-order measure above threshold.
7. Six principal languages (scripture templates): Vulgate Latin, unpointed Hebrew, modern Arabic Bible, Italian, German, English.
8. Twelve further languages (Table 4): Greek, Czech, Polish, Hungarian, Spanish, French, Welsh, Ukrainian, Turkish, Persian, Vietnamese, Nahuatl.
9. Mechanisms tested: simple and verbose substitution, consonantal (abjad) writing, abbreviation, codebooks, fixed-rule anagramming (Hauer–Kondrak), the Naibbe cipher, alternative reading orders and character inventories. Free anagramming (Newbold) deliberately untested.
10. Result 1: no reading system survives on withheld pages in any language; closest misses are Turkish anagram (0.2 bits/word outside window) and consonantal Hungarian (0.7); all 282 further-language hypotheses fail.
11. "Decipherment illusion" (§4.7): a free search over keys yields several bits/word of spurious signal on any text, which is why readings keep being announced.
12. Result 2: knowing a word barely predicts the next (held-out gain 0.010 / 0.019 bits for the two hands), lower than every one of 27 comparison texts incl. recipes, glossaries, a botanical catalog.
13. Yet the last glyph of a word predicts the first glyph of the next as strongly as in a recipe collection (edge-glyph coupling 0.130 / 0.243 bits, shuffle-corrected).
14. Generator procedure (§5.2, Table 2): per word, ~3/4 are frequency-weighted REUSE from the scribe's own vocabulary; ~1/50 (Scribe 1) to 1/20 (Scribe 2) are COPIES of one of the preceding ~20 words, mostly same page, nearly verbatim; the rest (~1/4, <1/5) are COINED letter-by-letter from the scribe's glyph habits.
15. Plus two habits: preferred words at line boundaries (distinct words, not edge-modified forms) and short-range word-length autocorrelation; refitted jointly these add +0.14–0.19 bits/token.
16. Model check: of 22 summary statistics the fitted procedure misses 2–3 per hand (self-simulation reaches that with p=0.16/0.06); unigram, token-shuffle and randomized-vocabulary controls miss 6–11 and are rejected.
17. Still unexplained by any generator (theirs, Timm–Schinner, Rugg grille, Naibbe): the edge-glyph coupling (generated pages give 0.009/0.001 bits), too-rare adjacent near-repeats, too-few hapaxes and too-frequent same-initial consecutive lines for Scribe 2.
18. Affixes/cores (§5.3): affixes and cores combine near-independently, filling a dense grid (98% of top 10x10 cells occur) — no comparison vocabulary matches this jointly.
19. Weak trace of content #1 (§5.4, Table 3): a LABEL REGISTER — the 864 primary label tokens favour initial o- beyond any position effect and recur across pages less than a nomenclature of real objects would (survives shuffled-label and running-text nulls).
20. Weak trace #2: a faint dependence of word choice on subject/section that survives fake-section and quire-aligned nulls; conclusion: text written onto finished drawings, a book "made to be looked at, not read".

## 3. timm-schinner-generator/

- SelfCitationTextgenerator-main.zip / dir: https://github.com/TorstenTimm/SelfCitationTextgenerator (MIT, (c) 2019 Torsten Timm; Zenodo DOI 10.5281/zenodo.2531632). Java source (37 files, `source/src/main/java/de/voynich/text/...`: Glyph.java, GlyphGroup.java, SelfCitationTextGenerator.java, canfollow/ (CurveLineCanFollow, StatisticCanFollow, VoynichCanFollow), morph/ (SlimGroupMorpher), sourcechooser/ (Page/Position/Random)), runnable `executable/text-generator.jar` + conf.properties (defaults: 1200 lines, 55 chars/line, 29 lines/page, seed line f103v.P.9, same_position_probability=28, morph probabilities add/remove 20, combine/split 30, replace 50, reuse_last 10). PROPERTIES.md documents every knob. Also Gephi graph files per quire and the chey_chedy.md note. The zip is 66 MB because of the gephi/graphs data.
- VoynichTextGenerator-master.zip / dir: https://github.com/TorstenTimm/VoynichTextGenerator — iOS Swift app (AutoCopyTextGenerator.swift, Glyph.swift, Substitution.swift, Levenshtein.swift). No license file seen.
- arxiv_1407.6639.pdf/.txt: Timm 2014 "How the Voynich Manuscript was created" (96 pp).
- Timm & Schinner 2019/2020 Cryptologia paper itself is paywalled; not fetched.

## 4. bowern-lindemann-entropy/

- chirila-Voynich-public.zip / dir (212 MB zip, 774 MB unpacked, 477 files): https://github.com/chirila/Voynich-public — the corpus named in the paper ("Corpus materials and code are available from github.com/chirila/Voynich-public"). Contents: Corpora/Voynich_texts (per transcription/hand/language), Corpora/Historical_texts (18 texts, 8 languages, list in Historical_texts_list.xlsx), Corpora/Wikipedia_texts (311 languages, list in Wikipedia_texts_list.xlsx), *_statistics.csv (the entropy tables: h1, h2, conditional entropy etc. per text), R code/ (Entropy_Functions.R, 0–6 Rmd pipeline), Python code/ (wiki corpus builders), plus a Gibberish_texts folder. No LICENSE file seen at top level — check before redistribution.
- lindemann_bowern_2020_lingbuzz_v1.pdf (lingbuzz 005522 v1), lindemann_bowern_2021_yale.pdf/.txt (2021 revision, 53 pp).
- The *_statistics.csv files are the "entropy tables" PLAN.md asks for.

## 5. gaskell-bowern-gibberish/

- danielgaskell-voynich-main.zip / dir: https://github.com/danielgaskell/voynich (modified MIT for code + gibberish data; Voynichese and meaningful sets keep their own terms). data/gibberish_transcriptions (38 anonymised volunteer gibberish texts, Unicode, unzipped), data/meaningful (72 texts), data/voynichese (5 transcriptions), results/metadata.csv (text, specialist flag, group), results/metrics_paperv1.csv and metrics_enciphered.csv (the metric values per text), results/plots.md. The metric-computation code itself is NOT in this snapshot (only data/ and results/), although the README says "code and datasets".
- gaskell_bowern_2022_gibberish.pdf/.txt (CEUR-WS 3313 paper4) and bowern_gaskell_2022_enciphered.pdf (paper6).

## 6. word-coordinates/

- lrozanova-voynich-units-main.zip / dir: https://github.com/lrozanova/voynich-units (MIT, (c) 2026 Rozanova; third-party data keep their terms). **data/voynich-units/morphometry_voynichese/voynichese_boxes/<folio>.js — per-token bounding boxes for 223 folios, scraped from voynichese.com** (integer coords snapped to a 3-px grid on a ~600-px-wide layout; token width 15–90 px). The paper (papers/rozanova_temerev_2026_arxiv_2608.17096.txt §2.6, §4.2) says provenance is "incompletely documented" and the boxes measure a transcriber's reading as much as ink geometry; their blind direct-pixel audit on 700-px Yale IIIF derivatives is in data/direct_pixel/results_unblinded.csv (300 boundaries: gap px, folio, line, flanking words). Measurement pipeline: analysis/direct_pixel/measure_direct_pixels.py. Also includes ZL3b.txt, voyn_101.txt, naibbe and self-citation control texts.
- The same ancillary bundle is in papers/rozanova_2608.17096_src/anc/ (arXiv e-print).
- yale_manifest.json: IIIF Presentation v3 manifest https://collections.library.yale.edu/manifests/2002046 (213 canvases incl. covers). yale_folio_to_iiif.tsv maps folio label -> IIIF image service id -> native size (e.g. f1r = https://collections.library.yale.edu/iiif/2/1006076, 2972x3766). Direct download per folio works without login: `<service>/full/full/0/default.jpg` (verified HTTP 200 on a /full/500,/ request), full TIFF at https://collections.library.yale.edu/download/tiff/<id>, whole-ms PDF at https://collections.library.yale.edu/pdfs/2002046.pdf (200). Rights: public domain per the Yale catalog.
- zenodo.json: Zenodo 18595646 "Voynich Manuscript - Full Dataset" (Papanikolaou) — embargoed until 2027-12-31, Greek-reading spreadsheets, no coordinates. Not useful.
- Not found: any glyph-level segmentation dataset.

## 7. cribs/

- voynich_nu_f068r1_tr.txt, f068r2, f068r3, f067v2: voynich.nu per-page transliteration files with Stolfi's locus-by-locus comments (star ring labels with clock positions).
- voynich_nu_f070v1 ... f073v_tr.txt (11 files): zodiac pages Pisces -> Sagittarius, label loci (`@L`) with position notes.
- stolfi_f68r3.htm / stolfi_f68r3_data.txt, stolfi_f70v2.htm, stolfi_f72v2_data.txt: Stolfi's 1998 page notes.
- bax_stars_analysed2_p1163_wayback.html(.txt): Bax 2014 table of 64 star labels (EVA, numbered; 70% o-initial) from f68r1–r3; bax_stars_f68r_p803_wayback.html(.txt): his earlier f68r post. (Live stephenbax.net returns 403; these are Wayback copies.)
- teague_cracks_in_the_ice.doc, f68r1_event_jvs.pdf: Journal of Voynich Studies items proposing Aldebaran/Pleiades identifications (hobbyist; leads only).
- sherwood_plant_list_p1..p14.html(.txt): Edith & Erica Sherwood's 124 folio-by-folio plant identifications (Wayback copies; live site is down). julianbunn_GA_Sherman_spreadsheet.htm(.txt): side-by-side Sherwood vs Dana Scott IDs. Tucker & Talbert 2013 HerbalGram list not fetched.
- f116v: stolfi_f116v.htm, stolfi_note016_f116v.txt (readings: michiton oladabas multos te tccr cerc portas; Newbold, Panofsky, Brumbaugh variants), ciphermysteries_f116v_p4559.html(.txt).

## 8. nomenclators/

- meister_1906_geheimschrift_kurie.pdf (35 MB) + _djvu.txt: Aloys Meister 1906, *Die Geheimschrift im Dienste der päpstlichen Kurie*, archive.org id diegeheimschrift00meis (public domain). Primary source for papal keys; mentions Simonetta 1474 and Milan/Venice usage (grep "Mailand", "Simonetta", "Mantova"). It does NOT contain the Milanese 1448 key table.
- Meister 1902, *Die Anfänge der modernen diplomatischen Geheimschrift* — NOT found on archive.org (creator search returns only the 1906 volume). Per the ciphermysteries page it prints a full Milanese key + nomenclator of 14 March 1448 (p.30), a 1483 key (p.31), Modena 1435 (p.35), Florence 1424 (p.50). Still needed as a primary source.
- domnina_tranchedini_verbum.pdf/.txt: review article on Nicodemo Tranchedini's *Vocabolario* (ojs.ppke.hu/verbum) — about the lexicographer, NOT the cipher ledger; low value.
- facsimiles_com_tranchedino.html(.txt): publisher description of Cod. Vind. 2398 (Francesco Tranchedino, Sforza chancery c.1475): "about 300 cipher keys", period 1450–1496; other sources say ~200 or "287 complete + 4 partial". Each key = alphabet with homophones (more for vowels), nulls, digraph/trigraph signs, and a proper-name nomenclature; forum owners of the 1970 ADEVA facsimile (Höflechner intro) report "a couple of hundred glyphs" per cipher. These are publisher/forum numbers, UNVERIFIED against the facsimile.
- ciphermysteries_tranchedino_p3700.html(.txt): Pelling blog with the Meister 1902 page references above.
- Simeone de Crema 1401 (Mantua): only secondary web mentions found (first Western homophonic cipher, extra symbols for vowels); no symbol count sourced. Kahn *Codebreakers* and Buonafalce, Cryptologia 32(1) 2008 "Cicco Simonetta's cipher-breaking rules" are paywalled/not fetched.
- Bottom line for item 8: no digitized table with a verified code-group count was obtained; the primary leads are Meister 1902 (not online) and the 1970 Höflechner facsimile edition.

## naibbe-greshko/

- Greshko 2025, Cryptologia, doi 10.1080/01611194.2025.2566408: the forum thread (voynich_ninja_thread5081.txt) says it is open access, but tandfonline returned 403 to both curl and WebFetch — HTML/PDF NOT obtained.
- zenodo_17219445.json: supplement record (CC-BY-4.0); files: Naibbe Cipher.xlsx, Voynichesque.xlsm, Supplementary Materials 1–4 PDF, several Figures xlsx, Gephi chart. The project already holds Naibbe_Cipher.xlsx and the supplement PDF in data/naibbe_zenodo_17219445/ (untouched). Added here: Voynichesque.xlsm (7.7 MB, the macro workbook that implements the cipher — VBA; do not enable macros).

## papers/

rozanova_temerev_2026_arxiv_2608.17096.pdf/.txt (+ e-print source rozanova_2608.17096_src/ with figures and the anc/ bundle), parisel_2026_arxiv_2604.19762.pdf/.txt, zattera_2022_ceur3313_paper10.pdf/.txt (12-slot grammar), bowern_gaskell_lingbuzz_005939.pdf/.txt, montemurro_zanette_2013_plosone.pdf/.txt (CC-BY), pastiche_llm_2026_arxiv_2609.20835.pdf. All open access.

## Tools written (in ../../tools/, outside the downloads)

- ivtff_tokens.py — IVTFF tokeniser / counter (run: `python -I tools/ivtff_tokens.py FILE...`).
- pdf2text.py — pypdf text extraction (re-adds the user site-packages path because -I drops it).
- html2text.py — tag stripper for saved HTML pages.


## Pruned 2026-10-17 18:10 PDT (user-approved)

- `bowern-lindemann-entropy/`: the 774 MB `chirila-Voynich-public/` clone and its 203 MB zip were
  deleted. Kept as `Voynich-public-master-slim/`: `Corpora/*_statistics.csv` (the three entropy
  tables), `README.md`, `R code/`, `Python code/`. Re-fetch: https://github.com/chirila/Voynich-public.
- `jre/` (192 MB portable Temurin 21 JRE) deleted. `ctl_timm_schinner.py` needs it only to regenerate
  `data/controls_synthetic/timm_schinner*.txt`, which are filed; re-download from
  https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jre/hotspot/normal/eclipse?project=jdk
  into `data/external/jre/` to rerun.
- `timm-schinner-generator/*.zip` (duplicate archives of the unpacked dirs) deleted.


## cremma/ — fetched 2026-10-17 20:17 PDT (phase-1 s18, approved scope: transcription XML only, no images)

- Source: https://github.com/HTR-United/CREMMA-Medieval-LAT (CREMMA Medii Aevi), release tag `v0.1.2`,
  tree/commit sha `9439fe33a07eeb2814fa4b94b65c280f20aa6ec1` (2023-10-04). Fetched by
  `tools/fetch_cremma.py` (run with `python -I`): GitHub git/trees API (recursive, not truncated, 662
  blobs) at that sha, then raw per-file GETs from
  `https://raw.githubusercontent.com/HTR-United/CREMMA-Medieval-LAT/v0.1.2/<path>`. Selection:
  `data/*/*.xml` plain variant only (121 files, the `.chocomufin.xml` twins excluded) plus `README.md`,
  `data-registry.csv`, `table.csv`, `htr-united.yml`. Byte sum checked before download: 6,982,175 B
  (XML 6,952,796 B + metadata 29,379 B) against the 200 MB stop. Images, txt, pdf, tex, ttf not fetched.
- Files: 125 selected = 121 XML + 4 metadata; plus `tree_v0.1.2.json` (the raw tree response) and
  `FETCH-MANIFEST.txt` (path, bytes, git blob sha1, source). Folder total 127 files, 7,168,138 B.
- Reuse: `cremma-medieval-lat-mlc1/` (83 files, created 20:04 by another session, unlogged, left
  untouched) was compared per path by git blob SHA-1 (sha1 of `blob <len>\0` + bytes); 82 files were
  byte-identical and were copied from it (81 XML + data-registry.csv, 5,216,588 B); 43 files were
  downloaded (40 XML + README.md, table.csv, htr-united.yml; 1,765,587 B). Its README.md differs from
  the v0.1.2 one (one BIS-193 link, i.e. the `main` version), so the tag version was downloaded.
- Verification: every file's git blob SHA-1 equals the tree entry's sha and the byte length matches,
  checked on the bytes received and again on the bytes written to disk: 125/125 OK, 0 mismatches.
- Licence: repo has no LICENSE file and README.md has no licence statement; `htr-united.yml` states
  CC-BY 4.0 (https://creativecommons.org/licenses/by/4.0/); the data paper (JOHD, doi 10.5334/johd.97)
  states CC0 per `workflow/research/phase-1-cremma.md` §2 (not re-read this session; Zenodo record
  8407213 says "other-open" per the same note). Conflict recorded, unresolved.
- Downstream: `tools/cremma_to_meta.py` -> `data/controls_realline/cremma_*.meta.json` (54 sidecars) and
  `data/controls_realline/CREMMA_MANIFEST.md`. Audit fixture (support-phase1-audit.md item 2): on
  Arras-861/056r, 12 of 70 transcribed MainZone lines change token count under the delimiter-split rule versus
  the delete-and-join rule (the audit reported 12 of 70 with its own tokenizer).

## 9. yale_scans/  (s45, fetched 2026-10-17 22:32-22:37 PDT by tools/fetch_yale_scans.py, log runs/s45/fetch_yale_scans.log; entry written 22:56 PDT, clock read with `date`)

- Source: Yale Beinecke Library IIIF Presentation v3 manifest https://collections.library.yale.edu/manifests/2002046 ("Cipher Manuscript", Beinecke MS 408; public domain per the Yale catalog). manifest_2002046.json: 403,033 bytes, sha256 317d58fd9ea90392a83d9858a91eada3d0b41416a3c835857dc0154bd123a309.
- pages/: full-resolution JPEG (`<service>/full/full/0/default.jpg`, ~2700-3000 x 3700-3800 px) of every canvas whose label names a folio (204 of 213 canvases; covers, flyleaves, head/tail/spine/fore-edge skipped). Total 546583767 bytes (523 MB on disk) in 268 s, 4 workers; cap was 6 GB. Every file's URL, byte count and sha256 is in yale_scans/MANIFEST.md (206 rows); pages_index.json maps file -> canvas label -> IIIF service id -> native size.
- Canvas labels are Yale's: single folios "1r" .. "116v"; foldouts appear as composite canvases ("69v and 70r", "85r (part)", "101v (part) and 102r") and the multi-page folios f67r/f68r/f72v/f90r/f95v are one canvas each. tools/segment_scans.py maps single-folio labels to ZL3b page ids and lists the rest as unmatched (runs/s45/segment_summary.json).
- Untrusted downloads: read only via `python -I` scripts in tools/; nothing is executed from this directory.

## models/ — s48 frozen vision weights (added Sat Oct 17 23:59:18 PDT 2026, clock read with `date`)

Downloaded by the s48 agent with huggingface_hub.snapshot_download (allow_patterns: *.json, model.safetensors,
*.model); used read-only by tools/plant_regions.py (transformers 4.57.5, use_safetensors=True). Total ~1.1 GB.

| dir | source URL | weights file | bytes | sha256 |
|---|---|---|---|---|
| models/dinov2-base | https://huggingface.co/facebook/dinov2-base | model.safetensors | 346345912 | d73036b56966966d07975d696bde331762f37297e2f095de8cea0040c3aa0841 |
| models/siglip-base-patch16-224 | https://huggingface.co/google/siglip-base-patch16-224 | model.safetensors | 812672320 | 2c63cb7d1f2e95ba501893cbb8faeb4ea9a3af295498d35097126228659c2af8 |

(openai/clip-vit-base-patch16 was tried first; it ships only pytorch_model.bin (pickle), so its config files were
deleted and SigLIP was used as the CLIP-type model.)

## lit-20261018/ — fake downloads found and handled (2026-10-18 16:07 PDT, clock read with `date`)

Three files saved under document names are HTML error pages. None was deleted or overwritten; each has a `NOTE-<name>.txt` beside it.

| File | What it actually is | Real document | Result |
|---|---|---|---|
| `voynich-nu-ivtff/ivtff_format.pdf` | HTML 404 page (355 B) | `voynich-nu-ivtff/ivtff_format.real.pdf` from https://www.voynich.nu/software/ivtt/IVTFF_format.pdf | FETCHED (PDF 1.7, 1,171,234 B) |
| `lit-20261018/meister-1902-pelling-zip/Meister1902.zip` | HTML 404 page (355 B) from nickpelling.com (still 404) | `Meister1902.real.zip` from the Wayback Machine copy of http://www.nickpelling.com/voynich/Meister1902.zip | FETCHED (zip 11,273,577 B, page scans; integrity test passed, not extracted). Closes the 'Meister 1902 not online' gap in section 8 |
| `lit-20261018/greshko-tandf-pdf/greshko.pdf` | HTML Cloudflare challenge page (5,865 B) from tandfonline | Greshko 2025, Cryptologia, doi 10.1080/01611194.2025.2566408 | NOT OBTAINED: tandfonline 403; Unpaywall/OpenAlex list only the publisher page; no Wayback snapshot |

## intake-phase1/ — primary documents fetched 2026-10-18 21:46 PDT

Untrusted downloads. Hashes are in `MANIFEST.tsv`. Quotes copied from text layers are in `QUOTES.md`. McCrone is an image scan and was not excerpted.

| File | What it is | Licence note |
|---|---|---|
| `hodgins-2009.pdf` | Hodgins to McCarthy, 17 February 2009 | No licence on the PDF. Hosted by Zandbergen |
| `mccrone-2009.pdf` | McCrone MA47613 scan, 8 pages, created 2009-04-01 | Not CC. Stored whole |
| `davis-2020.pdf` | Davis, Manuscript Studies 5.1, archive.org copy | Licence not stated in the first pages that were read |
| `layfield-davis-2026-pdf.pdf` | Layfield and Davis, Digital Medievalist 19 (2026), with Table 5 | Text CC BY 4.0. Figures may differ |
| `zattera-slot.txt` | Zattera slot IVTFF 1.5, built 2021-10-22 | Repo is GPL-3.0. The transcription's own grant is not a separate licence line |
| `greshko-supplement.pdf` | Zenodo 17219445 supplementary PDF | CC BY 4.0 |
| `greshko-entropy-csv.txt` | EVA rowwise conditional entropy 1.954 | GitHub `naibbe-cipher` |
| `guzy-2022.pdf` | Guzy, CEUR Vol-3313 paper 16 | CC BY 4.0 |
| `neal-marci-1665.html` | One Neal transcription page | No licence line. Cite only |
| `honkapohja-2021.pdf` | Abbreviation survey, Digital Medievalist 14 (2021) | Text CC BY 4.0 |
| `somogyi-2016.pdf` | Somogyi on Italian monoalphabetic ciphers | Licence line not read |

## intake-phase2/ — 2026 deposits fetched 2026-10-18 22:00 PDT

Untrusted downloads. Nothing in the zips was executed. Hashes are in `MANIFEST.tsv`. The identity calls are in `COMPARE.md`. None of these numbers is the frozen profile (`c-002` h2 2.109 on 34,857 tokens; `c-126` joint row 2.11 / 7,025 types / hapax 0.68).

| File | What it is | Licence note |
|---|---|---|
| `chang-2026.pdf` plus `chang-2026-package.zip` | Chang, inter-token preprint, Zenodo 19869630 | Text CC BY 4.0. Code MIT. Data follows the Zandbergen-Landini terms |
| `koshy-2026.zip` | Koshy inventory-transfer note, Zenodo 21634012 | MIT |
| `signorino-2026.pdf` plus `.ods` | Signorino height-transition entropy, Zenodo 20582885 | CC BY 4.0 |
| `amador-2026.pdf` plus `.zip` | Amador transcription-disagreement note, Zenodo 22982333 | CC BY 4.0. Zip is code; raw output member is empty |
| `lux-2026.pdf` | Lux preregistered stability audit, Zenodo 22850758 | CC BY 4.0 |
| `kinnison-2026.pdf` plus two figures | Kinnison positional-entropy preprint, Zenodo 18155058 | CC BY 4.0. Not the journal article |
| `helton-2026.pdf` | Helton nomenclator claim, record 19154142, file from 19154143 | CC BY 4.0. A candidate, not a reading |

## wave5-*/ — gap-analysis library batch 1 (fetched 2026-10-18 21:43 PDT, clock read with `Get-Date`)

Collection only (gather + validate; NOT ingested into findings/VKB, sorting deferred by user instruction).
Fetched by `tools/fetch_library_wave5.py` (run `python -I` from repo root); per-file URL, licence
evidence, bytes, sha256 in `wave5-MANIFEST.json` (26 items). Independent verification (recompute
sha256 from disk, PDF magic, zip integrity, Zenodo API md5 cross-check): 26/26 OK.

| Dir | Contents | Licence evidence |
|---|---|---|
| wave5-ceur3313/ | CEUR-WS Vol-3313 papers 1,2,3,5,7,8,9,11-16 (4,6,10 already held) | CC-BY-4.0 volume page |
| wave5-beasley-2024/ | Beasley OU thesis PDF, 621,614 B (ShareOK bitstream 7915fbcc) | open repository bitstream |
| wave5-parisel-2025/ | arXiv:2509.10573 directionality | CC-BY-4.0 per abs page |
| wave5-rao-2010-indus/ | Rao et al. J10-4016 (NSB entropy) | ACL Anthology open |
| wave5-decknamen-tei/ | Ruland 1612 + Sommerhoff 1701 TEI-XML (Zenodo 14638445) | cc-by-4.0 via API; md5 match |
| wave5-htr-model-medieval/ | HTR mlmodel 23.7 MB + metadata (Zenodo 7547438) | cc-by-4.0 via API; md5 match |
| wave5-ndd-entropy/ | simomarsili/ndd zip (64 files) | BSD-3-Clause via GitHub API |
| wave5-neurodecipher/ | j-luo93/NeuroDecipher zip (69 files) | NO LICENSE via API — read-only reference |
| wave5-cnt-tironian/ | CNT Tironian image corpus zip (11 files) | NO LICENSE via API — read-only reference |
| wave5-naibbe-code/ | greshko/naibbe-cipher zip, 45.6 MB (545 files) | MIT via GitHub API |
| wave5-fuchs-1542/ | Fuchs De historia stirpium djvu.txt | public domain (BHL) |
| wave5-geomancy-fasciculus/ | Fasciculus geomanticus djvu.txt | public-domain scan |

Already-held duplicates deliberately NOT re-fetched: CoReMA pools (`data/controls_daybreak/corema_pools/`),
Llull/Tacuinum/De gradibus djvu (`data/controls_tabular*/`), Naibbe supplements
(`data/naibbe_zenodo_17219445/`), Rozanova units (`data/external/word-coordinates/`).
Not obtained this batch: DISHAS tables (no direct file route verified), CATMuS dataset parquet
(>cap; model only), Sign2Vec data (copyright-closed), Gallica BnF (403), Simon Online (bot wall).
Untrusted downloads: never execute code from these dirs; read via `python -I` tools only.

