Sun Oct 18 20:53:58 PDT 2026 (read from `date`)

# Big picture: the production mechanism

Sources: FINDINGS-MAP (20:45 render), FINDINGS-GRAPH H nodes, D-066 (a)-(u), LEARNINGS L-204..L-330, VKB corpus_stats, results_s90/s107 (Llull check). This is a reading of filed evidence; it runs nothing and moves nothing on the scoreboard.

## 1. What the evidence says

**The line is the unit of composition.** Lines are physical units (F-01; X-03 ink-verified). The length rhythm stops at line breaks (F-04); roach r12 replicates it blind and Kalevala shows it more strongly (L-226): a metre-like rule per line. Prefix memory restarts at each line (F-14).

**Inside a line, cores come from a small pool.** In-line core reuse is Rw1 1.18-1.22 across the three transliterations (VKB, s87), with avoidance across line breaks of 0.26-0.86 (F-40). No natural text does this (34+ texts incl. lists, litanies, abjads, L-222; Tacuinum and De gradibus, F-49), nor human gibberish (s90). A per-line pool reproduces it with copy parameter 0 (F-41); roach r10 fits copy rate 0.02 (L-218). A draw from a line set, not reduplication or self-citation.

**Words are slot-built and letters are very predictable.** Prefix + core + suffix (F-11), chosen jointly (F-15). h2 2.12-2.13 (s102), z -4 to -8 against every corpus (L-321). Prefixes are near first-order (F-46); a line-held table overshoots lag-2 about 3x, and affixes are shared across adjacent lines (r6, L-212).

**Core order is weak**, between language and generator (F-12), and the generators get no closer to it than ciphers do (F-40, F-25).

**Vocabulary is local, and settings drift by batch.** Quires are narrower than any global lexicon (F-17); uncommon cores come from an order-symmetric quire pool (F-42); drift follows bound order within quires (F-32); affix/length features drift by quire beyond hand x section, p 0.0001 on all three transliterations (F-50, c-558). s111's subject arm was null (L-318).

**One system across scribes.** Currier A/B is scribes, not languages (F-16); one slot system in every hand; errors look like composition (F-21, SINGLE).

**Failing as built:** H-01 (net -17.5), H-02, H-03, H-04 (F-24!), period ciphers over recipes 0/12 (F-45), spec-built table encodings 0/18 with shuffled input fitting rhythm better (F-47), fixed/line-held/drifting affix tables (F-46, F-48), hard-way orthographies H-17 (s97).

**Mechanism stated as a description.** A writer, or five, works line by line:
1. Pick a small core set for the line from a quire-local stock.
2. Build each word with a slot grammar, with the prefix steered by the previous prefix.
3. Fill the line to a metre-like length pattern.
4. Retune affix habits between batches (quires).

Well supported; silent on whether step 1 encodes meaning.

## 2. Where it is tied

