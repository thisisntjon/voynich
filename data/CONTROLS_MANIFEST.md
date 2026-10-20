# Controls manifest (Phase 0, item 4)

Built 2026-10-17 (controls-builder agent). Loader: `corpora_ext.control_ext(name)` /
`control_ext_lines(name)` / `control_ext_pages(name)` in the project root. Raw downloads sit in
`data/controls_raw/<name>/` (untrusted; read as data only by `build_controls_ext.py`).
Rebuild everything with, from the project root:

    python build_controls_ext.py     # raw -> data/controls/*.txt
    python ctl_nomenclator.py        # nomen_word / nomen_syll / nomen_lines  -> results_ctl_nomenclator.txt
    python ctl_generators.py         # markov1 / rugg_grille / latin_merged / lull table -> results_ctl_generators.txt
    python ctl_naibbe.py             # naibbe_like -> results_ctl_naibbe.txt

File format for `data/controls/*.txt`: one source line per line (verse line, verse or paragraph);
lines beginning `## ` are section markers (book / chapter / sura / laisse), not text.
Tokenisation (`corpora_ext.tokenize`): lowercase, NFKD, drop all combining marks (nikkud,
harakat, Greek accents, Latin diacritics; long-s folds to s), token = run of Unicode letters.
Abjads stay unpointed consonantal text. The original `corpora.control()` is untouched; it does
not handle these files (it drops non-Latin letters).

Profile columns below: first 25k tokens, same definitions as `a1_profile.py` (h2 = character
conditional entropy with space as a symbol; SD = word-length SD; rep = immediate word repeats %).
Reference: Voynich EVA h2 2.13, SD 1.76, rep 0.90 %; Latin/Italian/German/English h2 3.11–3.30,
SD 1.95–2.91, rep 0.00–0.16 %.

## A. Natural languages (`data/controls/`)

| file | language / date | source | license | tokens (full) | h2 | SD | rep % | caveats |
|---|---|---|---|---|---|---|---|---|
| hebrew_torah.txt | Biblical Hebrew, unpointed | Sefaria API `https://www.sefaria.org/api/texts/{Genesis,Exodus,Leviticus,Numbers,Deuteronomy}?context=0&pad=0` (default Hebrew version returned by the API; version name not recorded, unverified) | Sefaria Tanakh text: public domain per Sefaria (unverified for the exact version) | 69,385 | 3.54 | 1.39 | 0.10 | nikkud and cantillation stripped, maqaf split; verse per line |
| arabic_quran.txt | Classical Arabic | tanzil.net `quranType=simple-clean` download (`https://tanzil.net/pub/download/`) | Tanzil terms: free use with attribution, text unaltered (we strip harakat — note) | 78,248 | 3.45 | 1.63 | 0.01 | harakat, superscript alef, tatweel removed; verse per line, sura sections |
| greek_herodotus.txt | Ancient Greek (Ionic), Herodotus Histories | PerseusDL canonical-greekLit `tlg0016.tlg001.perseus-grc2.xml` (raw.githubusercontent.com) | CC BY-SA 4.0 (Perseus) | 184,936 | 3.19 | 2.82 | 0.01 | polytonic accents stripped by the tokenizer; paragraph per line, book sections; not medieval |
| czech_bible_kralicka_1613.txt | Old Czech, Bible kralická 1613 (Gen, Ex, Lev) | cs.wikisource `Bible kralická (1613)/Genesis` etc. | PD text (1613); Wikisource transcription CC BY-SA | 76,893 | 3.40 | 2.41 | 0.13 | original 1613 orthography (w, ſ, ľ, g=j); marginal glosses sometimes glued to verse start |
| occitan_croisade_albigeoise.txt | Old Occitan, Chanson de la croisade albigeoise (c. 1213-19) | fr.wikisource `La Chanson de la croisade contre les albigeois/Chanson` (Paul Meyer ed. 1875) | PD | 82,388 | 3.16 | 2.21 | 0.03 | verse per line, laisse sections; Meyer's apparatus cut at the poem's end |
| oldfrench_roland.txt | Old French, Chanson de Roland, Oxford MS | fr.wikisource `La Chanson de Roland/Raoul Mortier` (Mortier transcription, reworked) | PD text; transcription hosted on Wikisource (licensing of the 1993 reworking unverified) | 29,524 | 3.14 | 2.30 | 0.04 | below 40k (the whole poem); laisse sections; editorial brackets kept as letters |
| mhg_nibelungenlied.txt | Middle High German, Nibelungenlied Hs. A (diplomatic) | Bibliotheca Augustana `https://www.tha.de/~harsch/germanica/Chronologie/12Jh/Nibelungen/nib_a_01..39.html` | Augustana: free for scholarly use (unverified) | 78,700 | 3.02 | 2.01 | 0.06 | **diplomatic transcription with scribal abbreviations kept** (e.g. `vn–`); half-lines joined per long line; aventiure sections |
| mhg_parzival.txt | Middle High German, Wolfram Parzival (Lachmann text) | Bibliotheca Augustana `.../13Jh/Wolfram/wol_pa01..16.html` | as above | 130,551 | 3.12 | 1.98 | 0.02 | normalised MHG with circumflexes (stripped); verse per line |
| catalan_tirant.txt | Medieval Catalan, Tirant lo Blanch (1490) | ca.wikisource `Tirant lo Blanch (1905)/1/Capítol N`, `/2/Capítol N` (Aguiló ed.) | PD | 205,824 | 3.10 | 2.36 | 0.00 | 1490 orthography with long s; chapter per section; paragraph per line |
| turkish_kanun_medeni_1926.txt | Turkish, Civil Code of 1926 | tr.wikisource `743 Sayılı Türk Kanunu Medenisi` | PD (statute) | 37,026 | 3.33 | 2.70 | 0.02 | **flagged**: modern Latin-script Turkish, legal register, not Ottoman; Gutenberg has no Turkish and tr.wikisource literary texts are stubs (Nutuk chapters total 3.5k words) |
| latin_macer_floridus.txt | Medieval Latin, Macer Floridus De viribus herbarum (11th c.) | la.wikisource `De viribus herbarum` (Panckoucke ed. via Corpus Corporum) | PD | 14,044 | 3.30 | 2.24 | 0.00 | the herbal; verse per line, chapter (plant) sections; small |
| latin_pliny_herbal.txt | Classical Latin, Pliny NH XX–XXVII (plant remedies) | la.wikisource `Naturalis Historia/Liber XX` … `XXVII` | PD | 76,561 | 3.34 | 2.71 | 0.00 | classical, not medieval; Greek plant names kept (alpha 47); used to pad the herbal plaintext |
| hawaiian_fornander.txt | Hawaiian | Gutenberg #72686, #73166, #74570 (Fornander Collection vols 1–3, bilingual) | PD | 427,956 | 2.57 | 2.49 | 0.38 | Hawaiian lines selected by charset heuristic (letters ⊆ aeiouhklmnpw); a few English lines pass (e.g. "i am like a man"); genealogies skipped |
| tagalog_urbana_feliza_1864.txt | Tagalog, 1864 prose | Gutenberg #15980 | PD | 36,740 | 2.83 | 2.97 | 0.12 | 19th-c. Spanish-style orthography; `~` (ng tilde) removed |
| tagalog_florante_1838.txt | Tagalog, 1838 verse | Gutenberg #15845 | PD | 23,760 | 2.89 | 2.71 | 0.20 | below 40k |

