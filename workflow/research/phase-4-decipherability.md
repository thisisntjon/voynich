# Phase 4 investigation: is a computational route to a reading possible, and which one?

Stamped Sat Oct 17 22:22:37 PDT 2026 (output of `date`). Read-only investigation for Phase 4 (t1). No board or entrant
runs and no downloads into the project. Exploratory scripts and outputs are in the session scratchpad
(`scratchpad/p4_solv/p4_checks.py`, `p4_sa.py`, `*.out`), not in the project. Web pages were treated as data.
WebFetch cached three PDFs in the harness tool-results folder (Copiale 2011, Kambhatla 2023, Kopal 2019). The first two
were text-extracted in the scratchpad; Kopal 2019 is scanned images and was not read.
**Unverified** marks claims I did not check against a primary text.

Inputs read: FINDINGS-REPORT.md, CONSTRAINTS-MAP.md, the PLAN.md Phase 4 heading, results_i1.txt, a6_solver.py header,
results_a6_k0 / a6b_*, period_nomenclators.md, greshko_naibbe.md.

## Verdict: CONDITIONAL

The computational Tier-1 route is **open only conditionally**. Information does not limit it. The ciphertext
over-determines any letter-level verbose homophonic key by roughly 40 to 300 times. What limits it is **model
identification**, and three conditions must hold:

1. **A planted control passes.** A solver must recover ≥90 % of letters, with the language ranked first, on a planted
   two-layer verbose cipher with nulls whose ciphertext matches Voynich on types, hapax share, h2 and A14. It must do
   this at 38k tokens with the unit segmentation **not** given (ladder L3/L4 below). Nobody has published such a
   result, and the project's existing positive control (a6, 100 %) uses a 21-symbol non-verbose cipher with spaces kept.
   If L4 fails with the best solver below, the computational Tier-1 route **closes** for this family.
2. **The plaintext stream is placed.** Under the project's segmenter, cores show core→core ordering *below* a
   within-line shuffle (A14: −0.0315). A letter-carrying core stream would sit far above it (check B below). So either
   plaintext rides the operator (affix) layer, or the cipher reorders, or the segmenter's units are not the cipher's.
   The key search must be pointed at a stream that can carry text.
3. **The board identifies the family.** Before any key-search result is read as evidence for "cipher", the confusion
   study (Q2) must show the features separate cipher from generator at the stated accuracy.

A word-level code at 7k types is a different case. Its key is **not determined**: unicity is about 23k words against
35k tokens, and 68 % of types occur once. A11 already rules it unhistorical, so that sub-route stays closed.

## Q1. Unicity distance and solvability

### Shannon estimate (scratchpad `p4_checks.out`, part a)

U = H(K)/D. For a homophonic key mapping n cipher units to 23 period letters, H(K) ≤ n·log2 23. D is the per-letter
redundancy. A character-trigram estimate on the project's controls gives a lower bound of D ≥ 1.8–2.1 bits/letter for
Latin (Pliny herbal), Italian (Dante), German (Faust), Occitan and Czech. The long-range value is about 3.1 if the
true H is near 1.5 bits/char (this is an assumption). The Hebrew control did not load through `corpora.control`, which
is Latin-script only, so no number is given for Hebrew. An abjad has higher per-sign redundancy loss and is
**unverified** here.

| Key model | Units n | H(K) bits | U at D=1.5 | U at D=3.0 | Available |
|---|---|---|---|---|---|
| Plain verbose homophonic | 120 | 543 | 362 letters | 181 | ~53,000 letters (A11) |
| Two-layer, ~41 prefix + ~50 core-like units, 300 in all | 300 | 1,357 | 905 | 452 | ~53,000 |
| Naibbe-size tables: 138 unigram + 276 bigram halves | 414 | 1,873 | 1,249 | 624 | ~53,000 |
| Word code at 7k types (V=20k plaintext words, D_word≈4.3) | 7,000 | ~100,000 | — | ~23,000 words | 34,857 tokens |

