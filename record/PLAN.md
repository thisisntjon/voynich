> **Historical campaign plan (15:25).** Current state: `README.md` → `workflow/PLAN.md` (workflow of record). Section 0 is still the proof bar. The ranking in §1, the Python version, and any note that Phase 0 has not been run are historical.

# Voynich crack attempt: multi-agent campaign plan

Written 2026-10-17 15:25 PDT (system clock). Project: `.`.
Status of the project at planning time: **not deciphered**; a1–a7, b1–b5, c2 batteries done,
literature survey done, user .docx audited. Read `docs/rounds/LEADS-AND-FINDINGS.md` first; this plan builds
on its sections A (constraints), B (dead ends), C (leads), D (open families), E (proof standard).

## 0. What "cracked" means here, and the honest prior

A crack is a fixed key plus a named language or code system that reads long continuous text
(ten consecutive pages), applies across Currier A/B, all five hands and all sections, matches
labels to illustrations without per-page retuning, fails on shuffled Voynich and on gibberish
controls, predicts held-out folios, and survives an adversarial agent that only sees the written
key. Nothing in the literature or locally meets this.

Prior, stated so later results can be judged against it: a Tier-1 reading is unlikely in any
campaign. Three outcomes are worth the tokens and are ranked below. Every phase must earn at
least Tier 3 or the campaign stops.

| Tier | Win condition |
|---|---|
| 1 | A reading passing the proof standard above |
| 2 | One of the three open families killed, or one favoured by a pre-registered margin on a joint scoreboard |
| 3 | A new hard constraint (section A of LEADS) with controls, reproducible by script |

## 1. What the existing evidence already leans toward (hypothesis to prioritise)

Three observations already measured locally pull in a direction nobody has followed up:

- Knowing the previous word helps very little (word-order shuffle costs 0.18 bits; FINDINGS §3).
- Topic alignment within a single hand is strong (NMI 0.275 / 0.333, rotation p 0.000 / 0.048; b5).
- Copying from nearby lines is real but small (column excess ~1.9 pp; b1, b4).

Pure self-citation generation predicts the opposite pattern on the second and third points.
Natural language in a cipher predicts strong sequential word information. The one family that
predicts weak syntax, strong topic, weak copying, uniform word lengths, no short function words
and a Zipf lexicon is a **codebook / nomenclator / non-syntactic notation** where each Voynich
word is a code entry, not a plaintext word. Nobody has tested a codebook against Voynich
statistics quantitatively (the earlier literature agents found no such source), so Phase 0's
synthetic nomenclator control is new ground and family 2 gets a full, fair test.

**Amendment 2026-10-17 16:18 PDT, after auditing the six earlier researcher notes.** The
promotion above is a hypothesis under test, not a finding, and the notes supply four reasons it
may fail, which PREREG now carries as metrics:

- Weak sequential information is not diagnostic: Naibbe ciphertext, self-citation output and
  human gibberish all reproduce it (Rozanova & Temerev; Gaskell & Bowern).
- "Strong topic" is weaker than LEADS reads it: Schwartz finds 0.2–0.3 bits/page, none in
  herbal, marginal under quire-aligned nulls; hand-1's largest rotation null (0.271) nearly
  equals the observed 0.275; bifolio-level similarity is confirmed and the original binding was
  the misbinding, so "section" is partly physical neighbourhood. Quire and bifolio nulls are
  mandatory.
- Edge coupling cuts against word = code entry: ~0.2 bits of MI across spaces (R&T), above
  every prose control, and 2.5 units/word locally (a5). Independent code entries predict ~0.
- Lexicon shape is wrong for a bounded code: 97 % edit-1 neighbourhoods look like coinage unless
  the "book" is enormous. (The ~70 % hapax figure cited here at first does not separate families:
  controls sit at 0.65–0.68 at matched size, m0/m4.)

