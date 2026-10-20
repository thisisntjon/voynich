# Red-team of the current picture, and next tests

Written 2026-10-18 12:09 PDT (clock read with `date`). This is a design input for the next runs, not a synthesis
or status file (D-058). It changes no finding. Every result it proposes must be filed through `workflow/TRIANGULATION.md`.
Sources read: AGENTS.md, workflow/FINDINGS-GRAPH.yaml, workflow/FINDINGS-MAP.md (generated 11:24), workflow/TRIANGULATION.md,
.inventory/registers/DECISIONS.md, .inventory/registers/LEARNINGS.md, and the result files cited below (opened, line ranges only).
Where a statement says "unverified", I did not find the file evidence to confirm or refute it.

## 0. The picture under test

The consensus: a procedural, line-by-line producer (a line-held affix table plus a core pool with weak order, reuse inside
the line, avoidance across lines), unlike any natural text tested. Top hypotheses are H-14 (net 2.7/1.0) and H-05 (3.0/3.0).
H-01 is at 0.0/17.5, built from F-01(s), F-04(s), F-05(s), F-11(m), F-12(m), F-13(s), F-26(m*, CONTESTED so 0) and F-40(s*).

## 1. Assumptions that would overturn it

### 1a. X-01: is the core/affix split made by the segmenter?
- What is solid. F-13 and F-40 (in-line reuse) survive unsegmented RawWord (s92 Part 1). A deterministic glyph merge
  (ch to one glyph, aiin to one glyph) cannot change word identity, so whole-word reuse cannot move with the alphabet.
  That second point is reasoning only. Merges that are ambiguous, or comma-split words, could still move it (unverified).
- What is not. F-11, F-14 and F-15 need a prefix/core/suffix cut. Their X-01 "discharge" comes from Zattera's 12-slot model.
  But Zattera and SlotSegmenter both cut the same EVA strings by positional glyph frequency (q-, o-, -dy, -aiin). Their
  agreement shows that EVA has positional glyph regularities. It does not show that those regularities are morphemes.
  We have no control that runs SlotSegmenter on natural texts at a matched core inventory and core length and asks whether
  it then manufactures "line signatures live in the affixes" (F-11) or "prefix remembers one word back" (F-14).
  Morphology that agrees across words produces exactly a one-word-back prefix or suffix memory: Bantu noun-class
  concord and Latin case agreement are examples. If lines are clauses, that memory would also reset at the line.
- The sign of core order flips with inventory size. A14 flipped this way (X-06). At Zattera's ~150 core types, cross-line
  avoidance disappears (s92 `Zattera_drop` IT2a: Rc1 1.016 against Rw1 1.108, results_s92.txt:69). So "cross-line
  avoidance" holds only for some segmentations and should be stated that way.

### 1b. Transliteration units
- h2 and type counts move with the alphabet: EVA 2.10, glyph+ 2.38, GC2a 2.51 (L-113, F-08). F-25 and F-35 exclude
  ciphers and encodings on h2 against the EVA band 2.05-2.15. The closest encoding sits at 2.174 (F-35). That margin of
  ~0.02 is an order of magnitude smaller than the alphabet effect (~0.3-0.4). If both Voynich and the cipher outputs are
  re-tokenised under each alphabet, the gap might not hold. I found no result that does this (unverified).
- CHARWIN (F-05, "strong" against H-01). I grepped every results file that reports CHARWIN for glyph+/GC2a/alphabet.
  Only s38, s72 and s79 mention an alphabet, and none of them pairs CHARWIN with one. CHARWIN's sign under other unit
  choices (ch/sh, benched gallows, i-runs) is therefore untested (unverified).
- Gallows. F-02 already separates paragraph gallows from the line-start vocabulary. 79 % of the effect survives on
  ordinary types (L-069). This is the best-defended unit choice.

### 1c. Reference corpora
- **Every natural comparator is in a European alphabet.** Hebrew and Arabic (unpointed) exist only in the older
  controls (data/CONTROLS_MANIFEST.md). None of the 23 F-40 texts or the 8 s80 languages is an abjad, a syllabary,
  an isolating or tonal syllable-spaced script (Tibetan tsheg, Vietnamese), a shorthand, or an agglutinative prose
  text. Finnish appears only as Kalevala verse.
- **Abbreviation was tested, and it matters.** CREMMA abbreviated graphemic Latin on real manuscript lines
  (results_s18.txt:178, :187) gives CHARWIN -0.152 (c15 -0.176). That is far from the -0.45..-0.74 "every language" range
  in F-05's statement, and shows that orthography alone moves the "strong" statistic more than halfway to Voynich's
  +0.094. The same rows give Moran -0.017, so abbreviation does not produce F-04's rhythm. F-04 is the H-01 link that best
  survives the "unusual orthography" objection.