Adding nulls and not knowing the language add little. Choosing one of 6 languages costs 2.6 bits. Null status costs
about 1 bit per unit, roughly n more bits. The segmentation rule adds an unknown number of bits. If it is a small
parametric rule, a few hundred bits; if it is a per-token choice, it is not bounded, and **unverified**. Even with
U = 2,000 letters, a verbose letter cipher is over-determined 25-fold. Unicity is a lower bound for an ideal attacker
with the correct cipher model. It says nothing about whether a search finds the key, or about a wrong model.

### Empirical record of homophonic and nomenclator solvers

| Case | Size | What it took | Source |
|---|---|---|---|
| Jakobsen 1995, fast hill-climb on digram matrices | simple substitution | the basis of every later nested hill-climb. Citation from memory: Cryptologia 19(3); **unverified** | — |
| Dhavare (and Low, Stamp), nested hill-climb for homophonic | synthetic; success rate vs alphabet size and length; Z408 | a generalised Jakobsen climb. The SJSU thesis is confirmed. The Cryptologia 2013 co-authorship and its numbers are **unverified** | https://scholarworks.sjsu.edu/etd_projects/207 ; https://works.bepress.com/mark_stamp/18 |
| Ravi & Knight 2011, Bayesian sampling | Z408, 408 chars, 54 symbols | letter n-gram LM plus word dictionary; first fully automatic Z408 | https://aclanthology.org/P11-1025/ |
| Berg-Kirkpatrick & Klein 2013 | substitution / Zodiac | EM-HMM needs very many random restarts. Use on Zodiac **unverified** | https://aclanthology.org/D13-1087/ |
| Z340 (Oranchak, Blake, Van Eycke 2020), AZdecrypt | 340 chars, 63 symbols | AZdecrypt alone **failed**. It worked only after Blake's search over transpositions found the right model; a crib-like fragment ("gas chamber") then fixed the key | https://www.theregister.com/2020/12/12/zodiac_killers_cipher_solved/ ; https://popsci.com/technology/zodiac-letter-decode |
| Copiale (Knight, Megyesi, Schaefer 2011) | 75,000 chars, 105 pages, ~90 symbols | the automatic homophonic attack with Knight 2006 language-ID gave **nonsense**, with only a "very slight" preference for German. It was solved by hand after humans found that the unaccented Roman letters are *spaces*, not nulls. The cluster map of symbol contexts helped | https://aclanthology.org/W11-1202/ (PDF text read) |
| Papal ciphers, 16th–18th c. (Lasry, Megyesi, Kopal 2021) | hundreds of letters | homophonic plus nomenclature, solved by hill-climbing/SA on the homophonic layer, with the nomenclature recovered from context. Details **unverified** (full text not read) | Cryptologia 45(6), doi 10.1080/01611194.2020.1755915 ; https://ecp.ep.liu.se/index.php/histocrypt/article/view/401 |
| Mary Stuart letters (Lasry, Biermann, Tomokiyo 2023) | 57 letters, ~50k plaintext words | SA on the homophonic layer, with humans handling the nomenclature; >1 year of manual work; language (French) identified during the solve. Press-grade; the paper was 403 | doi 10.1080/01611194.2022.2160677 (Crossref-verified) ; https://cryptool.org/en/posts/marystuartciphers ; https://www.scientificamerican.com/article/scientists-decipher-50-letters-from-mary-queen-of-scotts-before-her-beheading1/ |
| Kopal 2019, SA with fixed temperature for homophonic (CrypTool 2) | Z408 and others | PDF is scanned; numbers **not read** | https://ep.liu.se/ecp/158/012/ecp19158012.pdf |
| DECODE/DECRYPT historical LMs (Megyesi et al.) | HC/SA | historical LMs do better on ciphertext from the 17th c. or earlier | https://ecp.ep.liu.se/index.php/histocrypt/article/view/701 |

**What made the real blind successes work, in every case:** (i) the cipher units were known discrete symbols in a
transcription, with no segmentation problem; (ii) one plaintext letter (or a few) per symbol, with spaces or word
boundaries recoverable; (iii) a narrow language prior from provenance (German book, French ambassador, papal Italian);
(iv) humans solved the nomenclature from context after the letter layer fell; (v) when the cipher model was wrong
(Copiale spaces, Z340 transposition), the automatic solver failed until the model was corrected. **I found no blind
decipherment of a real cipher in which the unit segmentation was itself unknown**, nor one with a ~7k-type word
surface (**absence, not exhaustively searched**). Voynich fails (i) and (iii). So it sits outside the published
success envelope, though not by information. The solvable size is not the issue: Copiale at 75k chars and Mary Stuart
at ~50k words are larger than Voynich.

