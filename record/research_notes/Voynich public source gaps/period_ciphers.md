# Period ciphers, nomenclators, and 2024-2026 mechanism papers

Checked 2026-10-18 21:05 -07:00 (`Get-Date`). Nothing was saved into the repo except this note. A claimed plaintext is not treated as evidence. Already held, so not listed as missing downloads: Meister 1906, the local Naibbe-like generator, the Timm-Schinner jar, and the Megyesi "mostly under 100" quotation. Parisel arXiv:2604.19762 and Rozanova-Temerev arXiv:2608.17096 are already in `data/external/papers/`; they are cited for numbers, not as new files to fetch.

## Is the Greshko 2025 CC-BY PDF downloadable, and what does the main text say about entropy, repeats, hapax, and line position?

### Takeaway
Crossref records the article as CC-BY 4.0, but on 2026-10-18 the publisher PDF and HTML were still a Cloudflare challenge, Unpaywall and OpenAlex listed no PDF file, and the main text was not opened. The only numeric entropy table reached is the author's GitHub figure CSV, which is not the article body.

### Cited Findings
- Citation: Michael A. Greshko, "The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext," *Cryptologia*, pp. 1-37, published online 2025-11-26, doi:10.1080/01611194.2025.2566408. Crossref licence object: CC-BY 4.0, content-version vor, start 2025-11-26. Crossref `link` points at `https://www.tandfonline.com/doi/pdf/10.1080/01611194.2025.2566408` (intended-application similarity-checking). No Crossref abstract. — [Crossref](https://api.crossref.org/works/10.1080/01611194.2025.2566408)
- Unpaywall, record updated 2026-09-11: `is_oa` true, `oa_status` hybrid, `license` "public-domain" (conflicts with Crossref's CC-BY), `url_for_pdf` null, `has_repository_copy` false, only landing page `https://doi.org/10.1080/01611194.2025.2566408`. — [Unpaywall](https://api.unpaywall.org/v2/10.1080/01611194.2025.2566408?email=research@example.org)
- OpenAlex W4416723189, publication_date 2025-11-26: `any_repository_has_fulltext` false, `pdf_url` null, licence label public-domain. Abstract, reconstructed from the inverted index, says the Naibbe cipher is a verbose homophonic substitution doable by hand with 15th-century materials, that Latin and Italian ciphertexts stay decipherable, and that they "reliably reproduce many key statistical properties" at once. No entropy, hapax, repeat, or line-position figure is in that abstract. — [OpenAlex](https://api.openalex.org/works?filter=doi:10.1080/01611194.2025.2566408)
- HEAD on 2026-10-18 of `/doi/pdf/`, `/doi/pdf/?download=true`, `/doi/epdf/`, and `/doi/full/` returned HTTP 403, `cf-mitigated: challenge`. A reader proxy returned the same "Performing security verification" page. Wayback CDX for the pdf URL and for `doi/full/...*` with status 200 returned `[]`. The author page links the paper only to the Taylor & Francis full-text URL. — [author page](https://www.michaelgreshko.com/naibbe-cipher); [Wayback CDX](https://web.archive.org/cdx/search/cdx?url=www.tandfonline.com/doi/pdf/10.1080/01611194.2025.2566408&output=json)
- A DuckDuckGo snippet of the Taylor & Francis full-text URL, not the PDF, says verbosity, homophony, and respacing generate "VMS-like numbers of unique word types in VMS-like proportions" under the manuscript's word grammar, entropy, token-length distribution, and word-type length distribution. No numeric value is in the snippet. — [DuckDuckGo](https://html.duckduckgo.com/html/?q=Naibbe+cipher+conditional+entropy+word+types)
- Public figure data, not the article: `entropy_results_voyb.csv` gives rowwise character entropy / conditional character entropy of eva 3.860 / 1.954 and cuva 3.899 / 2.255. `entropy_results_naibberef_cuva.csv` gives twenty Naibbe runs with conditional character entropy from 2.311 to 2.339. The notebook defines those columns as rowwise Shannon and conditional character entropy and writes the CSV. — [voyb CSV](https://raw.githubusercontent.com/greshko/naibbe-cipher/main/figure_utils/entropy/entropy_results_voyb.csv); [Naibbe CSV](https://raw.githubusercontent.com/greshko/naibbe-cipher/main/figure_utils/entropy/entropy_results_naibberef_cuva.csv); [notebook](https://github.com/greshko/naibbe-cipher/blob/main/figure_utils/entropy/entropy.ipynb)
- Same repo, Gaskell-Bowern-style `metrics_voynichnaibbe.csv`: `repeated_words` is 0.00836 for "Voynichese - Currier B - EVA Basic" and 0.0012 for `naibbe_reference`. `unique_words` in that file is about 140-155, a window metric, not a manuscript type count. No hapax column and no line-initial or line-final column were in the header. — [metrics CSV](https://raw.githubusercontent.com/greshko/naibbe-cipher/main/figure_utils/gaskell_bowern_2022/newresults/metrics_voynichnaibbe.csv)
- Zenodo 10.5281/zenodo.17219445 (concept 10.5281/zenodo.16415087), published 2025-09-28, licence CC-BY-4.0, is the supplement, not the article. File list includes `Greshko 2025 - Supplementary Materials 1-4.pdf` (2,563,905 bytes) and no article PDF. — [Zenodo files](https://zenodo.org/api/records/17219445/files)
- Repo licence on the README is a modified MIT with a citation condition, not CC-BY. — [README](https://raw.githubusercontent.com/greshko/naibbe-cipher/main/README.md)

### Inferences
- The CC-BY claim is the publisher's Crossref licence, not a file that this check could download. Unpaywall's "public-domain" label and null `url_for_pdf` would be wrong if a repository PDF exists that those indexes missed; none was found.
- The GitHub conditional entropies cannot be scored against the frozen character h2 of about 2.11 until the rowwise definition is aligned. On the author's own EVA transcription the Voynich figure is 1.954, and the Naibbe CUVA runs sit near 2.32. That does not show a joint match to line edges, hapax about 0.68, or in-line reuse. Those three are absent from the files opened here.
- `naibbe_cv_vc_reuse.py` is an alternate consonant-vowel respacing implementation (header only was read). It is not a published line-position result.

### Gaps
- The main-text sentences on entropy, repeats, hapax, and line position were not read. What would refute the "still blocked" finding is an HTTP 200 body that begins with `%PDF` or the article HTML. A human browser was not used on 2026-10-18.
- Whether the printed article's hapax and repeat figures differ from the Zenodo supplement was not re-checked against the supplement PDF this session.

## Is Meister 1902 openly available, reprinted, or retabulated?

### Takeaway
HathiTrust has two US full-view scans (`pdus`). No Internet Archive item was found. No later paper that reprints the 1448, 1483, 1435, and 1424 key sizes was found in this pass.

### Cited Findings
- HathiTrust catalog 006176726: Aloys Meister, *Die anfänge der modern diplomatischen geheimschrift. Beiträge zur geschichte der italienischen kryptographie des xv jahrhunderts*, publishDates 1902. Item `hvd.hxub2m` (Harvard), `rightsCode` pdus, `usRightsString` "Full view", `lastUpdate` 20250111, URL `https://babel.hathitrust.org/cgi/pt?id=hvd.hxub2m`. Item `uc1.b4177709` (University of California), same pdus full view, `lastUpdate` 20260608. — [HathiTrust brief API](https://catalog.hathitrust.org/api/volumes/brief/htid/hvd.hxub2m.json)
- Internet Archive advanced search `diplomatischen AND geheimschrift AND meister AND year:1902` returned `numFound` 0. — [Archive.org](https://archive.org/advancedsearch.php?q=diplomatischen+AND+geheimschrift+AND+meister+AND+year:1902&output=json)
- Wayback CDX for `http://www.nickpelling.com/voynich/Meister1902.zip`: snapshot 20201212101737 status 200, length 11,269,303 bytes; snapshot 20251111024148 status 404. That is a personal-site zip, not a library edition. The live Pelling URL was already a 404 in the 2025 snapshot. — [Wayback CDX](https://web.archive.org/cdx/search/cdx?url=www.nickpelling.com/voynich/Meister1902.zip&output=json)
- OpenAlex journal-title search for "Voynich" from 2023-01-01 through 2026-10-18 (18 hits) and the Crossref records opened below do not include a paper that tables Meister's 1902 key sizes. — [OpenAlex](https://api.openalex.org/works?filter=title.search:Voynich,primary_location.source.type:journal,from_publication_date:2023-01-01,to_publication_date:2026-10-18)

### Inferences
- "Open" here means US full view under `pdus`, not a worldwide public-domain file and not an Internet Archive download. A non-US reader can still be refused by HathiTrust. What would refute that is a `pd` (not `pdus`) item or an Archive.org identifier.
- The page-by-page homophone, null, and nomenclature counts for Milan 1448, the 1483 key, Modena 1435, and Florence 1424 were not read off the scans in this session. The prior local note already said those counts were still open.

### Gaps
- Google Books and MDZ were not re-queried on 2026-10-18. A Kessinger reprint is only in the 2026-10-17 local note, not re-checked here.
- No later article was shown to reprint those four key sizes. Absence is only as far as the searches above.

## What public DECODE tables give 15th-century nomenclature sizes, alphabet sizes, and null rates?

### Takeaway
The nomenclature-size and null-rate statements already held locally come from CC-BY papers whose repository PDF still answers HTTP 200. This pass did not open a public table of 15th-century cipher-alphabet sizes, and it did not find a bulk database download.

### Cited Findings
- Beáta Megyesi et al., doi:10.1080/01611194.2022.2113185. Unpaywall on 2026-10-18: `is_oa` true, licence cc-by, `oa_date` 2022-11-03, `has_repository_copy` true. PDF URLs in that record: `https://edit.elte.hu/xmlui/bitstream/10831/114019/1/33206329.pdf` (submittedVersion, ELTE) and `https://uu.diva-portal.org/smash/get/diva2:1718372/FULLTEXT01` (DiVA; `url_for_pdf` null on that location, but the smash URL itself returned HEAD 200, `Content-Type: application/pdf`). Publisher `url_for_pdf` is null. — [Unpaywall](https://api.unpaywall.org/v2/10.1080/01611194.2022.2113185?email=research@example.org)
- The 2026-10-17 local full-text note, which says the CC-BY PDF was read, quotes: sample 1,610 DECODE keys, 1,384 with nomenclatures; in the 15th century "the vast majority (80%)" had nomenclatures with fewer than 100 elements and "about 50%" fewer than 50; about 93% of 15th-century nomenclature tables are simple substitution; about 25% contain syllables; 16% use digits. The top size bin is an open "100+". Those sentences were not re-extracted from the PDF on 2026-10-18. — local file `research_notes/External anchors/period_nomenclators.md` lines 39-43, citing [DiVA](https://uu.diva-portal.org/smash/get/diva2:1718372/FULLTEXT01)
- Same local note, citing Megyesi, Tudor, Láng, and Lehofer, "Key Design in the Early Modern Era in Europe," HistoCrypt 2021, `https://ecp.ep.liu.se/index.php/histocrypt/article/view/165`: 96% of 15th-century keys include nulls, and 94% of null sets have at least two codes; alphabets are "mostly homophonic." No mean cipher-alphabet size is stated there. Not re-opened on 2026-10-18.
- DECODE home page says the database holds images and metadata and that "all records in the database are open to the public," and it links to `https://de-crypt.org/decrypt-web`. No CSV, Zenodo dump, or GitHub bulk export was among the database links extracted from that page. — [de-crypt.org](https://de-crypt.org/)

### Inferences
- The under-100 nomenclature statement is already held and should not be re-imported as a new control. It still does not give ciphertext type counts, so it does not by itself test the frozen 7,025-type profile.
- A cipher-alphabet size table, if it exists, was not in the sources opened this session. What would refute that gap is a column of sign-inventory sizes in the HistoCrypt 2021 PDF or a DECODE export.

### Gaps
- Bulk download URL for the DECODE database: not found. The record browser is public; per-key counts were not exported.
- Null-rate and size percentages above rest on the 2026-10-17 read. A refutation would be the PDF text differing from that note.

## What open texts exist for Tranchedino and other 15th-century cipher ledgers, and how large are the codebooks?

### Takeaway
No open transcription of the Tranchedino ledger, and no counted codebook size from a primary open text, was retrieved. The open paper at the URL previously treated as Domnina is Judit W. Somogyi's 2016 article, and its abstract gives no entry counts.

### Cited Findings
- `https://ojs.ppke.hu/verbum/article/view/405` citation metadata, read 2026-10-18: Judit W. Somogyi, "Caratteristiche strutturali di cifrari monoalfabetici italiani nei secoli XV e XVI," *Verbum - Analecta Neolatina* 17, no. 1-2 (issued 2016-12-01), pp. 195-217. PDF: `https://ojs.ppke.hu/verbum/article/download/405/410`. The English description says the paper covers Italian monoalphabetic code books of the 14th and 15th centuries, a two-part security scale (letter substitution, and the number and kind of safety elements), and a reconstructed cipher from coded and decoded texts of Maffeo di Treviglio. The description contains no nomenclature size, alphabet size, or null count. — [OJS](https://ojs.ppke.hu/verbum/article/view/405)
- GitHub repository search `tranchedino OR tranchedini cipher` did not surface a ledger transcription in the returned items (the query matched unrelated "cipher" repositories; `total_count` was 100,150 and `incomplete_results` false, so this is a bad query, not a census). — [GitHub search](https://api.github.com/search/repositories?q=tranchedino+OR+tranchedini+cipher)
- The prior local note's publisher figures for Cod. Vind. 2398 ("287 complete and four partial," "about 300" keys) were not re-checked against a facsimile or transcription. They stay unverified.

### Inferences
- Somogyi is an open structural description of Italian codebooks, not a Tranchedino transcription. It could test the open problem only if the PDF's scale is numeric. That PDF was not text-extracted, so it is not yet a scored control.
- A drifting affix table and a combinatory-table hypothesis are not addressed by any ledger transcription found here.

### Gaps
- Domnina's Tranchedini article was not located as a separate open file in this pass. The earlier identification of OJS 405 as Domnina is contradicted by the page's own citation tags.
- Codebook sizes for Tranchedino, and for any other 15th-century ledger with an open transcription, were not established from a primary text this session.

## Which 2023-2026 papers propose a listed mechanism and publish comparison numbers?

### Takeaway
The only 2023-2026 text opened here that both names a listed mechanism (slot table, grille) and prints joint numeric thresholds is Parisel, arXiv:2604.19762, already on disk. It does not use character h2, a 7,025-type count, or hapax about 0.68. No newly fetched paper publishes a joint match to that frozen profile.

### Cited Findings
- Christophe Parisel, "Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript: Implications for Cipher-Like Structure," arXiv:2604.19762v2, 16 June 2026 (extract dateline 17 June 2026). No Creative Commons URL was in the arXiv API entry. Code: `https://github.com/labyrinthinesecurity/currier-signatures`. Mechanisms tested: a parametric slot generator (prefix and suffix pools, lexicon of about 1,000 words) and a Cardan grille after Rugg 2004. From the local text extract of the public PDF, opened this session: whole-manuscript end-class to start-class rate 80.6% and polarization 0.786 (Table 2). Dialect thresholds in Table 1: Currier A, E to S 71.0% with pass band [56%, 86%], cross-boundary MI 0.5856 with pass at least 0.29, Zipfian R2 0.863 and CV 1.45, bilateral Se=3 Ee=3, 9,892 words; Currier B, E to S 64.3% with pass band [50%, 79%], MI 0.4980 with pass at least 0.25, intermediate R2 0.805 and CV 1.53, Se=3 Ee=7, 19,640 words. The prose also says Currier A 71.0% versus 64.1%, which disagrees with the table's 64.3%. q is 5,285 word-initial and 2 word-final; iin is 0 initial and 3,958 final. Neither generator hits all four signatures for either dialect. The slot model fails high cross-boundary MI and the E to S rate together; the grille fails the E to S rate and Zipfian shape together. — local extract `data/external/papers/parisel_2026_arxiv_2604.19762.txt` lines 20-32 and 233-267; [arXiv](https://arxiv.org/abs/2604.19762)
- Greshko 2025, verbose homophonic substitution, is the other mechanism paper with public numbers, but those numbers are the GitHub entropies and `repeated_words` above, not a line-position or hapax table, and the article PDF was not opened. The local Naibbe-like generator is already held.
- Liudmila Rozanova and Alexander Temerev, "A Glyph Is Not a Letter, a Token Is Not a Word, a Space Is Not a Space," arXiv:2608.17096v1, updated 2026-08-17. This abstract does not propose a verbose cipher, grille, combinatory table, homophone system, or abbreviation. It reports controls: glyph conditional entropy 2.7 bits against about 3.5 for Latin, Italian, and English; next-token prediction under 1% of token entropy against 2-10% in controls; 0.2 bits of mutual information at token edges; about 70% singleton types against 41% and 59-60%; uncertain blanks narrower on the page, AUC 0.905. A Voynich-imitating cipher and a self-citation generator match the low entropy and weak token order and miss the edge coupling and the hapax rate. Already held locally. No CC licence in the API entry. — [arXiv abstract](https://export.arxiv.org/api/query?id_list=2608.17096)
- Darren Helton, "Deciphering the Architecture of Beinecke MS 408: A Statistically Validated Nomenclator Cipher with Medieval Italian Plaintext," Zenodo 10.5281/zenodo.19154142, publication_date 2026-03-21, licence CC-BY-4.0. The record's mechanism label is a three-layer nomenclator. Published counts in the description, not a reading: 109 lemmas, 60.3% of a 33,710-token corpus, dictionary-shuffle 0/10,000. No h2, hapax, line-edge, or in-line reuse figure is in that description. Code link, not opened: `https://github.com/d-w-h/voynich-nomenclator`. — [Zenodo](https://zenodo.org/api/records/19154142)
- Crossref, issued 2026-09-07, no abstract and no CC licence (only a text-and-data-mining policy URL): Rod Kinnison, "The Voynich Manuscript's positional entropy collapse: comparative evidence from languages and ciphers," doi:10.1080/01611194.2026.2697318. Torsten Timm, "The challenge of analyzing a dynamic text: why the Voynich manuscript resists conventional interpretation," doi:10.1080/01611194.2026.2693462. Torsten Timm and Andreas Schinner, "The Voynich manuscript: discussion of text creation hypotheses," doi:10.1080/01611194.2023.2225716, issued 2023-07-19, also no abstract and no licence URL. — [Crossref Kinnison](https://api.crossref.org/works/10.1080/01611194.2026.2697318); [Crossref Timm 2026](https://api.crossref.org/works/10.1080/01611194.2026.2693462); [Crossref Timm-Schinner 2023](https://api.crossref.org/works/10.1080/01611194.2023.2225716)
- OpenAlex also lists, without abstracts retrieved here: "Singulion Structure and the Voynich Manuscript," 2026-01-01, doi:10.4000/16k0a, CC-BY on the OpenAlex location; the OpenEdition page returned an Anubis bot wall. "CRYPTOGRAPHIC MEANING OF THE VOYNICH MANUSCRIPT," 2023-01-01, doi:10.28995/2686-679x-2023-4-92-107, not OA in that record. — [OpenAlex journal filter](https://api.openalex.org/works?filter=title.search:Voynich,primary_location.source.type:journal,from_publication_date:2023-01-01,to_publication_date:2026-10-18)
- Christophe Parisel, arXiv:2604.25979v2 (Currier A/B; Beta-Binomial, 185 folios, 2 components by BIC, 89% held-out folio labels; ch/sh switch, Delta AIC 2,549, 195 of 197 folios, 92% of variance) and arXiv:2509.10573v4 (directionality via n-gram perplexity) name no verbose, grille, combinatory, homophone, or abbreviation mechanism in the abstracts fetched. — [arXiv Currier](https://export.arxiv.org/api/query?id_list=2604.25979); [arXiv direction](https://export.arxiv.org/api/query?id_list=2509.10573)

### Inferences
- Parisel is the public test of the live combinatory-slot idea, and it fails a joint positional profile. That profile is not the frozen one. Sig1 is an end-class to start-class rate, not line-initial or line-final glyph habit, and the slot lexicon is about 1,000 types, not about 7,025. It does not speak to character h2 or hapax about 0.68. Using it as a scored control would measure different quantities.
- Helton's 109-lemma figure, if taken only as a codebook size, sits with the already-held "under 100 to low hundreds" nomenclature range. The 60.3% coverage is a claimed decode statistic. It was not checked against h2, line edges, hapax, or in-line core reuse.
- Kinnison's title is the closest unread 2026 candidate for a cipher-versus-language entropy comparison. Until the PDF is opened, it supplies no number and no licence that would make a copy clearly reusable.
- No source opened here is a public dataset that jointly reports character h2 near 2.11, about 7,025 types, hapax near 0.68, line-edge habits, and in-line word reuse for a verbose cipher, a grille, a combinatory table, a homophone system, or an abbreviation system.

### Gaps
- Kinnison 2026 and Timm 2026 have no Crossref abstract. Their quantitative claims, mechanisms, and whether a PDF is free are unverified. What would refute "no numbers" is the article text.
- Singulion (doi:10.4000/16k0a) was not read. The Anubis wall blocked the landing page.
- In-line core reuse is not a reported column in the Greshko CSVs or the Parisel tables that were opened.
- arXiv's 19 "Voynich" hits were title-listed; only the abstracts named above were fetched. A paper whose title omits "Voynich" would have been missed by the OpenAlex title filter.