# Phase 4 investigation: scribal errors, corrections and erasures as content-side evidence

Stamped 2026-10-17 22:18 PDT from `date`. Investigation only. Nothing was pre-registered or put on the board, no
run_v2, board or entrant script was touched, and nothing was downloaded. The exploratory checks below are scratch
work: the scripts and outputs are in the session scratchpad `p4_errors/` (x1_ditto.py, x2_skip_corr.py,
x3_confusion.py, with *_out.txt). They ran on ZL3b paragraph (P) units only, seed 20261017. They are **not
pre-registered and not replicated on RF1b/IT2a. Treat every number here as exploratory.**

## 0. The point that governs every lead

Error signatures can show that **an exemplar existed**, but they cannot show that it **meant anything**. Eye-skip,
dittography, misreading of similar glyph shapes, and correction back to a valid form all happen when someone copies a
fair copy from a draft. A draft made by a table or a procedure, such as Timm–Schinner self-citation or a Rugg grille
worked on scratch paper, produces the same signatures. The only error type that requires meaning is an **error of
sense**, for example a synonym substitution or a grammatical "correction" that changes form but keeps the sense. To
detect it you must already be able to read the text. So the honest ceiling of this whole line of work is
"copied vs composed on the page". That is a production fact, not a content fact.

There is one useful interaction with the constraints map. Copying, if proven, has to coexist with A1 and A5: the
line is a unit, with a per-line cadence that real copied prose does not show (CREMMA, s18). So a copy would have to
be **line-for-line from an exemplar laid out the same way**. Otherwise the producer composed each line as it was
being written down. Either finding narrows the producer. Neither one reads a word.

## 1. Ranked leads

### Rank 1: Physical corrections classified by image (lead 3, human-only core)