### What the project's own data add

- **results_i1** shows that recovering classes by clustering, the Copiale route, collapses at Voynich-like types: type
  ARI 0.044 at m=3 and 0.010 at m=5. A cluster-first, assign-second pipeline is therefore closed. The search must be
  joint.
- **Check B (scratchpad, exploratory).** I enciphered Latin (Pliny herbal) letter by letter into "cores" with k
  homophones per letter and wrapped it at 9 tokens per line. Core→core MI excess over a within-line shuffle came out
  +0.52 (k=1), +0.50 (k=3), +0.44 (k=6) and +0.30 (k=12). Naibbe-like 1- or 2-letter tokens gave +0.09. Voynich cores
  under the project's segmenter sit at **−0.0315** (A14). The statistic is analogous to A14's but not the same code,
  so comparability is **unverified**. If it holds, no letter-carrying core stream in reading order is consistent with
  A14.
- **Check C (scratchpad, crude SA).** A planted verbose homophonic cipher of 38k units, with segmentation and spaces
  given, trigram LM from a different Latin text, 40k SA steps, 3 seeds:
  - 69 or 138 units: best seeds reach 74–75 % letter accuracy. The found key **outscores the true key** (−3.204 vs
    −3.241 bits/char), so a trigram objective alone is mis-specified. a6 adds a unigram KL term for this reason.
  - 15 % nulls from 20 null types added: accuracy drops to 37 %, and one seed collapses.

  This is a weak solver. AZdecrypt-class solvers with 5–6-gram LMs do much better on Z408-size texts. But it shows
  that nulls and the objective, not length, are what bite.

## Q2. The identifiability (confusion-matrix) study, minimal and pre-registerable

**Purpose.** Measure whether the board's features can tell producer classes apart at Voynich size, before any Tier-2
verdict is read. This tests the red team's claim directly: 7/10 quantities tie by construction, nothing survives BH,
and verdicts flip.

**Corpus: 30 texts at 38k tokens each, 6 per class, all on real lines.** Lines follow the Voynich line-length and
paragraph distribution unless a producer has its own line mechanism.

| Class | Six texts |
|---|---|
| C1 Verbose homophonic with nulls, two-layer (affix operators + core) | Latin, Italian, German, Occitan, Czech, plus 1 Latin with operator affixes as nulls. Key parameters (homophones 3–6, null rate 5–20 %, unit size) drawn at random from a frozen range |
| C2 Naibbe (Greshko reference code, 78-card) | Latin ×2, Italian ×2, German, and 1 with the author's speculative line-edge nulls added |
| C3 Procedural generators | Timm–Schinner self-citation, the project's s28 edge-table generator, the 7k habit generator (n6), a Rugg-style grille table, and 2 **matched twins**: generators built from the pools and tables of two C1 texts (the red team's construction) |
| C4 Meaningless human-like | resampled pooled gibberish writers (the pool is only ~10k tokens, so this is the weak class; flag it), and 5 texts from a Markov model of the human gibberish |
| C5 Script controls (meaningful, not ciphered) | Latin written as a syllabary (CV units), Italian syllabary, unvocalised Hebrew (abjad), unvocalised Latin abjad, and 2 real-language texts in a non-alphabetic romanisation |

**Blinding.** One agent builds the texts from seeds. A second agent holds the sealed label file, sha256 in the stub.
A third agent scores. Labels are opened only after the result file is written.

**Features.** The v2.1 board's 10 judged quantities, plus A5 (within-line Moran I), A6 (CHARWIN), A7 (F1 residual)
and A14 (next-prefix excess, core→core excess), all computed exactly as for Voynich. Features are standardised on the
30 texts only.

**Classifier, pre-committed.** Nearest-centroid with leave-one-text-out; no tuning. Also report per-feature
univariate AUC for cipher (C1+C2) vs generator/meaningless (C3+C4), plus where Voynich falls (posterior and distance
to each centroid).

**Decision thresholds, frozen before running:**

