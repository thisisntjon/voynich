# Phase 4 investigation — routes to a reading (Tier 1)

Main session, 2026-10-17 22:25 PDT (clock read). Jon asked for this at 22:12 ("investigate leads on how we can solve"). Five agents ran read-only; no board or entrant script was run. Every number below comes from an **exploratory scratchpad check** (not pre-registered, ZL3b unless stated) or from a cited source. The detail, the URLs and the unverified marks are in the five topic files:

| Angle | File | Verdict |
|---|---|---|
| Decipherability / solvers | [phase-4-decipherability.md](phase-4-decipherability.md) | **CONDITIONAL**: the information is there; no solver has been shown to work at our segmentation uncertainty |
| Internal anchors (labels, plants) | [phase-4-internal-anchors.md](phase-4-internal-anchors.md) | One live lead: same-plant pairs (P≈0.05, needs 1–2 h of human freezing) |
| Comparators / source text | [phase-4-comparators.md](phase-4-comparators.md) | No transcribed comparator is ready to serve as a crib; the recipe quire looks like an antidotary (name-headed entries) |
| Units (EVA, spaces, ink) | [phase-4-units.md](phase-4-units.md) | EVA is not hiding a reading; spaces are the only lever; the s30 lift-split swing is a regex artefact |
| Scribal errors / corrections | [phase-4-scribal-errors.md](phase-4-scribal-errors.md) | Sight errors cannot give content evidence; physical corrections coded by a human are the only upside |

## What the investigation changed

1. **A possible load-bearing constraint (unverified; check first).** A cipher whose cores carry plaintext letters in reading order scores **+0.30 to +0.52** core→core MI excess over a within-line shuffle in planted tests, and Naibbe-like tokens score +0.09. Voynich cores sit at **−0.03** (CONSTRAINTS-MAP A14). The agent's statistic is not A14's exact code. If the gap holds under A14's own code, **cores cannot carry letters in reading order**, and the letter-order noisy-channel search (t1) is aimed at the wrong stream. The remaining cipher space would then be: plaintext in the affix stream, cores as nulls (s43 tests the twin), or a reordering cipher. s34's residual result (0/1022 glyph-class partitions leave a language-like residual, against 345/1022 planted) points the same way.
2. **The key is over-determined, if it is a letter-level verbose homophonic.** Unicity needs about 180–1,250 plaintext letters; we have ~53k (40–300×). A 7k-type word code stays undetermined (about 23k words needed against 35k tokens). Every real blind solve found (Copiale, Mary Stuart, papal ciphers, Z340, Kambhatla 2023) had known units, recoverable boundaries and a narrow language prior. None had unknown segmentation (search not exhaustive).
3. **Solver feasibility is unproven even with segmentation given.** A crude SA on a planted 38k cipher reaches 75% letter accuracy, and the trigram objective prefers a wrong key. Adding 15% nulls drops it to 37%. The positive-control ladder has to come before any Voynich run, and it runs on CPU, so t1's GPU gate is no longer needed.
4. **Anchor leads are few and need people.** The only internal route that predicts untouched material is same-plant pairs: a pharma label names its herbal partner page, then that is used to predict partners for unmatched pharma plants under blind human judging. The recipe quire is an antidotary-shaped list (285 paragraphs, 241 distinct first words, max share 3%), so an entry-by-entry alignment needs a Latin Antidotarium text (library). Zodiac monomoiria is contradicted (299 labels, 264 types). Fontana's decoded captions are a usable solver positive control, not a mechanism.
5. **Closed or deprioritised:** dittography (in-line repeats match shuffle; the line-turn test cannot detect copying even in real CREMMA copies), eye-skip (no repeated 5–6-word sequences to compare), numerals and degree numbering (s29 null), duplicated-illustration labels (null), label-in-own-page (d6 null), ink-level units at local resolution (lift tier 0.4–1.4 px, inferred), and Davis scribes as a new unit (already `$H`; hand and language are confounded).
6. **s44 (voynich-08, 22:23)** answers the red-team U1 attack: at 773 lines A is +0.135 and B +0.218, both far above all Latin prose. A overlaps only one short verse hand.

## Proposed Phase 4 plan (for the gate)

Re-scoped intent: **decide whether Tier 1 is reachable at all, cheapest decisive test first**, rather than running a key search conditional on a Phase 3 cipher win. Phase 3 ended in a tie (results_s35.txt), so the old trigger never fires.

CPU track. One pre-registered stub per step. Each step's outcome gates the next.

| Step | Test | Decides | Cost |
|---|---|---|---|
| P4-D1 | A14's exact core→core statistic on planted letter-carrying ciphers (6 languages), Naibbe, the s10 twin, and Voynich (all/A/B) | Whether "cores do not carry letters in reading order" becomes a constraint. If yes, the solver target moves to the affix stream or reordering ciphers | ≈1 h |
| P4-D2 | Solver ladder L1–L4 (SA/MCMC homophonic, 5-gram LM, null flags, segmentation search). L4 = a planted cipher matched to Voynich on types, hapax, h2 and A14, with segmentation unknown. Fontana captions as a real-world control | **If L4 fails in all six languages, the computational Tier-1 route closes, and that is written down** | ≈0.5–1 day |
| P4-D3 | Blind identifiability study: 30 texts, 6 per class, 38k tokens, board metrics plus A5/A6/A7/A14, leave-one-out nearest-centroid. Pass is ≥20/24 cipher-vs-generator and ≥9/10 on twins | Whether any Tier-2 verdict means anything; ≤16/24 withdraws them (red-team item) | ≈0.5 day |
| P4-U1 | Space regimes: does the comma rate climb toward line end, and do `A,B` pairs also appear elsewhere as `AB`? | Which spacing is right; the only unit lever that moves word metrics | ≈1 h |
| P4-COMP-1 | Recipe incipit repetition and alphabetical-run test, plus zodiac period-7 and same-position stem tests, each checked first on a planted antidotary or planet ring | Whether the recipe quire is an ordered antidotary, which would set up a later alignment | ≈2 h |