The evidence settles assembly, not meaning. The live split is **H-05 / H-19 (meaningless procedure from a table or row) vs H-06 / H-16 / H-18 (each line is a content unit, such as an entry whose cores name one thing's attributes or category).** H-07 survives only as "pool without copying" (the F-41 pool).

- **Scoreboard:** H-05 +4.0 / 0.0, H-06 2.0 / 3.7, H-07 2.0 / 7.0, H-14 2.0 / 5.3. H-16, H-18 and H-19 are all 0 / 0. H-05's lead is moderate links on at-risk findings (F-14, F-40*, F-46*) plus weak links; its strong counter (F-30) is CONTESTED and weighed 0.
- **Both-sides evidence:** F-17, F-50 (content shift or batch retune), F-42 (register or pool), F-12 (list content or cursor).
- **H-18 (category conlang) is untested.** Yet it predicts F-40: words of one philosophical-language entry share category radicals, so if the segmenter calls the radical the core, in-line reuse and cross-line avoidance follow, and a compositional script gives low h2. No such text has been scored. **H-16 (notation)** has only a constructed sigla control (s97), and no real shorthand.
- **Every meaning-vs-meaningless test so far is uninformative:** X2 (stars positional, s106), s103 INCONCLUSIVE, s105 HOLD, s111 batch arm HOLD, and the image nulls (A0: true caption link r 0.09, found ~40% at N 119, L-330).

## 3. Fragile load-bearing findings

1. **X-01 (SlotSegmenter units) is at risk under 20 findings, and P-28/s96, the test meant to discharge it, was rejected (D-065, L-205).** In-line reuse depends on the core definition:
   - roach r7: 4/15 blocks under an MDL core definition (L-213).
   - roach r11: Voynich itself passes on 6/15 blocks under S1, and on 0 and 2 under S0 and S2 (L-222).
   - z +2 (slot estimator) vs z +21 (word estimator) (L-321); the most physical stream fails 2 of 3 segmenter cells.

   F-40 holds only as a whole-text, reference-class claim.
2. **The h2 anomaly depends on the alphabet.** F-08 says entropy and type counts *are* alphabet artefacts, yet L-321 makes low h2 a signature anomaly. Every h2 uses EVA units, and scan glyph counts match EVA only 0.337 exactly (L-325). Re-score h2 on another inventory (ligature-merged ch/sh/cth) before s113 judges on it (D-066 r).
3. **H-19 rests on one 957-token OCR table** (s107, Llull Tabula generalis 1515). The Llull table already on disk is negative: Ars brevis Fig. 4 rows give Rw1 0.000 (p 1.0) on words, 0.628 on stems (results_s90.txt:152, 183). FINDINGS-GRAPH does not mention it (grep checked); H-19's status should cite it.
4. **F-50 is SINGLE, same-tree, and rests on unverified Davis hands (X-08).**
   Its frozen Test-A set includes n_tokens, n_lines and Rw1 (affix-only is descriptive, L-327); an unrecognised scribe per quire would give the same result; the transliterations share scans. roach r15 is the gate.
5. **LOQO exclusions are void:** F-23 and F-30 are CONTESTED by s101/r13 (L-224, L-319; true producers recovered 0-4/15). H-05's status line "fails LOQO 0/15" is not evidence.
6. **F-14/F-46 magnitude depends on the prefix boundary** (Zattera: a sixth); the H-05 link rests on a sign, not a size.
7. **s111's subject null** was powered before A0 set real links at r 0.09 (unverified at that scale); it should not yet count against H-06.

## 4. Ranked leads

**1. Line-set structure test (the single most decisive test not run).**
- *Evidence:* in-line reuse is a draw from a per-line set (F-40, F-41), but nobody has asked *what the line sets are* (no co-occurrence test found by grep of results and registers).
- *Test:* order-free and held out by bifolio.
  1. Count within-line co-occurrence of distinct core pairs against a quire-conditioned exchangeable null (the F-41 pool: lines resampled within quire, with line lengths and per-line repeat counts kept).
  2. If pairs exceed the null, classify the structure. *Table/row* (H-05/H-19): a small finite set of recurring tuples, a low-dimensional lattice embedding, and rows reused across quires and hands. *Content* (H-06/H-16/H-18): graded clusters that follow A1 image categories and section, with no exact recurrence of tuples. *Pool* (H-07-weak): no excess.
  3. Fixture first, on three planted books (grille-on-table, topic model, F-41 pool). Each must be recovered on 8/10 or more before real data. Run on SlotSegmenter cores, whole words and glyph 3-grams.
- *Refuted if:* pair lift stays at the null in all representations. The mechanism is then just a pool, and H-05, H-06 and H-18 lose their distinctive predictions about lines.
- *Cost:* low (1 worker, hours, data on disk).
- *Splits:* H-05/H-19 vs H-06/H-16/H-18 vs H-07: the only lead that moves the central tie either way, powered by ~3,184 lines, not ~119 pages.

**2. H-18 / H-16 positive control.**
- *Test:* score a category-language text through the F-40 signature, h2 and rhythm, using s97 code. Candidates: Wilkins's Real Character or Dalgarno transcriptions, or a Latin herbal re-encoded with a radical-per-category scheme fixed a priori. Add one real shorthand or abbreviation text for H-16.
- *Refuted if:* in-line reuse stays below 1 with its cross-line avoidance.
- *Cost:* low once sourced (anachronism is fine for a structural control).
- *Splits:* H-18 from H-05. This is also the cheapest way to give H-18 a falsifiable prediction (its status asks for one).

**3. s115-A2 at A0-calibrated power.**
- *Test:* do label and body cores predict the frozen A1 categories on held-out bifolios, with page, hand, quire and position controls?
- *Refuted:* only a positive result is informative. At 40-74% power, a null cannot refute H-06.
- *Cost:* medium. It is gated on A1b kappa.
- *Splits:* content (H-06/H-16/H-18) from meaningless procedure (H-05/H-07/H-19). A pass would be the first crib and would open the decoding path (D-066 g).

**4. A segmenter-free, alphabet-varied signature by roach.**
- *Test:* roach, blind, measures Rw1, cross-line avoidance and h2 on raw words and glyph n-grams under two glyph inventories (EVA and ligature-merged), with in-line reuse taken against the within-page expectation (L-228).
- *Refuted if:* in-line reuse or low h2 vanishes outside SlotSegmenter/EVA; then F-40 and G2's criteria need restating.
- *Cost:* low.
- *Splits:* none directly; decides whether X-01 and h2 can bear the leads above.

**5. F-50 under independent hands.**
- *Test:* r15 (running), plus a re-run with the hands derived from scan shape (L-325), or within single scribes.
- *Refuted if:* the drift collapses within verified scribes. That would make it scribe habit, not batch retuning.
- *Cost:* low.
- *Splits:* weakly H-05 batch vs H-06 content; mainly protects G2's drift premise.