- Primary binary task, C1+C2 vs C3+C4 (24 texts): **≥ 20/24 correct (83 %)** for the board to be usable for Tier 2.
  Binomial p vs 0.5 is about 0.0008, and the Clopper–Pearson lower bound is about 0.63. At ≤ 16/24, the red team is
  confirmed: Tier-2 verdicts from this board are withdrawn, not just weakened.
- Matched-twin task, which of each pair is the cipher: 2 pairs here, extendable to **10 pairs**. It must reach
  **≥ 9/10** (sign-test p 0.011). Below that, the 7/10-tie problem is structural, and only the non-tied features
  (A5/A6/A7) may be cited.
- Five-class accuracy, reported but not gating: ≥ 15/30 (p 0.0002 vs 0.2 chance).
- A Voynich assignment counts only if the binary classifier passes and Voynich's margin between the two nearest
  centroids exceeds the median margin of correctly classified texts.

Scale-check figures: 22/30 gives p 0.008 and CP lower 0.54; 24/30 gives p 0.0007 and CP lower 0.61. Cost: CPU only,
30 board-scale scorings under the concurrency cap. The texts must be generated with mechanisms frozen before scoring
(the provenance rule of 22:09).

## Q3. Solver plan, positive control first

**Run first: SA/MCMC homophonic search over cipher units** (AZdecrypt / CrypTool-2 / Lasry class), extended so that
the state includes each unit's null flag and a parametric segmentation rule. Reasons:

- It is the only family with a record on long real homophonic and nomenclator texts: papal ciphers, Mary Stuart,
  Z408, and Z340 once the model was right.
- Cost grows linearly in text length, so 38k units is cheap on CPU and no GPU is needed. That removes t1's GPU gate.
- a6 is already a working harness with a unigram-KL objective.

The other candidates are second:

- **EM noisy channel** (Knight 2006; the t1 plan) is the weaker sampler on homophonic ciphers. Ravi & Knight 2011
  beat it, and Berg-Kirkpatrick & Klein needed very many restarts. Keep it as a cross-check only.
