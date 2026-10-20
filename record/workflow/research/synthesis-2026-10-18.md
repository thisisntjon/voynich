# Where the evidence points, taken as a whole (voynich-08, 2026-10-18 02:38 PDT)

> **Dated snapshot.** From 03:14 PDT the live answer to 'where it points' is `workflow/FINDINGS-MAP.md` §1, generated from
> `workflow/FINDINGS-GRAPH.yaml` (D-058). This file is kept as the record of the 02:38 reading.

Sources: workflow/CONSTRAINTS-MAP.md (A1–A21, dots 1–26), result files s1–s69, Argon's s51–s54, s60 and s63, roach r1/r2.
Claims stay in three classes:
- **Measured:** pre-registered, filed and verified.
- **Inference:** my reading across results. It is marked as an inference and names its refuter.
- **Decipherment:** none exists.

## 1. What the text is, measured

1. **Lines and words are real units of the manuscript.**
   - The line edge is marked (A1). The rhythm of word lengths within a line is real (A5).
   - Both survive with drawing gaps removed or split (s65). Both replicate on a second machine with fresh code (roach r1).
   - Ink gaps agree with the transcribers' spaces (A19, scoped to the s45 alignment).
2. **Words are assembled from parts.** Every word is a prefix, a core and a suffix (A13–A17).
   - The prefix and suffix depend strongly on the word's core. The core's class predicts the prefix by about 0.65 bits (s69).
   - Making affixes depend on the core fixes both the word-form count and the character-model sign (s67).
   - Words drawn whole give the wrong character-model sign (s57, s61). Freely assembled words are far too many (s58).
3. **The slot layer has a short, line-scoped memory.**
   - A word's prefix also depends on the previous word's prefix, and on almost nothing further back (s69).
   - That memory restarts at every line break, and gallows words weaken it.
   - None of our codes or generators has it. Rugg's table-and-grille has it, about five times too strongly.
4. **The cores have no syntax but do have local reuse.**
   - Different cores do not follow each other in an ordered way (A14).
   - The same core recurs at short range more than chance (s56). New forms are only weakly derived from nearby words (s62).
   - Many "rare cores" are one-glyph shifts of where the segmenter draws the boundary (A21). Rare-core figures therefore partly measure the segmenter.
5. **The A/B split is a split between hands.**
   - Currier A and B line up with Davis's hands (dot 12). Parisel's per-folio switch is the hand (s68).
   - Slot profiles are hand-associated and tell hands 2 and 3 apart on most held-out pages (A20). Hand was not separated from section or quire.
6. **Vocabularies are local.** Each quire uses a narrower set of words than any global-lexicon model produces (s67). Quire M is the extreme case.

## 2. What the evidence weighs against, measured

| Family | Result | Strength |
|---|---|---|
| Plain natural language | repetition runs opposite to every language tested (s56); no core syntax (A14) | strong |
| Letter cipher with letters in the cores | 12/12 planted ciphers show core order; Voynich does not (P4-D1, s43) | strong |
| Verbose-homophonic cipher, letters in the affixes, filler cores | the solver reads it at every rung, but no member of the family matches the manuscript on h2, core order and rhythm at once (s50) | evidence, not proof (Q3, D-057) |
| Naibbe (per-word random table) | prefix stream orderless against Voynich's ordered one (s64) | strong at default settings; per-line table untested |
| Musical overlay, superimposed streams | s24, s34, s51 | tested negative |
| Liturgy, charms, copied without understanding, conlangs | s37 | tested negative |
| Antidotary, alphabetical or zodiac ordering | s52 | null with powered controls |
| Internal crib from plant labels | images match, labels do not (s48, s53, s54; D-053) | route closed |
| Local-memory, slot-wrapper, whole-word and assembly producers | 0–2 of 6 on held-out pages or quires (s57, s58, s61, s67) | four designs fail |

## 3. Where it points (inference; each line names what would refute it)

- **A word-level procedure, not a letter-level one.** Each word is chosen as core plus a hand-specific frame. The frame depends on the core and on the previous word's frame, and it restarts per line.
  - Refuter: a letter-level cipher of any known language that reproduces s69's one-word, line-reset prefix memory together with A14. None of the 12 planted letter ciphers or the s50 family does.
- **The nearest known mechanism is a table read in sequence** (Rugg-style grille or table), with less dependence than Rugg's version. It is the only reference class with an ordered prefix stream.
  - Refuter: a table producer, fitted quire by quire, that still fails the held-out prediction set.
- **Meaning is not decided.**
  - Cores behave like vocabulary: local reuse, quire-local sets, no syntax. That fits content words in a list-like or labelling text, and it also fits a generator drawing from page pools.
  - Our statistics cannot separate these two once a shared slot layer is present (L-130, s55).
  - Deciding it needs an anchor. There is no internal one (D-053), and no external crib is in hand.
- **Not "solved", and not "a hoax proven".** No reading exists. The tested cipher families are disfavoured, not excluded in general.

## 4. Where the project stands against its tiers

- **Tier 1 (reading):** not reached. Solver power is shown on planted ciphers only, and the manuscript was not run (no matched L4).
- **Tier 2 (family decided by a pre-registered margin):** reached for some families.
  - Disfavoured: the verbose-homophonic family as built (s50).
  - Excluded: the per-word random-table family at default settings (s64).
  - Excluded on held-out prediction: the lexical producer designs (s57–s67).
- **Tier 3 (hard constraints):** A1–A21 plus dots 1–26.
  - New tonight: the line-scoped prefix memory (s69), core-dependent affixes (s67), and solver-versus-construction (s50).

## 5. What would move it next (ranked; detail for the phase-5 gate)

1. **The table-and-grille family, tested on held-out quires.** It is the one mechanism the measured slot memory points to. One frozen design, a stated table size, prefix memory as a target, and leave-one-quire-out scoring. It would be the fifth producer, under D-056.
2. **Boundary-aware segmentation.** Re-score the rare-core and slot results (s56, s62, s69 and A21) under a second, independent segmenter. This tests whether the picture depends on our segmenter (A21 caveat). Roach's r3 already uses its own segmenter for three claims.
3. **Meaning-side tests that need no anchor.**
   - Whether core sets track illustration type within a hand.
   - Whether quire-local vocabularies nest the way topical vocabularies do, compared with page-pool generators.
   - Argon's s66 covers quire turnover.
4. **Lower value now:** the s50 follow-ups (language identification; a wider L4 construction). The construction conflict, not solver power, is the finding.

## Update 2026-10-18 02:58 (s76): A14 at risk
Under Zattera's segmenter, core->core order is positive (+0.074..+0.079). A14 may be an artifact of SlotSegmenter's
~2,400 sparse core types. Until s80 (A14 at matched inventory size, Voynich vs P4-D1 ciphers vs language) reports, read
§1.4's "no syntax", §2's letter-in-core row and the s50 h2/A14 conflict as provisional.
