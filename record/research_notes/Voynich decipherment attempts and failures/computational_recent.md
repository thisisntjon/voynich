# Computational, Statistical and Linguistic Analyses of Voynichese (focus 2019 to Oct 2026)

Notes compiled 2026-10-17 14:57 PDT (clock read from `date`). Items from 2024 to 2026 are marked **[2024-26]**. Where a figure comes only from a search-engine summary and not from the primary document, it is marked "(summary-level, unverified against primary)". About 17 tool calls were used. Primary documents opened in full: Lindemann & Bowern 2020 entropy paper (lingbuzz 005522, read via pdftotext), arXiv 2608.17096 abstract page, voynich.nu a2_char, a5_synt and transcr pages.

## 1. Character-level entropy (Bennett 1976 and later; alphabet and transcription effects)

### Takeaway
Every study finds the same result: Voynichese single-character frequencies (h1) are normal, but conditional (second-order) entropy h2 is anomalously low. h2 is about 2.2 bits in EVA-like transcriptions and about 2.4 in "minimal" glyph groupings, against 2.85 to 6.25 bits for 294 Wikipedia languages and about 3.0 to 3.5 for European languages. Regrouping glyphs moves h2 by a few tenths of a bit. No tested transcription choice closes the gap. The cause is rigid positional constraints on glyphs within the word.