Not obtained: **medieval Latin with abbreviations unexpanded** — no plain-text diplomatic Latin
corpus found (TRIDIS and EMMO expand silently; Abbreviationes is a database). The Nibelungenlied
Hs. A file above is the only diplomatic-with-abbreviations text in the set (MHG, not Latin). A
1515 blackletter print of Llull (archive.org ARes54311) was fetched but its OCR is unusable.
Pseudo-Apuleius Herbarius and Hildegard's Physica: no open plain text found (archive.org has only
Middle-English/German editions of Apuleius). Occitan troubadour lyric was not used; the Croisade
is an Old Occitan epic instead (larger, same period).

## B. Constructed / asemic texts (`data/controls/`, generated table in `data/controls_synthetic/`)

| file | content | source | license | tokens | h2 | SD | caveats |
|---|---|---|---|---|---|---|---|
| ignota_hildegard_glossary.txt | Lingua Ignota, Roth-1895 sample via Wikipedia | en.wikipedia `Lingua ignota` wikitext (`{{lang|art-DE|…}}` entries) | CC BY-SA | **53** | n/a | n/a | only the 30-entry sample + sample sentence; the full 1011-word glossary exists only in Higley 2007 (copyright) and Pitra 1882 (not found on archive.org) |
| enochian_keys_dee.txt | Enochian: the 18 Keys + Call of the Thirty Aethyrs | Crowley, Liber LXXXIV vel Chanokh (Equinox I.7–8, 1912), Wayback copy of hermetic.com/crowley/libers/lib84 | PD (1912) | 1,287 | 2.94 | 2.73 | Golden-Dawn phonetic spelling (`zodacare`), not Dee's MS orthography; Liber Loagaeth tables not found online in text form |
| trithemius_steganographia_1608.txt | Trithemius Steganographia (Frankfurt 1608) | archive.org `SteganographiaBSB1608` OCR | PD | 48,906 | 3.68 | 4.81 | raw OCR of a 1608 print: long-s→f errors, line breaks kept; contains the spirit-name tables and conjurations mixed with Latin prose |
| trithemius_polygraphia.txt | Trithemius Polygraphia (+ Clavis) | archive.org `b30534756` (Wellcome) OCR | PD | 111,411 | 3.48 | 3.29 | same OCR caveats; the Ave-Maria cipher word tables are in there but not isolated |
| controls_synthetic/lull_ars_brevis_table.txt | Llull Ars brevis Figure-4 table, 84 columns × 20 compartments | **generated** from the rule (no free Latin text of Ars brevis found; Brepols/LLT only) | n/a | 1,680 | 2.60 | 0.22 | one compartment per line, column = page |

