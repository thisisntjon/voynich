# Voynich MS: bird's-eye view (library entry, lib01, 2026-10-19)

One page. Facts are quoted or paraphrased from the source named on each line; open the source before citing a number.
This page does not replace the project's source of truth (`workflow/FINDINGS-GRAPH.yaml`, `.inventory/registers/`, results files).
Longer syntheses already in the project: `reports/Voynich decipherment attempts and failures.md` (2026-10-17) and
`reports/Voynich public source gaps.md` (2026-10-18), `workflow/research/public-baseline.md`.

## Hard facts (physical object and history)

| fact | source (held copy) |
|---|---|
| Parchment radiocarbon date: four bifolio samples, combined 1404-1438 (95%); dates the skins, not the writing or the ink | Hodgins to McCarthy, 17 Feb 2009 (`data/external/intake-phase1/hodgins-2009.pdf`); Zandbergen `extra/carbon.html` (`library/web/voynich_nu/`) |
| Calf-skin parchment (protein analysis 2014); goat-skin cover; not a palimpsest (microscopy 2009, multispectral 2014) | Zandbergen `origin.html` |
| Iron-gall ink throughout with minor variation; mineral pigments; materials consistent with a 15th-c. date | McCrone report 1 Apr 2009 (`intake-phase1/mccrone-2009.pdf`, image scan); `origin.html`; Clemens (ed.) 2016 Yale facsimile (catalogue) |
| Production bifolio by bifolio: Currier's hands and text statistics are consistent per bifolio | `origin.html`; Currier 1976 seminar (NSA, catalogued) |
| Currier A / B "languages" (Currier 1970s); Davis 2020 identifies five scribal hands; Layfield & Davis 2026 bifolio table | Davis 2020 Manuscript Studies 5.1 (`intake-phase1/davis-2020.pdf`); Layfield & Davis 2026 Digital Medievalist 19 (`intake-phase1/layfield-davis-2026-pdf.pdf`) |
| Provenance chain: Georg Baresch (Barschius) letter to Kircher 1639; Marci letters to Kircher 1640/1641; Marci letter of 1665 sent with the MS to Kircher in Rome; earlier Kircher-Moretus mention found by Smolka | Zandbergen `letters.html`; Neal translations (`library/web/philipneal/`, Wayback copies) |
| "Jacobus de Tepenec" (courtier of Rudolf II) faded name on f1r; Marci letter reports ownership by Rudolf II (sale c. 1600 "almost certain" per Zandbergen) | `history.html`, `intro.html` |
| Collegium Romanum (Kircher) library -> Jesuit collection; Wilfrid Voynich acquired it in Italy and showed it in 1912 (the "Villa Mondragone" location rests on Kraus's later statement) | `history.html`, `intro.html` |
| H. P. Kraus donated the MS to the Beinecke Library in 1969; now Beinecke MS 408 | `history.html`; Beinecke IIIF manifest 2002046 (213 canvases, `library/primary/beinecke/manifest_2002046.json`) |
| Catalogue wording still differs: IIIF record "[ca. 1401-1599?]"; pre-1600 page "s. XV ex-XVI [?]" | `reports/Voynich public source gaps.md` (quotes the Yale pages) |

## Schools of thought (what kind of text is it?)

| school | representative published work (in `catalogue.tsv`) | project weight (FINDINGS-MAP sec. 1, 2026-10-19 01:23) |
|---|---|---|
| Natural language written plainly | many language claims (Ninja master list counts 65 language-claim threads, all rejected, per the 2026-10-17 report) | H-01 disfavoured (0 / 17.5) |
| Natural language in an invented verbose / abbreviating script | Lindemann & Bowern 2020; Bowern & Lindemann 2021 | H-17 weakened |
| Cipher: letter substitution, verbose homophonic, table ciphers | Friedman/Tiltman/Currier (NSA papers); Greshko 2025 Naibbe cipher (Cryptologia) | H-02 disfavoured; H-03 disfavoured as built; H-04 excluded at defaults; H-14 narrowed |
| Code / nomenclator / lexical system | Megyesi et al. 2022 (nomenclator sizes) | H-06 live (2.0 / 3.7) |
| Meaningless: hoax, table-and-grille, self-citation, gibberish | Rugg 2004; Rugg & Taylor 2016; Timm & Schinner 2019; Gaskell & Bowern 2022 | H-05 weakened (4.0 / 0.0); H-07 disfavoured as built; H-08 disfavoured |
| Constructed / philosophical language; shorthand or notation | (few published tests) | H-18 live, untested; H-16 weakened |
| Subject matter only (herbal, astrological, balneological, pharmaceutical) | Tucker & Janick 2018/2019; Taiz & Taiz 2011; Panofsky via D'Imperio 1978 | H-20 live, untested |

## Leading decipherment claims and their status

| claim | status and where it was refuted | source |
|---|---|---|
| Newbold 1921/1928: Roger Bacon, micro-shorthand + anagrams | refuted by Manly 1931 (marks are ink cracking; anagrams unconstrained) | `solvers.html`; Manly 1931 Speculum (catalogue) |
| Feely 1943 abbreviated Latin; Strong 1945/47 | rejected | `solvers.html`; report 2026-10-17 |
| Brumbaugh 1978; Stojko 1978 (Ukrainian); Levitov 1987 (Cathar) | not accepted | `solvers.html` |
| Bax 2014 partial decoding (proper names) | candidate readings only; no extension to running text | `page-facts/plants/raw/bax_2014_partial_decoding.pdf` |
| Cheshire 2019 proto-Romance (Romance Studies) | widely rejected; project report notes peer review outside Voynich studies is weak evidence | catalogue; report 2026-10-17 |
| Rugg 2004 hoax via table and grille | mechanism reproduces some statistics; project H-05 weakened (s71) | catalogue; FINDINGS-MAP |
| Timm & Schinner 2019 self-citation generator | reproduces low-level statistics; project H-07 disfavoured as built | catalogue; FINDINGS-MAP |
| Greshko 2025 Naibbe cipher | shows a period-feasible cipher can produce Voynich-like text; not a decipherment | catalogue; project H-04 |
| 2026 Zenodo deposits (hundreds) | self-published, mostly unreviewed; check-first candidates in `unchecked_claims.tsv` | `catalogue.tsv` rows with source zenodo |

## Where this project's findings sit (summary of FINDINGS-MAP, not new results)

Lines are units of the text (F-01); word lengths follow an in-line rhythm that resets at line breaks (F-04); every word is
prefix + core + suffix with line signatures in the affixes (F-11); the same core recurs at short range, unlike language (F-13);
there is no internal crib (F-20). Net weight currently favours a table-and-grille style procedure (H-05) and keeps a
word-level lexical system (H-06) live; plain natural language (H-01) carries the most weight against. Current stage (PLAN.md):
D-073 external validation and held-out meaning only. Use `catalogue_to_findings.tsv` to see which published sources the
project already cites, and `unchecked_claims.tsv` for published claims not yet checked (check-first rule, D-066 dd).