- **What exists.** ZL3b marks 20 `<!corr?>` and 1 `<!erased?>` (grep of data/ZL3b-n.txt; loci f1v.7, f16r.2,
  f19r.2, f27r.6, f39r.12, f42r.19, f50v.8, f58v.3, f67v2.4, f78r.29, f79r.21, f85r1.13, f86v6.20, f87r.7,
  f88v.20, f93v.6, f102v2.31, f107v.44, f108r.43, f112r.1 ×2).
  - These marks are transcriber flags, not a catalogue of corrections.
  - No published list of corrections was found. On voynich.ninja, Winkler asked for a list and none was shown, and
    -JKP- says he has one but has not posted it
    ([thread 2658 p5](https://www.voynich.ninja/archive/index.php/thread-2658-5.html), 2019).
  - The forum's most-cited correction type is a glyph changed in place, e.g. e→s or ch→sh, with examples on f82r
    and f75r. Some posters also argue that a later restorer retraced faded glyphs
    ([thread 2658](https://www.voynich.ninja/archive/index.php/thread-2658-4.html); all forum claims unverified).
  - Erasures by scraping are said to be visible on the vellum but hard to see on scans (forum, unverified).
  - The 2024 multispectral imaging covered 10 folios and reported on marginalia only
    (`research_notes/External anchors/multispectral_marginalia.md`). As far as that note records, it reported no
    corrections inside the main text.
- **Exploratory check (x2).**
  - Only 9 of the 21 flagged words are attested elsewhere in the text, against 0.74 for random tokens of the same
    length.
  - So the flagged spots are *rarer* forms than usual. The likely cause is selection: an uncertain reading tends to
    produce a hapax.
  - The ZL flags therefore cannot answer "corrected into a valid word". You have to see the before-form and the
    after-form.
- **Smallest test.**
  - Freeze the list first: the ZL 21 plus any list -JKP- supplies, fixed before anyone looks.
  - A human codes each item from the Beinecke scans as (before glyphs, after glyphs, confidence) without seeing the
    word frequencies.
  - Statistic: the share of edits where *after* is an attested type and *before* is not.
  - Null 1: the same glyph edit applied at random positions in random tokens. This is the base rate at which the edit
    produces a valid word by chance.
  - Null 2: run the same coding on a generator executed by hand. A person writes 2 pages with the Timm–Schinner
    procedure and makes and corrects natural slips.
- **What would count.**
  - If corrections overshoot Null 1 toward valid types, that shows checking against a norm. Both an exemplar and a
    procedure can be that norm.
  - It becomes exemplar-side evidence only if the corrected form is *more context-predicted* than its rivals, i.e.
    it matches the word the line above or the procedure would not make. Even then it is not meaning.
- **Cost.** About 20–60 items at roughly 5 min each of image work, for a human. Coding scripts take under an hour.
  Power is weak at n≈20.

### Rank 2: Visual-confusion signature of misreading (new lead; a copying test with a generator comparison)

- **The idea.** A copyist misreads glyphs that look alike. So hapax tokens one substitution away from a frequent type
  should be *enriched* for confusable pairs, relative to the pairs that separate frequent types from one another.
- **Exploratory check (x3).**
  - The confusable set was chosen a priori from the top ZL single-glyph alternates: a/o, r/s, o/y, a/y, k/t, g/m,
    e/o, d/g.
  - The confusable share among hapax→frequent substitutions is 0.120, against 0.315 among frequent↔frequent pairs.
    That is a ratio of 0.38: a *depletion*.
  - By hand: hand 1 0.31, hand 2 0.49, hand 3 0.45.
  - Generators: Timm–Schinner 0.36, Schwartz 0.44, c2 0.56, markov1 0.66.
  - **No misreading signature. Voynich sits inside the generator range.**
  - Caveat: the confusable set is circular, because transcribers hesitate exactly where the lexicon has minimal pairs.
    A palaeographer's confusable set fixed in advance (Davis's glyph table) would be cleaner.
- **Smallest test.** Pre-register the confusable set from Davis 2020's letterform table rather than from ZL. Run on
  all three transliterations, with real copied Latin as a positive control (CREMMA abbreviation-mark confusions)
  and the generators as negative controls.
- **What would count.** A ratio above the generator range and close to the Latin positive control would be evidence
  of copying. It would not be evidence of meaning.
- **Cost.** About 1 h CPU. No human work, except fixing the confusable set from the paper (human or reader).

### Rank 3: Scribe-specific variant spellings (lead 4)

- **Prior art.**
  - Davis, "How Many Glyphs and How Many Scribes?", *Manuscript Studies* 5(1), 2020/2021
    ([Penn repository](https://repository.upenn.edu/mss_sims/vol5/iss1/6), [MUSE](https://muse.jhu.edu/article/754633)).
    The full text was not read here, so its content is unverified.
  - Pelling lists Scribe 2 slips on f26r and on the top 12 lines of f115r
    ([2021](https://ciphermysteries.com/2021/06/19/what-mistakes-did-scribe-2-never-make)). Timm objects that the
    "errors" are ordinary forms.
- **Project files.** Hand already explains most of the -edy/-aiin variance (η²=0.734, s35 Part 1A). Hand-1 NMI holds
  (A8).
- **Why it does not separate the families.** Different hands copying one exemplar should differ only in
  *orthographic* choices: free variants of the same word in the same context. They should not differ in the
  sequence of words.
  - Without a passage that two hands both copied, word variants per hand are confounded with section and with drift
    in a generator.
  - No such duplicated passage exists. See Rank 5: there are no repeated 5-grams in the whole text.
- **Smallest test.**
  - Inside one section written by two hands (where Davis's map gives this, e.g. Q13/Q20 splits), test whether the
    hands differ on *minimal-pair* variant ratios (ch/sh, a/o in fixed frames) while matching on core vocabulary.
  - Null: page-label permutation within the section.
  - Generator: c2 with per-hand drift.
- **What would count.** Hands that split only on glyph-level free variants (copyists' habits), with identical core
  and affix sequence statistics, point to a common exemplar. Hands that split on affix-slot use (A13/A14) point to
  separate composition.
- **Cost.** Needs Davis's page→scribe table (in the paper, human transcription about 1 h) and about 1 h CPU.
  Unverified: whether ZL `$H` already equals Davis's five scribes. ZL hands 1–5 suggest it does, but this was not
  checked.

### Rank 4: Dittography at the line turn (lead 2)

- **Exploratory check (x1).**
  - Within-line adjacent repeats: 287/30,939 = 0.93%, against a within-line shuffle median of 284. **Repeats sit
    exactly where a bag-of-words line puts them.**
  - Real Latin strongly *avoids* adjacent repeats (CREMMA prose 5 observed vs 34 shuffled). Gibberish shows 43 vs 64.
    Generators run 0.7–1.3× their shuffle (Timm–Schinner, markov1, c2, Schwartz).
  - Repeats concentrate mid-line: first pair 0.34%, middle 1.10%, last pair 0.57%.
  - Cross-line repeats (last word of line n equal to the first word of line n+1): 6/3,923, against a line-permutation
    median of 9 (p=0.92). No excess.
  - The real CREMMA copies show no excess either: 10 vs 14. **So line-turn dittography has no power even in genuine
    medieval copies.**
  - A generator, Schwartz reuse, does produce a line-turn excess (27 vs 17, p=0.01). So excess repeats would point to
    generation, not copying.
- **Reading.** The "qokedy qokedy" rate is not a copying-error pattern. It equals the expected rate given the line's
  word multiset, which is generator-like or "repetitive-formula"-like.
- **Smallest test.** Pre-register a repeat/shuffle ratio by line position on the three transliterations, against
  CREMMA, gibberish and the generators. It is cheap (minutes). It adds a constraint ("no repeat-avoidance") but is
  not content evidence. Prior art for the repeat rate: c-006, c-021, c-081 in CLAIMS.

### Rank 5: Eye-skip, saut du même au même (lead 1). Not testable on the text alone

- **Exploratory check (x2).** There are 167 repeated distinct-word 3-grams, 1 repeated 4-gram ("ol shedy qokedy
  qokeedy", f75v/f84r) and **no repeated 5- or 6-grams** in the paragraph text.
- **Why that kills the test.** Eye-skip is detected by collating two witnesses, or a passage that occurs twice, and
  neither exists here. Single-witness proxies (a trigram *a x b* where the bigram *a b* is also attested: 3,341
  cases) are dominated by the high rate of shared bigrams and have no null that separates them from generation.
- **What would revive it.** Physical evidence of omission repair: interlinear or marginal insertions with a caret.
  None were found in ZL comments or the forum sources read. Needs a human scan of all pages for insertions (a few
  hours). If insertions exist and sit at a repeated word, that is copying evidence.

### Also considered

- **Pelling's error rate (~1 per line on f111r, 2014).** Rare forms are treated as errors, which is circular, as
  Carmen and Timm object ([Pelling 2014](https://ciphermysteries.com/2014/01/15/errors-voynich-manuscript)).
  Not testable without an independent norm.
- **Wax-tablet or pecia copying.** Speculative (same sources). No test.
- **Literature 2020–2026.** No paper or book with a catalogue of corrections or a copying-error analysis was found.
  Davis's forthcoming book is cited only via forum reposts (multispectral note). Searches covered Davis, Zandbergen,
  Stolfi and voynich.ninja. Coverage was partial: four web searches and four page fetches, so absence is unverified.

## 2. Bottom line

- No lead gives content evidence. All of them can at most establish **copied vs composed on the page**.
- Three cheap exploratory checks found nothing that a generator lacks:
  - no misreading enrichment (ratio 0.38, inside generators 0.31–0.66);
  - no line-turn dittography (6 vs 9, and real copies also show none);
  - repeats at the shuffle rate.
- The single human-dependent item with any upside is Rank 1: image-coding a frozen correction list. It would join
  the Phase 4 human-input set (O-021, O-018, O-030, O-016) and be judged against a hand-executed generator.
- Refuters checked: replication on RF1b/IT2a (not done), a palaeographic confusable set (not done), Davis's
  scribe table (not read). Until those are done, everything above is **unverified/exploratory**.