## C. Synthetic nomenclator (`ctl_nomenclator.py`, seed 20261017, `data/controls_synthetic/`)

Plaintext: Macer (14,044 tokens) then Pliny XX–XXVII, cut at 35,000 tokens; 79 sections follow
the plaintext chapters/books. Alphabet: 20 ASCII letters `acdefghiklnoqrstxy` + `p`, `m` (the
last two reserved for line-edge markers). Keys are saved as `nomen_word.key.json`,
`nomen_syll.key.json`; page/line/section layout in `<name>.meta.json`.

| file | scheme | tokens | types | h2 | mean len | SD | rep % |
|---|---|---|---|---|---|---|---|
| plaintext (Macer+Pliny) | — | 35,007 | 9,168 | 3.343 | 5.87 | 2.525 | 0.00 |
| nomen_word.txt | 12 prefix classes (top-50 / top-300 / Latin-ending classes) × 150 cores (2–3 symbols) × 10 suffixes; one-to-one; top-50 words get 2-symbol cores | 35,007 | 9,168 | 3.178 | 5.33 | 1.588 | 0.00 |
| nomen_syll.txt | 1,797 Latin syllables → fixed 2–3 symbol units, concatenated | 35,007 | 9,166 | 3.764 | 5.37 | 2.380 | 0.00 |
| nomen_lines.txt | nomen_word + lines 6–10 words, pages 10–25 lines, line-initial `p` (0.20), line-final `m` (0.15) | 35,007 | 10,080 | 3.204 | 5.38 | 1.602 | 0.00 |
| Voynich EVA first 35k | — | 34,857 | 7,025 | 2.109 | 4.99 | 1.788 | 0.84 |

Reading: a slot code with randomly drawn cores reproduces the Voynich word-length SD (1.59 vs
1.79) but not the low h2 (3.18 vs 2.11) nor the immediate repeats (0 vs 0.84 %). To get the h2
down a codebook would need cores drawn from a very restricted glyph grammar, which is what the
slot-induction test in Phase 1 should measure.

## D. Generators and the two extra controls (`data/controls_synthetic/`)

| file | script | tokens | types | h2 | SD | rep % | notes |
|---|---|---|---|---|---|---|---|
| markov1.txt | ctl_generators.py | 35,000 | 10,890 | 2.107 | 3.455 | 0.88 | Markov-1 chars trained on `corpora.voynich()`; h2 matches by construction, SD far too wide |
| rugg_grille.txt | ctl_generators.py | 35,000 | 4,221 | 2.512 | 1.134 | 0.13 | 250-row table of Voynich's top 40 prefixes / 60 mids / 40 suffixes (frequency-weighted, 1/8 empty cells), 40 grilles with random row offsets, grille swapped each line; key in `rugg_grille.key.json` |
| naibbe_like.txt | ctl_naibbe.py | 34,994 | 29,813 | 4.080 | 3.333 | 0.00 | unigram/bigram split p=0.5, six random tables chosen per unit, 1–4-symbol entries; keys in `naibbe_like.key.json`; nearly every token is a hapax, as expected of a randomiser |
| latin_merged.txt | ctl_generators.py | 35,000 | 8,460 | 2.719 | 2.835 | 0.09 | Augustine with i,o,u,y→a, b→p, d→t, g→k, m→n; h2 drops 3.30→2.72 |
| lull_ars_brevis_table.txt | ctl_generators.py | 1,680 | 816 | 2.603 | 0.218 | 0.00 | see B |

All synthetic files have `<name>.meta.json` = `{"pages": [{"page", "section", "lines": [[tok…]…]}]}`.

## Sources that failed

- gutendex.com API: timeouts (used Gutenberg's own search pages instead).
- sacred-texts.com (403/404 for the Dee pages), esotericarchives.com (connection refused),
  hermetic.com (403; the Wayback Machine copy worked).
- Sefaria-Export GitHub raw JSON: 404 (the live API worked).
- Project Gutenberg: no Turkish, no monolingual Hawaiian texts.
- oc.wikisource API returned HTML, not JSON (Occitan taken from fr.wikisource instead).
- No free text of Llull's Ars brevis, Hildegard's Lingua Ignota glossary or Physica, Pseudo-Apuleius,
  Dee's Liber Loagaeth, or any unexpanded-abbreviation Latin corpus.