- **Most F-40 natural texts are OCR on imposed lines**, not manuscript lines (s87 corpus list: "pages 173" quotas).
  The real-line exceptions are CREMMA, verse, and s89's OCR-column glossaries. Line-bounded statistics (Rc1, line reset)
  on imposed lines test the scorer more than the genre.
- **Missing genres.** These are the genres where the in-line reuse and line-held frame are natural. None appears in the
  s87/s89/s90 lists (grep for donatus|paradigm|declen|conjug|grammar returned 0):
  - recipe text with quantity sigla and numerals kept as tokens (℞, ℥, ʒ, "ana", "i", "ii");
  - grammatical paradigms and drills (Donatus, declension tables);
  - name-permutation tables (Kabbalistic, Lullian wheels written out; Lull was tested only as s90 "tables").
  The closest natural text on stems is Kalevala parallelism verse (Rw1 0.723, s89).
- Note that s80's "below every matched language" (F-12) is drawn from six narrative or verse texts. On list genre, the
  Dispensarium antidotary reads K100 +0.068 (s87), close to Voynich's s80 +0.045.

### 1d. Statistics with known biases
- **Matched-K MI (F-12, F-39, the "weak order" part of F-40).** At K=200-400 with ~6k held-out tokens, the bigram table
  has 40k-160k cells. The shuffle excess cancels first-order bias only when the unigram shapes match, and Voynich's core
  frequency curve is not a language's. The estimator family already flipped once (X-06). The numbers disagree:
  - s80: Voynich K100 +0.045, interval excludes 0;
  - s87 (results_s87.txt, VOY rows): Voynich K100 +0.021 p 0.227 (ZL3b), +0.010 p 0.358 (RF1b);
  - roach r4: null at K=100.
  Yet roach r4 is filed as `agrees: true` on F-12, and s87's line-pool generator (+0.024) and s67 CA (+0.021) equal the
  manuscript at K100. So "no generator has its weak order" (F-40) is not supported at K=100 on s87's own rows.
- **Double sampling in fitted producers.** D-062 found that a line-scoped producer regenerated from observed quire
  vocabulary recovers a planted instance of itself on only 4/15 folds (FX1). I found no positive control (planted-truth
  recovery) in results_s67/s81/s91 (grep for control|power hits only imported file names). So every "fails LOQO 0/15"
  exclusion (F-23, F-30 against H-05, F-34 core side against H-14, F-41) has unknown power against the 8/15 bar.
- **Calibrated rather than fitted parameters.** s93's LP93 parameters are "calibrated ... keeps loc in [0.95, 0.985] and
  o100 in band" (s93 script line 161). If that band is the whole-manuscript target, the LOQO evaluation of F-41/ULP93 is
  in-sample (unverified which data set the calibration used).
- **Per-quire power.** F-21 is already CONTESTED on this. The same 15-quire, 8/15 rule underlies the producer exclusions
  above.

## 2. H-01 "against" links that an unusual script or orthography could also produce

| Link | Why a natural language in an unusual orthography might give it | Control that would test it |
|---|---|---|
| F-05 (s) CHARWIN > 0 | Abbreviation already moves Latin to -0.15/-0.18. A verbose orthography with a small closed set of word endings (sigla for -us/-orum, positional allographs) adds character-level predictability and shrinks word-list advantage | Latin and Italian encoded with heavy suspension, contraction and function-word sigla, plus positional allographs; Classical Tibetan (syllable slots); all scored by n5 CHARWIN under 3 alphabets |
| F-11 (m) slot frame carries line signatures | Any agglutinative or templatic orthography written syllable by syllable has a rigid slot grammar | SlotSegmenter fitted per text on Tibetan, Swahili and Turkish prose, and on syllable-spaced Latin, at Voynich's matched core inventory |
| F-12 (m) order below every matched language | Comparators are six narrative or verse European texts. List and recipe content orders weakly (Dispensarium +0.068); a morpheme- or syllable-level "core" may order differently from a word | s80 pipeline on recipe/antidotary texts with real lines, on syllable-spaced texts, and on stems cut to Voynich's core length |
| F-13 / F-40 (s) in-line reuse > chance | Every comparator writes whole words in an alphabet. Recipe lines repeat quantity sigla ("ʒ ii ... ʒ ii"), paradigms repeat a stem with changing endings, and written reduplication (Malay, Vietnamese, Tagalog) repeats adjacent words | R_within/R_cross/locality on: an antidotary with sigla kept; Donatus/declension drills; a reduplicating language with reduplicants as separate tokens; Tibetan |
| F-01 (s) line-start vocabulary | Record-per-line content (recipe steps, glossary lines) gives line-initial vocabulary without any procedure. Voynich lines are not alphabetical (F-28), but record-initial words ("Recipe", "Item", "Accipe") need no ordering | jsd_first on real-line recipe and glossary manuscripts. s89's T class has real OCR lines but was scored only for the core signature |
| F-04 (s) rhythm | Survives: abbreviated CREMMA real lines give Moran -0.017 | Keep. Re-check once on Tibetan and recipe real lines in the same run |