So the three families enter Phase 1 on equal footing. The generation family uses the real
Timm–Schinner code and Schwartz's reuse/copy/coinage procedure, not only local reimplementations,
because the one 2026 source that ran held-out tests landed on generation. Family 1 gets one
serious GPU attack and is then closed or kept on a numeric margin.

Corrections to earlier drafts of this plan: period nomenclator sizes (Tranchedino, Simeone de
Crema) are unsourced in the project record and must be fetched from scholarly sources before
Phase 2C uses them; Davis's five-scribe model is contested and the proof standard says "all
hands as transcribed" rather than "five"; f1r marginal columns are Marci's and are not cribs;
f116v readings changed under 2024 multispectral imaging; Capricorn and Aquarius folios are lost,
so any ordered-ring test is on an incomplete zodiac; Sherwood/Tucker plant lists are hypotheses
to falsify, not identifications.

## 2. Phases, gates and agents

Each phase has an author agent and a separate critic agent. The critic never sees the author's
conclusion before scoring. Every number goes into one machine-readable scoreboard
(`scoreboard/scoreboard.json`) through one scoring pipeline, so real text, controls and simulators
are measured identically. All scripts stay stdlib+numpy/scipy/sklearn (already installed,
Python 3.11.9; RTX 5080 16 GB available for Phase 2L).

### Phase 0: pre-registration and infrastructure (1 session, 3 agents)

Deliverables before any new measurement is read:

1. `PREREG.md`: the metric list (A1–A8 plus sequential-word MI, within-hand topic NMI, copy
   locality, lexicon growth curve, slot coverage), the thresholds that count as "favours X",
   and the kill criteria for each family. Written by the orchestrator, signed off by the critic.
2. `scoreboard/score.py`: one function that takes a tokenised corpus with page/line/section/hand
   metadata and emits every metric. Refactored from a1/a2/a4b/a7/b1/b3/b4/b5. Unit-tested on
   the existing results files (must reproduce them to the printed precision).
3. Data agent fetches, into fresh untrusted directories under `data/external/`:
   second transliterations (GC v101, FSG, CD, Takahashi, and RF v1b, the ZL+GC merge, via
   voynich.nu IVTFF files) so every Phase-1 result is checked for transliteration robustness;
   the Schwartz 2026 preprint text; Timm & Schinner generator code (Glyph.java, GitHub);
   Lindemann & Bowern lingbuzz papers; the Gaskell & Bowern gibberish corpus and 42-metric code
   (public at github.com/danielgaskell/voynich); Rozanova & Temerev's image-derived space-width
   data (the one known source of word coordinates, needed for C3); Naibbe cipher materials;
   Zattera's 12-slot grammar paper (CEUR 3313) as the slot-induction baseline to beat (F1 0.27);
   Parisel arXiv 2604.19762; Montemurro & Zanette 2013. Report what exists and what does not.