Human-input track (Jon only; these are the only routes to an anchor this pipeline cannot produce):
- (a) Freeze the same-plant pairs (ZL's 14 "Same plant as" notes plus Stolfi's 7) and mark which label sits on which plant on the scans: 1–2 h. This unlocks anchor test P4-A1 and then the partner-prediction test P4-A2.
- (b) Code the 21 ZL-flagged corrections and erasures from the scans: before and after glyphs, about 5 min each.
- (c) HathiTrust `hvd.hxub2m` (Meister 1902, pp.30–31) and the open-access Greshko paper, both in a US browser.
- (d) Optionally, a Latin Antidotarium Nicolai text via library or scan, for the alignment.

Not proposed: P4-U2 alphabet bake-off (expected null; run only if P4-U1 moves something), the 30-folio ink pilot (only if P4-U1 is inconclusive; ~120 MB download needs approval), any GPU work.

**Stop rule (proposed).** If P4-D1 confirms the core constraint, L4 fails in all six languages, and P4-A1 is null (or unavailable), write up "Tier 1 is not reachable by computation from this transcription". After that the project is model selection plus human-input archival work.

**Overlap with running work.** voynich-08's s39 (F1/CHARWIN per stream), s41 (suffix→prefix coupling) and s43 (cores-as-nulls twins) are adjacent to P4-D1. P4-D1 should reuse s39/s43 outputs and not duplicate them; the comparison is on planted ciphers, which those tests do not include.

## Results (Phase 4 execution, main session)

**P4-D1** (`p4d1_core_order.py`, stub `p4d1_core_order.prereg.sha256`, result `results_p4d1_core_order.txt`; run 1 crashed and is kept as `results_p4d1_core_order.run1-crashed.txt`, with AMENDMENT 1 in the docstring). **Verdict by the pre-registered rule: MIXED.** 17 of 18 cells are CLEAR and 1 REACHES Voynich.
- The instrument reproduces s34 exactly: ZL3b ALL −0.0315. Voynich ranges from −0.024 to −0.090 over 3 transliterations × ALL/A/B (V_max −0.0244).
- **Letter-in-core (K1)** and **chunk-in-core (K3, Naibbe-like units)** are CLEAR in all 12 cells: +0.061 to +0.154 after re-segmentation, and oracle +0.32 to +0.59.
- **Word-in-core (K2)** ranges from −0.018 to +0.037. Dante reaches Voynich (−0.018), Faust is −0.004, and Caesar is only +0.006.
- Null cores (K0) give +0.001 and transposed letters (K4) −0.008 to +0.003. Voynich sits below both.
- What the evidence supports, as description beyond the verdict:
  - With plaintext-independent affixes, cores that carry letters or 1–2-letter chunks in reading order do not produce A14, in any of 6 texts × 4 languages.
  - Cores that behave like *word codes* can. Natural word order avoids repeating the same word adjacently, and the within-line shuffle breaks that avoidance.
  - Voynich's negative excess therefore looks lexical, not alphabetic.
- Not tested: affixes that carry plaintext, and whole-word homophony in which prefix and suffix are part of the code.

**P4-U1** (`p4u1_space_regimes.py`, stub and result `results_p4u1_space_regimes.txt`). **Verdict (ZL3b): BOTH**, and RF1b agrees. IT2a marks no uncertain spaces at all, so it gives UNDECIDED; the design did not anticipate this.
- P1: commas rise over the last quarter of the line, D +0.040 (null q99 +0.009, p 0.0005), with stratified D +0.043. So some commas are squeezed real spaces.
- P2: the joined form `AB` exists as a standalone token for 42% of comma pairs against 25% for length-matched dot pairs (R 1.66, dR CI [+0.148, +0.185]). Both parts standalone: 0.82 vs 0.99. So many commas are junctures.
- **Pre-registered reading: the comma class is a mixture.** Neither "merge all" nor "split all" is right. Deciding boundaries one by one needs evidence other than the transcription, so the gap-only ink pilot (§2 of phase-4-units.md) is no longer optional if spacing matters. It still needs the ~120 MB download approval.

**Effect on the plan.**
- P4-D2's planted L4 target must not be letter-in-core with free affixes, because that family is excluded by A14 on 12/12 cells.
- A solver ladder now has to model either (a) plaintext in the affix stream or in whole words, or (b) a word-level code. (b) is period-implausible at 7k types and undetermined by unicity (phase-4-decipherability.md).
- This is a re-scope of D2, so it goes back to Jon before D2 is built.
