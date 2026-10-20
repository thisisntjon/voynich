# X-01 published-first check: split-free cousins of the 9 slot-dependent findings

Written 2026-10-19 11:18 PDT (clock read with `date`). Read-only literature check: no runs, no web access.
Scope: F-11, F-12, F-13, F-14, F-15, F-30, F-34, F-39, F-40 (all `rests_on: X-01`; c-592 says no tested
segmenter recovers planted books). Question per finding: is the effect, or a close cousin, already published with a
statistic that needs no prefix/core/suffix split? Paths are relative to `data/external/` unless stated.

## Sources opened, and what could not be opened

Opened and read in part: Rozanova & Temerev 2026 (`papers/rozanova_temerev_2026_arxiv_2608.17096.txt`, "R&T");
Parisel 2026 (`papers/parisel_2026_arxiv_2604.19762.txt`); Timm 2014 (`timm-schinner-generator/arxiv_1407.6639.txt`);
Timm 2016 (`library/corpus/papers/VL00131.txt`); Dominik 2026 (`library/corpus/papers/VL00735.txt`); Stellar 2026
(`library/corpus/papers/VL01153.txt`); Gaskell & Bowern 2022 (`gaskell-bowern-gibberish/gaskell_bowern_2022_gibberish.txt`,
"G&B"); Lindemann & Bowern 2021 (`bowern-lindemann-entropy/lindemann_bowern_2021_yale.txt`, character entropy only);
Zattera 2022 (`papers/zattera_2022_ceur3313_paper10.txt`); Stolfi grammar page
(`library/web/voynich_nu/text/www.voynich.nu/hist/stolfi/grammar.html.txt`); Zandbergen syntax page
(`library/web/voynich_nu/text/www.voynich.nu/a5_synt.html.txt`); Morgallet 2026 Naibbe audit methods notice
(`library/corpus/papers/VL00665.txt`); `workflow/CONSTRAINTS-MAP.md` B2 (lines 84-100); `page-facts/*/facts.tsv`
(no sequence statistics; nothing relevant); `library/unchecked_claims.tsv`, `BIRDS-EYE.md` (nothing new).

Unverified (not local or not opened): Currier 1976; Reddy & Knight 2011 (8.85 % next-word gain, quoted only via
CONSTRAINTS-MAP:98-100); Smith & Ponzi 2019 (VL00203); Timm & Schinner 2019/2020 papers (only their code is local);
Rugg 2004, Rugg & Taylor 2016; Greshko 2025 Naibbe paper (`lit-20261018/greshko-tandf-pdf/greshko.pdf` is a Cloudflare
page, see NOTE there); Schinner 2007. **Catalogue defect:** `library/corpus/papers/VL00070.txt` is labelled Schinner 2007
but its text is Amancio et al. 2013 (lines 1-8); Schinner 2007 is known here only through Timm 2014:515-520.
The team register `lab/workflow/research/published-findings-register.md` was not opened.
Of the 560 corpus texts, most 2026 Zenodo items are unrefereed; only VL00131, VL00735, VL01153, VL00665 were used.

## F-11 Slot frame; line rhythm and next-word dependency live in the affixes

1. Split-free cousins. (a) Next-word dependency at word edges: R&T 409-424: shuffle-corrected MI between the last
   glyph of token t and the first glyph of t+1 is 0.197 bits (5.7 % of next-first-glyph entropy), above every prose
   control (0.018-0.120); "in Voynichese it is concentrated in the boundary glyph pair (ratio 2.9)" and "knowing the
   whole preceding token predicts the next first glyph no better than its last glyph does". Table 4 (436-446): token to
   token 0.067 bits (0.81 %). Parisel 9-16, 370-376: cross-boundary MI 0.230 bits vs 0.054-0.173 in four languages,
   97 % in specific grapheme transitions. Currier 1976 and Smith & Ponzi 2019 are the original reports (unverified).
   This is the split-free form of "the next word's prefix takes most positive word-to-word dependency".
   (b) Word-length rhythm: G&B 201, 230-235: positive word-length autocorrelation in the VMS (long-long-short-short),
   but over one flattened vector, not within lines; CONSTRAINTS-MAP 91-93 already notes the within-line form is
   not found. No published split-free decomposition of the rhythm into word edges.
2. Contradiction: none found.
3. Primary: within-line shuffle-corrected MI(last glyph_t; first glyph_t+1) vs MI(word_t; word_t+1) (published, R&T
   Table 4). Backup for the rhythm half: within-line Moran I of word length, and the share kept by a within-line
   shuffle that preserves the sequence of fixed-width word edges (first glyph, last glyph). No published number.
   Run needed: partial (dependency half has an external line; rhythm half does not).

