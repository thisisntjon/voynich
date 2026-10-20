> **Snapshot of 2026-10-19.** The research is paused and this is a handover copy. Status lines, queues, assignments and "next" actions below describe the team at that moment and are historical. Start at the repository's `README.md`.

# Voynich project: report of findings

> Superseded 2026-10-18 16:01 PDT: see FINDINGS-MAP section 1 / D-068. Last event this report covers: 2026-10-18 13:23 (s103 INCONCLUSIVE). Not covered: roach r6-r12, D-067 (F-34 CONTESTED), s104-s109, s101 and D-068 (F-23/F-30 at-risk). Known stale lines: section 10 says s93 'reaches the core signature' (rejected, D-064) and that s94 and s96 are running (s94 stopped at fixture, L-221; s96 rejected, D-065); the line-held prefix table there is superseded by the multi-scale state (D-067 amended, L-217). Current status: workflow/FINDINGS-MAP.md and workflow/PLAN.md Phase log.

Written 2026-10-17 22:09 PDT by voynich-08 (project lead session). Covers everything established on the project to this
hour. Every number is traced to a result file and a claim id in `.inventory/registers/CLAIMS.md`; the one-page map is
`workflow/CONSTRAINTS-MAP.md`. Phase 3 (the cipher-vs-generator pair) and s34 (superimposed streams) were still running
when this was written; their verdicts are not in here. Corrections from Sylvie's review of 22:07 are applied throughout.

## 1. The honest headline

We have not read a word of the manuscript, and nothing here predicts a word, a name or a number on pages we have not
looked at. What we have is a much sharper description of how the text is organised, a set of explanations that have
been tested and failed, and a short list of properties any surviving explanation must now reproduce. In the project's
own tiers this is Tier 3 work (constraints), with no Tier 2 (a favoured family) and no Tier 1 (an anchor into content).

## 2. How the evidence was produced

- Three independent transliterations (ZL3b, RF1b, IT2a) in the EVA alphabet; most results hold on all three.
- Every experiment since this afternoon was pre-registered: the script was hashed before it ran, the hash is in a stub
  file, and the result file prints the hash and whether it matched. A ledger (results_s23.txt) verified 122 of 124
  stub lines; the two failures are pre-crash originals superseded by amended lines.
- Controls are real-line corpora, not re-wrapped text: 21 fifteenth-century Latin manuscripts from the CREMMA
  transcription release (57k tokens), four verse and epic corpora in real lines (Nibelungenlied, Roland, the Croisade,
  Dante), 38 volunteers' meaningless writing on real lines (about 10k tokens), and the project's synthetic generators
  and ciphers.
- The manuscript's own variability is measured: 200 random 41-page splits give every statistic a width, so a
  "match" has a stated margin (results_s15.txt).

## 3. What is established (each holds on all three transliterations unless stated)

**The line is a unit of the text, not of page layout.** The first glyph of a line is far more predictable than the
glyph after any other space. Real Latin prose lines show almost none of this (excess +0.008 pooled); the manuscript
shows +0.173 at the same size (results_s18.txt). Re-wrapping the Latin into pseudo-lines changes nothing beyond the
manuscript's own width. Caveat from s32: at 114 to 201 lines, two single Latin verse or formulaic hands (a Priapea
manuscript, a book of charms) fall inside the manuscript's interval; from about 500 lines up, every verse and prose
control is well below it. Drawing gaps inside a line do not behave as line ends (gallows at 0.3 percent after a
drawing versus 22 percent at true line starts), so these are the scribe's lines, not the illustrator's
(results_s35_physical_codicology_quire_network.txt).

**The line-initial effect is mostly paragraph-initial gallows plus a line-start vocabulary.** The line-final set is not
distinctive: rhymed verse exceeds the manuscript on the line-final side (results_s17.txt, results_m5_line_anatomy.txt).

