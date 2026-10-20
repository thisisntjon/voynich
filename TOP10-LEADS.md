> **Historical (superseded 2026-10-17 23:33).** Current state: `README.md` → `workflow/FINDINGS-REPORT.md`. Findings from this file are in `.inventory/registers/`.

# Top 10 leads (agent-executable only) — ranked by decision value per token

Compiled 2026-10-17 evening from LEADS-AND-FINDINGS, C/E/F/G/K/N/O rounds,
J-series, REGISTER-DIFF, BREWER-LEWIS-CHECK, SCOUT-EXTERNAL.
Constraint honoured: NO human-assigned work. Every item is runnable by an
agent in this folder/env today. Status remains: not deciphered.

1. **Joint producer bake-off v2 (habit + section pools + line rules + edge).**
   Why: N1/N2 habit fakes residual (p=0.04), N3b sheet habit reproduces
   sheet cohesion (A on 3/3 transcriptions), G1 edge filter works held-out,
   C2 section pools reach NMI — but never in one run under one parameter
   count. One combined generator scored on frozen board either joint-passes
   (generation Tier-2) or its residual gaps become the sharpest constraint.
   Cheapest decisive experiment left in statistics.

2. **Power repair for section vocabulary (N3b Q1 = C).**
   Why: N3b positive control itself failed held-out null (median p=0.82) —
   the test cannot see its own effect. Larger strata / pooled sections /
   token-level (not NMI) statistic with demonstrated power on HT_sec first.
   Without it, "content vocabulary exists" is undecidable, and K-family
   claims float. Gate: control passes before manuscript is scored.

3. **Lossy-code period attestation via open corpora.**
   Why: K4 mechanism (many-to-one shared codewords) has zero period
   attestation; register steal #1 (1477 quid-pro-quo substitution table)
   + Cappelli abbreviation corpus + Brewer 2022 CEUR talk (open access,
   agent-fetchable) can confirm/refute period plausibility and supply
   control material. Moves family weights more than another K sweep.

4. **Hapax/type-budget mechanism hunt.**
   Why: every producer fails hapax (0.31 vs 0.68) or types (15–25k vs
   7,025) — the single most consistent quantitative miss (K2/K4/C2).
   Test inventory-capped generators (fixed 7k-type pool with Zipf draw +
   mutation-for-novelty budget) for whether hapax 0.68 is reachable
   without wrecking h2/NMI. Identifies what kind of novelty process ran.

5. **Author-order (singulion) sensitivity re-run of sequence statistics.**
   Why: Layfield & Davis order is hypothesized, M2 already flips findings
   across transcriptions; Heaps, drift, topic, F1-residual all assume
   current binding. Re-score headline sequence metrics under singulion
   order vs bound order vs shuffled-order null. Cheap (existing scripts,
   permuted page order), protects every sequence claim on file.

6. **Direct-ink resegmentation at scale (O1 follow-through).**
   Why: O1 proved boxes misrepresent ink (corr +0.194) and ./, hierarchy
   is real in ink (4.79 vs 3.14 px). E1 resegmentation was inconclusive
   partly on box geometry. Re-derive uncertain-space joins from direct
   ink on the 6 QC folios, then re-run E1/A6c checks there. Only lead
   that improves the *data* every other test consumes.

7. **Context-only homophone recovery, round 2 (no spelling features).**
   Why: J1v2 passed its gate only via spelling (circular on I1 controls);
   J3 collapse then failed. Open question with a clean gate: can wider
   context (±2, line-position, section) reach m=3 ARI ≥0.15 without
   spelling? Pass revives key path honestly; fail retires homophone
   recovery at this corpus size for good. Bounded configs, pre-registered.

8. **Register steal verification: quid-pro-quo + Cappelli controls.**
   Why: REGISTER-DIFF steal items are unverified titles. Fetch primaries
   (1477 incunabulum records, Cappelli abbreviation lists — open web),
   build two small control corpora in data/external/, score on board.
   Converts external claims into team-owned controls for K-family tests.

9. **Label-referent test v2 with location codes + image classes.**
   Why: a3/D6 own-page tests are underpowered/null; register + IVTFF
   location codes separate label registers cleanly. Test label↔image-class
   (plant-part/jar/star) association instead of label↔page-text: the last
   plausible crib surface. Null here at adequate power closes cribs.

10. **Second-transliteration full-board robustness (RF1b/IT2a already local).**
    Why: M2 showed winner-flips; N-series already runs 3 transcriptions —
    extend frozen scoreboard entrants to all three and publish a
    robustness matrix. Lowest discovery value, highest credibility value:
    determines which headline numbers may leave this folder.

Explicitly excluded (human work, per instruction): library/paywall access,
forum registration, expert elicitation, facsimile handling. Excluded as
closed: language solvers as filed, slot induction variants, topic models,
f57v periods, lone-rambler tests, J3-style class collapse.

## Status updates (this session)

- #5 DONE (`p1_order_sensitivity.py`): Heaps β order-fragile (bound 0.716
  inside quire-permuted 0.679–0.835); rare-word locality quire-robust.
  Note: builder's `results_p1_order.txt` is a separate artifact.
- #7 DONE, GATE FAILED (`j4_context_only.py`): wider context hurts;
  best context-only m=3 ARI 0.044 vs 0.15 bar. Homophone recovery retired.
- #8 SCOPED (`STEAL-VERIFY.md`): Cappelli scan confirmed available;
  quid-pro-quo genre verified free-text; 1477 item unverified (self-cited).
- #9 DONE (`q1_label_crib.py`, `Q_RESULTS.md`): label vocabularies are
  image-class-specific (z=+5.2 within-illus) but zodiac positional crib
  is null; label surface exhausted at current power.
- #10 DONE (`p2_robustness.py`): EVA-family transcriptions agree tightly
  (h2 2.126–2.137); GC alphabet diverges as expected.
- #1–#4, #6: builder-owned / in flight (K/N/M/O rounds). Not duplicated.