4. Controls agent builds the missing control classes, each run through `score.py`:
   - natural languages not yet tested: Hebrew (unpointed), Arabic, Greek, Czech, Occitan,
     Old French, Middle High German, Catalan, Turkish; medieval Latin with abbreviations
     left unexpanded;
   - **nomenclator-encoded Latin herbal**: take a Latin herbal (Pseudo-Apuleius or Macer
     Floridus from the web, else Pliny/Augustine) and encode it with a three-slot code
     (prefix class, core index, suffix class) with period-plausible rules. Three variants:
     word-level code, syllable-level code, code with line-edge markers. This control has never
     been built by anyone locally and is the single most informative new object in the plan;
   - constructed or asemic texts: Hildegard's Lingua Ignota, Enochian, Trithemius tables,
     Lullian combinatoric tables, a modern asemic sample;
   - generators: c2 section-seeded self-citation at its best settings, Rugg grille, Markov-1,
     the real Timm–Schinner generator if its code runs;
   - cipher-with-randomiser: a Naibbe-style control (random unigram/bigram split, six tables);
   - sound-merged natural text (Lindemann & Bowern's "script ignores sound distinctions"), and
     Hawaiian / Tagalog, the natural texts closest to Voynich on h2.

Gate 0: `score.py` reproduces a1/a2/b3/b4/b5 numbers; PREREG.md is frozen (hash recorded).

### Phase 1: joint family discrimination (1 to 2 sessions, 4 agents)

The C1 lead, run once, blind, on everything from Phase 0. One author agent runs the scoreboard;
three family-advocate agents (language, codebook, generation) each receive the scoreboard and
must argue their family survives, citing only PREREG thresholds; the critic rules.

New metrics beyond what exists:

- **Lexicon growth**: new-type introduction rate against token position, by section and hand.
  Language follows Heaps' law; a bounded codebook saturates; copy-and-mutate grows linearly
  with drift. Measured locally for the first time.
- **Slot coverage**: induce prefix/core/suffix slots by positional entropy (b3 C2 shows the
  prefix class carries second-order information); measure how much of the prefix×core×suffix
  product space is occupied, and whether the occupied cells look like a designed table
  (near-uniform usage of cores within a prefix) or like a language (sparse, Zipfian).
- **Sequential vs topical information**: adjacent-word MI, same-line MI, same-page MI, same-section
  MI, as a profile. Language: steep decay from adjacent. Codebook list: flat, page-level.
  Generation: adjacent and previous-line spikes.
- **Held-out perplexity bake-off** (C4): slot model vs Markov vs c2 generator, leave-one-quire-out.
- **Published separating signatures**: edge-coupling MI across spaces (R&T), hapax profile,
  Moran's I of word length (Gaskell & Bowern), within-word character position bias (their one
  metric that separates Voynich from human gibberish), left-to-right vs right-to-left model
  asymmetry (Parisel), and the Montemurro & Zanette information-vs-scale curve.
- **Nulls**: permutation, rotation, quire-aligned and bifolio-aligned, for every contiguous label.

Gate 1: the critic issues a ranking of the three families with margins. If one family falls below
its PREREG kill threshold, it is retired and documented in LEADS section B. Phase 2 budget goes
to the survivors in proportion to their margin.

### Phase 2: deep attack on each surviving family (2 to 4 sessions, parallel branches)

**2C, codebook / notation (expected primary branch).**
- Treat each induced slot value as a symbol; ask what the code indexes. Test the star labels
  on f68r1–r3 and the zodiac labels as ordered lists (a code index should show arithmetic or
  alphabetical regularity along a ring; language names should not).
- Fit the Voynich slot table against the synthetic nomenclator control from Phase 0. If the
  synthetic control reproduces all section-A constraints at once, which no generator has, that is
  a Tier-2 result on its own.
- Search for the "book": alignment of the induced core inventory size with known period code
  inventories (Tranchedino, Simeone de Crema, Milanese chancery nomenclators are documented;
  literature agent fetches sizes and structure). Test whether prefix classes behave as section
  operators (C6) versus topic vocabulary via within-hand cross-section migration.
- Labels at scale (C7): rerun the label-in-page test on all labelled pages, not 40, with the
  rotation null.

**2L, language in an invented script (one GPU attack, then close or keep on margin).**
- Decipherment with word boundaries dropped and verbose units allowed, which a5/a6 never did:
  simulated-annealing homophonic solver plus a neural noisy-channel decipherer (byte-level LM
  per target language, Luo-style undersegmented decipherment) on the RTX 5080.
- Targets: all Phase-0 languages, including abjads with vowels omitted.
- Positive controls at matched ciphertext length for every cipher variant (verbose, nulls,
  dropped boundaries, abjad). A variant that cannot recover its own control is not reported.
- Kill criterion (pre-registered): best language must beat the pseudo-Voynich null by more than
  the gap between any two wrong-language real texts. Otherwise family 1 is closed for letter-level
  substitution with any of these languages, which is a Tier-3 constraint.