## F-12 Cores carry weak order, below language and mostly below letter-in-core ciphers

1. Cousins (whole tokens, no split): R&T Table 4 (436-446): token-to-token 0.81 % of capped token entropy vs 2.03-9.71 %
   for prose; 410-430: the deficit is "robust" in ordering but its size depends on the vocabulary cap (0.8x the lowest
   control at a 250-type cap, noise floor at 4,000). R&T 696-698: Naibbe cipher of Latin 1.25 % / 1.06 % vs Voynich
   0.79 %. Stellar VL01153:23-26: excess token MI dI(1) = 0.243 bits, "a factor 5.4 below Latin", lag >= 2 at the 0.011
   floor. Zandbergen a5_synt 75-86: lack of repeated phrases of 2+ words. Dominik VL00735:52-56: "categorical CORE
   identity contributed no detectable advantage once its spelling was included". Reddy & Knight 8.85 % (unverified).
2. Contradiction (partial, sign): R&T Table 4 (442) gives Currier A token-to-token -0.043 bits, and Table 12
   (appendix, about line 1195) A -0.53 % vs B +0.41 %. F-12 claims positive order; at whole-word level the sign in A is
   not positive at a 2,000 cap. Same cap-dependence our c-420 records; not a refutation of the matched-K statement.
3. Primary: held-out, within-line shuffle-corrected whole-word adjacent MI at matched vocabulary cap K (top-K types,
   rest pooled), vs matched languages and letter ciphers. Backup: R&T's edge-free "token identity" share. Published:
   yes for languages (R&T, Stellar) and one cipher (Naibbe). Run needed: partial (A/B sign at matched K, and the
   cipher bracket beyond Naibbe).

## F-13 The same core recurs at short range, opposite to language

