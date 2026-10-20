# Period nomenclators and cipher keys (15th century) as an external anchor

Stamped: `Sat Oct 17 20:08:10 PDT 2026` (output of `date`).
Scope: O-016, O-017, L-095, and the synthesis claim that "DECODE statistics show 7k-type codebooks are implausible".
Read-only: I read web pages and nothing went into the project except this note. WebFetch saved three open-access CC-BY PDFs (HistoCrypt 2021, HistoCrypt 2022, Cryptologia 2022) into the harness tool-results folder, outside the project. I extracted their text into the session scratchpad and grepped it there. Quotes are a few words each.
**Unverified** marks a claim I saw only second-hand, through a search summary, a forum or blog relay, or a publisher blurb, and not in a primary or peer-reviewed text I opened.

## 1. Is Meister 1902 digitised? Yes, at HathiTrust, but full view is US-only

| Where | Result | URL |
|---|---|---|
| HathiTrust catalog record 006176726 | *Die anfänge der modern[en] diplomatischen geheimschrift. Beiträge zur geschichte der italienischen kryptographie des xv jahrhunderts*, Schöningh 1902. Online Books Page lists it as "page images at HathiTrust; US access only". | https://catalog.hathitrust.org/Record/006176726 (via https://onlinebooks.library.upenn.edu/webbin/who/Meister%2c%20Aloys%2c%201866%2d1925, page read) |
| HathiTrust item hvd.hxub2m (Harvard copy) | A search summary describes it as Public Domain in the US, 82 page scans (**unverified**). Cloudflare returned 403 to curl, WebFetch and the built-in browser, so I could not open it. A US user in a normal browser should get full view. | https://babel.hathitrust.org/cgi/pt?id=hvd.hxub2m&seq=1 |
| archive.org | Not there. A `creator:(Meister, Aloys)` search returns 34 items, and the only *Geheimschrift* items are the two 1906 scans (`diegeheimschrift00meis`, `diegeheimschrif00meisgoog`). Phrase searches for "diplomatischen Geheimschrift" and `title:(anfänge) AND title:(geheimschrift)` return 0. | https://archive.org/advancedsearch.php |
| Google Books | Not checked directly, because the Books API returned 429 (daily quota). Web searches found no books.google hit. **Unverified absence.** | — |
| MDZ (digitale-sammlungen.de) | The search page failed to render ("Fehler bei der Darstellung"), and web searches found no MDZ hit. **Unverified absence.** | https://www.digitale-sammlungen.de/de/search?query=Meister+Anf%C3%A4nge+diplomatischen+Geheimschrift |
| Gallica, Internet Culturale | The Gallica SRU endpoint returned an HTML shell to curl, and an extended web search found no Gallica or Internet Culturale copy. **Unverified absence.** | — |
| Print | Kessinger facsimile reprint, ISBN 9781168330376. | https://www.amazon.de/dp/1168330378 |

**Action for O-017:** a US-based human opens `hvd.hxub2m` in a browser and reads p.30 (Milan 14 March 1448), p.31 (1483), p.35 (Modena 1435) and p.50 (Florence 1424). The page numbers come from Pelling, see the on-disk `data/external/nomenclators/ciphermysteries_tranchedino_p3700.html.txt`. Meister 1906 cites the 1902 book as "S. 14 ff." for the Italian state ciphers (on-disk `meister_1906_geheimschrift_kurie_djvu.txt`, Lavinde section, footnote 1).

## 2. Sourced sizes of individual keys

