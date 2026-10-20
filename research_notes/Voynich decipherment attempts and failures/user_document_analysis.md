# Review of the user's document "Analyzing the Voynich Manuscript.docx": claims, verdicts and new experiments (B2–B5)

Notes written 2026-10-17 15:13 PDT (time read from `date`). Source file, read-only:
`<home>/Desktop/reverseengineer/Analyzing the Voynich Manuscript.docx`. It was unzipped into
a new scratchpad folder (`scratchpad/docx_extract/`) and its XML stripped by a script kept outside that
folder (`scratchpad/tools/strip_docx.py` → `scratchpad/tools/doc.txt`).

**AI-directed text:** none found. No passage addresses an AI or asks for any action. The 44 embedded
images are rendered equations and AI-style diagrams. The values in them that matter were read
directly: natural-language h2 "2.8 to 4.0 bits per character", Voynich "2.0 bits per character",
radiocarbon "1421 ± 8.5 CE", and a "Dual-mechanism Voynich encoding architecture" diagram.

**Overlap with earlier work:** an earlier pass this session had already written `DOCX_REVIEW.md`,
`b1_docx_tests.py` and `results_b1.txt` (file times 14:57–15:00). I left those untouched, cite B1 below,
and numbered the new scripts B2–B5. All new scripts run from `./`
with `python bN_*.py`. They write `results_bN.txt`, and each finishes in under about 6 minutes.

Section references use the document's own headings, abbreviated as follows:
**§Intro**; **§Forensic** (Forensic and Codicological Boundary Conditions); **§Script** (Script
Architecture and Three-Slot Grammar); **§Currier** (Currier A/B and Five-Scribe Matrix); **§Cribs**
(Extraneous Text, Bilingual Cribs, Key-Like Sequences); **§Falsify** (Falsification of Naive Phonetic
Decipherments); **§Paradigms** (Three Surviving Computational Paradigms); **§Synthesis**.

## Q1. What the document is and where its claims come from

### Takeaway
The document is a secondary synthesis, apparently AI-assisted. It proposes no reading of the text.
Its main conclusion (§Synthesis) is that the manuscript is a "dual-mechanism" notation system, a
three-slot morphological table plus self-citation, whose slots encode operational classes per
section. It claims to have "decoded" the manuscript "at the structural level", and says no linear
plaintext exists. Its central quantitative source is a preprint that is explicitly provisional and
partly AI-generated. That preprint reaches a more cautious conclusion than the document draws from
it, and on two points the opposite one.