**2G, generation (null model; must be kept honest).**
- Take c2 to its best joint fit and count free parameters against the number of constraints hit.
  Report the minimal rule set that reaches every section-A target at once, or prove by search
  that no setting does. Either answer is a Tier-3 result.

### Phase 3: cribs and the facsimile (1 session, 2 agents, Chrome)

- Crib agent compiles every proposed crib (f116v, f1r alphabet column, f17r/f66r marginalia,
  zodiac month names, star names, plant identifications from Sherwood/Tucker lists, f57v ring)
  and tests each against the best Phase-2 mapping only, never the other way round.
- Image agent uses the Beinecke scans in Chrome to (a) replace the word-index column proxy with
  measured x-coordinates on 30 sampled pages for the C3 test, and (b) retest the f57v "17×4"
  claim at glyph level per ring. If a bounding-box dataset turned up in Phase 0, use that instead.

### Phase 4: blind validation (only if a candidate reading exists)

A fresh replicator agent receives only the written key and ten held-out pages it has never seen,
and must produce a reading. The critic scores it against shuffled Voynich and against the
gibberish controls. Nothing is called a reading unless this passes.

### Phase 5: write-up

Update `docs/rounds/LEADS-AND-FINDINGS.md` sections A–D with every new verified line; append dead ends to
section B; publish a report with the scoreboard table.

## 3. Agent roster

| Role | Count | Scope |
|---|---|---|
| Orchestrator (this session) | 1 | Owns PREREG, scoreboard, gates, LEADS updates |
| Data / infra | 1 | Fetch transliterations, papers, datasets; untrusted dirs; `score.py` refactor |
| Controls builder | 1 | Language corpora, nomenclator control, constructed-text controls, generators |
| Family advocates | 3 | Language, codebook, generation; argue only from PREREG metrics |
| Decipherment compute | 1 | GPU solvers with matched positive controls |
| Literature / cribs | 1 | Period nomenclators, crib catalogue, Schwartz preprint claims |
| Image (Chrome) | 1 | Beinecke scans, x-coordinates, f57v rings |
| Adversarial critic | 1 per phase | Never the author; rules on gates |
| Replicator | 1 (Phase 4 only) | Reads from key only |

Agents are briefed from this file plus `docs/rounds/LEADS-AND-FINDINGS.md`; each returns findings, not dumps,
and writes results to `results_dN_*.txt` with the same seed convention (20261017).

## 4. Order of execution and stopping rules

1. Phase 0 now (infrastructure and controls can run in parallel with the data fetch).
2. Phase 1 as a single Workflow run: scoreboard, then three advocates, then critic.
3. Phase 2 branches in parallel, weighted by Gate 1 margins; 2L is capped at one GPU session
   unless its margin clears the kill line.
4. Phase 3 after Phase 2 produces a best mapping; earlier if the image agent is idle.
5. Stop the campaign when a phase returns no Tier-3 result, and write up.

Rough cost: Phase 0 and 1 are the cheapest and most informative (roughly 8 agents total);
Phase 2 is the expensive part and is only funded for families that survive Gate 1.

## 5. What would refute this plan's premise

If Phase 1 finds high sequential-word information once words are re-segmented (the 0.18-bit
figure was measured with Voynich spaces kept), the codebook promotion in section 1 is wrong and
2L becomes primary. That check is in the Phase 1 metric list for that reason.

## 6. Progress check and next round (2026-10-17 16:45 PDT, system clock)

Status: **not deciphered.** Four sessions have run a–h plus m0–m3 today. The map is
`TEAM-HANDOFF.md`; numbers live in `results_*.txt`.

### What the day settled (combined across sessions)

1. **No producer joint-passes the frozen seven-band board** (`results_g0/g1/h1`). Generators
   without an edge table miss cross-space coupling; given one (G1) they pass coupling and then
   miss held-out entropy, first-glyph divergence and repeats, and none carries transferable word
   order (`results_f3`); ciphers miss line edges; both codebook designs miss entropy by more
   than a bit (`results_ctl_nomen*`).
