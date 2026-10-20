# controls_period: period plaintexts for s102 (D-066 (h))

Written 2026-10-18 12:52 PDT (`date`) by the s102 run. Downloads made 12:46-12:50 PDT into the then-empty folders
`raw_it/` and `raw_de/`. They are untrusted data: read as text only by `s102_period_ciphers_recipes.py` (run with
`python -I`), never executed. Files are byte-exact downloads, except `Buoch_von_guoter_Spise_rendered.txt`. That file was
rendered from the parse-API JSON beside it by a scratchpad HTML-to-text script (`python -I`), outside this folder.
The body line ranges and noise filters are in `PERIOD_SRC` in the s102 script, not here. End-of-line hyphenation is
joined. Original spelling is kept. Abbreviations are kept as the '~' / '&' plaintext symbols (s102 docstring).

## Used

| text | file | source URL | edition | language, date | licence | sha256 | body lines |
|---|---|---|---|---|---|---|---|
| P1 (part 1) | `data/controls_realline/cremma_all_marks.meta.json` (pages with hand CLM13027, Egerton821, H318, Latin16195, Phi_10a135; section Medic) | HTR-United CREMMA-Medieval-LAT v0.1.2 (see `data/controls_realline/CREMMA_MANIFEST.md`) | diplomatic HTR ground truth, marks kept | Latin medical MSS, 12th-15th c. | per CREMMA manifest (CC-BY) | be53d490c342df533d2c218a33f5892bba49be377fcf9023da39293b56b01115 | real MS lines, 18,096 tokens |
| P1 (part 2) | `data/controls/latin_macer_floridus.txt` | la.wikisource *De viribus herbarum* (see `data/CONTROLS_MANIFEST.md`) | Panckoucke ed. via Corpus Corporum | Latin herbal-remedy verse, 11th c. | PD | 00c484e965af06b52ff4fc323af3e14071d3476fd59b8f85a5b7ec1e1a7b35b2 | verse lines; fills P1 to 22,500 |
| P2 (part 1) | `raw_it/librodicucinade00fratgoog_djvu.txt` | https://archive.org/download/librodicucinade00fratgoog/librodicucinade00fratgoog_djvu.txt | L. Frati (ed.), *Libro di cucina del secolo XIV*, Livorno 1899 (Anonimo Veneziano); OCR | Venetian recipes, 14th c. | archive.org NOT_IN_COPYRIGHT | f466e12c9ff61a32e1e4534af5d5fa7f28aa4188a954ceb1137c612b9270d75b | 520-2972 |
| P2 (part 2) | `raw_it/b21525213_djvu.txt` | https://archive.org/download/b21525213/b21525213_djvu.txt | F. Zambrini (ed.), *Il libro della cucina del sec. XIV*, Bologna 1863; OCR | **Tuscan** recipes, 14th c. (fills P2 to 22,500; not northern) | Public Domain Mark | 1b167fdb127cbb5c3c9dd4ea5159ffaf497a49580556bcc08cd874d9309d8edf | 1704-4334 |
| P3 (part 1) | `raw_de/bub_gb_I0QSAAAAYAAJ_djvu.txt` | https://archive.org/download/bub_gb_I0QSAAAAYAAJ/bub_gb_I0QSAAAAYAAJ_djvu.txt | F. Pfeiffer (ed.), *Zwei deutsche Arzneibücher aus dem XII. und XIII. Jh.*, Wien 1863; OCR | Alemannic (Zürcher Arzneibuch, 12th c.) and Bavarian-Austrian (13th c.) remedies | Public Domain Mark | 9fa4c19aed390b7629dfb77592ef9a31a9218fcd6b82987bbf380ab9f447789b | 528-3152 |
| P3 (part 2) | `raw_de/Buoch_von_guoter_Spise_rendered.txt` (from `Buoch_von_guoter_Spise_parse.json`, sha256 7f26da93aff18bb446dce0bf37b9875c03eeebd3187e77de4450266d521b9790) | https://de.wikisource.org/w/api.php?action=parse&page=Das_Buoch_von_guoter_Spise | Bibl. des Litt. Vereins Stuttgart IX, 1844 (Wikisource, proofread) | East Franconian (Würzburg) cookery, c. 1350 | Wikisource PD | efb119a0a75104e53bb94978d7cb99bf11b9098362977db733e8e2eeb9c97410 | 98-601 |
| P3 (part 3, fill only) | `raw_de/b24880681_djvu.txt` | https://archive.org/download/b24880681/b24880681_djvu.txt | Konrad von Megenberg, *Buch der Natur*, ed. Pfeiffer, Stuttgart 1861; OCR | Bavarian, c. 1350 (books IV-V: trees and herbs) | Public Domain Mark | 18684bb864ece18f510fa383f0c04828248591926840db7f829e5c03411a1b0a | 21844-27770 (used only past 22,500) |

The printed-edition line breaks of P2 and P3 are not manuscript lines, so s102 re-lines both to ZL3b line lengths.
P1 keeps real manuscript lines and verse lines.

## Downloaded, not used (left in place)

- `raw_it/illibrodeicolori00riccuoft_djvu.txt`: Guerrini and Ricci (eds), *Il libro dei colori*, 1887. Northern Italian pigment recipes, 15th c., with about 9k words of Latin mixed in. Not used, because filtering out the Latin is heuristic. sha256 c74932d8…c843a.
- `raw_it/illibrodellacuc00zambgoog_djvu.txt`: a duplicate of the Zambrini edition with worse OCR.
- `raw_it/illibrodellacuci00bolouoft_djvu.txt`: an HTTP 500 error page.
- `raw_it/b30608235_djvu.txt`: about 3k words, possibly in copyright.
- `raw_it/DueCodiciDiSegreti_djvu.txt`: about 1.7k words.
- `raw_de/Buoch_von_guoter_Spise.wikitext`: transclusion stubs only.