### Cited Findings
- The document's source [2], "How the Voynich Manuscript was written" (bootloops.ai/voynich.pdf), is
  by Matthew D. Schwartz (Harvard Physics) and dated 1 October 2026. Its first page says: "This work
  is preliminary. Some content remains AI-generated and is still being validated." It is not
  peer-reviewed. It concludes that readings in 18 languages fail held-out tests, that a keyless
  reuse/copy/coinage procedure reproduces most summary statistics, and that only "two weak traces of
  content remain: distinctive label words and a faint dependence of word choice on subject". It
  suggests "a book made to be looked at, not read". — [Schwartz 2026 preprint](https://bootloops.ai/voynich.pdf)
- The same preprint states: "Tests for section-specific grammar and for dependence of dialect on
  content are negative". It reports the subject effect as "roughly 0.2 to 0.3 bits per page". That
  effect comes from the astronomical and balneological sections; the herbal section "shows no tint of
  its own". — [Schwartz 2026](https://bootloops.ai/voynich.pdf). **This contradicts the document's
  §Synthesis claim** that slot-1 prefixes encode section-specific operational classes ("qo- marks
  active procedural states, ot-/ok- astronomical degrees, ol- pharmaceutical substances") and that
  morphology "maps deterministically" to subject matter.
- The document's specific numbers trace to Schwartz: the 227 text pages; Bayes factor > 100; Scribe 1
  pure A; Scribes 2, 3 and 5 B; Scribe 4 split; the mixture preferred on "77%" of a Latin control's
  pages; and slot inventories of 181/498/160 for Scribe 1 and 175/429/109 for Scribe 2. The figures
  are quoted correctly. — [Schwartz 2026](https://bootloops.ai/voynich.pdf)
- The "four statistically independent structural layers (R², non-shared variance)" and the
  "table reference + probabilistic selection" synthesis come from the document's source [12], a
  ResearchGate paper ("Structural Analysis of the Voynich Manuscript – Elucidating a Knowledge System
  through Statistical Methods"). The page returned HTTP 403, so its authors, review status and
  methods are **unverified**. — [ResearchGate 402516478](https://www.researchgate.net/publication/402516478_Structural_Analysis_of_the_Voynich_Manuscript_-Elucidating_a_Knowledge_System_through_Statistical_Methods)
- The other sources mix primary literature (Bowern & Lindemann; Timm & Schinner arXiv 1407.6639;
  Rozanova & Temerev arXiv 2608.17096) with Wikipedia, blogs, forums, Reddit, YouTube, a Scribd upload
  and a 2026 tutoring-company blog (eduKate Singapore, cited for the f57v/f49v "key-like sequences").
  — document works-cited list, items 1–65

### Inferences
- The document reads as a confident, AI-written digest of the Schwartz preprint and blog literature.
  Where it goes beyond Schwartz (§Synthesis slot semantics, "decoded at the structural level"), it
  cites either the unverifiable ResearchGate paper or nothing.

### Gaps
- Source [12] could not be read (403), so the "four-layer" R² claims stay unverified.

## Q2. Forensic, codicological and provenance claims (§Forensic, §Intro)

### Takeaway
The broad claims are already known and correct: parchment from 1404–1438, iron-gall ink, an
Alpine/N-Italian/S-German milieu, the Prague ownership chain, and singulions. Several details
overreach. The claim that the inks were "proven contemporaneous" is disputed. Origin is "pinpointed"
from merlons that critics call non-diagnostic. The "error-doubled" radiocarbon recalculation is an
amateur blog analysis.

### Cited Findings
- Radiocarbon dating of 4 samples to 1404–1438 at 95% confidence (Hodgins, University of Arizona,
  2009) is **already known**. — [voynich.nu carbon page](https://www.voynich.nu/extra/carbon.html) (via
  local note physical_provenance.md Q1)
- The document's refinement (1421 ± 8.5 CE; error "doubled" to give 1406–1434 or 1394–1443) is cited
  to Edith Sherwood's personal website (doc [14]). It is not peer-reviewed. **Unverified**: not checked.
- McCrone (2009) found iron-gall ink, azurite, a copper green and gum. Yale conservators say the inks
  look "from the same period". Wikipedia calls the claim that the ink was proven to be added soon after
  the parchment was made "erroneous". The document's "proving contemporaneous early-15th-century
  inscription" is therefore **overstated**. — [Omeka/McCrone record](https://omeka.ischool.utoronto.ca/items/show/463); [Wikipedia](https://en.wikipedia.org/wiki/Voynich_manuscript)
- The swallowtail merlons are "a single detail on a single page". Such merlons also occur in Sicily,
  Russia, the Kremlin, and German, Swiss and Austrian lands. The document's word "pinpoints" is
  **overstated**; "mildly supported" is the fair reading. — [Cipher Mysteries](https://ciphermysteries.com/category/places-of-interest/milan/page/2); local note physical_provenance.md Q7
- Layfield & Davis (2026) propose an original singulion structure; the document repeats this
  correctly. **Already known.** — local note physical_provenance.md
- The f1r columns are attributed by Davis (2024) to Marci (1662–65), an early decoding attempt. The
  document says much the same ("analytical indexing by Marci"). **Already known.** — local note physical_provenance.md Q5

### Inferences
- None of these claims bears on decipherment beyond setting the date and place, which the literature
  had already established.

### Gaps
- Sherwood's recalculation and Hodgins's formal figures were not checked.

## Q3. Script, slot-grammar and entropy claims (§Script) — tested in B2 and B3

### Takeaway
Most of the slot-grammar facts hold on our data and are already known (Tiltman, Stolfi, Lindemann &
Bowern). One gallows rule is a genuine effect beyond the bigram statistics. Two of the document's
supporting arguments fail. Its "word-shuffle leaves h2 intact, proving word-internal origin" argument
is a mathematical tautology. Its "two-state HMM splits final versus non-final glyphs" claim did not
reproduce: the HMM finds a vowel-like class {o, a, e (y)}, as Sukhotin and Schwartz do.

### Cited Findings
- **h2 values.** The document gives "2.0 bits" for Voynich against "2.8–4.0" for "250 languages".
  The published figures are about 2.16 (EVA Maximal) against 2.85–6.25 across 294 Wikipedia
  languages. Our a1 gives 2.13, and B3 gives 2.126 with spaces as a symbol, against 3.11–3.30 for the
  controls. The direction is right; the document's figures are slightly off. —
  [Lindemann & Bowern, lingbuzz 005522](https://lingbuzz.net/lingbuzz/005522/v1.pdf) (via computational_recent.md); `results_a1.txt`, `results_b3.txt`
- **Size figures.** "~35,000 words / ~170,000 glyphs": our paragraph text has 34,857 tokens and
  173,928 EVA characters (140,577 units after collapsing glyphs). **Supported.**
- **q→o binding (C1).** P(o|q) = 0.977, and 99.3% of q are word-initial. A bigram pseudo-text
  reproduces this exactly, so it is a first-order fact. **Supported; already known** (Currier,
  Tiltman). — `results_b3.txt`
- **Prefix classes and gallows (C2).** P(gallows | qo-) = 0.841 and P(gallows | o-) = 0.565, against
  0.331 after a word-internal o. The bigram null gives 0.403 / 0.417, with no qo- vs o- difference.
  P(gallows | y-) = 0.748. For ch-/sh-/d- it is 0.041 / 0.018 / 0.007. **Supported, and it is a
  genuine second-order (slot-level) dependency, not a bigram artefact.** — `results_b3.txt`
- **Word-final glyphs (C3).** n is word-final 0.99 of the time, m 0.97, y 0.87, r 0.82. No control
  letter reaches 0.9; the maximum is Latin m at 0.51. g and v were too rare to test (fewer than 200
  tokens). **Supported; already known** (Lindemann & Bowern: 93% of words end in y, n, l, r, m or s).
  — `results_b3.txt`
- **Word-shuffle invariance of h2 (C4).** The claim is true but carries no information. With the space
  counted as one symbol, a word shuffle changes h2 by exactly 0.000 in Voynich, in the null and in all
  six controls. Every bigram across a boundary is (last letter, space) or (space, first letter), and a
  shuffle preserves both counts. The document's "crucially … proving" (§Script, last paragraph) is
  therefore **invalid as evidence**. The informative contrast is a shuffle of letters within words:
  h2 rises by +1.48 bits for Voynich, against +0.59 to +0.77 for the controls. That is a new way to
  express that Voynich's predictability lives inside the word. — `results_b3.txt`
- **Two-state HMM (B2).** The document says it splits Voynich into word-final (m n g v y) vs other.
  We trained Baum-Welch on 42k characters with 20 restarts. In EVA with spaces, the best split is
  {o y c a s n g …} vs {h e d i k l r t q p m f …}. m sits with the gallows, and the AUC for
  word-final rate is only 0.67. Collapsing glyphs gives {o e a h} vs the rest. Without spaces the
  split is {o y a n g u} vs the rest (AUC 0.79). The controls split cleanly into vowels and consonants
  (vowel accuracy 0.88–1.00, except Alice with spaces at 0.56). **Not reproduced.** The HMM finds a
  vowel-like {o, a, e, y} class mixed with some finals, not a clean word-final class. Restart stability
  is low: 6–11 of 20 restarts give the same partition. The controls are also unstable (5–15 of 20), so
  instability is not Voynich-specific. This fits Zandbergen's report that the Reddy & Knight HMM
  result depends on initial conditions. — `results_b2.txt`; [voynich.nu a2_char](https://voynich.nu/a2_char.html)
- **Sukhotin (B2).** With spaces kept, the vowels are o h a y n g b u, at 0.729 alternation within
  words. With spaces removed, they are o y a c e s n, at 0.816. The document says a e o y at 74%, and
  a g c n o y without spaces. The instability between the two settings is **reproduced in kind**,
  though the sets differ. The Latin, Augustine and German controls give identical sets either way.
  The document's description of 74% as a "low" alternation rate is **contradicted**: the controls
  range from 0.70 to 0.82, and the shuffled null sits at 0.50. Voynich's alternation is in the
  natural-language range. Schwartz likewise finds that Sukhotin separates {a, e, o, y} strongly (38–63
  SD, against 68 for Latin), but the class found differs between the two halves of the manuscript. —
  `results_b2.txt`; [Schwartz 2026](https://bootloops.ai/voynich.pdf)
- **Single-edit neighbourhoods (C5).** 97.2% of the 2,000 commonest Voynich types have a vocabulary
  neighbour one edit away. The bigram null gives 84.1% and the controls 53–84% (Dante 83.8%).
  **Supported:** this is the basis of the document's argument against Bax's cribs. — `results_b3.txt`
- **Glyph registers (Cappelli abbreviations, numerals 2/4/8/9).** These are paleographic resemblance
  claims from blogs (doc [5], Cipher Mysteries). They are **known proposals, not tested** here.
- **Slot inventory counts.** These are quoted from Schwartz and are **unverified**: they depend on his
  segmentation, which was not replicated.

### Inferences
- The slot structure is real and partly higher-order (qo- → gallows). It constrains any theory, but
  it does not tell meaning apart from generation, because a generator with slot rules reproduces it
  by design.

### Gaps
- Reddy & Knight's exact HMM setup (alphabet, spaces, initialisation) was not checked against
  ours. The B2 negative holds only for our setup.

## Q4. Currier A/B, scribes and section structure (§Currier) — tested in B1 and B5

### Takeaway
The section signatures quoted in the document (-edy, qo-, the o/e drift) were verified by B1. The
claim that NMF clusters track hand × subject replicates strongly in B5. Section separates within a
single scribe, and a meaning-free self-citation generator does not reproduce this. Against a strict
"contiguous fake-section" null, however, the within-scribe margin is small. That fits Schwartz's
"faint subject tint" better than the document's "deterministic mapping".

### Cited Findings
- Sterneck, Polish & Bowern (2021) found that LDA/LSA/NMF clusters "match closely to a conjunction of
  scribe and subject matter". **Already known.** — [Yale PDF](https://alumniacademy.yale.edu/sites/default/files/2021-07/Topic%20Modeling%20in%20the%20Voynich%20Manuscript.pdf) (via hoax_vs_meaning.md)
- B1 measured the -edy rate at 0.52% in Pharma and 25.98% in Biological. -edy is 0.00% in 6 of 9
  Herbal-A quires. qo- is 0.29% in Zodiac labels, and qok- reaches 16.25% in Biological. **Verified.**
  — `results_b1.txt`
- **B5 replication.** NMF (TF-IDF, K = 8, 871 chunks of 40 words, page boundaries ignored) gives NMI
  with section 0.379, with hand 0.375 and with Currier language 0.346. A page-block permutation null
  gives 0.055 / 0.043 / 0.021. A token-shuffled corpus gives 0.014. — `results_b5.txt`
- **Within one scribe.** Hand 1, Herbal-A vs Pharma: NMI 0.275 (page-permutation null 99th percentile
  0.040). Hand 2, Bio vs Herbal-B vs Astro: 0.333 (null 99th percentile 0.104). Under the stricter
  rotation null, the page-label sequence is rotated so fake sections stay contiguous. Hand 1 gives
  p < 1/n, but the largest rotated value (0.271) almost equals the observed one. Hand 2 gives
  p = 0.048. — `results_b5.txt`
- **Meaning-free generator (B4) through the same pipeline.** Self-citation seeded with each page's
  real first line gives section NMI 0.098–0.129, near its own nulls. Within hand 1 it gives 0.002–0.028,
  not significant. Within hand 2 it gives 0.10–0.11, not significant (rotation p 0.29 and 0.76). **So
  page-local copying plus a seed line does not reproduce Voynich's section structure.** —
  `results_b5.txt`
- **Natural-language controls, same pipeline.** Dante's canticles: NMI 0.017, rotation p 0.022.
  Augustine's books: NMI 0.155, rotation p 0.575. Caveat: the "book 13" label also absorbs trailing
  matter in that file. Voynich's section NMI is far larger than either control's label NMI. That
  matches its well-known section- and hand-specific vocabulary, which is larger than authorial topic
  drift. — `results_b5.txt`
- Schwartz's conditioned test found subject dependence beyond hand and page order, but only "roughly
  0.2 to 0.3 bits per page". Under quire-aligned nulls it fell to the margin, and the herbal section
  showed none. — [Schwartz 2026](https://bootloops.ai/voynich.pdf)
- "Bowern & Gaskell 2022" is listed in §Paradigms as verbose-cipher work. Gaskell & Bowern 2022 is
  the human-gibberish experiment. This is a **misattribution**. — local note hoax_vs_meaning.md

### Inferences
- The section signal is too strong for a simple page-local copier and survives within a single
  scribe. To produce it, a meaningless generator would need settings or seed vocabulary that change
  by section, which is cheap to add. NMF alignment therefore shows that word choice depends on
  section. It does not show that the words carry meaning, and it does not support the document's
  per-slot semantics. Our hand-1 result rests on Herbal-A vs Pharma, which also differ in quire and
  in when they were written. The near-tie with the largest rotated null means writing-order drift
  cannot be excluded.

### Gaps
- No quire-aligned null was run, although Schwartz found it the harshest. Hand 3 (Stars vs Herbal-B)
  is too unbalanced to test.

## Q5. Marginalia, cribs and key-like sequences (§Cribs)

### Takeaway
Most of the items are known blog and forum observations, restated as "decisive breakthroughs". The
f116v–Cod. Sang. 754 link is presented in its own source as resemblances, not matches. The f116v
readings themselves were changed by the 2024 multispectral imaging. None of these items supplies a
crib for the main text.

### Cited Findings
- Brian Cham (23 Dec 2014) credits the discovery to "Job" and explicitly offers "resemblances" rather
  than matches. Zandbergen and J.K. Petersen disagree on details, and Winkler reads "gas" as "gans".
  The document's claim that both manuscripts share "the exact same anomalous diacritic" goes beyond
  the source. — [Cham 2014](https://briancham1994.com/2014/12/23/cod-sang-754-and-the-voynich-manuscript/)
- Davis's 2024 multispectral imaging finds the f116v lines "similar to Voynichese but not identical",
  with Germanic features. Some letters long read as "p" may be [u] or [v]. She offers no
  interpretation. "michiton oladabas" remains an uncertain transcription. — [Davis 2024](https://manuscriptroadtrip.wordpress.com/2024/09/08/multispectral-imaging-and-the-voynich-manuscript/) (via physical_provenance.md)
- The zodiac month names are a probable later Romance (Occitan or northern French) addition by an
  early reader, not the author. The document's "Catalan/Occitan/Alpine Romance" is in line with this.
  **Already known.** — local note physical_provenance.md Q5
- The under-paint "rot", the "g" on f1v and f9v, the "fo" on f2v and the Voynichese under paint on f2r
  are blog-level observations (doc [13], [205]–[208]). They are **unverified** here: checking them
  needs a facsimile.
- B1 found that the f57v ring repeats, with a 16-character block "trycoldrvxkmptry". The best period
  in EVA characters is 13, so "17 × 4" is **unverified** in EVA terms. ZL transcribes only "oror
  sheey" on f116v, so the charm cannot be tested from the transcription. — `results_b1.txt`
- Bax's oror on f15v: ZL reads line 1 as "poror.orshy…" and line 2 as "chor.or.oro.r". The
  document's description of reduplicative context is **broadly confirmed**. daiin occurs 816 times and
  dain 211 times, and 1,723 tokens end in -dain or -daiin. That supports the document's objection to
  reading kydain as "Kantaron". — ZL3b via `corpora.py` (checked this session)

### Inferences
- The marginalia anchor early users in German- and Romance-speaking circles, but they are later or
  peripheral layers. The document's step from "rot under paint" to "the encoding language is German"
  is a non sequitur. A German-speaking colourist does not fix the language of the text.

### Gaps
- No facsimile inspection was done of f2r, f4r, f7r, f49v or f57v.

## Q6. Falsified decipherments and the "three surviving paradigms" (§Falsify, §Paradigms) — tested in B4

### Takeaway
The Bax and Cheshire rebuttals are standard and correct, and are **already known**. The claim that
self-citation needs hard-coded line rules is **supported by B4**. A Timm-style copier with no position
rule produces no line-edge effect. Seeding each page with its real first line spreads almost none of
that line's p-bias to later lines. The document then counts this as evidence against the generative
view, yet its own §Synthesis keeps self-citation and simply adds the line rules.

### Cited Findings
- Cheshire 2019: the University of Bristol backtracked on its publicity. Davis and linguists rejected
  "proto-Romance". **Already known.** — [Guardian 2019](https://www.theguardian.com/science/2019/may/17/university-backtracks-on-disputed-voynich-manuscript-theory); local note language_claims.md
- Bax 2014's proper-name readings are not accepted. **Already known.** — local note language_claims.md
- **B4, lines 2+ of each page.** Real Voynich has first-glyph JSD 0.172 (null 0.002). Line-initial p
  is enriched ×16.0 and line-final m ×16.6.
  - The self-citation simulation has the same page and line layout, copies from the same column with
    p = 0.28, and mutates to real vocabulary neighbours with p = 0.7. It gives JSD 0.0006–0.0010,
    equal to its null, with p ×1.0–1.2 and m ×0.9–1.0.
  - Seeded with real first lines, it gives JSD 0.004–0.005 and p ×1.5–1.8.
  - The calibrated variant, with weaker copying and more mutation, gives p ×0.9–1.2.
  - Dante verse has a large last-glyph JSD (0.167) from rhyme, but no p or m effect.

  **No line-edge effect emerges without an explicit rule.** — `results_b4.txt`
- Schwartz's generator is likewise rejected on Scribe 2's pages when its "line-position and length
  terms" are removed. No keyless generator reproduces the coupling of edge glyphs across word breaks
  (0.009 / 0.001 bits generated, against 0.130 / 0.243 real). — [Schwartz 2026](https://bootloops.ai/voynich.pdf); [Rozanova & Temerev 2026](https://arxiv.org/abs/2608.17096) (via computational_recent.md)
- Our simulator overshoots the copy statistics: an immediate repeat rate of 2.2–5.9% against 0.87% in
  Voynich, and same-column edit-distance-1 copies at 10–19% against 4.4%. The pages it produces are
  therefore more copy-heavy than Voynich, which if anything should help line effects propagate. —
  `results_b4.txt`
- "A 2026 Bayesian cross-validation study" in which every verbose-cipher reading fails on held-out
  pages is Schwartz's result. It agrees with our a6 negative, though a6 used a different solver family.
  It is **not independently verified**. — [Schwartz 2026](https://bootloops.ai/voynich.pdf); `README.md` §6
- Greshko's Naibbe cipher (Cryptologia 2025) shows a verbose cipher is feasible, but it "fails in
  several major ways" by its author's own account. The document lists "Greshko 2025" under paradigm 1
  without that caveat. — local note cryptanalysis_history.md

### Inferences
- Line-edge effects are evidence of a layout-aware writing procedure, whether a cipher with line rules
  or a generator with line rules. They are not evidence of meaning, which is how the document uses
  them in §Paradigms.

### Gaps
- The real Timm & Schinner Glyph.java was not run. B4 is a reimplementation in the same spirit, not
  their code.

## Q7. Does the document get further than the state of the art or our own experiments?

### Takeaway
**No.** It reads no text, and its §Synthesis is an interpretation that its own main source partly
contradicts. Its testable sub-claims mostly hold, are mostly already published, and add nothing beyond
our earlier experiments a1–a7. Two of its supporting arguments are invalid: the word-shuffle "proof"
and the HMM final/non-final split. The new experiments B2–B5 sharpen three points, none of which
advances decipherment:
1. The slot rule qo- → gallows is a genuine higher-order dependency.
2. Section-specific vocabulary survives within a single scribe, though only narrowly against
   contiguous nulls, and a page-local self-citation copier does not reproduce it.
3. Line-edge effects require explicit line rules in any generative model.

### Cited Findings
- As of October 2026 the manuscript is undeciphered. Three model classes remain live (an
  underspecified natural-language script, a verbose or complex cipher, structured meaningless
  generation), and none reproduces the full statistical profile. — local note computational_recent.md (synthesis of [arXiv 2608.17096](https://arxiv.org/abs/2608.17096) and Greshko 2025)
- The document's claim that it "decoded the manuscript at the structural level" rests on its own
  slot-to-meaning assignments (prefix = operational class, core = attribute, suffix = state).
  Nothing in it tests these. Schwartz reports that "tests for section-specific grammar … are
  negative". — [Schwartz 2026](https://bootloops.ai/voynich.pdf)

### Inferences
- **What holds:** the date and milieu, the slot positional rules, the low h2, the Currier/scribe
  structure, the section signatures (B1), the NMF clustering (B5), the rejection of Bax and Cheshire,
  and the need for explicit line rules (B4).
- **What fails:** that word-shuffle invariance proves anything (B3 C4); the HMM final/non-final split
  (B2); 74% Sukhotin alternation described as "low" (B2); morphology mapping "deterministically" to
  subject (B5's margin under contiguous nulls; Schwartz); the "decisive breakthroughs" from the
  marginalia; inks "proven" contemporaneous; merlons "pinpointing" the origin.
- **What is new here, from our runs:** the exact-zero shuffle tautology; prefix → gallows measured
  against a bigram null; a within-scribe NMF test with a meaning-free generator passed through the
  same pipeline; and B4's quantification that seeded self-citation does not spread line-edge bias.
- **Next tests that could change the picture:** a quire-aligned null for B5; a generator whose seed
  vocabulary changes by section, to see whether it matches the 0.27–0.33 within-hand NMI; edge-glyph
  coupling (Rozanova & Temerev) as a target for B4-style generators; and a glyph-level retest of
  f57v.

### Gaps
- The HMM and Sukhotin results depend on the alphabet chosen (EVA or collapsed glyphs). v101 and
  Currier alphabets were not tested. The B5 numbers depend on K = 8 and 40-word chunks. A K sweep was
  not run, so their sensitivity is **unverified**.