**Neighbouring words inside a line have related lengths.** Lag-1 word-length Moran I is 0.157 against a line-shuffle
99th percentile of 0.081. It survives removing repeated words, has under 3 percent cross-line share, and none of the
evaluated controls reaches it: Latin pools sit near zero or negative, verse negative, human gibberish 0.098 (below its
own null), the best generator 0.129 (results_s21.txt; Daybreak's independent ablation). The gibberish pool is small
(38 writers, short samples), so this is strong against the controls tested, not a theorem about all meaningless
writing.

**That rhythm localises to the affix slots.** Under the project's prefix/core/suffix segmentation, removing prefix and
suffix material removes about 96 percent of the measured excess, and keeping only the affix sequence keeps about 90
percent; core lengths alone are indistinguishable from the null (results_s33_line_scales_interlock.txt, Argon,
re-run with a verified hash). The effect is present in Currier A (0.117) and B (0.169), hands 1 to 3 and 5, and the
paragraph sections. Caveats: the segmenter was fitted on the same transcription, its units are operational, and the
ablation changes the statistic's normalisation. "Localised by this ablation" is supported; "explained" is not.

**Correction 22:35 (independent replication):** the line-initial result below replicated cleanly on public data with new code; the B coupling did not keep its margin, because short Latin verse manuscripts reach it. See `workflow/research/replication-roach.md`.

**Word-to-word coupling across a space is real ordering, cheap to make, and strongest in Currier B; short Latin verse reaches it.** The last glyph of a
word predicts the first glyph of the next (+0.22 to +0.24 bits above every real-line control in B). Currier A sits
inside the language range on the same statistic (results_s20.txt). Any skewed last/first table, even one rank-mapped
from Dante, regenerates the coupling, so its size proves nothing about the mechanism (results_s2, results_s30). The
largest excess dependencies concentrate on the next word's prefix; core-to-core ordering sits below its shuffled
baseline (results_s34_morphology_syntax_geography.txt). The earlier "99 percent of sequential information" headline is
withdrawn: on positive entries it is about 86 percent, and pairwise measures overlap.

**Section vocabulary rides on prefixes over a shared core pool.** The top fifty shared cores cover 80 to 85 percent of
tokens; prefix-alone section NMI is 0.29 and the conditional information of section given prefix, holding the core
fixed, is positive at the permutation floor. Hand-1 section vocabulary holds against a powered generator and a bifolio
null (NMI 0.275) but sits at the 1/55 permutation floor, which every generator seed also reaches, so it cannot be
ranked (results_n6.txt, results_p1_bifolio.txt).

**A character model beats the word list on held-out pages** (+0.094). Every language control is strongly negative;
only human gibberish shares the sign (results_n5.txt, results_s17.txt). This is compatible with strong internal word
structure and many rare words; it is not by itself a sign of meaning.

**A held-out word-order residual exists** (+0.046, interval 0.036 to 0.056) and a powered 7k-type habit generator does
not reproduce it on two of three transliterations (results_n6.txt). This is the thinnest thing a content hypothesis
can still stand on.

**Entropy and type counts depend on the alphabet; the edge and coupling anomalies do not.** Conditional character
entropy runs 2.10 (EVA) to 2.51 (GC2a); type counts 4.5k to 8.4k under boundary variants; the line-edge profile and
coupling stay positive under all (results_s2, results_p2.txt, results_s30).

**Physical layout.** Bifolios within a quire cluster on entropy and glyph rates but not on the coupling or the rhythm;
the two sides of one leaf are closer than the two halves of one sheet; the line-above copying signal survives
within-bifolio permutation and a 50-sheet bootstrap (results_s35_...). These use transcription-aligned boxes; the
pixel-derived boundary test is a separate step not yet run.

**Labels are reachable without content.** A class-conditioned generator with the manuscript's 837 label types
reproduces the label-to-image association tests. It was conditioned and tuned to those statistics, so it shows that the
statistic can arise without decoded content, not how the labels were made.

**Period practice bounds the cipher option.** About 80 percent of fifteenth-century nomenclators have under 100
entries; no period code approaches 7,000 word types. A 7k-type ciphertext is period-plausible only as a verbose
homophonic cipher with nulls, implying roughly 53k plaintext letters (B-prior-art, results_s2 2C).

## 4. What has been tested and failed

- Simple substitution, Naibbe-style and word-code families on the board (earlier phases; INDEX "do not resume").
- "The line-edge profile is scribal layout habit": killed by the CREMMA real-line control (s18).
- "Human gibberish already reproduces the within-line rhythm": killed at the within-line level (s21); withdrawn caveat
  recorded in L-115.
- "Musical or hybrid notation with a pitch slot at the word edge" (s24, Jon-approved, pre-registered): all three
  predictions fail on all three transliterations. No band-diagonal ordering beyond margins, no line-end reset beyond
  verse, no syllable-sized residue. Decision D-046.
- Five earlier negatives (column copying, hand-2 topic NMI, three others) are underpowered or seed-unstable, not
  negatives; nothing in the Phase 2 family survives multiple-comparison correction (results_s23.txt).
- Within-manuscript "matches" claimed without widths before 20:10 are superseded by the s15 widths.

## 5. The picture the constraints draw

A word behaves as two layers. A core drawn from a shared pool, with cores avoiding their neighbours, and an operator
layer of prefix and suffix that carries the within-line rhythm, the across-space coupling (in B) and the section
vocabulary. Every line-level signature lives in the operator layer. Whatever produced the text produced it line by
line, with a per-line cadence that neither scribes copying prose, poets, nor volunteers writing nonsense reproduce,
and the ordering is disciplined in a way free gibberish is not. The two families still standing, a verbose cipher with
nulls and a procedural generator, must each produce an operator stream with per-line cadence over a core stream with
almost none. Prior art for the ingredients: Gaskell and Bowern 2022 (word-length autocorrelation, gibberish
comparison), Stolfi 2000 and Zattera 2022 (word structure), Ponzi 2019 (line ends versus drawing gaps). The project's
contribution is the quantitative package: matched real-line nulls, pre-registration, ablation and reconstruction,
subgroup comparison, and the kills.

## 6. What is open

- Which producer reaches the held-out word-order residual at 7k types (O-045).
- An ink-driven token stream from the scans (O-048) and the pixel-derived boundary test.
- Whether the two layers are independent streams (s34, pre-registered, queued) and whether either family's mechanism
  predicts the three unbanded statistics in advance (Phase 3, running).
- Whether Currier A alone sits inside the Latin range on the line-initial profile (red-team request, not run).
- Nothing here supplies a crib. Tier 1 needs an anchor this pipeline does not produce: a name, a number, a reading
  that predicts held-out material.

## 7. Addendum, 22:58: results since the report was written

- **Phase 3 ended in a tie** (results_s35.txt). The letter-level cipher was the first entrant to reach the character-model
  advantage, and the copy-mutate generator the first to reach the word-order residual. Each failed the other's statistic,
  and neither came near the within-line rhythm. No family is favoured.
- **Superimposed glyph streams** (s34): no split of the glyph classes leaves a language-like residual (0 of 1,022 splits),
  while planted Latin leaves 345. The independence half of the test was invalid, because the selector failed its control.
- **Independent replication on a second machine:** the line-initial result reproduced to within a few thousandths. The
  B-coupling margin did not hold, because short Latin verse manuscripts reach it. A3 has been corrected
  (workflow/research/replication-roach.md).
- **Currier A alone** (s44) sits at +0.135, level with the top single verse or formulaic manuscripts. B, at +0.218, is far
  above every Latin row. Most of the gap to Latin prose belongs to B.
- **The two layers have different jobs.** The within-line rhythm lives in the prefixes and suffixes (s33, s39). The
  held-out word-order residual lives in the cores (s39). The cores order like words, not letters (main session's P4-D1).
  The prefix stream is strongly ordered and matches neither Latin nor any generator (s40). A cipher carrying plaintext in
  either layer, with the other layer as nulls, does not reproduce the manuscript (s43). Best-supported shape: a word-level
  core stream under an ordered operator layer. Neither layer is padding.
- **Not discriminating:** copying from the line above keeps cores and frames equally often (s42, tie). The B coupling is
  spread over the empty and y endings, and it is not B-specific (s41).
- **Still running:** the GPU ink-boundary job (s45).

## 8. Addendum, 23:33: the scans, Argon's two-layer producers, and what they change

- **The line constraint is in the ink** (s45, GPU, Yale scans). Line breaks detected from the page images reproduce the
  line-initial profile within 0.007 on 127 pages. Word breaks from the ink are still too noisy to judge. When ink gaps
  are used, the rhythm and coupling rise far above their bands, and the agreement check against the transcribers' spaces
  is owed.
- **Two-layer producers reach most of what we measure** (s36, Argon). A wrapper that writes prefixes and suffixes in the
  manuscript's order, over a pool of cores, reaches the word-order residual on every cell. It also reaches the
  within-line rhythm on ZL3b and the character-model advantage on some transliterations. It does this whether the cores
  are copied-and-mutated or Latin word stems. So the statistics we have measure the architecture, not where the cores
  came from, and they can no longer tell a generator from a message under that wrapper. Caveat: the wrapper is fitted to
  the manuscript's own affix transitions, so the rhythm is partly reached by construction.
- **Three more framings fail** (s37, Argon): liturgical and charm texts, text copied without understanding, and historical
  constructed languages. The line cadence appears only when a line-edge and affix-agreement automaton is planted.
- **Gallows words interrupt the coupling** (s37). Splitting words at internal gallows pen-lifts flips the rhythm negative
  (s38). How word boundaries are drawn is now the main open measurement question.
- **The ten-theories bundle is exploratory** (incoming/ten-theories/). None of it was pre-registered, and all of it touches
  the held-out pages. It is design input, not evidence.

What this means for strategy: further cipher-versus-generator entrant pairs will tie. The next decisive steps are the ones
that do not run through the board. These are the solver ladder with a planted control and the blind identifiability
study (Phase 4), the word-boundary check, and the human anchor work on same-plant labels.
`workflow/research/strategy-2026-10-17.md` has the order.

## 9. Addendum, 23:52: the word unit is physical

- **The scribe's spaces are in the ink** (s47). Gaps measured on 127 scanned pages agree with the transcribers' certain
  spaces at κ 0.87, and at 0.81 where the pairing is not built in. The uncertain spaces, the commas, are physically
  intermediate gaps. Pen-lifts at gallows are not gaps. Together with s45, which found ink line breaks reproduce the line
  profile, the open item on ink-derived units is closed. Lines and words in the transcription are the manuscript's own.
- **Consequence:** s45's inflated ink-word numbers were alignment noise. Argon's gallows-split stream is not the scribe's
  segmentation. Every word-level constraint rests on the physical unit, but any coupling figure must state its comma rule.
- **Running at this hour:** the GPU same-plant image map (s48), the blind identifiability study (s49), the solver ladder
  (s50) and the matched-size B-coupling check (s51).

## 10. Addendum, 01:08: identifiability, local memory, and a first held-out mechanism test

- **No internal anchor.** Sketches resemble their herbal pages in the scans (s48, s53), but labels show no link to the text
  (s54), so the image route to a reading is closed for now (D-053).
- **Where the text sits.** On the board as built, Voynich falls between word codes and generators (s49). Without line-edge
  features, code and generator cannot be told apart at all, and Voynich lies outside both classes (s55).
- **Cores have local memory.** The same core comes back within about 20 words more often than chance, most strongly for rare
  cores (s56). Natural languages and word codes do the opposite.
- **But local memory is not the producer.** A copy-and-vary model fitted to that profile on 166 pages failed all six
  pre-registered predictions on the 41 held-out pages, in all three transliterations (s57). It has no line rhythm, no
  prefix order and the wrong character-model sign. The repetition belongs to the cores, while the order belongs to the
  slot layer.
- **Next:** test the two-layer architecture (ordered affix wrapper over local-memory cores) on the same held-out pages (s58).
  The solver ladder (s50) is still running.
- **Update 01:20: the layers are chosen together (s58).** Putting a counted affix wrapper over the cores and testing on the
  held-out pages gave 1 to 2 of 6. The wrapper alone gets the character-model sign right, so that comes from the affixes.
  It misses the rhythm and the distinct line starts, and it makes far too many word forms because it picks affixes without
  looking at the core. The scribe chose the whole word as one unit, with a state lasting more than one word. Next: s61.
- **Update 01:28: where new rare words come from (s59, tentative).** The pre-registered test was inconclusive because its
  null model failed a control. In the same run, a new rare core is no more likely to have a one-letter relative just before
  it than anywhere else on its page, while a planted copy-and-edit producer is. Exact repeats cluster locally (s56), but
  variants spread over the page like a vocabulary. A confirmation on the 166 training pages is running (s62).
- **Update 01:38: the producer ladder ends (s61).** A third producer chose whole words by line position and the line's
  earlier prefix, with memory. It matched the vocabulary size and the repetition, and still failed 5-6 of 6 predictions on
  the held-out pages. Across s57, s58 and s61, no producer built from word or affix context reaches the line rhythm. Words
  behave as built from parts under tight rules: drawn whole, the character-model sign goes the wrong way; assembled freely,
  there are far too many words. As agreed in advance (D-056), producer building on this split stops here.
- **Update 01:47: two results.** (1) The confirmation of the rare-word test (s62) found a small local effect after all:
  a new rare word has a one-letter relative nearby about 2 % more often than chance. That is far weaker than a copy-and-edit
  producer and weaker than ordinary Latin, so new words are mostly not made by editing the previous ones. (2) The Naibbe
  cipher, a published 2025 design that makes Voynich-like words, is excluded at its published settings (s64): it picks a
  table at random for each word, so its prefixes have no order, while the manuscript's prefixes are strongly ordered.
- **Update 01:59: the fourth producer, tested quire by quire (s67).** It built words from parts, chose prefixes and
  suffixes by the core's class, and added a fitted length rhythm. It failed on 14-15 of 15 held-out quires. Two rules are
  confirmed: affixes depend on the core, and this keeps the word count and character-model sign right. Two properties no
  producer reaches: the order of the prefix stream, and the narrow vocabulary each quire uses. Producer building stops;
  those two properties are the next things to measure directly.
- **Update 02:05: two checks from the literature.** (1) Parisel's 2026 'switch' between folios is the scribe: inside
  each scribe's pages the setting varies smoothly rather than flipping (s68). (2) Drawings interrupting a line do not inflate
  our line statistics: removing them changes the results by at most 6 % (s65). The shorter word before a drawing, reported
  by Steckley and Steckley, partly reflects how certain glyphs are counted.
- **Update 02:19: what the prefix stream remembers (s69).** A word's prefix depends on its own core and on the previous
  word's prefix, and on very little further back. That memory restarts at every line break and passes through gallows words
  weakened. None of our codes or generators shows it. The only reference that does is Rugg's table-and-grille method, with
  five times too much. That points to one concrete comparison worth testing next.
- **Update 02:27: the solver ladder (s50) and two of Argon's results.** Our solver reads planted ciphers of the most
  discussed family (letters hidden in the word endings, filler cores) at every difficulty level, so solving power is not
  what stands in the way. But no cipher of that family could be built that matches the manuscript on all five measures at
  once. That counts against the family, not as proof, and says nothing about whether the manuscript itself is readable.
  Argon found slot profiles that go with each hand (enough to tell hands 2 and 3 apart on most held-out pages, though hand was not separated from section or quire), and
  that most 'rare' cores are one-letter shifts of the boundary our segmenter draws, which tempers dots 16 and 20.
- **Correction 2026-10-18 02:33 (steward review <team-comms>):** the 41 held-out pages have been reused by many studies, so this report now
  calls them held-out, not untouched. The word-boundary result (s47) shows agreement with the transcription's spaces
  using the s45 alignment; it is not boundary discovery without the transcription. Argon's scribe result is about
  profiles associated with each hand, not a proven per-scribe grammar.
- **Update 02:58: a second segmenter (s76).** Splitting words with Zattera's published slot model instead of ours
  keeps most of the picture: prefix memory, its line reset, prefixes tied to cores and local repetition. One result
  reverses. With Zattera's ~100 core types, cores do follow each other in order; with our ~2,400 they seemed not to. That
  may be a limit of the measurement rather than a fact about the text, and it matters because the exclusion of
  letter-in-core ciphers and part of the s50 result rely on it. A size-matched test (s80) decides it.
- **Update 02:59: roach's blind replication (r3).** A second machine, with its own code, word-splitting rule and no access
  to our numbers, confirms that word endings and beginnings depend on the word's core, and that the word-length rhythm
  stays inside lines. The prefix-order effect appears again but smaller, so its size depends on how words are split.
- **Update 03:19: roach's blind test of core order (r4).** With the vocabulary pooled to the same sizes, the manuscript's
  word cores follow each other with only a faint order, far below what any cipher hiding letters in the cores produces.
  The earlier wording, that cores order less than chance, goes: the test's own shuffled control was not clean enough to
  support it.
- **Update 03:27: two results that change the picture.**
  - **Core order (s80).** Comparing every text at the same vocabulary size shows the manuscript's word cores do follow
    each other in order, weakly: less than real languages, and mostly less than ciphers that hide letters in the cores.
    The earlier "no order" came from a measure that gives the same negative sign for Dante. Letter ciphers of that kind
    are back on the table.
  - **Reading order (s79).** Almost nothing we found depends on the order the pages are bound or the direction they are
    read. Only a slow drift across pages does.
- **Update 04:00: the cipher re-test (s82) and roach's second replication (r5).**
  - **s82.** The simple cipher families can now produce the faint core order, so that no longer rules them out. They still
    fail on three other properties: the glyph sequences are too unpredictable, they lack the line rhythm, and they lack the
    prefix memory.
  - **r5.** Roach's independent code confirms that cores carry word order across held-out quires and repeat inside lines.
    It also shows that the prefixes and suffixes carry order too.
- **Update 2026-10-18 12:07 PDT: the cipher arm, the core layer, and an audit.** (Current grades: `workflow/FINDINGS-MAP.md`.)
  - **Ciphers with letters in the cores fail (s81, s82, s83; D-061).** A table of affixes held for a whole line reproduces
    the prefix memory on held-out quires, but every cipher that hides plaintext letters or syllables in the cores fails
    them, including the line-held (sticky Naibbe) version.
  - **The cores match no kind of writing tested (s87, s89, s90).** No natural, ritual, list, gibberish or constructed text
    repeats words inside a line the way the manuscript does, and no generator gives its faint core order.
  - **A per-line pool of cores gets half of it (s91).** It reproduces the in-line repeats and the avoidance across lines on
    held-out quires, but it is too local to each quire and gets the word-level battery wrong. Argon's s93 reports a version
    with a shared vocabulary that reaches the core signature; s94, running, tests one book-wide vocabulary independently.
  - **Lead audit D-063 corrects four earlier results.** Four verdicts in Argon's s85, s86 and s92 were filed as passes
    against their own pre-registered calls or with no threshold. "Outside both word code and generator" (s55, Section 10 above) and "transposition and null
    glyphs do not explain the text" (s75) are now contested; so is the mechanism behind the homophone-cipher failure (s83,
    s88), though that cipher still fails. Argon's s96 re-tests them under amended rules (running).
  - **Composition, not copying, is now weak evidence (s95).** The per-quire test cannot tell copied from composed Latin
    at quire size, so it neither supports nor refutes the earlier reading.
- **Correction 2026-10-18 12:30 (Sylvie review, D-066).** (1) Line and drawing-gap robustness is supported (F-18, F-19; s45/s47); broad independent-ink validation is NOT: s92's physical-gap rate equals its base rate, s86 Part 3 had no threshold, and s93's physical lines are inadmissible. (2) Short-range prefix dependence (F-14) does not establish an exact one-step frame law; s98 (lag-2) tests it. (3) The core/pool/line-state architecture is a target model and has not jointly passed all constraints: s91 full signature 21/45 folds, s93 rejected and over-recurrent about 2.6x, s94 pending. Supported component findings and the D-063/D-064/D-065 retractions stand.
- **2026-10-18 13:23: s103 (Voynich herbal vs LJS 419 and Sloane 4016) is INCONCLUSIVE.** The printed 'copying drift excluded' is not accepted: the test's positive control is below its detectable effect (runs/s103/LEAD-READING.md). It neither supports nor excludes copying drift, disguise or invention.
