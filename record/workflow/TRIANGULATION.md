# Triangulation: how a result enters the findings map (D-058)

Adopted 2026-10-18 03:12 PDT (clock read with `date`). This applies to every agent filing a result: voynich-08, Argon, roach, Daybreak.

## Where things live (one home each)

| What | Canonical home | Never put it in |
|---|---|---|
| A number | `.inventory/registers/CLAIMS.md` (c-id) | prose docs, except by citing the id |
| What a finding is, its evidence lines, what it rests on, where it points | `workflow/FINDINGS-GRAPH.yaml` (F-, H-, X-, P- ids) | new summary files |
| The narrative of a constraint | `workflow/CONSTRAINTS-MAP.md` (A-rows, dots) | — |
| The generated view of all relationships | `workflow/FINDINGS-MAP.md` | hand edits (it is regenerated) |
| What we learned, including failures | `.inventory/registers/LEARNINGS.md` | — |
| Decisions and kills | `.inventory/registers/DECISIONS.md` | — |
| The plan and the assumption registry | `workflow/PLAN.md` | — |

A new synthesis, status or summary file is sprawl. Update the graph and regenerate the map instead.

## The filing procedure (every result, every agent)

1. **Gate the result.**
   - The pre-registration stub must verify: `grep -v "^#" STUB | tr -d '\r' | sha256sum -c -`.
   - The verdict must follow from the pre-registered rule as written. Verdict prose that contradicts its own numbers is overridden by the numbers.
   - Read the printed outcome of each pre-registered call (`... = True/False`) and file that, not the summary prose. A call printed False cannot discharge an assumption (D-063). A threshold not written before the run gives a descriptive result only.
   - A stub that fails, or a script modified after its run, means the result enters the graph only as `unverified: true` lines, which count for nothing until the run is re-frozen.
2. **Register the number.** Add a CLAIMS row (c-id) for each headline number.
3. **Place it in the graph.** For each finding the result bears on:
   - If it measures the same property in a new way, add an evidence line `{axis, by, ref, claim, agrees}`. Choose the axis honestly: same code on another transliteration is `data`, not `impl`. A run that imports our producers, encoders or loaders is not `impl` either, whoever ran it; `impl` means code written independently (roach).
   - If it disagrees, set `agrees: false`. The finding becomes CONTESTED until a later line records `resolved:`.
   - If it tests an assumption the finding rests on (a second segmenter, leave-one-quire-out, ink instead of transcription), add `discharges: [X-..]` to that line.
   - If it is a new property, add a new F entry with `rests_on` and `points` (for / against / excludes, strength, why).
   - If it changes a hypothesis, assumption or pending test, update H, X or P.
4. **Run the gate.** Run `python tools/findings_graph.py render`. It must exit 0. Then look at the sections that changed:
   - §1 scoreboard: did the ranking move?
   - §2 grades: did anything become CONTESTED?
   - §5 gaps: which finding now needs a new axis?
5. **Act on what moved.**
   - **A load-bearing (◆) finding goes CONTESTED, or an assumption becomes `flipped`.** Stop and run `pivot-check.md` (PLAN rule 3) before any other work. Every finding resting on it is listed in §3.
   - **A hypothesis's net weight changes sign.** Record a D- row and revise `workflow/PLAN.md`'s next steps.
   - **A gap in §5 shows `none: design one`.** The next experiment chosen should close the cheapest missing independent axis of the highest-weight finding. A roach blind replication supplies `impl`; scan measurements supply `physical`; Zattera or LOQO supply `seg` and `split`; s79's transforms supply `order`.
6. **Check sprawl at every filing point.** Run `python tools/findings_graph.py sprawl`, then fix anything new:
   - a result file referenced nowhere: file it or tombstone it;
   - a root `.md` not declared under `docs:` in the graph: declare it, or archive it via curate;
   - an unlinked recent claim: link it to a finding, or note why it stands alone.

## Grades

| Grade | Meaning | Counts in the scoreboard as |
|---|---|---|
| TRIANGULATED | agreeing lines on ≥3 axes, at least one leaving our own pipeline (`impl`, `physical` or `external`) | 1.0 |
| CORROBORATED | agreeing lines on ≥2 axes | 0.67 |
| SINGLE | 1 axis | 0.34 |
| CONTESTED | a disagreeing line not yet resolved | 0 |

- **At-risk assumptions.** A finding resting on an at-risk assumption that no line has discharged is weighted half.
- **Absence findings.** A finding that says something does not happen (`kind: absence`) must carry a powered positive control at matched conditions. This rule exists because A14 had no such control and was then put at risk (s76).

## Why this design

- **Agreement across independent routes.** A finding is believed in proportion to how many independent routes reached it. Re-running our own code on another transliteration is the weakest route, because the three transliterations share scans and glyph set.
- **Visible chains.** Every conclusion names its assumptions, so when one falls, everything resting on it is listed (§3) instead of rediscovered.
- **The next test is chosen by the map.** §5 gives the cheapest missing independent axis of the most load-bearing findings.

## Replication by default (Phase 7, 2026-10-18 13:07)

A result may change a hypothesis's weight or a finding's grade only after either an independent implementation (roach, written without this tree's code) reproduces it, or the lead audit passes (stub verified, creation time before results, printed calls filed as printed, thresholds unchanged). Until then its evidence lines carry `unverified: true`.

## Exclusions need power (D-068, 2026-10-18 15:43)

A result that excludes a producer or mechanism ("fails the bar on Voynich") counts as evidence only if the same pipeline and criterion pass a planted true instance of that producer on >= 10/15 held-out folds. Below that the exclusion is filed as UNINFORMATIVE and its line carries `unverified: true`. s101 (c-454) showed F-23 and F-30 exclusions at 0-4/15.