### Cited Findings
- Bennett (1976), as tabulated on voynich.nu: h1 for normal languages 3.91 to 4.14 vs Voynich 3.66; h2 3.01 to 3.37 vs Voynich 2.22; h3 2.12 to 2.62 vs 1.86. Bennett used his own alphabet. Hawaiian was the only language with similarly low values. — [voynich.nu a2_char](https://www.voynich.nu/a2_char.html)
- Lindemann & Bowern, "Character Entropy in Modern and Historical Texts" (27 Oct 2020; updated 2021). They built a Voynich corpus split by Currier language, Davis scribal hand and transcription, plus 294 Wikipedia language samples and 18 historical texts in 8 languages (316 comparison texts in total; the 2021 update reports 311 samples). — [lingbuzz 005522 PDF](https://lingbuzz.net/lingbuzz/005522/v1.pdf); [Yale alumni-academy copy](https://alumniacademy.yale.edu/sites/default/files/2021-07/Character%20Entropy%20in%20Modern%20and%20Historical%20Texts%20Comparison%20Metrics%20for%20an%20Undeciphered%20Manuscript.pdf)
- Same paper: H1 is 3.88 for "Minimal" Voynich and 3.94 for "Maximal" Voynich (Maximal is equivalent to EVA). The corpus range is 3.72 to 4.82, so H1 is unremarkable. — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)
- Same paper: across all Voynich subsets, alphabet sizes run from 20 to 45 characters and h2 from 1.95 to 2.50 bits. Full Voynich h2 is 2.159 for Full Maximal and 2.157 for Simplified Maximal; dropping 20 rare characters changes h2 by only 0.09%. Minimal Voynich averages h2 about 2.43 vs about 2.16 for Maximal. The Wikipedia h2 range is 2.85 to 6.25, so no language reaches Voynich levels. — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)
- Same paper: English Wikipedia h2 is 3.45. With 10,000-word windows, h2 is accurate to about 0.1 bit (SD 0.039). Voynich A has about 11k words and B about 23k (about 38k in total), enough for reliable A and B estimates but less reliable per section, hand or folio. Latin-script texts range from 2.8 to 3.8. — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)
- Same paper: what matters is how common glyph sequences are composed (Minimal vs Maximal), not the inclusion of rare characters. Language B has lower h2 than A in every transcription. Word-final -edy is 86 times more common in B (1 in 5 B words ends in it), and word-initial qo- is about twice as common in B (also about 1 in 5 words). Removing those two sequences brings A and B h2 within 3% of each other. — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)
- Same paper: positional rigidity. 41% of words end in y, and 93% end in y, n, l, r, m or s. In the Simple Maximal transcription, 11 bigrams have conditional probability above 50% and make up 29.5% of the text (Minimal: 23 bigrams, 23.9%). English Wikipedia has 4 such bigrams, making up 3.1%. The closest natural texts are Min Dong, Hakka and Venda, which are tonal or written without tone or vowel marking. Conclusion: a simple monoalphabetic substitution cannot change h2, so if the text is a cipher it is more complex than that, and most polyalphabetic ciphers are ruled out. The authors favour "the script ignores certain sound distinctions" of the underlying language. — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)
- **[2024-26]** Rozanova & Temerev, arXiv:2608.17096 (17 Aug 2026), using ZL with matched prose, cipher and pseudo-text controls: glyph conditional entropy about 2.7 bits vs about 3.5 for Latin, Italian and English. They argue glyphs resolve into multi-symbol units rather than one-to-one letters. — [arXiv 2608.17096](https://arxiv.org/abs/2608.17096)
- A forum summary says only systematic conflation of phonemic distinctions (for example, merging all vowels into one sign) reproduces Voynich-level h2. The Voynich behaves as if choosing among about 4 equally likely continuations where Latin has about 10. — [voynich.ninja thread 3344](https://www.voynich.ninja/archive/index.php/thread-3344.html) (forum, secondary)

### Inferences
- The two h2 figures (2.16 to 2.2 in Lindemann & Bowern and Bennett vs about 2.7 in Rozanova & Temerev) probably differ in alphabet grouping and in whether spaces count as characters. Report h2 as a range of about 2.0 to 2.7 depending on segmentation, always below about 2.85, the lowest of 294 languages.

### Gaps
- I found no systematic published table of h2 across the EVA, v101, Currier and FSG alphabets. voynich.nu shows only plots (Stallings 1998).

## 2. Word-structure models (Stolfi, Zattera, Emma May Smith, Bowern & Lindemann): word, syllable or something else?

### Takeaway
Most Voynich "words" fit a small left-to-right slot grammar. Zattera reports 86.6% of tokens fitting 12 slots. This is far more regular than natural-language words. The 2020s literature increasingly treats the space-delimited token as a unit of uncertain status: perhaps a syllable- or morpheme-like chunk, or a cipher group. It is not necessarily a word.

### Cited Findings
- Zattera, "A New Transliteration Alphabet Brings New Evidence of Word Structure and Multiple 'Languages' in the Voynich Manuscript" / slot model (Voynich 2022 conference, CEUR Vol-3313 paper 10). Each word type is built from 12 slots, each empty or holding one glyph. 86.6% of tokens fit. "Separable words" (splittable into two valid words) account for 3,249 tokens (10.4%). — [CEUR Vol-3313 paper10](https://ceur-ws.org/Vol-3313/paper10.pdf) (figures summary-level, unverified against primary); [Voynich Reconsidered blog](https://www.goodreads.com/author_blog_posts/24929186-voynich-reconsidered-zattera-s-separable-words?tab=author)
- Critique: slots 7 to 11 share glyphs with slots 0 to 2, so the sequence wraps around and strings like "sheolkeedy" can be split several ways. A forum post reports Zattera's grammar F1 = 0.27. — [voynich.ninja thread 4134](https://www.voynich.ninja/thread-4134.html); [thread 4418](https://www.voynich.ninja/archive/index.php/thread-4418-7.html) (forum, second-hand)
- Lindemann & Bowern: "All characters are heavily restricted in whether they can appear at the beginning, middle, or end of the word." Even in the Minimal grouping, S, Z, Q, W, X and Y are word-initial; a, E, e, i, t, k, p and f are medial; and N, M, 3, K, L and others are final. "Whatever method was used ... it created written words that are highly constrained in form." — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)
- Bowern & Lindemann, "The Linguistics of the Voynich Manuscript" (Annual Review of Linguistics 7, 2021; preprint 2020). It argues for treating the text as natural language, or as a meaningful encoding of one, and makes statistical arguments about phonology, morphology and structure. — [Yale alumni-academy PDF](https://alumniacademy.yale.edu/sites/default/files/2021-07/The%20Linguistics%20of%20the%20Voynich%20Manuscript.pdf) (could not fetch; file over 10 MB; content from search summary)
- **[2024-26]** Rozanova & Temerev (2026): "a token is not a word, a space is not a space". Knowing one token predicts the next by less than 1% of token entropy, below every matched control (2 to 10%). Glyphs at token edges share about 0.2 bits of mutual information, more than any prose control. About 70% of token types are hapax (singletons), vs 41% and 59 to 60% in the controls. Order sits "at the edges of tokens and at graded boundaries". — [arXiv 2608.17096](https://arxiv.org/abs/2608.17096)
- voynich.nu treats word structure as "a unique property of the Voynich MS text" (Stolfi's paradigm is covered on the a3_para page). — [voynich.nu analysis](https://voynich.nu/analysis.html)

### Inferences
- Several features point to tokens being sub-word units, syllables or a verbose cipher's letter-codes rather than lexical words: low-entropy rigid slots, high hapax rate, near-zero token-to-token predictability, and cross-boundary edge coupling. The same features also fit a meaningless generator.

### Gaps
- I did not retrieve primary text for Stolfi's crust-mantle-core numbers or for Emma May Smith's specific findings (her blog work on word-final and line-position glyphs). Treat both as not covered here.
- I could not extract the Annual Review paper's figures (the PDF was too large to fetch).

## 3. Currier A/B, Davis's scribes, line and paragraph position effects

### Takeaway
A/B is robust at word level and largely reducible at character level to a few affixes (-edy, qo-). Davis (2020) identifies 5 scribes by paleography, and Lindemann & Bowern show the hands cluster with A and B in h2. Line-position effects are real and survive shuffle nulls on ZL3b. Gallows glyphs favour paragraph and line starts; m and g favour line ends. Feaster (2022) gave the first systematic method for these.

### Cited Findings
- Davis, "How Many Glyphs and How Many Scribes? Digital Paleography and the Voynich Manuscript", Manuscript Studies 5(1) (2020). Five scribes (Currier had proposed 7). She classified 67 pages Currier left unassigned and differed from him in 32 cases. Scribe 1 wrote 113 of 227 pages (summary-level). Key letterforms: EVA k and in/iin. — [Penn repository](https://repository.upenn.edu/mss_sims/vol5/iss1/6)
- Critique: forum posters question the evidence base (EVA-k comparisons shown only for some scribes; Archetype uploads from the Zodiac only). — [voynich.ninja thread 3890](https://www.voynich.ninja/archive/index.php/thread-3890.html) (forum)
- Lindemann & Bowern: Hand 1 (Language A) has h2 nearly identical to A; Hands 2 and 3 (B) are close to B; Hands 4 and 5 are slightly higher (mostly labels). Labels have higher h2 than running text. — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)
- Feaster, Voynich 2022 (CEUR Vol-3313 paper 12): a systematic method for detecting uneven positional distributions of words and glyphs within lines and paragraphs. Positional patterns are more widespread than assumed, and a word's glyph makeup depends on its line position. Examples: gallows favour paragraph and line openings; [m] and [g] favour line endings. — [CEUR Vol-3313 paper12](https://ceur-ws.org/Vol-3313/paper12.pdf) (summary-level)
- **[2024-26]** A computational study on ZL3b tested line-initial token bias, paragraph-initial prefix concentration and line-final token bias against several shuffling null models; all were significant at empirical p = 0.000999 (the minimum for 1,000 permutations). Attribution unclear; possibly a preprint. — [synapsesocial record](https://www.synapsesocial.com/papers/69eefdb5fede9185760d4635) (unverified authorship)
- Historical: D'Imperio (1978) found split gallows "seem only to occur on first lines of paragraphs, and in labels". Currier noted unattached finals scattered through B much more than A. Currier's "line as a functional unit" is a named topic on voynich.nu, but no numbers are given there. — [voynich.nu a5_synt](https://www.voynich.nu/a5_synt.html)
- **[2024-26]** Stolfi's Note 084 (2025 to 2026) examines line-initial glyphs on f83r. — [Stolfi Note 084](https://www.ic.unicamp.br/~stolfi/voynich/work/Notes/084/Note-084.txt)
- **[2024-26]** Parisel, arXiv:2509.10573 (script directionality) and arXiv:2604.19762, "Evidence of layered positional and directional constraints in the Voynich manuscript: implications for cipher-like structure". Abstracts not retrieved. — cited in a search summary of [arXiv 2608.17096](https://arxiv.org/pdf/2608.17096)

### Inferences
- Line-level effects are hard to reconcile with ordinary prose, where line breaks are arbitrary. They are a key constraint that any cipher or generator must reproduce (Naibbe reportedly reproduces some, see below).

### Gaps
- I found no published effect sizes (for example, ratios of line-initial frequency to baseline) beyond qualitative statements and p-values.

## 4. Machine learning, LLM and AI decipherment attempts (2016 to 2026)

### Takeaway
Every ML or LLM "decipherment" lacks ground truth and validation on known-meaningless controls. Language-ID methods always return some language. Translation tools and LLMs produce fluent output from noise. The 2026 LLM-assisted preprints are hypotheses about the text's nature, not readings.

### Cited Findings
- Hauer & Kondrak (TACL 2016/2018, University of Alberta): a language-ID algorithm scored 97% on 380 versions of the Universal Declaration of Human Rights and picked Hebrew for the VMS, assuming alphagram anagramming and dropped vowels. They fixed spellings, then used Google Translate. — [Atlas Obscura](https://www.atlasobscura.com/articles/voynich-manuscript-artificial-intelligence-solved); [artnet](https://news.artnet.com/art-world/ai-decode-voynich-manuscript-1241105)
- Criticisms: Argamon said Google Translate produces a coherent translation even from meaningless input, which leaves "huge latitude" for impressionistic reading. Dunin: "Hebrew, and dozens of other languages have been identified before." Forum users pointed out the method was never tested on known-meaningless text. — [Mental Floss](https://www.mentalfloss.com/science/archaeology/researchers-claim-crack-voynich-manuscript-using-ai-experts-are-skeptical); [voynich.ninja thread 2262](https://www.voynich.ninja/printthread.php?tid=2262)
- Earlier topic-modelling studies (Montemurro & Zanette 2013; Sterneck, Polish & Bowern 2021) found section-linked "topical" structure. Amancio et al. 2013 (PLOS ONE) found statistics mostly compatible with natural language and incompatible with shuffled text. — [voynich.nu a5_synt](https://www.voynich.nu/a5_synt.html); [PMC3699599](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3699599/)
- **[2024-26]** "A Generative Grammar Underlying the Voynich Manuscript, the Pastiche Hypothesis: Evidence from Large Language Models" (arXiv 2609.20835, 2026). It combines string modelling with LLM-based image decoding and phonetic modelling, and argues the text is a structured pastiche of recurring symbolic units, not encoded language. — [arXiv 2609.20835](https://arxiv.org/pdf/2609.20835) (abstract via search summary only)
- **[2024-26]** Self-published LLM-era claims (Zenodo, Academia.edu, PyPI "voynich-morphemic-decryption", including a "99.8% confidence" claim) are unreviewed. A voynich.ninja member said an AI-generated paper was "hallucinating hundreds of obviously wrong claims". Keishi Oi's artificial-language paper is reportedly under Cryptologia review (2026). — [PyPI](https://pypi.org/project/voynich-morphemic-decryption/); [voynich.ninja thread 5382](https://www.voynich.ninja/printthread.php?tid=5382); [thread 5613](https://www.voynich.ninja/thread-5613.html)

### Inferences
- The recurring evaluation failures are: no held-out ground truth; no negative controls (gibberish, Naibbe-type ciphertext, shuffled text); unconstrained free parameters (anagramming, vowel dropping, choice of language); and fluent post-hoc translation. Gaskell & Bowern's gibberish result (section 7) makes the negative-control requirement unavoidable.

### Gaps
- A search summary attributed an "80% of words matched to Hebrew" figure to the Naibbe paper. This appears to conflate it with the Hauer & Kondrak claim, and I discarded it.

## 5. Transcriptions: EVA, ZL v3b, Takahashi, v101, and transcription uncertainty

### Takeaway
ZL v3b (Zandbergen, EVA-based, IVTFF 2.0) is now the standard reference: 36,278 words and 157,304 characters, with uncertain spaces and alternative readings encoded. Token counts differ by about 5% across transcriptions (about 33k to 38k). Uncertain spaces are physically and statistically distinct from real spaces.

### Cited Findings
- Counts per voynich.nu:
  - ZL v3b: 5,385 loci, 740 paragraphs, 36,278 "long words", 157,304 characters; includes alternative readings and uncertain spaces.
  - Takahashi IT (1999) v2a: 37,919 words, 155,292 characters.
  - Glen Claston v101 v2a: 38,242 words, 157,096 characters; keeps stroke-combinations as single signs.
  - FSG v2a: 33,332 words, paragraph text only.
  - Currier/D'Imperio v2a: 16,258 words (partial).
  - Reference Transliteration RF v1b, merging ZL and GC via the STA superset alphabet: 37,848 words; keynote at Voynich 2022, 30 Nov.
  - IVTFF format: v1.7 April 2020, v2.0 Feb 2023.
  — [voynich.nu transcr](https://www.voynich.nu/transcr.html)
- The comma marks an uncertain space. Currier and FSG write N and M where EVA has in and iin. Character identity and word boundaries are transcriber judgments, and OCR is proposed as a more objective route. — [voynich.nu transcr](https://www.voynich.nu/transcr.html)
- **[2024-26]** Rozanova & Temerev: blanks that transcribers marked uncertain are physically narrower on the page (AUC 0.905 from image coordinates) and behave like word-internal junctures. — [arXiv 2608.17096](https://arxiv.org/abs/2608.17096)
- Lindemann & Bowern: transcription system choice has a "negligible" effect on entropy, but glyph compositionality (Minimal vs Maximal) has an appreciable one, about 0.27 bits. — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)

### Gaps
- voynich.nu gives no release date for ZL v3b, so the "2025" in the brief is unverified.

## 6. Top unresolved statistical anomalies and what would count as a solution

### Takeaway
The anomalies most often treated as agreed are these: (1) very low h2 with normal h1; (2) rigid slot-like word structure and few distinct word types; (3) a Currier A/B split carried largely by a few affixes; (4) line- and paragraph-position effects; (5) near-zero token-to-token predictability with a high hapax rate and odd repetition (adjacent near-duplicate words). An accepted solution would need to reproduce all of these from a historically plausible method and produce verifiable, non-arbitrary plaintext.

### Cited Findings
- Low h2, positional rigidity and A/B differences are covered in sections 1 and 3. — [lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf)
- Tiltman (1967): runs of 2 to 5 near-identical groups strung together. — [voynich.nu a5_synt](https://www.voynich.nu/a5_synt.html)
- Weak token order, edge coupling and a 70% hapax rate. A Voynich-imitating cipher (Naibbe) and a self-citation generator (Timm & Schinner style) reproduce the low entropy and weak order but not the edge coupling or the vocabulary profile, which makes these a discriminating benchmark. — [arXiv 2608.17096](https://arxiv.org/abs/2608.17096) **[2024-26]**
- Bowern & Gaskell, "Enciphered after all?": word-level metrics are compatible with some encipherment types. The open question is whether a cipher can produce the word-level peculiarities. — [lingbuzz 005939](https://lingbuzz.net/lingbuzz/005939/current.pdf) (summary-level)

### Inferences
- The success criterion implied by this literature has three parts. A method should be (a) historically plausible for the 15th century; (b) able to reproduce the whole statistical profile, including A/B and line effects, not a subset; and (c) yield plaintext through a fixed, low-latitude key that others can apply blind, with text matching the illustrations. No proposal meets (c).

### Gaps
- I found no formal published "acceptance criteria" document. The criteria above are inferred.

## 7. Notable developments 2022 to 2026

### Takeaway
The field's quantitative centre has shifted from "which language?" to "which generating process?". Hoax-by-gibberish (2022), verbose homophonic cipher (Naibbe, 2025) and LLM/pastiche work (2026) are all being tested against the same statistical benchmarks.

### Cited Findings
- International Conference on the Voynich Manuscript 2022 (University of Malta; virtual, Nov to Dec 2022), proceedings in CEUR-WS Vol-3313. Papers include Zattera (slot model), Feaster (positional patterns), Gaskell & Bowern, and the RF transliteration keynote. — [CEUR Vol-3313](https://ceur-ws.org/Vol-3313/paper4.pdf); [voynich.nu transcr](https://www.voynich.nu/transcr.html)
- Gaskell & Bowern, "Gibberish after all?" (2022): 42 volunteers wrote gibberish. It is significantly non-random and, depending on sample, replicates either natural language or Voynichese on nearly all metrics tested, including Zipf. The samples were too short to test page- and quire-level structure. — [CEUR Vol-3313 paper4](https://ceur-ws.org/Vol-3313/paper4.pdf); [Gaskell GitHub](https://raw.githubusercontent.com/danielgaskell/voynich/main/README.md)
- **[2024-26]** Multispectral imaging (Sept 2024). Lisa Fagin Davis released 2014 Lazarus Project scans of 10 folios (1r, 8r, 17r, 26r, 47r, 70v1, 71r, 93r, 102v1, 116v). On f1r they reveal three marginal columns (Roman a-z, Voynich characters, and an offset Roman alphabet), attributed by handwriting to Marci (owner 1662 to 1665) as a probable early decoding attempt. Davis says they will likely not aid decipherment. — [The Art Newspaper](https://theartnewspaper.com/2024/09/25/voynich-manuscript-scans-reveal-early-decoding-attempt); [Medievalists.net](https://www.medievalists.net/2024/09/hidden-secrets-of-the-voynich-manuscript-revealed-through-cutting-edge-scans/)
- **[2024-26]** Greshko, "The Naibbe cipher: a substitution cipher that encrypts Latin and Italian as Voynich Manuscript-like ciphertext", Cryptologia (online about 26 Sep 2025; also reported as Nov 2025). It is a verbose homophonic substitution that splits plaintext into short letter groups, maps them via tables, and uses dice and playing cards for randomness. Its output matches glyph frequencies, word lengths and some positional patterns, and it is decipherable. Greshko concedes "incomplete replication of Voynich B's properties", says it "fails in several major ways", and does not claim the manuscript was made this way. — [Sci.News](https://www.sci.news/othersciences/linguistics/voynich-manuscript-cipher-14466.html); [The Debrief](https://thedebrief.org/voynich-manuscript-breakthrough-the-secret-behind-the-most-mysterious-book-in-the-world-may-involve-an-ancient-cipher-system/); [Schneier](https://www.schneier.com/?p=71287)
- **[2024-26]** arXiv 2026 wave: Rozanova & Temerev 2608.17096 (units critique, controls including the Naibbe cipher); Parisel 2509.10573 and 2604.19762 (positional and directional constraints); the pastiche-hypothesis paper 2609.20835. — [arXiv 2608.17096](https://arxiv.org/abs/2608.17096); [arXiv 2609.20835](https://arxiv.org/pdf/2609.20835)

### Inferences
- Community consensus as of Oct 2026, inferred from these sources: unsolved. The statistics rule out simple substitution of a European language, and they leave three live classes: an underspecified natural-language script, a verbose or complex cipher, and structured meaningless or pastiche generation. Recent work (Naibbe, 2608.17096) suggests none of these yet reproduces the full profile.

### Gaps
- I found no later Voynich conference after 2022 (2024 to 2026). It may exist but did not surface.
- I found no new corpus release from 2024 to 2026 beyond the Davis images. I could not confirm the date of ZL v3b.
- I did not retrieve Naibbe's quantitative tables (entropy and word-length numbers).