| Key | Alphabet and homophones | Nulls | Nomenclature / code entries | Source and grade |
|---|---|---|---|---|
| Lavinde, papal (Avignon), 1379 | Every letter enciphered uniformly, with signs, letters and digits mixed. Meister: "alle Buchstaben … gleichmäßig umschrieben" | Present, as "Trugzeichen" | "typically a dozen-or-so" word signs (Pelling) | Meister 1906 pp.21–22, on disk (primary). Pelling https://ciphermysteries.com/2016/07/06/fifteenth-century-cryptography (blog) |
| Mantua, Simeone de Crema, 1401 | Reversed-alphabet base of 23 letters plus about 10 extra signs, about 33 signs in all. The vowels have homophones (a: 3 forms, e: 3 forms). i has none, and 6/7 were left free. | None shown | None shown | Kahn, *Codebreakers* (1967) p.107, relayed by https://kryptografie.de/kryptografie/chiffre/de-crema.htm. Kahn's page itself is **unverified** (not opened), and the per-vowel counts are that site's table. Pelling (same blog URL) has "multiple shapes to each of the five vowels". |
| Milan, Zaninus Riccio key, 1424 (reconstructed by Florentine codebreakers from intercepts, Florence State Archives) | — | — | "165 substitutions" in total, a lower bound because the key was derived from letters. The commenter adds that few Tranchedino keys have more. | Mark Knowles, comment on https://ciphermysteries.com/?p=3700 (on disk). Forum grade, **unverified**. |
| Florence 1424, Modena 1435, Milan 1448 (Meister 1902 pp.50, 35, 30) | Not read | Not read | Not read. Pelling calls the 1448 key "surprisingly complex", and Knowles says the 1435 key has "a large number of characters". | On-disk p3700 page. Counts **open** until hvd.hxub2m is read. |
| Mantua ducal cipher, 1450 | "two homophonic shapes per consonant" (except x, z and the '9' sign), "three … per vowel" | "some nulls" | A mini-codebook of common words plus a nomenclator of "roughly the same (small) size" as 1401 | Pelling 2016 blog (URL above). Blog grade. |
| Milan, Tranchedino-ledger alphabet, c.1450–55 | Three shapes per vowel, plus shapes for doubled letters and shorthand | "a few more nulls than before" | "more than eighty special entries" | Pelling 2016 blog (URL above). Blog grade. |
| Tranchedino ledger, Vienna ÖNB Cod. 2398, 1450–1496, compiled c.1475 | Vowels get more signs than consonants. Signs for digraphs and trigraphs. | "numerous 'dummies'" | Mostly proper nouns. No per-key count found. Key count: "287 complete and four partial" (facsimilefinder) or "about 300" (facsimiles.com). 169 folios. | https://www.facsimilefinder.com/facsimiles/francesco-tranchedino-secret-diplomatic-documents-facsimile and on-disk `facsimiles_com_tranchedino.html.txt`. Publisher grade, **unverified**. "A couple of hundred glyphs" per key comes from a forum and is **unverified**. |
| Papal, 15th century (DECODE) | — | — | Variable-length codes were standard, "more sophisticated" than elsewhere | Megyesi et al. 2022 Cryptologia (below), §8 |

Not found: Buonafalce, Cryptologia 32(1) 2008, doi 10.1080/01611190701756585, is paywalled; its abstract says Simonetta's 1474 rules address already old-fashioned ciphers. I found nothing for Sesena. Lange & Soudart was not reached. Domnina, "Nicodemo Tranchedini's Diplomatic Cipher: New Evidence", contains a table of a 1449 system: https://ojs.ppke.hu/verbum/article/download/405/410/609 (the PDF is over 10 MB, so not read; the paper's identity comes from a search summary and is **unverified**). The on-disk Domnina file is a different article, a review of the *Vocabolario*.

## 3. What DECODE actually says (peer-reviewed, read in full text)

- **Megyesi, Tudor, Láng, Lehofer, Kopal, de Leeuw, Waldispühl, "Keys with nomenclatures in the early modern Europe", Cryptologia 48(2) 2024, online 2022, doi 10.1080/01611194.2022.2113185, CC-BY.** Repository copy: https://uu.diva-portal.org/smash/get/diva2:1718372/FULLTEXT01. The sample is 1,610 DECODE keys, of which 1,384 have nomenclatures.
  - Size bins are 1–10, 11–20, 21–50, 51–100 and 100+. The top bin is open, and the authors say they could not count tables of "thousands of elements".
  - The direct published statement is this: in the 15th century, "the vast majority (80%)" of keys had nomenclatures "with less than 100 elements", and "about 50% even fewer than 50". In the 15th century, sizes of 21–100 were "most frequent". By contrast, more than 80% of 18th-century tables exceed 100.
  - About 93% of 15th-century nomenclature tables are simple substitution, so each entry has one code and nomenclature homophony is rare.
  - About 25% of 15th-century tables contain syllables, and 16% use digits.
  - Caveat: "all the 16 Italian cipher keys" in the sample are 15th-century. Over 900 keys come from Austria. The Italian chancery material (Tranchedino, Milan, Florence) is therefore thinly represented, and the 15th-century statistics are not specifically Italian.