2. **The one producer that matches entropy, edge coupling and held-out word order together is
   a verbose homophonic cipher of real language with glyph-flow choice** (`results_f3`). It
   still misses line edges, type count, hapax share and repeats. Naive class recovery on top of
   it fails on Voynich (`results_f4`), but the same procedure also loses the known key on the
   control once homophones are inflated to Voynich-like type counts (`results_i1`), so that
   negative is a power failure, not evidence against the family.
3. **Words look generated from glyph rules more than drawn from a lexicon**: a character model
   beats a word list on held-out Voynich and loses on every language control
   (`results_m0`, `results_m3`), the glyph position lock is the strongest of any corpus, and
   both are stable across four transliterations (`results_m2`).
4. **Visual same-column copying is at most minor** once real coordinates are used
   (`results_m1`), which removes the mechanism Timm–Schinner's generator leans on hardest.
5. **Topic evidence is weaker than first read** (quire null, `results_c1`), and the original
   codebook promotion in §1 is withdrawn. The codebook family survives only as a skewed,
   templated code, which is the cipher family under another name. Families are now two:
   encoded language (cipher/notation) versus content-free generation.
6. **The line-edge profile is the universal failure, and m5 now says what it is**
   (`results_m5_line_anatomy.txt`): the gallows/p effect is paragraph-initial (83 % of
   paragraph-first lines, mostly rare types never seen mid-line), ordinary line starts are a
   y/d/t/s word-choice profile, line ends draw from a small m/g type set, and d-initial words
   drift toward line end. Line starts are vocabulary choice, not an added marker glyph (79 %
   of the first-glyph divergence survives restricting to ordinary mid-line types); line ends
   are both, vocabulary dominant with a measurable flourish component (+12.5 pp strip-attested,
   stronger in B). A producer needs those four draws, not two glyph rules.
7. **Labels are a habit register, not nomenclature** (`results_m6_labels.txt`): o-initial, no
   qo-, hapax-rich, no list order, recurrence at chance once matched on frequency; the
   published label-entropy excess is mostly vocabulary rarity.