## 3. Hypotheses the evidence does not exclude (missing from H-01..H-15)

- **H-16 (proposed): a natural language in an invented verbose or positional orthography.** Plaintext is carried by
  orthographic rule, not by a key: syllable- or morpheme-spaced, with positional allographs and closed sigla. H-01 says
  "written plainly", while H-02 and H-03 are ciphers, so this falls between them. F-35 closes plain syllabary, abjad and
  root-pattern encodings on h2 and CHARWIN only. That closure is alphabet-bound (1b) and was never run on the line battery.
- **H-17: a notational or record system.** Pharmacy, recipe, accounting or astronomical records, one record per line,
  with quantity and unit sigla. This predicts in-line reuse of sigla, cross-line change, a line-held frame, and weak order.
- **H-18: a shorthand** (Tironian-type notae), where common words and endings collapse to signs. No shorthand corpus is
  held. A synthetic notae encoder of Latin is buildable.
- **H-19: a paradigm, drill or mnemonic text** (declension and conjugation drills, ars memoriae, name-permutation tables).
  Same core, varying affix within the line, new core on the next line: this is close to the F-40/F-41 signature.
- **H-20: an a priori or category language** (words composed from category + difference slots). Lingua Ignota and Lull
  were tested only in s90's limited form, and no generator with compositional slot words exists.
- H-06's "list-like content" overlaps H-17. H-17 is separable because it predicts in-line reuse, which F-40 counts
  against H-06.

## 4. Process risks

- **Same code path as "independent" confirmation.**
  - F-34's impl line reuses S81.encipher and S64.load_greshko, and F-24's impl line reuses our producers (both already
    marked unverified).
  - F-12's data, method and split lines all come from one script (s80). Its only outside line, roach r4, is null at K=100
    and is filed as agreeing.
  - F-40's non-Slot bands were built from the same data (D-063).
  - s80, s87 and s92 import the same scorers (`scoreboard/metrics_new.py`, `s56_core_repetition_lag.py`,
    `p4d1_core_order.py`; s80 and s92 headers). A bug there would replicate across "axes".
- **Not re-tested after the A14/X-06 flip (s80, 03:19).**
  - The s50/s72 L4 and L4w constructions were tuned to resolve an "h2/A14 conflict" (L-311), so their failures were judged
    partly against a target now known to be wrong.
  - H-03's "disfavoured as built" leans on those constructions.
  - D-047 (Phase 3 tie) and the P4-D1 exclusion reasoning predate the flip.
  - s83's "too much core order" (F-39) uses the same matched-K estimator, whose K100 value for Voynich itself is unstable
    across s80, s87 and r4.
  - F-26 and F-37 wait on P-28 (s96, running). The others have no pending run.
- **Selection after the fact.** Grille "weakened" variants, LP91 to LP93, and the cadence filter (s93 M4) were each added
  after seeing a failure. A pass at the end of that chain is a fitted pass, whatever the LOQO wrapper.

## 5. Red-team tests (do not duplicate P-26 s94 or P-28 s96)

