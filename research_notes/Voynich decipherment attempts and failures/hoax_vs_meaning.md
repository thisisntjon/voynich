# The Voynich Manuscript: "No Meaning" (Hoax/Generated/Gibberish) vs "Meaningful Text"

Research cut-off: searches run 2026-10-17. Sources include peer-reviewed papers, preprints, blogs and forums, and each item below says which. Items from 2024 to 2026 are tagged **[2024–26]**.

## 1. Rugg's table-and-Cardan-grille hypothesis (Cryptologia 2004) and Rugg & Taylor (2016)

### Takeaway
Rugg showed that a table of syllable fragments read through a moving grille can quickly produce text that looks like Voynichese, and Rugg & Taylor (2016) argued that several of the manuscript's unusual statistics could come from such a low-tech hoax. The main objections are that the Cardan grille dates from about 1550, a century after the radiocarbon date of the vellum, and that the mimicry was never shown to fit the full statistical profile. The tables were never derived from the real text, and the method needs ad hoc rules. A 2026 preprint reports that a Rugg-style grille generator fails a joint four-signature test.

### Cited Findings
- Rugg's method uses a modified Cardan grille over a large table of meaningless syllables to generate Voynich-like text — [Wikipedia: Gordon Rugg](https://en.wikipedia.org/wiki/Gordon_Rugg)
- Rugg's own position is that he showed the manuscript *could* be a hoax, not that it *is* one — [RFE/RL](https://www.rferl.org/a/1053943.html). Rugg stressed he had not set out to prove a hoax, and his prime suspect is Edward Kelley, the Elizabethan con-man who also produced the "Enochian" language — [Boston Globe 2014](https://www.bostonglobe.com/ideas/2014/02/23/why-scholars-can-resist-uncrackable-voynich-manuscript/FWGMJjrqolrQ50L86SpkQP/story.html)
- Dating of the first work is inconsistent across sources. A 2003 news report describes the grille demonstration ([MIT crypto list archive](https://datwww.mit.edu/bloom-picayune/crypto/15126)), while the Cryptologia article is usually cited as 2004 ([Klausis Krypto Kolumne](https://scienceblogs.de/klausis-krypto-kolumne/2016/10/28/has-gordon-rugg-solved-the-mystery-of-the-voynich-manuscript-text-part-2/?all=1)).
- Rugg & Taylor, "Hoaxing statistical features of the Voynich Manuscript," *Cryptologia* (2016; peer-reviewed). It argues the main unusual features are "explicable as products of a low-technology hoax", with table and grille selection producing the appearance of the two Currier "languages" — [Cipher Mysteries](https://ciphermysteries.com/2016/09/14/gordon-rugg-man-cracked-mystery-voynich-manuscript-cracks-not). Taylor was Rugg's student, and the paper examined four statistical properties, including word-frequency distributions — [Klausis Krypto Kolumne](https://scienceblogs.de/klausis-krypto-kolumne/2016/10/28/has-gordon-rugg-solved-the-mystery-of-the-voynich-manuscript-text-part-2/?all=1)
- Objections from Nick Pelling (blog, not peer-reviewed), all at [Cipher Mysteries](https://ciphermysteries.com/2016/09/14/gordon-rugg-man-cracked-mystery-voynich-manuscript-cracks-not):
  - Anachronism: the grille dates from about 1550, but the vellum is radiocarbon-dated to the early 15th century, and the handwriting and quire numbers also look 15th-century.
  - Weak mimicry: the output resembles Voynichese only "if you didn't look too closely," and the tables were never reconstructed from the actual text.
  - Ad hoc rules: line-initial, line-final, paragraph and section-specific cases need extra rules, which Pelling calls a modern computer-science layering.
  - Pelling called the paper "specious quasi-academic nonsense."
- Commenters in the same thread (forum-level, not peer-reviewed), at [Cipher Mysteries](https://ciphermysteries.com/2016/09/14/gordon-rugg-man-cracked-mystery-voynich-manuscript-cracks-not):
  - Generated text has abnormally few unique words and low edit distance.
  - The claimed binomial word-length distribution was not shown from actual generated output.
  - The statistical oddities are pushed into the choice of tables rather than arising from the method.
  - The frequent words *otol* and *odaiin* co-occur in the same f1r paragraph, which a hoax must treat as coincidence.
- Schinner (2007, *Cryptologia* 31:95; peer-reviewed) supported the hoax side using random-walk mapping:
  - Normal texts behave like uncorrelated random walks, but the Voynich text does so only up to about one line length, and positive correlations build up beyond that.
  - He concluded the text is consistent with stochastic generation of the Rugg type.
  - He also cautioned that the grille is "just a possibility and far from a proof."
  - Sources: [Der Standard](https://www.derstandard.at/story/2846340/das-geheimnis-des-voynich-codes), [Voynich Ninja quoting the paper](https://www.voynich.ninja/archive/index.php/thread-1812-4.html), [Boing Boing 2007](https://boingboing.net/2007/04/17/analysis-suggests-th.html)
- **[2024–26]** Parisel, "Evidence of Layered Positional and Directional Constraints in the Voynich Manuscript," arXiv 2604.19762 (v1 26 March 2026, v2 16 June 2026; preprint, not peer-reviewed). It tests a parametric slot-based generator and a Cardan grille implementing Rugg (2004) against a four-signature criterion, and finds "neither class reproduces all four signatures simultaneously." It also reports that generators whose only mechanism is frequency concentration cannot satisfy the joint profile for either dialect. The author says the findings do not discriminate between the natural-language, gibberish and cipher hypotheses — [arXiv 2604.19762](https://arxiv.org/abs/2604.19762)

### Inferences
- The grille's role in the debate has shifted from "this is how it was made" to "a hoax is feasible." Its weak point is that it fits the statistics only after hand-tuning the tables. The anachronism objection weakens if one allows a table-based method that does not need Cardan's grille, but Rugg's specific mechanism is still tied to roughly 1550.

### Gaps
- I could not read the full text of Rugg 2004 or Rugg & Taylor 2016 (paywalled), so the four properties tested and the numeric fit are unverified.
- I found no peer-reviewed formal rebuttal of Rugg & Taylor; the critiques I found are from blogs and forums.
- I did not get the list of the four signatures in Parisel 2026.

## 2. Timm's self-citation hypothesis (2014) and Timm & Schinner (Cryptologia 2020)

### Takeaway
Timm proposes that the scribe generated text by copying earlier words, often from nearby lines, and modifying them by glyph substitution. Timm & Schinner implemented this as a simple algorithm and claim it reproduces Zipf's laws, binomial-like word lengths, long-range correlations and the similarity of neighbouring words. Critics say it is underspecified and "stretchy" enough to be unfalsifiable, misses line-position effects, and needs finely tuned mutation probabilities.

### Cited Findings
- Timm, "How the Voynich Manuscript was created," arXiv 1407.6639 (v1 24 July 2014, v3 9 December 2015; 96 pages; preprint). It studies relationships between similarly spelled words to reveal the text generation method — [arXiv 1407.6639](https://arxiv.org/abs/1407.6639)
- Timm & Schinner, "A possible generating algorithm of the Voynich manuscript," *Cryptologia* (online 25 May 2019, issue dated 2020; peer-reviewed; paywalled, code on GitHub) — [Voynich Ninja](https://www.voynich.ninja/archive/index.php/thread-3647.html)
  - The authors claim the method is executable "even by a medieval scribe" without tools and reproduces the statistical key properties, including both Zipf's laws — [Voynich Ninja](https://www.voynich.ninja/archive/index.php/thread-2790-2.html)
  - The implementation is said to reproduce long-range correlations, the "binomial-like" word-length distribution and both Zipf's laws — [Voynich Ninja thread 2790](https://www.voynich.ninja/archive/index.php/thread-2790-18.html) (forum quotation of the abstract; I did not verify it against the paper itself)
- Klaus Schmeh described the method as making a few text pieces and then repeating them many times with changes, which is the "self-citation." He later framed it as a partial model of an unconscious cognitive process — [Voynich Ninja](https://www.voynich.ninja/archive/index.php/thread-3647.html)
- The paper explains the gap between its output and real Voynichese by appeal to unconscious "spontaneous impulses" of the scribe — [Voynich Ninja](https://www.voynich.ninja/archive/index.php/thread-3647.html)
- Jorge Stolfi (forum) says the copying part is easy but the mutation part would need finely tuned probabilities at each word, which makes it an implausible forger's choice. The authors reply that the regularities arise without parameter tuning — [Voynich Ninja](https://www.voynich.ninja/archive/index.php/thread-3647.html)
- MarcoP (forum, September 2021) reports that the Timm & Schinner output gives flat line-position plots, while Quire 20 of the manuscript shows clear positional preferences. On this test the line effects are **not reproduced** — [Voynich Ninja thread 3647](https://www.voynich.ninja/archive/index.php/thread-3647.html)
- Other forum criticisms, all at [Voynich Ninja](https://www.voynich.ninja/archive/index.php/thread-3647.html):
  - Emma May Smith: the rules are not explained, and appeals to aesthetics leave a "closed box."
  - RenegadeHealer: the method is vague on execution (line by line or page-wide) and flexible enough to fit any uniform asemic text, so it is unfalsifiable, though a meaningless text remains a sound null hypothesis.
- Another forum objection is that the method is "not very well formulated" to test. Timm's reply is that the scribe "had complete freedom to vary some details" — [Voynich Ninja thread 2790](https://www.voynich.ninja/archive/index.php/thread-2790-18.html)
- Gaskell & Bowern (2022) say their results are "generally consistent" with self-citation, and that their volunteers often intuitively copied and modified earlier words — [Gaskell & Bowern, CEUR Vol-3313 paper 4](https://ceur-ws.org/Vol-3313/paper4.pdf)

### Inferences
- Self-citation is the most developed "no meaning" generator. Its strongest feature is that it explains the high similarity of adjacent words and the low information content naturally, without a table. Its weakest points are line-position structure and the lack of a fully specified, falsifiable procedure.

### Gaps
- I could not access the Cryptologia full text, so I cannot confirm whether it claims to reproduce Montemurro-style section keywords, Currier A/B, or label behaviour.

## 3. Gaskell & Bowern (2022), "Gibberish after all?"

### Takeaway
In a peer-reviewed conference paper (4 anonymous reviewers), 42 volunteers wrote 1–3 pages of handwritten "gibberish." It matched Voynichese on most low-level metrics: lower information content, more repetition, positive autocorrelation of word lengths, weaker Zipf fit, and positional bias. A random-forest classifier put all five Voynich transcriptions closer to gibberish than to 75 meaningful texts, though with low confidence. The samples were too short to test page-, section- and quire-level structure, which the authors concede "pose a serious challenge" to the hoax hypothesis.

### Cited Findings
All findings in this section are from [Gaskell & Bowern, "Gibberish after all? Voynichese is statistically similar to human-produced samples of meaningless text," Proc. International Conference on the Voynich Manuscript 2022 (Malta), CEUR-WS Vol-3313, paper 4](https://ceur-ws.org/Vol-3313/paper4.pdf).
- **Participants:** 42 volunteers in total.
  - 39 were Yale undergraduates in Bowern's Voynich course: 19 from 2018, before they learned the Voynich statistics, and 20 from 2019, later in the semester.
  - 3 were naive members of the public, and the authors added 3 samples of their own.
  - All were fluent English speakers. They wrote in pen, without punctuation, in lowercase Latin letters.
- **Comparison corpus:** 75 meaningful texts (5.6 million words). The Voynich corpus had five transcriptions or subsets: Glen Claston's v101, Takahashi EVA Full, EVA Basic, and the Currier A and Currier B subsets.
- **Metrics:** 42 metrics, including:
  - DEFLATE compression and h2 conditional character entropy
  - repeated and tripled characters and words
  - character and word position bias within lines and words
  - Moran's I autocorrelation of word lengths
  - Levenshtein-based vocabulary diversity and Zipf fit
- **Results:**
  - Gibberish varies widely and can replicate meaningful text on every variable tested (36 probable, 6 plausible).
  - Gibberish means differ from meaningful text (p < 0.05) in the same directions the Voynich text differs.
  - The Voynich text plausibly resembles meaningful text on 38 of 42 metrics and gibberish on 41 of 42. The exception is character position bias within words.
  - The random forest classed all five Voynich transcriptions as more like gibberish, "albeit with low confidence."
- **Word-length autocorrelation:** meaningful text is usually negatively autocorrelated (long-short-long-short), while both the Voynich text and gibberish are positively autocorrelated. Participants reported that after a run of long words they would correct by switching to short words.
- **Text wrapping:** 31 samples included illustrations, and 17 showed evidence of word lengths chosen to wrap around them, comparable to f29v. The authors say this is hard to quantify.
- **Contamination check:** they found no significant specialist versus non-specialist differences. The 2018 and 2019 cohorts differed only modestly (for example, 11% higher character position bias), and dropping the authors' samples changed nothing.
- **Topic words:** one participant captioned a drawing "pitshol" and reused "pitshol"/"pitsholh" nearby, which suggests gibberish can produce rudimentary "topic words."
- **Limitation stated by the authors:** the samples are too short to test whether gibberish can reproduce the larger structural features, such as topic words, which "at present … pose a serious challenge to proponents of the hoax hypothesis."
- **Companion paper:** Bowern & Gaskell, "Enciphered after all?", was presented at the same conference. Both papers are agnostic, with the conflicting titles intended — [Voynich Ninja thread 4531](https://www.voynich.ninja/thread-4531.html)
- Code and data are public at github.com/danielgaskell/voynich — [GitHub README](https://raw.githubusercontent.com/danielgaskell/voynich/main/README.md)

### Inferences
- This is the strongest empirical support for "meaningless *could* be the case" at the low level: humans writing gibberish naturally produce low entropy, repetition and positive length autocorrelation. It does not test Currier A/B, page-level or section-level keyword structure, line-initial and line-final glyph effects (character position bias within lines is *not* significantly different between the Voynich text and meaningful text), or labels. The participants used the Latin alphabet, not a novel script.

## 4. Evidence for meaning: Montemurro & Zanette 2013, Amancio et al. 2013, topic modelling, illustrations

### Takeaway
Three lines of peer-reviewed work find structure typical of language. Montemurro & Zanette (2013) find section-specific keywords at language-like scales. Amancio et al. (2013) place the text inside the natural-language range on network and intermittency measures. Sterneck, Polish & Bowern (2021) find topic clusters that align with scribe plus illustrated subject. Critics point out three problems. Co-occurrence is assumed rather than shown to be semantic. The topic structure may reflect the scribes, or Currier A/B, rather than meaning. And the low-level tests (Zipf and others) are also passed by gibberish.

### Cited Findings
- Montemurro & Zanette, "Keywords and Co-Occurrence Patterns in the Voynich Manuscript: An Information-Theoretic Analysis," *PLoS ONE* 8(6): e66344 (2013; peer-reviewed) — [PMC3689824](https://pmc.ncbi.nlm.nih.gov/articles/PMC3689824)
  - **Data and method:** Stolfi's EVA transcription, reordered into five thematic sections: Herbal, Astrological, Biological, Pharmacological and Recipes. For each word they measure how much it tells about which section it comes from, corrected against shuffled text.
  - **Peak scale:** information per word peaks at about 600–800 words (optimum 807), similar to natural languages and unlike yeast DNA or Fortran code.
  - **Peak height:** slightly above English and below Chinese, where natural languages range from about 0.2 bits/word (Latin) to 0.6 (Chinese).
  - **Keywords:** the top keywords are *shedy, daiin, qokeedy, chedy*. Keyword networks share prefixes and suffixes.
  - **Section links:** the strongest is Herbal with Pharmacological, which share plant drawings. The second is Recipes with Astrological, which share a star-like motif.
  - **Their claims:** hoax methods "can hardly account for the presence of Zipf's law," and the results "limit severely the scope of the hoax hypothesis." They concede the semantic reading rests on "assuming that co-occurrence reveals semantic affinity."
- Amancio, Altmann, Rybski, Oliveira Jr. & Costa, "Probing the Statistical Properties of Unknown Texts: Application to the Voynich Manuscript," *PLoS ONE* (2 July 2013), doi 10.1371/journal.pone.0067310 (peer-reviewed) — [PMC3699599](https://pmc.ncbi.nlm.nih.gov/articles/PMC3699599) / [arXiv 1303.0347](https://arxiv.org/pdf/1303.0347)
  - It uses word statistics, network topology (assortativity, degree, selectivity) and intermittency, calibrated on the New Testament in 15 languages plus English and Portuguese books.
  - The Voynich text is mostly compatible with natural languages and incompatible with random (shuffled) texts. Wikipedia summarises this as compatible "in 90% of cases" — [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript)
- Sterneck, Polish & Bowern, "Topic Modeling in the Voynich Manuscript," arXiv 2107.02858 (2021; preprint, reportedly later published). They apply LDA, LSA and NMF to text chunks and find that clusters "match closely to a conjunction of scribe and subject matter (as per the illustrations)." They warn that without a consistent word representation, no clear topic structure would be expected — [Yale PDF](https://alumniacademy.yale.edu/sites/default/files/2021-07/Topic%20Modeling%20in%20the%20Voynich%20Manuscript.pdf), [ar5iv](https://ar5iv.labs.arxiv.org/html/2107.02858)
  - Forum critique: the "sections" in their Figure 1 do not seem to be based on the illustrations, and the open question is whether the topic signal reflects scribe or subject — [Voynich Ninja thread 4834](https://www.voynich.ninja/thread-4834.html)
- Lisa Fagin Davis identified five scribes from letterforms that change between sections but not within them — [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript). Because scribes line up with sections, scribe identity is a confound for "keywords cluster by section."
- Bowern & Lindemann, "The Linguistics of the Voynich Manuscript," *Annual Review of Linguistics* (2021; peer-reviewed review) "provide arguments for treating the document as natural language" — [Annual Reviews](https://annualreviews.org/doi/abs/10.1146/annurev-linguistics-011619-030613). Their h2 is about 2 for the Voynich text versus 3–4 for natural languages — [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript)
- Gaskell & Bowern's 2022 data undercut the Zipf argument: gibberish can satisfy Zipf's law, though with a weaker average fit — [CEUR 3313/4](https://ceur-ws.org/Vol-3313/paper4.pdf)
- **[2024–26]** "The Application of Latent Semantic Analysis to the Voynich Manuscript" (ResearchGate, about 2025–26; peer-review status unknown). I saw only its abstract, so its results are unverified — [ResearchGate](https://www.researchgate.net/publication/405027080_The_Application_of_Latent_Semantic_Analysis_to_the_Voynich_Manuscript)
- **[2024–26]** Forum analyses (not peer-reviewed) running LDA, BERTopic and NMF page by page against the illustrated sections — [Voynich Ninja thread 4834](https://www.voynich.ninja/archive/index.php/thread-4834.html)

### Inferences
- The 2013 "pro-meaning" results argued against random or shuffled text, not against a human or algorithmic process with memory. Self-citation and drifting gibberish could in principle produce section-local vocabulary. Whether they reproduce the 600–800-word peak and the herbal–pharma linkage has not been tested in published work I found. Section and scribe alignment also means section keywords could reflect five scribes with different habits rather than different topics.

### Gaps
- I found no peer-reviewed paper that directly reruns Montemurro & Zanette's measure on Timm & Schinner output or on long gibberish. Forum claims of this kind may exist but were not located.
- I found no study that statistically links label words to the specific plants or images they sit beside.

## 5. Hoax-author theories (Kelley, Wilfrid Voynich) and what dating and provenance imply

### Takeaway
The radiocarbon date of the vellum (1404–1438, University of Arizona, 2009) together with 1639 and 1665/66 letters describing the book effectively excludes Wilfrid Voynich as forger and makes Kelley, active in the 1580s, unlikely. He would have had to use century-old blank vellum, and Rugg's grille would be roughly contemporary with him rather than with the vellum. A medieval (15th-century) hoax or a meaningless text is not excluded.

### Cited Findings
- **Vellum date:** the 2009 University of Arizona AMS radiocarbon tests gave 1404–1438, consistent across all samples. 2014 protein testing showed calfskin, and multispectral imaging showed it is not a palimpsest — [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript)
- **Inks and paints:** McCrone Associates found the paints consistent with the period. The text is iron-gall ink, and the pigments include azurite. Wikipedia calls claims that the ink was proven to be added soon after the parchment was made "erroneous" — [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript)
- **Provenance:**
  - Georg Baresch's 1639 letter to Kircher is the earliest confirmed mention.
  - Marci's letter of 1665/66 repeats Mnishovsky's claim that Rudolf II paid 600 ducats. The only matching record is a 1599 purchase from Carl Widemann for 600 florins.
  - Voynich acquired the book in 1912, and Kraus donated it to Yale in 1969.
  - All from [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript)
- **Who has been suspected:**
  - Voynich himself has been suspected of forgery. Eamon Duffy argues the radiocarbon date effectively rules out a post-medieval forgery.
  - Mnishovsky, using Baresch as a test subject, and an Andreas Müller-style hoax on Kircher have been floated.
  - Dee and Kelley appear among speculative authors.
  - All from [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript)
- Kelley is Rugg's prime suspect because he produced Enochian — [Boston Globe](https://www.bostonglobe.com/ideas/2014/02/23/why-scholars-can-resist-uncrackable-voynich-manuscript/FWGMJjrqolrQ50L86SpkQP/story.html)
- Pelling's anachronism point is that the handwriting and quire numbers are 15th-century, so a grille hoax would need a late-16th-century forgery on old vellum — [Cipher Mysteries](https://ciphermysteries.com/2016/09/14/gordon-rugg-man-cracked-mystery-voynich-manuscript-cracks-not)
- The vellum date does not date the ink. Unused pristine vellum surviving for a long time is "not impossible … but quite improbable" (forum opinion) — [Voynich Ninja](https://www.voynich.ninja/archive/index.php/thread-5008-11.html)
- René Zandbergen is described as suspecting the text has genuine meaning that may never be decipherable — [Boston Globe](https://www.bostonglobe.com/ideas/2014/02/23/why-scholars-can-resist-uncrackable-voynich-manuscript/FWGMJjrqolrQ50L86SpkQP/story.html)

### Inferences
- The live "no meaning" position today is a 15th-century meaningless text (glossolalia, asemic writing, or self-citation, possibly made in good faith) rather than a Kelley or Voynich forgery. Gaskell & Bowern explicitly frame it as "automatic writing or glyptolalia."

### Gaps
- The voynich.nu pages on dating and forgery could not be fetched (the URL I tried returned 404). I found no source that quantifies the "old blank vellum" scenario.

## 6. Has any generator reproduced ALL key properties? What remains unexplained on each side?

### Takeaway
No. As of October 2026 I found no generator, meaningless or cipher, that is shown to reproduce the full set together: low h2, binomial word lengths, Zipf, Currier A/B, line-initial and line-final effects, section keywords and label behaviour. Timm & Schinner come closest for the "no meaning" side but miss line-position effects. Greshko's Naibbe cipher (Cryptologia, November 2025) shows that a 15th-century-feasible cipher of Latin or Italian can match many properties, but it fits Currier B incompletely. A 2026 preprint shows grille and slot generators fail a joint positional and directional test. The meaningful side has no decipherment and has never explained the very low h2 or the extreme similarity of neighbouring words.

### Cited Findings
- **[2024–26]** Greshko, the "Naibbe cipher," *Cryptologia* (online 26 November 2025; peer-reviewed; independent researcher and science journalist) — [Sci.News](https://www.sci.news/othersciences/linguistics/voynich-manuscript-cipher-14466.html)
  - It is a verbose homophonic substitution cipher of Latin or Italian into Voynich-like glyph strings, executable with early-15th-century materials, in 78-card tarocchi and 52-card deck variants.
  - It reproduces "many properties … at once" and an expanded slot grammar.
  - Its replication of Currier B is incomplete.
  - It does not show that the manuscript actually used this cipher.
- The author calls the Naibbe cipher a proof of concept, not a solution — [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript); [IFLScience](https://www.iflscience.com/is-this-how-the-voynich-manuscript-was-made-a-new-cipher-offers-fascinating-clues-81786)
- **[2024–26]** Parisel, arXiv 2604.19762 (2026 preprint) — [arXiv](https://arxiv.org/abs/2604.19762)
  - It reports right-to-left optimisation within words and left-to-right dependency at word boundaries, which are absent in English, French, Hebrew and Arabic.
  - Slot-based and Rugg grille generators fail the joint four-signature profile.
  - It does not discriminate between gibberish, language and cipher.
- **[2024–26]** Parisel, "Directionality of the Voynich Script," arXiv 2509.10573 (September 2025; preprint): an n-gram perplexity asymmetry suggests right-to-left optimisation — [arXiv 2509.10573](https://arxiv.org/html/2509.10573v2)
- Timm & Schinner output does not show line-position trends (forum test, 2021) — [Voynich Ninja 3647](https://www.voynich.ninja/archive/index.php/thread-3647.html)
- Gaskell & Bowern 2022 could not test page, section or quire structure — [CEUR 3313/4](https://ceur-ws.org/Vol-3313/paper4.pdf)
- Low h2 (about 2 versus 3–4 for natural languages) is a property natural language struggles to explain — [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript). Gibberish also has lower mean h2 than meaningful text — [CEUR 3313/4](https://ceur-ws.org/Vol-3313/paper4.pdf)
- Basic counts: about 37,919 word tokens, 8,114 types, more than 170,000 characters — [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript)
- **[2024–26]** Self-published "decipherments" (for example, a Zenodo package from December 2025 and a 2025 ResearchGate PDF claiming 99.8% confidence) are not peer-reviewed and are not credible evidence — [Zenodo 17794596](https://zenodo.org/records/17794596), [ResearchGate](https://www.researchgate.net/publication/393106168_Deciphering_the_Voynich_Manuscript_Complete_2025)

**Scorecard** (my synthesis of the sources above; "untested" means I found no published test):

| Property | Rugg grille | Timm & Schinner | Human gibberish (G&B) | Naibbe cipher |
|---|---|---|---|---|
| Low h2 / low information | claimed | claimed | yes | many props (unspecified) |
| Binomial-like word lengths | claimed, disputed | claimed | not specifically reported | untested here |
| Zipf | claimed | yes (both laws, claimed) | yes (weaker fit) | ? |
| Similarity of adjacent words | partial | yes (core mechanism) | yes (repetition) | ? |
| Currier A/B | claimed via table switch | not verified | untested | B incomplete |
| Line-initial/final effects | via ad hoc rules | **no** (flat) | char-line bias not distinctive | ? |
| Section keywords (M&Z) | untested | not verified | untested (too short) | ? |
| Labels | untested | untested | anecdotal ("pitshol") | ? |
| Joint positional/directional (Parisel 2026) | **fails** | untested | untested | untested |

### Inferences
- **State of the debate, October 2026:** the low-level statistics no longer discriminate between the hypotheses. Gibberish, self-citation and a verbose cipher can all produce low entropy, Zipf behaviour and slot-like words.
- The discriminating evidence has moved to large-scale and positional structure: section and scribe keywords, Currier A/B, line effects, directional constraints, and labels. No side has a model that passes all of these.
- The "no meaning" side must explain section-level vocabulary and line-position regularities with a historically plausible procedure.
- The "meaning" side must explain h2 of about 2, positive word-length autocorrelation and adjacent-word similarity, and it still lacks a decipherment.
- Recent momentum (2025–26) has been toward historically plausible cipher models (Naibbe) and stricter benchmarks (Parisel) rather than new hoax models.

### Gaps
- I found no peer-reviewed 2024–2026 work from the hoax or gibberish side; the latest substantive work there is Gaskell & Bowern 2022.
- I found no Scientific American or New Scientist coverage of 2024–2026 work in this search.
- The full texts of the Cryptologia papers (Rugg 2004, Rugg & Taylor 2016, Timm & Schinner 2020, Greshko 2025) were paywalled, so their exact numeric fits are unverified.