- **Megyesi, Tudor, Láng, Lehofer, "Key Design in the Early Modern Era in Europe", HistoCrypt 2021**, https://ecp.ep.liu.se/index.php/histocrypt/article/view/165. The sample is 700 keys, of which 251 15th–16th-century keys were described by hand.
  - 96% of 15th-century keys include nulls, against 27% in the 18th century, and 94% of null sets have at least two codes.
  - 15th-century keys mix letters, digits and graphic signs in "almost all keys".
  - Alphabets are "mostly homophonic".
  - Across all centuries, 72% of keys contain more than 100 plaintext entities.
- **Megyesi et al., "What Was Encoded in Historical Cipher Keys in the Early Modern Era?", HistoCrypt 2022**, https://ecp.ep.liu.se/index.php/histocrypt/article/view/404. 15th–16th-century nomenclatures are dominated by personal and place names. About 20% of 15th-century keys encode numbers. There are no size figures beyond the trend.
- **Héder & Megyesi, "DECODE v2", HistoCrypt 2022**, https://ecp.ep.liu.se/index.php/histocrypt/article/view/397. The database has 2,939 records, of which 1,667 are keys. 15th–16th-century sources are mostly keys rather than ciphertexts. No size statistics.

**Verdict on the synthesis claim.** DECODE does publish a statement that 15th-century nomenclators were small, mostly under 100 entries. None of the four papers states a 15th-century maximum. None mentions "7k" or ciphertext vocabulary size. The claim "DECODE shows period codebooks of 7k types are implausible" is supported only as an inference: no sourced 15th-century nomenclator comes within an order of magnitude of 7k. The claim is wrong if it is read as a statement about ciphertext type counts.

## 4. Bottom line for the project

- **The largest sourced 15th-century code vocabulary is in the low hundreds.** The best figures are 165+ substitutions for Milan 1424 (forum grade), more than 80 nomenclator entries for Milan c.1450 (blog grade), and DECODE's open "100+" bin, which holds about 20% of 15th-century keys (peer-reviewed). I found no source for any pre-1500 nomenclator in the thousands. The DECODE paper's remark about tables of "thousands of elements" refers to later centuries (**inference**, not stated by century). So a 7k-entry 15th-century *codebook* has no period support.
- **A ~7k-type *ciphertext* vocabulary is a different matter, and it is period-consistent.** A 15th-century chancery key enciphers plaintext words letter by letter, keeps word spaces (Bonavoglia, "Venetian Cryptanalysis Treatises of the Renaissance", HistoCrypt, https://ecp.ep.liu.se/index.php/histocrypt/article/download/389/347/290, says Simonetta's 1474 rules apply to ciphers "with spaces among words left visible"), and adds a few hundred code signs at most. Ciphertext word types are then roughly plaintext word types, multiplied by homophone spellings of each, plus nulls inserted inside words. A ~38k-token Latin or Italian plaintext already has thousands of word types (**not measured here**). Two or three homophones per vowel multiply that further. The 7k figure therefore does not need a large nomenclature.
- **The tension is elsewhere, and it is already measured in-project.** Homophony and nulls raise type counts and break exact repeats. L-002 found that homophonic letter solvers with Voynich word spaces kept land at the null. A period key also has a sign inventory of roughly 33 (1401) to perhaps 100–200 signs (forum, **unverified**), far more than Voynich's ~20–30 EVA glyphs, unless the cipher is verbose. So "homophony × modest nomenclature" is plausible for the type count, but it has to be tested against the low h2 and the repeat structure, not against the vocabulary size.

## 5. Leads still open

1. Read Meister 1902 at HathiTrust `hvd.hxub2m` (a US browser should get full view) and count, for each of the four keys, homophones per letter, nulls and nomenclature entries.
2. Domnina's 1449 Tranchedini table (ojs.ppke.hu verbum 405, PDF over 10 MB).
3. DECODE records filtered to before 1500. The database UI is at https://de-crypt.org/decrypt-web/RecordsList; per-key counts would need its export or API, which I did not try.
4. Kahn p.107 (1401 key), and Buonafalce 2008 if a library copy is available.