8a. **The transferable word-order signal (F1/F3/K) is dead as a discriminator** (`results_n1.txt`,
   `results_n2.txt`, both pre-registered, 18:17 and 18:24): a meaningless generator with a global
   word-pair habit on about 4 % of draws (p = 0.04) reproduces the manuscript's held-out residual
   on all three transliterations (+0.042 / +0.039 / +0.035 vs the manuscript's interval) while
   edge coupling, repeats and h2 all pass. Transferable word order no longer separates encoded
   text from generation. Every passage citing F1/F3/K residuals as evidence for meaning is
   withdrawn, including the 18:10 assessment's "single best argument for content".
8b. **Page-level MI falls too; hand-1 topic alignment is the last content-side signal**
   (`results_n3.txt`, pre-registered 18:50): the N2 habit generator matches the page-level MI on two
   of three transliterations and the manuscript fails its own null on the third; hand-2 section NMI
   fails the quire-block null; hand-1 section NMI holds by 0.013 and 0.005 on two transliterations,
   with generator seeds spanning 0.15–0.30. Thin, and still to be checked against a 7k-type
   generator and the bifolio null (O-041).
8. **Joint board verdict (`results_m4_phase1_board.txt`, 43 corpora, pre-registered rule):**
   no family is in. Under the draft in/out rule generation has the fewest outs overall and in
   Currier A (margin 2 and 3) and ties with the code family in B, but that edge is partly
   artefact: generators match entropy, repeats and position lock by construction, and the
   natural-language controls have no real line edges, so they are out on the three edge bands
   by design. Fourteen of 23 metrics carry no weight because the L, C and G control ranges
   overlap at 25k tokens, which means most of the new metric families do not separate the
   families at this size. The robust result is the pair of anomalies that no control family
   reaches at all: the line-edge first-glyph profile (0.176 vs at most 0.117 anywhere) and the
   word-boundary glyph coupling (0.181 vs at most 0.146, the best being the Latin herbal Macer Floridus, with Dante at 0.141). Those
   two, together with m5's anatomy, are the targets for the next producer.

### Next round, ranked by value per token

| # | Test | Why now | Owner / file | Cost |
|---|---|---|---|---|
| 1 | **Line-initial word anatomy**: is a line-initial p-word "p + ordinary word" (marker) or a different vocabulary? Same for line-final m/g. | Settles the one target every producer misses; decides whether the rule is a null-glyph (cipher) or a word choice (generator) | m5, done (point 6) | done |
| 2 | Joint board over all controls with per-family ranges | done, see point 8 | m4 | done |
| 3 | **Frozen bands on RF1b/IT2a/GC2a** | A band that a retranscription crosses is not a band | m7, done: bands move by at most 0.01 h2 on ZL3b/RF1b/IT2a; the h2 and sd_len bands are alphabet-specific (glyph+ and v101 break them) | done |
| 4 | **Labels as a register** (entropy, o-initial, list order, Schwartz's trace) | Only untested text class; cheap; Schwartz's one "trace of content" | m6, done (point 7) | done |
| 5 | **Joint producer**: flow cipher + the line mechanism m5 finds + a hapax-heavy table, scored once on the full board without per-metric tuning | Tier-2 if it passes; F_RESULTS step 2, blocked on #1 | next session, prefix j | medium |
| 6 | **Key search under the F3 model**: noisy-channel decipherment (plaintext LM × homophone channel × flow choice) with EM/annealing on the RTX 5080, validated first on the F3 cipher whose key is known, then run against the 15 language controls' LMs | The only path from "family" to "key"; F4 showed naive clustering is not enough | after #5, GPU | high |
| 7 | Second-order checks: quire/bifolio nulls on everything page-contiguous; label split | PREREG v2 hygiene | with #2 | low |

Stop list (closed today, do not reopen without a new assumption): topic models and NMF; f57v as
a period key; column-copying with better coordinates; random-core or numeral codebooks;
Latin/Italian/German letter solvers with Voynich spaces kept; Naibbe as-is; parameter nudges on
c2's two line rules.

### Sprawl and organisation (census 16:42)

At the 16:42 census the top level held 130 entries: 15 summary markdowns, 51 scripts, 51 result
files; `data/` was 1.6 GB. After the 17:20 docs move and the 18:10 pruning (18:50 recount): 163
entries, 10 markdowns, 67 scripts, 70 result files; `data/` 393 MB.

Done now: this file carries the plan and the round log for the m-series; the shared map
`TEAM-HANDOFF.md` got an m-series section instead of a new summary; no new markdown was added
by this session beyond `PREREG-v2-DRAFT.md` (a proposal) and this one. Nothing was moved,
because four sessions load scripts and results by path.

Done 17:20 (approved by the user, executed by the decryption session): the eleven closed round
logs now live in `docs/rounds/` (FINDINGS, INVESTIGATION, DOCX_REVIEW, LEADS-CHASE,
LEADS-AND-FINDINGS, C/E/F/G_RESULTS, RESEARCH-PLAN, README-a-series); the root `README.md`
is a short entry point. Still proposed, pending the user's go:
- `results/`: move all `results_*.txt` and point each script's output path there in one sweep.
- Done 18:10 (user-approved): the 0.9 GB corpus clone, its zip, the 192 MB JRE and two duplicate
  generator zips were deleted; `data/external/` is about 310 MB by `du` (was 1.3 GB; the
  Gaskell–Bowern and Timm–Schinner trees remain). Details in its README.
- One runtime: everything should run on either uv's 3.13 or the system 3.11; pick uv and add
  the m/ctl scripts' needs to `pyproject.toml` (numpy, scipy, scikit-learn already declared).