- **LM-scored beam** (Nuhn et al. 2013; Kambhatla et al. 2018, https://aclanthology.org/D18-1102/) was designed for
  1:1 ciphers and degrades as the symbol count rises toward 138–400 units.

**Objective.** 5- or 6-gram char LM per language, from period text where possible (Megyesi 2023), plus a unigram-KL
term, plus a word-boundary term. Six languages run in parallel. The language is chosen by held-out LM gain over the
pseudo-Voynich null (the a6b design).

**Positive-control ladder.** Each rung is pre-registered, with plaintexts held out from the LMs and 3 seeds. A rung
passes at ≥ 90 % letter accuracy with the true language ranked first.

| Rung | Planted cipher | Status |
|---|---|---|
| L0 | 21 symbols, spaces kept | done: a6 POS 100 % |
| L1 | Verbose homophonic, 138 units, segmentation given | crude check 75 %; needs the real solver |
| L2 | L1 plus 15 % nulls, null status unknown | crude 37 % |
| L3 | Two-layer: operator affixes plus core, units unknown; solver sees EVA glyph strings and must also search the segmentation rule from a frozen family (e.g. slot grammar) | not run |
| L4 | L3 with key parameters tuned so the ciphertext matches Voynich: types 7k ±15 %, hapax 0.68, h2 2.1 ±0.05, A14 core→core ≤ 0, and A5 inside the s15 width | not run; **this is the gate** |

**Close rule.** If the best SA/MCMC solver, with EM as a cross-check, fails L4 in all six languages at 38k tokens
within a stated budget (proposed: 50 CPU-hours), the computational Tier-1 route closes for the verbose-homophonic
family. That does not show that Voynich is not a cipher; it shows that a computer will not read one built this way.
If no cipher meeting L4's targets can be constructed at all, that is itself evidence against the family. Record it
as such.

**Only if L4 passes:** run on Voynich (Currier B first, then A), with the pseudo-Voynich null and a section-split
consistency test: the key from half the pages must decode the other half. Content is judged only against untouched
material.

## Q4. Neural and LLM decipherment, 2018–2026, and its record on real ciphers

- **Kambhatla, Born, Sarkar 2018** (EMNLP): beam search with a neural LM; 1:1 ciphers. https://aclanthology.org/D18-1102/
- **Aldarrab & May 2021** (ACL), seq2seq without language ID: 1:1 only, homophonic left as future work. Borg cipher
  (first 256 chars) SER 3.91 % monolingual and 5.47 % with the 14-language model.
  https://aclanthology.org/2021.acl-long.561/ ; https://arxiv.org/abs/2012.15229
- **Aldarrab & May 2022**, segmenting numerical ciphers: 27 % segmentation error on three real homophonic ciphers,
  against 2 % on synthetic (search summary; **unverified**). This is relevant because Voynich's problem is segmentation.
- **Kambhatla, Born, Sarkar 2023** (EACL Findings), recurrence-encoded causal Transformer (text read):
  - Synthetic homophonic, ≤ 85 keys at 400–700 chars: near-perfect.
  - Z408: SER 1.9 %, or 0.4 % with 5 human corrections.
  - Real TNA_SP106/5 (171 chars, 47 symbols): SER 1.13 %. BnF-f01 also solved.
  - Borg, zero-shot into Latin: 45 % SER, falling to 3.9 % after 3 human word fixes.
  - Stated limit: O(n²) attention makes ~1,500 chars "extremely compute inefficient".
  - It assumes letter-level homophony with word boundaries given.

  https://aclanthology.org/2023.findings-eacl.160/
- **Attention-LSTM homophonic, arXiv 2606.05078 (2026):** synthetic only, needs a known shared code pool, and fails
  outside it (abstract only). https://arxiv.org/abs/2606.05078
- **HistCiph (Bruton, Beloucif, Megyesi 2026):** a benchmark only, with no model results on the abstract page.
  https://aclanthology.org/2026.resourceful-4.2/
- **On Voynich:** Hauer & Kondrak 2016 ("Hebrew") was rejected by specialists. LLM-assisted forum "decryptions" in
  2025 were dismissed, and the forum bans them. arXiv 2609.20835 ("pastiche" via LLMs) is **unverified**, with no peer
  review seen. https://www.mentalfloss.com/science/archaeology/researchers-claim-crack-voynich-manuscript-using-ai-experts-are-skeptical ;
  https://arxiv.org/pdf/2609.20835

**Record:** neural methods have solved only *short, known-type* real ciphers, all letter-level homophonic or 1:1 with
known units, and the longer ones needed human correction. None has read a real undeciphered cipher whose type was
unknown, and none is built for 38k tokens with unknown segmentation. Use: at most a cross-check decoder on single
Currier-B pages *after* L4 fixes a unit hypothesis.

## On the red team's claim

It is correct as far as it goes. A matched twin ties a cipher by construction, so the board cannot separate them
there. Two things follow:

- **Q2 is the test of whether the board identifies anything at all.** Without it, Tier-2 "leans" have no stated error
  rate.
- **A key search is the separator the board lacks.** Only a cipher yields a key that decodes held-out pages. That is
  why Phase 4 should not wait on a Phase 3 Tier-2 verdict. It should wait on L4.

## Ranked next tests

1. **Core-stream check with the project's own segmenter**, cheap, CPU, pre-registered. Run A14's exact core→core
   statistic on Naibbe, on the s10 cipher twin, and on C1-style planted ciphers. If every letter-carrying cipher
   lands well above 0 and Voynich stays at −0.03, the "cores carry letters in order" sub-family closes. Point the
   search at the affix stream (s37 already queued) or at reordering ciphers.
2. **Positive-control ladder L1→L4** with a proper SA/MCMC solver: 5-gram LMs, KL term, null flags, segmentation
   family. L4 is the Tier-1 gate, under the close rule above.
3. **The 30-text confusion study** (Q2), to settle the red-team claim and give every Tier-2 statement an error rate.
4. **Only if L4 passes:** the Voynich run, with six LMs, the pseudo-Voynich null and split-half key consistency.
5. **Neural cross-check**, after a unit hypothesis exists, on single pages.
6. **Human-input items** (O-016/O-017: Meister 1902 key sizes; Naibbe main text). These bound L4's parameter ranges
   (homophones, nulls, nomenclature size) better than guesses do.