1. Cousins: Timm 2016 VL00131:336-356 (Table 2, whole words): chance that two consecutive words are identical
   {n,m-1} = 0.95 %, same position in the previous line 0.99 %, "increased chance that a word is identical to one of
   the previous words in the same line"; 731-735: unchanged when line-initial and line-final words are removed;
   746-748: Quran consecutive identical 0.01 %, "natural languages usually avoid using the same word twice in a row".
   Timm 2014:456-459, 497-510: repeated words peak within three consecutive lines; Latin lower; the decay is VMS-only.
   R&T 422-424 and Table 4: adjacent tokens within one edit 1.12x shuffle (A 1.20, B 1.07) vs prose 0.47-0.56.
   Zandbergen a5_synt 71-72 (D'Imperio 1978): same word repeated two or three times; near-identical words in vicinity.
   G&B 171, 226: repeated_words higher in VMS and gibberish than in meaningful text. Internal: c-382 already has
   whole words R(2) 1.41.
2. Contradiction: none. Caution: R&T's catalogue control (Species Plantarum) amplifies near-identical neighbours 2.57x.
3. Primary: whole-word R(d) = identical-token rate at distance d over a within-line shuffle, d = 1..20, with a
   rare-type stratum. Backup: R&T edit-1 adjacency ratio. Published: no exact-identity-vs-shuffle ratio (R&T's
   edit-1 ratio may include identical pairs: unverified); Timm gives raw rates without a shuffle. Run needed: partial
   (cheap confirmation; the external lines exist).

## F-14 Prefix stream: one-word memory, resets at line breaks

1. Cousins: Dominik VL00735:20-26: classes "defined from word-initial characters and length rather than interpreted
   morphemes"; predecessor class improves held-out next-class prediction by 0.0415 / 0.0644 / 0.0413 nats per token
   (folio-grouped, bootstrap > 0); 160-174: predecessor gain +0.1458 inside a line, +0.1074 at artificial midpoints,
   -0.0273 at recorded cross-line boundaries, labelled exploratory: "line-boundary reset remains a hypothesis".
   R&T Table 5 (455-464): edge internality at continuation line breaks -0.036 [-0.072, -0.002] vs mid-line 0.064
   (already logged, CONSTRAINTS-MAP 94-96). Stolfi grammar 1379: "strong correlation between certain features of
   consecutive Voynichese words" (vowel-harmony analogy; not quantified on the page).
2. Contradiction: none published. (Internal roach r6, c-442: affixes do not reset; not literature.)
3. Primary: held-out gain of the first-glyph (or first-two-glyph) class of word t given that of word t-1, inside lines
   vs across line breaks, with a lag-2 decay check (Dominik's statistic, fixed-width). Backup: R&T edge MI split by
   boundary type. Published: yes for the in-line gain; the reset is published only as exploratory. Run needed:
   partial (pre-registered reset and lag profile).

## F-15 Prefix and suffix are chosen together with the core

1. Cousins (qualitative only): Stolfi grammar 230-292: frequencies mismatch the grammar "largely due to dependencies
   between the various choices"; daiin 866, qokeedy 305, qokaiin 266 vs deedy 3. Timm 2014:278-300: frequency of a
   word predictable from similarly spelled words. Zattera 134-145: some slot combinations rare (double pedestal 17
   tokens). No split-free quantitative number found.
2. Contradiction: none. Dominik VL00735:54-56 (preceding word identity does not predict following-word endings) is
   between words, not within.
3. Primary: within-word MI between word-initial and word-final glyph bigrams, stratified by word length, against a
   length-preserving recombination null. Backup: observed word-type count vs the count from that recombination.
   Published: no. Run needed: yes.

## F-30 Weakened table-and-grille and constrained assembly do not predict held-out quires

1. Cousin: Parisel 22-28, 502-542: a Cardan grille implementing Rugg 2004, 15 configurations plus five sweeps, never
   meets a four-signature joint criterion (end-to-start class transition rate, cross-boundary MI, boundary Zipf
   shape); in honest form the net sequential signal is about 0.002 bits vs 0.181 (A) and 0.165 (B). A parametric
   slot generator also fails (different failure mode). All four signatures are split-free.
2. Contradiction: Rugg 2004 / Rugg & Taylor 2016 claim a grille reproduces VMS features (unverified, not local).
   Internally F-30's LOQO exclusion is already uninformative (s101 c-454, roach r13 c-542).
3. Primary: Parisel's joint criterion (cross-boundary MI plus end-to-start rate) on a weakened grille. Published: yes
   for Rugg's grille. Run needed: no (cite Parisel; our own exclusion has no power).

## F-34 Line-held affix table reproduces prefix memory; sticky Naibbe predicts no quire

1. Cousins: R&T 696-698 and abstract 24-28: Naibbe ciphers of Latin reproduce low entropy (h2 2.71) and weak token order
   (1.25 % / 1.06 %) but not edge coupling (0.006 vs 0.197 bits), not near-neighbour excess (edit-1 0.82 vs 1.12), not
   the hapax share (41 % vs 70 %). Morgallet VL00665 is a methods notice; its results are in a paper not local
   (unverified). No published line-sticky Naibbe.
2. Contradiction: none.
3. Primary: R&T's edge-glyph MI and edit-1 ratio on line-sticky Naibbe output (for "predicts none"). Backup: the F-14
   primary (first-glyph class gain and line reset) on the same output (for "reproduces prefix memory"). Published:
   yes for default Naibbe, no for the line-sticky variant. Run needed: partial.

## F-39 Homophone cores: too little same-core repetition; excess order depends on stripping

1. Cousins: R&T 696-701: Naibbe (letter-level homophonic) has more token order (1.25 %) and fewer near-identical
   neighbours (0.82) than Voynich (0.79 %, 1.12): both halves of F-39 at whole-token level for one cipher. Synthetic
   homophonic ciphers: calibrated-attack differential +0.13 to +0.52 vs Voynich -0.15 to +0.08; boundary crossing
   3.8-12.4 % vs 2.5 %. Stellar 16-20: h2 2.17 vs 3.02-3.52 references.
2. Contradiction: none. R&T 428-432 note the order deficit shrinks or vanishes with the vocabulary cap, the
   same fragility F-39's "order half" shows under other segmenters.
3. Primary: whole-word identical-adjacent ratio within lines (as F-13) on syllable/chunk homophone ciphers with a line
   table. Backup: whole-word MI at matched cap. Published: yes for letter-level Naibbe; no for syllable/chunk
   homophones or a per-line table. Run needed: partial.

## F-40 No natural or constructed text reuses words in-line; no generator has the weak order

1. Cousins: Timm 2016 VL00131:336-356 vs 721-723 and 746-756: VMS consecutive identical 0.95 %; Quran row n gives
   0.61, 0.68, 0.66, 0.62, 0.26, 0.01 % at m-6..m-1 (avoids d = 1-2, elevated at d >= 3 vs 0.2-0.5 % in other lines);
   English and Latin poetry tables at 1237+ (values not extracted). Timm 2014:497-510: Latin repeats less; English
   level comparable, but only VMS has the consecutive-line rise. R&T 422-424: prose near-neighbour ratios 0.28-0.56.
   Stellar 26-28: near-identical repetition drops 1.41x across folio and 1.29x across paragraph boundaries (page, not
   line). G&B 226-229: gibberish and VMS have more repeated words than meaningful text.
2. Contradictions / tensions: (a) R&T Table 4 (446): Species Plantarum records amplify near-identical neighbours
   2.57x, a list genre with reuse (compare s107 Llull, c-451); exact-word in-line rate not reported. (b) R&T 700, 671-679:
   the Timm-Schinner self-citation port reproduces weak token order (0.5-0.6 % vs 0.79 %) and edit-1 1.06-1.23; this
   generator is not among F-40's four pool generators (results_s87_amend1.txt:67-70), so "no generator has its weak
   order" is contested at whole-token level. (c) G&B report raw repeat rates without a shuffle; F-40's gibberish
   null (0.54 vs shuffle) is a different baseline: reconcile, not refute. (d) Timm 2014:456-459 has repeats peaking
   over the next three lines, which fits cross-line avoidance only at adjacency across the break.
3. Primary: whole-word R_within(1) and R_cross(1) (identical tokens vs within-line shuffle) on Voynich; c-431 already
   measured the reference texts on whole words (0.009-0.193), so only the Voynich whole-word side and the two
   missing controls (catalogue records, Timm-Schinner generator) are new. Backup: R&T edit-1 ratio. Published: no
   exact R_within/R_cross; near cousins exist. Run needed: partial.

## Summary table

| finding | published split-free cousin (id) | contradiction | proposed primary statistic | run needed? |
|---|---|---|---|---|
| F-11 | R&T edge-glyph MI 0.197 bits, ratio 2.9 (rozanova_temerev_2026:409-446); Parisel cross-boundary MI 0.230 (parisel_2026:370-376); G&B word-length autocorr, flattened | none | within-line shuffle-corrected MI(last glyph t; first glyph t+1) vs word-word MI | partial (rhythm half unpublished) |
| F-12 | R&T token order 0.81 % vs prose 2-10 %, Naibbe 1.25 % (Table 4, 696); Stellar dI(1) 0.243 bits, 5.4x below Latin (VL01153:23-26) | partial: R&T Currier A whole-token order negative (-0.043 bits; -0.53 %), cap-dependent | held-out whole-word adjacent MI at matched cap K vs languages and ciphers | partial |
| F-13 | Timm 2016 consecutive identical 0.95 % vs Quran 0.01 % (VL00131:336-356, 746); R&T edit-1 ratio 1.12 vs prose 0.47-0.56; Timm 2014 3-line peak | none | whole-word identical-token R(d) vs within-line shuffle, rare stratum | partial (confirm only) |
| F-14 | Dominik initial-glyph classes: held-out gain 0.041-0.064 nats; +0.146 in line vs -0.027 across break, exploratory (VL00735:20-26, 160-174); R&T line-break -0.036 | none | held-out gain of first-glyph class t given t-1, in-line vs across break, lag 2 | partial (reset pre-registered) |
| F-15 | Stolfi grammar dependencies, daiin/qokeedy vs deedy (qualitative, grammar.html:230-292); Timm 2014:278-300 | none | within-word MI(initial bigram; final bigram) by length vs recombination null | yes |
| F-30 | Parisel Cardan grille fails 4-signature joint criterion; net signal 0.002 vs 0.18 bits (parisel_2026:502-542) | Rugg 2004 / Rugg & Taylor 2016 claim success (unverified) | Parisel joint criterion (cross-boundary MI + end-to-start rate) | no |
| F-34 | R&T default Naibbe: edge MI 0.006 vs 0.197, edit-1 0.82 vs 1.12, hapax 41 vs 70 % (rozanova_temerev_2026:696-698) | none | R&T edge MI + edit-1 ratio on line-sticky Naibbe; F-14 stat for the memory half | partial |
| F-39 | R&T Naibbe: more order (1.25 %) and fewer near-repeats (0.82) than Voynich; homophonic differential +0.13..+0.52 (696-701) | none (order half cap-fragile, as in R&T 428-432) | whole-word identical-adjacent ratio on syllable/chunk homophones with line table | partial |
| F-40 | Timm 2016 Quran d=1 0.01 % vs VMS 0.95 %; R&T prose 0.28-0.56; Stellar page-anchored reuse (VL01153:26-28) | tension: R&T catalogue 2.57x near-repeats; R&T Timm-Schinner port reproduces weak token order (0.5-0.6 %) | whole-word R_within(1) and R_cross(1) on Voynich (refs already whole-word in c-431) + catalogue and Timm-Schinner controls | partial |
