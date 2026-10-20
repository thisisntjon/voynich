# Voynich public text-structure sources (1976–2026)

Scope: measurements and machine-readable files not already scored locally. Possessed and not treated as new: ZL3b EVA, Takahashi IT2a, RF1b, Claston v101, Currier, Friedman, Landini–Stolfi interlinear, Gaskell–Bowern gibberish, the Timm–Schinner jar, Lindemann–Bowern entropy (including vowel-merged Latin). No decipherment is endorsed. Corpora were not downloaded.

## Zattera slot grammar (2022 and later)

### Takeaway
The 2022 CEUR paper is CC BY 4.0; the slot table is an automatic IVTFF “Slot” file inside GPL-3.0 library v4j, and the grammar work continues in notes through 11 October 2026. The slot file is cited in the local paper extract but is not in the project tree.

### Cited Findings
- Paper: Massimiliano Zattera, “A New Transliteration Alphabet Brings New Evidence of Word Structure and Multiple ‘Languages’ in the Voynich Manuscript,” International Conference on the Voynich Manuscript 2022, CEUR-WS Vol-3313, paper 10. Licence on the paper: CC BY 4.0. — [CEUR-WS Vol-3313 paper 10](https://ceur-ws.org/Vol-3313/paper10.pdf); licence and statistics read from the local text extract of that PDF at `voynich/data/external/papers/zattera_2022_ceur3313_paper10.txt`.
- Published coverage: each word type is 12 slots (0–11); 86.6% of tokens decompose under the slot rules; “only 1.5% of tokens are words not following this pattern and appearing at least twice.” Nine of 12 slots have a very small glyph inventory; `d` is the exception that can occupy three slots. — same CEUR PDF extract.
- Grammar bake-off (Table 2), SLOT_MACHINE: 3,110 generated strings, 1,113 true positives, precision 0.358, recall 0.216, F1 0.270. The paper says this models 62% of tokens and 1,113 word types (21.6%). Unpruned SLOT model: 4,643,467 strings, F1 0.001. Comparators in the same table include Roe F1 0.043, Vogt (recipes) F1 0.024, Stolfi F1 0 (recall 0.881 on an effectively unbounded set). — same CEUR PDF extract.
- Section tree: page-to-section accuracy 92% versus 54% when pages are randomly grouped (11 rules vs 5). Majority Slot-alphabet text used for that test: 38,469 tokens and 8,343 word types. — same CEUR PDF extract.
- Code is included. Footnote: analysis used v4j, “made available as open-source,” https://github.com/mzattera/v4j. GitHub API on 2026-10-18: `mzattera/v4j`, licence SPDX GPL-3.0, default branch `master`, pushed 2026-10-17T15:27:12Z. Recent commits include “Release 15: Note 12 published” (2026-04-15) and cleanup through 2026-10-17. — [v4j repository](https://github.com/mzattera/v4j); [README](https://raw.githubusercontent.com/mzattera/v4j/master/README.md).
- Slot table file, still at the path named in the 2022 paper: `Interlinear_slot_ivtff_1.5.txt`. Header fetched this session: `#=IVTFF Slot 1.5`; built by `BuildSlotVersion` on 20211022.0905 from the Landini–Stolfi interlinear; “Last edited on 2021-09-21.” It is a remapping, not a new eyewitness reading. Repo `Transcriptions/LICENSE` says the LSI file came from voynich.nu and “It is assumed above texts can be distributed freely.” — [slot IVTFF](https://github.com/mzattera/v4j/blob/master/eclipse/io.github.mzattera.v4j/src/main/resources/Transcriptions/Interlinear_slot_ivtff_1.5.txt); [transcription LICENSE](https://raw.githubusercontent.com/mzattera/v4j/master/eclipse/io.github.mzattera.v4j/src/main/resources/Transcriptions/LICENSE).
- Later notes, not a second journal edition of Table 2: Note 008 (grammar; updated 22 Feb 2022) restates 62% of tokens / 21.6% of types and F1. Note 009 (updated 18 Sep 2022) is the five-cluster / Currier claim. Note 011 (updated 29 Dec 2024, v4j release 14.0.0) redoes Vogt’s token-length claims on the Slot alphabet, paragraph loci P0/P1 only, per cluster, against a shuffle; the author says all three Vogt observations hold, line-final length looks normal, and first lines of paragraphs are longer. Note 012 (updated 11 Oct 2026, release 15.0.0) tests position-specific word types. Site footer on note 011: CC BY-NC-SA 4.0, which is stricter than the CEUR paper’s CC BY 4.0. — [note 008](https://mzattera.github.io/v4j/008/); [note 009](https://mzattera.github.io/v4j/009/); [note 011](https://mzattera.github.io/v4j/011/); [note 012](https://mzattera.github.io/v4j/012/); [note index](https://mzattera.github.io/v4j/).
- Note 012’s one fully printed test (Herbal-A, Slot alphabet, paragraph text): “standard” population 3,302 tokens and 1,006 types; first-line-of-paragraph sample 1,293 tokens and 768 types. Type `Sol`: 46 times in the standard population (1.4%), 18 expected in the sample, 29 observed (2.2%), binomial test p=0.01. The series themselves are in “Interesting Words.xlsx” in that note’s folder; the direct file URL was not opened. — [note 012](https://mzattera.github.io/v4j/012/).

### Inferences
- The missing local object is the Slot-alphabet IVTFF plus `WordLength` / `InterestingWords` outputs, not another copy of the CEUR PDF. Note 012 bears on line-edge glyphs and in-line reuse; note 011 bears on word-length rhythm. Both post-date the 2022 table and were not in the possessed scored list.
- F1 0.270 is a type-coverage score for a word grammar, not character h2. High Stolfi recall with F1 0 is the over-generation case the local profile should not treat as a match.

### Gaps
- No second peer-reviewed revision of Table 2 was found. Notes 007–012 are working notes; 008 and 009 say they can be obsolete relative to current `master`.
- The xlsx named in notes 011 and 012 was not retrieved, so the per-position mean lengths and the full “interesting word” lists are not copied here.
- Whether `InterestingWords` implements the same line-edge definition as the local profile was not checked in the Java source.

## Public transcriptions, 2022–2026

### Takeaway
No new full EVA, Currier, or v101 release, and no multispectral retranscription with a download URL, was found beyond the IVTFF set whose public README is still dated 24 March 2026 and is already mirrored. The new open files are comparison code and derived tables, not a new diplomatic reading.

### Cited Findings
- Live file `http://www.voynich.nu/data/000_README.txt`, first bytes fetched 2026-10-18, still begins “Latest update: 24/03/2026” and describes IVTFF 2.0. That date line matches the local mirror `voynich/data/external/voynich-nu-ivtff/000_README.txt`. The local header, not re-fetched past 500 bytes, says the five IVTFF 2.0 files add paragraph markers and Lisa Fagin Davis hand ids in `$H`. Local file headers already show GC2a and IT2a “modified 25/06/2025.” — [voynich.nu data README](https://www.voynich.nu/data/000_README.txt).
- The README names a `/beta` directory “still subject to change.” Its listing was not opened this session. — same URL.
- The fetched README excerpt does not state a licence.
- Jesús Amador García, “Lo que no aguanta un cambio de transcripción” (26 Sep 2026), CC BY 4.0. Three EVA transcriptions named “Takahashi, F y C” on the same 137 folios: readers disagree on 20.0% of words; on 29% of lines they disagree even on how many words there are. Against Claston v101, repeated four-word sequences found in either system do not appear in the other. Claimed mechanisms: v101 splits words the page joins, and EVA merges signs v101 keeps, “perdiendo 867 de 8.423 tipos de palabra.” Deposit files: a PDF and `Voynich_informe97_codigo.zip` (540,858 bytes). The zip was not opened, so it is not confirmed as a new transcription rather than comparison code. — [Zenodo 10.5281/zenodo.22982333](https://doi.org/10.5281/zenodo.22982333).
- Veronika Lux, “How stable are quantitative claims about Voynichese?” (19 Sep 2026), CC BY 4.0, PDF only (no code file in the deposit). Preregistered battery on ZL3b, IT2a, and GC2a v101, restricted to 4,879 common lines; RF1b only as a derivative check. Outcome numbers are inside the PDF, not in the metadata read here. — [Zenodo 10.5281/zenodo.22850758](https://doi.org/10.5281/zenodo.22850758).
- Zattera’s Slot file (above) is a 2021 automatic remap of LSI, not a 2022–2026 correction of the manuscript.

### Inferences
- A 2024–2026 multispectral correction of the main text is not in the public IVTFF directory as of the README date already held locally. Amador’s 20% word-disagreement and 867-type gap is a measurement the possessed transcriptions do not themselves publish. Lux is a cross-transcription audit of claims the project already scores; the PDF is new only if those policy-grid numbers are not already in `m7`.

### Gaps
- The 2024 multispectral blog was not opened this session, so a corrected EVA limited to marginalia or f116v was not confirmed or ruled out. What would refute the “no new full transcription” line is a file under `voynich.nu/data/` or `/beta` dated after 24/03/2026, or a Beinecke/Lazarus download of a revised full text. `/beta` was not listed.
- Amador’s “F” and “C” are not expanded in the Zenodo metadata that was read.

## Measurements of repetition, word length, quires, and line edges (2019–2026)

### Takeaway
Four open 2026 deposits add numbers the possessed generators do not contain: position-locked word types (Zattera note 012), inter-token predictability (Chang), a one-axis section gradient from entropy-raising merges (Koshy), and vertical height-transition entropy (Signorino). Peer-reviewed companions mostly restate structure or are paywalled without a data file.

### Cited Findings
- Zattera notes 011 and 012, numbers and licences as in the first section. Note 011 confirms, but does not print, Vogt’s three length effects on the Slot alphabet. — [note 011](https://mzattera.github.io/v4j/011/); [note 012](https://mzattera.github.io/v4j/012/).
- Youngsan Chang, “Beyond Token Generation: Inter-Token Structure in the Voynich Manuscript” (29 Apr 2026), CC BY 4.0. Files: PDF plus `Chang_2026e_Voynich_InterToken_package.zip` (1,412,488 bytes). On ZL3b as he counts it: 23,753 tokens, 12,688 types, 8,510 lines. Bigram entropy 11.7001 versus line-internal shuffle 12.7229. Next-token top-1 accuracy 0.6917 versus 0.5505; top-3 0.8168 versus 0.6912. The metadata also names suffix-to-prefix transitions and line-boundary contrasts; those figures were cut off in the API description. Single-author Zenodo preprint, not a journal article. His 12,688 types are not the local ~7,000-type EVA count, so the segmentation differs. — [Zenodo 10.5281/zenodo.19869630](https://doi.org/10.5281/zenodo.19869630).
- Nitin Stephen Koshy, “Inventory transfer” (28 Jul 2026), software, MIT. One zip, `epachayan/voynich-transfer-v1.0.0.zip` (1,234,746 bytes). Method: greedy adjacent glyph-pair merges that raise h2; transfer of one region’s merge list to another. Stated result: one register gradient, 84% of variance on one axis, anchored by Herbal-A and Biological-B; Currier A/B is a threshold on that continuum; the gradient is “reproducible by both meaningful and meaningless” controls (description cut off there). — [Zenodo 10.5281/zenodo.21634012](https://doi.org/10.5281/zenodo.21634012).
- Benedetto Signorino, “Glyph Height Transition Entropy in the Voynich Manuscript” (7 Jun 2026), CC BY 4.0, type Dataset. Files: PDF and `Voynich_Height Transition Analysis.ods` (939,515 bytes). Takahashi EVA; each glyph classed by eye as A/M/B/C. 157,373 transitions, 225 pages; mean per-page entropy of the 16 height transitions about 3.49 bits, maximum 4.0. This is vertical class entropy, not character h2. — [Zenodo 10.5281/zenodo.20582885](https://doi.org/10.5281/zenodo.20582885).
- Rod Kinnison, “The Voynich Manuscript’s Positional Entropy Collapse” (Zenodo 5 Jan 2026), CC BY 4.0. The record calls itself a preprint under peer review and deposits a PDF plus two figures, no code. It compares positional entropy, n-gram cross-entropy, and local edit-distance overlap under recto–verso splits. v1.01 says a BPC normalisation bug was corrected for BPC2/BPC3 and ΔBPC. OpenAlex lists the same title as Cryptologia with DOI `10.1080/01611194.2026.2697318` and an OA link to this Zenodo record; the Zenodo record’s own DOI is the Zenodo one and the journal page was not opened. Numeric BPC results were not in the metadata. — [Zenodo record](https://doi.org/10.5281/zenodo.18155058); OpenAlex listed [10.1080/01611194.2026.2697318](https://doi.org/10.1080/01611194.2026.2697318).
- Andrew Steckley, arXiv:2404.13069 (14 Apr 2024): token distributions inside paragraphs depend on line and paragraph boundaries and on nearby drawings. The PDF is already under `data/external/lit-20261018/steckley-2404.13069/`. No separate data repository appeared in the arXiv API record. The abstract snippet does not give the rates. — [arXiv:2404.13069](https://arxiv.org/abs/2404.13069).
- Christophe Parisel, arXiv:2604.25979v2 (5 May 2026), “A Quantitative Confirmation of the Currier Language Distinction.” Beta-Binomial mixture on eleven character-pair substitution ratios, 185 folios, no Currier labels: BIC selects 2, held-out folio accuracy 89.2%. The PDF says the split remains at within-quire language boundaries, and that A/B is a projection of a higher-dimensional system whose dominant piece is a boolean parameter. PDF already at `data/external/lit-20261018/parisel-2604.25979/`. No code URL in the arXiv record. Figures above were read from that local text extract, lines 1–20. — [arXiv:2604.25979](https://arxiv.org/abs/2604.25979).
- arXiv:2509.10573v4, “Directionality of the Voynich Script” (11 Sep 2025): n-gram perplexity asymmetry for LTR versus RTL. The snippet gives the method, not the perplexity figures, and no data URL. — [arXiv:2509.10573](https://arxiv.org/abs/2509.10573).
- Vladimír Matlach, Barbora Anna Janečková, Daniel Dostál, “The Voynich manuscript: Symbol roles revisited,” PLOS ONE 2022, CC BY. Abstract: a subset of symbols is tested as compounds/ligatures; they “suggest” a smaller alphabet and a steganographic account. No counts and no data URL in the OpenAlex abstract. — [PLOS ONE 10.1371/journal.pone.0260948](https://doi.org/10.1371/journal.pone.0260948).
- Same authors’ Cryptologia 2023 paper is a discussion of the 2022 Malta proceedings (linguistic versus non-linguistic structure). OpenAlex gives no OA URL and no licence. DOI 10.1080/01611194.2023.2225716. — [Crossref DOI](https://doi.org/10.1080/01611194.2023.2225716).
- Torsten Timm and Andreas Schinner, Cryptologia 2019, “A possible generating algorithm of the Voynich manuscript,” DOI 10.1080/01611194.2019.1596999, no OA URL and no licence from OpenAlex. Abstract: network similarity of tokens “support[s] the so-called hoax hypothesis”; a self-citation generator’s sample meets both Zipf laws. This is the journal version of the generator already held as a jar, not a new transcription. — [DOI 10.1080/01611194.2019.1596999](https://doi.org/10.1080/01611194.2019.1596999).
- L. Acedo, “A Hidden Markov Model for the Linguistic Analysis of the Voynich Manuscript,” Mathematical and Computational Applications 2019, CC BY. Abstract: two-state transitions “similar” to known languages; vowel/consonant assignment “matches some previous tentative” readings. No corpus or code URL in the abstract. — [MDPI 10.3390/mca24010014](https://doi.org/10.3390/mca24010014).
- Ivan Zelinka, Melvin Alexis Lara de León, Leah Windsor, René Lozi, Applied Soft Computing 2023, CC BY-NC-ND: deep-learning and classical similarity between Voynich characters and other alphabets. The abstract does not name a winning language or a downloadable matrix. — [DOI 10.1016/j.asoc.2023.110217](https://doi.org/10.1016/j.asoc.2023.110217).
- Topic-model preprint already visible on arXiv and not in the possessed list: arXiv:2107.02858 (6 Jul 2021), LDA, LSA, and NMF on Voynich pages. The API summary stops before the numerical comparison. No code URL was in that summary. — [arXiv:2107.02858](https://arxiv.org/abs/2107.02858).
- Reddy and Knight 2011 and the Gaskell–Bowern materials are the possessed comparisons. This pass did not find a separate Reddy–Knight download beyond the workshop paper as cited by Zattera (ACL-HLT workshop, 2011, pp. 78–86). The anthology URL was not fetched. — citation inside [CEUR paper 10](https://ceur-ws.org/Vol-3313/paper10.pdf).
- Bradley Hauer and Grzegorz Kondrak, TACL 2016, CC BY: 97% language-ID accuracy on 380 languages for monoalphabetic substitution; 93% average decryption word accuracy on 50 anagrammed ciphertexts in 5 languages; on the Voynich manuscript the same pipeline “suggest[s] Hebrew.” Those percentages are not a Voynich decryption score. No code URL in the abstract. — [DOI 10.1162/tacl_a_00084](https://doi.org/10.1162/tacl_a_00084).
- Matthew Arthur Carlo, Zenodo 23 Jun 2026, two CC BY PDFs and no code bundle: a layered constraint list (h2, word length, Zipf, a two-state HMM, line position) and a general “SSA” operator set. Metadata claims a slot grammar plus another generator can meet the joint constraints; the generator is not specified in the text that was read. Treated as an unreviewed checklist, not a new table. — [10.5281/zenodo.20812255](https://doi.org/10.5281/zenodo.20812255); [10.5281/zenodo.20812623](https://doi.org/10.5281/zenodo.20812623).

### Inferences
- Against the local profile (EVA h2 about 2.11, about 7,000 types, hapax about 0.68, weak next-word information, strong line edges, in-line core reuse), the files that can actually be scored are Chang’s zip, Koshy’s zip, Signorino’s ODS, and Zattera’s slot IVTFF plus the two xlsx files if they can be located. Chang’s top-1 of 0.69 is not yet comparable: his type count is almost double the local EVA count.
- Signorino’s 3.49 bits is near the 4-bit ceiling of a 16-event alphabet, so it does not by itself reproduce the low horizontal h2.
- Koshy’s 84% one-axis gradient is a quire/section vocabulary result, and his own metadata says meaningless controls can reproduce it. That is a claim to score, not a finding that the gradient is linguistic.

### Gaps
- Matlach, Acedo, Zelinka, Steckley, Parisel 2604.25979, and Kinnison: the PDFs may contain tables, but those tables were not extracted, and no public corpus URL was confirmed for them.
- Reddy and Knight’s data deposit, and Hauer and Kondrak’s code, were not found in this pass. What would refute that is a linked repository on the ACL/TACL PDF.
- Many other 2026 Zenodo “decryption” records appeared in OpenAlex (Markov-method, Arabic, IMASM). They are not listed above because the metadata offered a claimed translation rather than a control measurement.

## Abbreviation, Tironian notes, and shorthand controls

### Takeaway
No open diplomatic Tironian or medieval-shorthand corpus, long enough to score as practitioner notation, was identified. The one sourced review points at the literature and does not itself release running text.

### Cited Findings
- Lindemann and Bowern, in the local text of the entropy paper, already test this class of control and reject it for h2: parallel diplomatic versus normalised historical texts, and Hebrew with and without niqqud, “conclude that the unusual character entropy of Voynich is not attributable to conventional scholarly abbreviations or the absence of characters that represent vowels.” H1 is ordinary (3.94 Minimal, 3.91 Maximal) while h2 is the odd quantity. Those diplomatic samples sit in the possessed Bowern–Lindemann corpus, so they are not a new file. — sentences read in `voynich/data/external/bowern-lindemann-entropy/lindemann_bowern_2021_yale.txt` lines 742–762; public versions [arXiv:2010.14697](https://arxiv.org/abs/2010.14697) and [lingbuzz/005522](https://lingbuzz.net/lingbuzz/005522).
- Alpo Honkapohja, “Digital Approaches to Manuscript Abbreviations: Where Are We at the Beginning of the 2020s?,” Digital Medievalist (2021), CC BY, DOI 10.16995/dm.88. OpenAlex calls it a survey of English, French, Old Norse, and some Dutch, German, and Celtic work, plus a conditioned/unconditioned abbreviation typology. The HTML article body did not load in this session (no occurrence of “Tironian” or “Cappelli” in the fetched shell). OA PDF linked by OpenAlex: `https://journal.digitalmedievalist.org/article/id/7025/download/pdf/`. — [DOI 10.16995/dm.88](https://doi.org/10.16995/dm.88).
- A related but different object: a 2023 regex paper for resolving abbreviations in 116 early-modern Latin and Spanish School of Salamanca editions, CC BY, Zenodo 10.5281/zenodo.8163156. That is expansion software for printed scholarly editions, not a Tironian diplomatic transcript, and the edition files were not confirmed downloadable. — [Zenodo 10.5281/zenodo.8163157](https://zenodo.org/record/8163157).

### Inferences
- A shorthand control that could still move the local profile would need running diplomatic text with the abbreviation marks kept, longer than the Bowern historical samples already on disk, and a licence that allows reuse. None was verified.

### Gaps
- No Tironian-note corpus URL, token count, or licence was found. OpenAlex queries for “Tironian notes digital corpus” did not return a transcription project. Cappelli Online / Ad fontes and the Bochum Abbreviationes database were not fetched; their availability is unverified.
- The Honkapohja PDF was not opened, so any corpus it names is not listed here.

## Lullian or combinatory tables

### Takeaway
No open diplomatic transcription of a combinatory or Lullian table longer than the local 957-token 1515 OCR sample was found.

### Cited Findings
- An OpenAlex search for “Ramon Llull Ars brevis diplomatic edition transcription” returned no works. — query against [OpenAlex works API](https://api.openalex.org/works?search=Ramon%20Llull%20Ars%20brevis%20diplomatic%20edition%20transcription).
- The local control note already records the short samples that failed the length test: 1515 Tabula generalis OCR, archive.org `ARes54311_djvu.txt`, Public Domain Mark 1.0; and a 1617 Zetzner OCR under about 200 cells. Those are possessed, not new. — `voynich/data/controls_tabular/README.md`.

### Inferences
- Prose Opera corpora (if added later) would not answer the table question unless the combinatory grid is transcribed as text rather than omitted or pictured.

### Gaps
- Corpus Corporum, the Ramon Llull database, and lullianarts table images were not fetched this session. What would close the gap is a TEI or plain-text grid of Ars brevis / Tabula generalis with a stated token count above a few hundred and an open licence. None was verified.

## What careful reviews say failed or was not replicated

### Takeaway
The sourced objections are about what the statistics mean, not a published failed rerun of the same code. Amancio 2013 and Timm–Schinner 2019 contradict each other on “language-like versus hoax.” Zattera 2022 shows section clusters can be word-structure artefacts. Lindemann–Bowern show low h2 is not what abbreviations or vowelless Hebrew look like. A 2026 reviewer explicitly says Amancio and Montemurro were not refuted.

### Cited Findings
- Network / “compatible with language”: Diego R. Amancio et al., PLOS ONE 2013, CC BY. Abstract: metrics that separate real text from shuffled text include assortativity, degree, and selectivity; the Voynich manuscript “is mostly compatible with natural languages and incompatible with random texts,” and they offer keyword candidates. The abstract does not name a language and does not mention PCA. — [PLOS ONE 10.1371/journal.pone.0067310](https://doi.org/10.1371/journal.pone.0067310).
- Opposed result, same general method family: Timm and Schinner 2019 (citation above) say a network analysis of token similarity supports meaningless self-citation, and that their sample reproduces both Zipf laws. — [DOI 10.1080/01611194.2019.1596999](https://doi.org/10.1080/01611194.2019.1596999).
- Not a replication failure: Rozanova and Temerev, arXiv:2608.17096 (2026), already held locally, write that Amancio et al. 2013 and Montemurro and Zanette 2013 “are therefore not contradicted; they measure the edge scale, or longer-range co-occurrence, rather than adjacent token identity.” — local extract `voynich/data/external/papers/rozanova_temerev_2026_arxiv_2608.17096.txt` lines 771–774; [arXiv:2608.17096](https://arxiv.org/abs/2608.17096).
- Topic / section clusters: Zattera 2022, after a 92% versus 54% section tree on four short glyph sequences, says differences between sections “is not a difference in their Voynich vocabularies” but in word-internal structure, and that clustering on bag-of-words or TF-IDF can surface the generator rather than plaintext terminology. That is an alternative account of topic-like page clusters, not a reimplementation of Montemurro and Zanette’s keyword statistic. — [CEUR paper 10](https://ceur-ws.org/Vol-3313/paper10.pdf).
- Language identification from entropy, including Hebrew: Lindemann and Bowern (citation in the abbreviation section) state the aim is not a claim of the form “Voynichese is Hebrew,” and that abbreviations and missing vowel letters do not produce the Voynich h2. H1 stays inside the alphabetic range 3.57–4.82 while h2 does not. — `lindemann_bowern_2021_yale.txt` lines 108–121 and 739–762; [arXiv:2010.14697](https://arxiv.org/abs/2010.14697).
- Hauer and Kondrak’s Hebrew suggestion is the pipeline result quoted above (97% / 93% on known ciphers; “suggest Hebrew” on Voynich). Zattera 2022’s argument against it, as a class of cipher rather than a rerun: slot structure “rules out” simple substitution, including letters sorted before substitution, because a sorted cipher should have one glyph per slot and frequent repetitions, which he says the manuscript does not. He does not recompute their 93% word accuracy. — [CEUR paper 10](https://ceur-ws.org/Vol-3313/paper10.pdf); [TACL paper](https://doi.org/10.1162/tacl_a_00084).
- PCA language identification: no paper in this pass both uses PCA to name a plaintext language and is answered by a reviewer who says that PCA result failed to replicate. Zelinka et al. 2023 is deep-learning alphabet similarity, not a PCA table. — [DOI 10.1016/j.asoc.2023.110217](https://doi.org/10.1016/j.asoc.2023.110217).

### Inferences
- The conflict worth scoring is Amancio (“incompatible with random texts”) versus Timm–Schinner (“hoax” / self-citation can make Zipf). Rozanova’s reading is that the network papers measure edges and long range, which the local profile already treats as separate from weak next-word identity. Zattera’s 92% section tree is the direct caution against reading quire vocabulary clusters as topics.
- Hauer and Kondrak’s 97% and 93% are accuracy on constructed ciphers. Using them as a Voynich success rate would misread the abstract.

### Gaps
- Montemurro and Zanette 2013 was not re-read for a critic who recomputed their keyword information and got a different number. Rozanova says the result stands at a different scale.
- No sourced failed replication of a named PCA language call was found. What would close that is a review that names the PCA study, the language it ranked first, and a recomputation.
- Matlach, Janečková, and Dostál 2023 may discuss which Malta papers failed, but the article is not open in the OpenAlex record and was not read.