| # | Test | Decision it changes | Cost |
|---|---|---|---|
| RT-1 | **Orthography gauntlet.** Encode Latin prose, Italian and a Latin antidotary under 4 deterministic orthographies: (a) syllable-spaced with Tibetan-style slot letters, (b) heavy suspension/contraction with function-word sigla, (c) positional allographs plus verbose digraphs, (d) (b)+(c). Add real Classical Tibetan (tsheg-split). Run the whole board on real or record lines: jsd_first, Moran, CHARWIN, h2 (3 alphabets), the SlotSegmenter battery (F-11/F-14/F-15 calls), s80 matched-K order, Rw1/Rc1/locality. Freeze stub; pass = reaches Voynich's band on ≥4 of the H-01 link statistics | If any orthography crosses CHARWIN > 0 or Rw1 > 1: downgrade F-05 and F-13/F-40 links to "against plain script only", add H-16, and reopen H-01 inside H-16. If none does: H-01's strong links gain a real orthography control, and F-05 can carry `matched: true` | 1.5 days build, < 2 CPU-h |
| RT-2 | **Record and drill genres on real lines.** (i) A recipe/antidotary transcription with sigla and numerals kept as tokens (diplomatic source; or Dispensarium with quantity tokens re-inserted from its own text, flagged synthetic); (ii) Donatus/declension drills; (iii) a reduplicating language with reduplicants as separate tokens; (iv) Swahili verse-lined (concord). Score the F-40 four-part signature, F-14 prefix memory with line reset, and F-01 | Any natural text passing F-40 C1 removes "no natural text reuses words in-line" (F-40, H-01 s; H-06 m). F-14's "only Rugg's grille shows it" changes if concord text shows it. H-17/H-19 enter the graph | 0.5 day sourcing, 1 CPU-h |
| RT-3 | **Matched-residue segmenter null (X-01).** Fit SlotSegmenter and Zattera on each natural text so that core inventory (700-4,000) and mean core length match Voynich; also run them on Voynich with glyphs shuffled within words (keeps lengths, kills position). Recompute the F-11 ablation share, F-14, F-15 and F-12 | If natural texts yield ~96 % affix-borne rhythm or one-back prefix memory: F-11/F-14/F-15 are segmenter properties and X-01 is re-flagged at-risk for them. H-14 and H-05 lose F-14(m). If not: X-01 is properly discharged for the slot findings | 1 day, 2-3 CPU-h |
| RT-4 | **Alphabet sweep of the h2 and CHARWIN exclusions.** Re-tokenise Voynich and every cipher or encoding output behind F-25, F-35, s82 and s83 under EVA, glyph+, GC2a, ch/sh-merged, aiin-merged and benched-gallows-merged. Report each gap per alphabet | If the h2 gap closes under any defensible alphabet, the H-02/H-03 "against" from F-25/F-35 go to "EVA-conditional", and the cipher arm (D-061) reopens. CHARWIN's sign under each alphabet settles F-05's robustness | 3-4 CPU-h, half a day |
| RT-5 | **Power of the LOQO 8/15 bar.** For each producer family behind an exclusion (weakened grille s71, sticky Naibbe s81, CA s67, ULP93 s93), generate a synthetic manuscript at fixed true parameters, then re-fit and score it on its own 15 folds with the identical pipeline. Report its own pass rate | If true producers recover < 8/15 (FX1 got 4/15), the exclusions in F-23, F-30, F-34 (core side) and F-41 become "no power", and H-05 and H-07 statuses revert from weakened/disfavoured to untested-at-power. If they recover ≥ 12/15, the exclusions gain a powered positive control (TRIANGULATION absence rule) | 1 day code, 3-4 GPU-h on the 5080 |
| RT-6 | **Estimator check on weak core order.** On Voynich, the 6 languages, s87's list texts and the 4 pool generators, compute K-matched order with plug-in, Miller-Madow, NSB and a unigram-matched permutation null (match K and the class-frequency entropy). Reconcile s80 (+0.045), s87 (+0.021, p 0.23) and r4 (null) | If Voynich K100 order is not separable from 0 or from G_linepool, then F-12 is restated as "order ≤ noise at K≥100", F-40's "no generator has its weak order" is withdrawn, and the F-12→H-01 (m) and F-39→H-02 (s*) links are reweighed | 0.5 day, 1-2 CPU-h |
| RT-7 | **Independence audit (process).** Parse each results header's "local import" list and tag every impl/seg/split line whose run shares a producer, scorer or loader module with the finding's primary line. Recompute grades with those lines demoted to the `data` weight | A grade drop on a ◆ finding triggers pivot-check. Expected movers: F-12, F-24, F-34, F-40 | 2-3 h |
| RT-8 | **Post-flip legacy sweep.** List every claim and decision computed before s80 (03:19) that used the full-inventory core statistic or tuned against it (P4-D1, s50/s72 L4/L4w, H-03 "as built", D-047), and re-score the cheap ones with RT-6's estimator | H-03 may move from "disfavoured as built" to "untested"; L4w gets rebuilt without the A14 target | 3-4 h |

Suggested order: RT-7 and RT-6 first (cheap, and they decide how much RT-3/RT-5 matter). Then RT-5 (GPU), then RT-2 and
RT-4. RT-1 is the largest, but it is the test that bears most directly on H-01.

## 6. What would refute this red-team

- If RT-1 and RT-2 show no orthography or genre reaching CHARWIN > 0 or Rw1 > 1 with cross-line avoidance, the H-01
  case is stronger than now, and H-16..H-20 can be filed as tested and disfavoured.
- If RT-5 shows true producers pass at ≥ 12/15, the LOQO exclusions are powered.
- If RT-6 shows Voynich K100 order robustly above every generator, F-40's generator half stands.
- I did not check: CHARWIN under other alphabets, beyond the grep in 1b; which data s93's calibration used; whether s92's
  "60 stem re-segmentations" matched core length; and whether s81/s91 carry a planted-recovery control in their scripts
  rather than their result files.
