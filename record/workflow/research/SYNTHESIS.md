# Investigation synthesis — "top 10 leads" (stamped 2026-10-17 19:33 PDT from `date`)

> Superseded 2026-10-18 16:02 PDT: phase-0 investigation synthesis (historical; FINDINGS-GRAPH.yaml docs). It was adopted as the sequence on 2026-10-17 19:36 (TEAM-HANDOFF); that sequence is finished. The current queue is D-066 and workflow/PLAN.md `Current stage:`; status is FINDINGS-MAP section 1 / D-068.

Inputs: A-lead-harvest.md (34 leads), B-prior-art.md (7 literature items), C-constraints.md (power
curves, floors, multiplicity), D-stress-test.md (attack), E-dependencies.md (graph, wave plan, prefixes
s1–s16/t1), prereg-v2-freeze.md (instrument), plus the peer results that landed during the
investigation: results_p1_bifolio.txt (19:24), results_n4.txt (19:28), results_n5.txt (19:29). Every
number below is in one of those files or the result file it names. A separate ranking, TOP10-LEADS.md at the root (19:25, muse wonder (helper agent; self-identified 20:02 via Jon's paste)), was not an input to the angles and is compared in the conflicts table.

## Verdict on the hypothesis

**Killed as stated, refined to a sequence.** The hypothesis was "roughly ten leads that, pursued in a
planned order, move the question past *not deciphered* (Tier-2 or better)". Four of six angles reached
the same conclusion independently: three unknowns sit upstream of nearly every item on the baseline
list, and no item on the list builds the control that would retire any of them. Until those land, no
lead can deliver a Tier-2 verdict that survives its own refuter.

- **U1 — line edges.** The line-edge first-glyph profile (JSDf 0.176) is the metric outside every
  family, but every language control is pseudo-lined (v1: 9-word lines; m4: 8×20). Real-line numbers
  on disk are verse (0.034) and 1608 print (0.0026). B found the field has the same gap
  (Rozanova–Temerev and Schwartz both cut their controls to the Voynich line template) and found the
  corpus that closes it: CREMMA Medii Aevi, 21 Latin manuscripts, 7,274 real lines, abbreviations
  kept, CC0. One download.
- **U2 — coupling.** The +0.18-bit cross-space coupling is measured against a within-line shuffle
  that also destroys line position; Feaster (CEUR 3313) showed the Smith–Ponzi word-break anomalies
  are partly positional. A position-stratified null and a non-Voynich edge table (fit on Currier A,
  score B) are needed before "+0.18 bits of ordering" can be cited, and before a producer handed
  Voynich's own table can be said to have reached it (REDTEAM #1).
- **U3 — unit.** h2, the one band that kills every generator, and the type/hapax figures are
  alphabet-specific: GC2a gives h2 2.540 (p2), glyph+ 2.397 (m7). v2 §2 states this; the band has
  not been re-derived on a fixed unit inventory.

## What landed during the investigation (changes the picture)

- **n4:** hand-1 section NMI **falls** (matched by the 7k synthetic generator on ZL3b and IT2a; holds
  only on RF1b); hand-2 is not evidence; F1 at 7k is inconclusive because the 7k generator has no
  power (h2 3.27). The bifolio null itself does not kill the manuscript's hand-1 signal (p=0.000).
  Consequence: the last content-side signal is gone as evidence, as B predicted from Schwartz §5.4.
- **n5:** of the three "generation signatures", position lock is non-diagnostic, but
  char-beats-wordlist (+0.094) and Moran I of word length (+0.141) are **outside both** producer
  families and outside the natural-language range, on all three transliterations. They do not split
  the families; they are two more joint-anomaly targets nothing reaches (O-043, c-293–295, L-099).
- **p1 rerun:** bifolio null restored to its own file; the filed Part D interval did not reproduce
  (now [+0.03, +1.98], P=0.021).

## What each angle changed

**A (harvest).** 34 leads; top by value per cost: v2 bands from within-manuscript variability, the
real-line control, the non-Voynich edge table, generation signatures on cipher output (now done: n5),
gibberish on the board, the K4 code run, then the joint pair. Found the p1 overwrite and j4/p2 prefix
reuse. No n4–n7 text exists in any doc; prefixes s1 onward are free.

**B (prior art).** (1) m5's anatomy is a replication (Timm 2014, R&T §3.6, Steckley 2024), but the
real-line control is a genuine field gap and CREMMA fills it; a cheap pre-test exists (RN-Top PR #5:
line-final -am odds ratio 22.9 in native lines vs 1.8 re-lined). (2) The coupling has a published
positional confound (U2). (3) Schwartz §5.4 already finds the section tint weak (0.2–0.3 bits/page,
two sections only, negative once quire is conditioned on); the bifolio is the historically right null
unit (Layfield & Fagin Davis 2026, unopened). (4) DECODE statistics kill the codebook family on
historical grounds: 72 % of 700 keys have >100 entities, names dominate, 96 % of 15th-century keys use
nulls; no period code reaches 7k types. The period-plausible cipher is a homophonic alphabet + nulls +
a small names list; null glyphs (O-024) become the untested, historically grounded family. (5)
Gaskell–Bowern already scored one line-position metric where Voynich sided with *meaningful* text
(charbias), the one of 42 where it is not gibberish-like; their corpus keeps real line breaks.

**C (constraints).** Power: hand-2 c1 p=0.133 is a power failure (needs injected share 0.60; the
manuscript's NMI corresponds to ~0.5–0.65), not a negative; hand-1 "survives" only at the 1/55 floor.
m1's filed P=0.068 is one seed; seeds 0–9 give 0.003–0.093, 7 of 10 "detect". m6 Lc/Ls tests have no
power. Floors: all seven bands readable from ~5k tokens; the 41 held-out pages average 6,849 tokens,
width jsd ±0.036, cross ±0.027. Currier A fails m_final in 40/40 bootstrap draws: a real band failure.
Multiplicity: 582 p-values today, 291 below 0.05; nothing content-bearing survives Bonferroni or BH.
Execution: GPU shows 13.2 GB of 16.3 GB used by other processes; 3.6 GB RAM free; strict spaces drop
7 % of tokens. Infeasible as specified: item 9 (no script, no positive control, GPU busy); the Phase 2
tournament (both entrants carry Voynich's edge table and c2 lexicons, so the expected edge/NMI
difference is zero; it separates only on h2/types, which is the lexicon-size confound); item 1 (the
target, not a lead); full m4 reruns under four sessions.

**D (stress test).** U1–U3 as above; the replacement is a sequence; Tier 1 needs human-input evidence.

**E (dependencies).** Wave plan with a concurrency cap (≤3 experiment processes, ≤1 board-scale, ≤1
NMF job); scoreboard.json is read-modify-written whole, so each scorer needs its own --out; m4-style
boards glob every sidecar in data/controls_synthetic, so experimental sidecars go to runs/. Prefixes
s1–s16 and t1 assigned with prereg stubs. GPU is needed only for the key search.

**v2 freeze.** PREREG-v2.md frozen 19:27 (hash f8c42d76…), run_v2.py, 39 gibberish sidecars (10,023
tokens; single writers too short for the extras). No X ranges file yet. Currier A already fails a v1
band.

## Conflicts between angles, and how they resolve

| Conflict | Resolution |
|---|---|
| A: real-line control is medium cost, "no 15th-c. prose scribe exists"; E: "nothing on disk, cannot be fixed in advance" | B found CREMMA (CC0, real lines, graphematic). Cost drops to a download plus a sidecar builder. E's stand-ins (Nibelungenlied real lines, Dante verse, gibberish real lines) run first as the pre-test. |
| A ranks the K4 code run #6; B kills codebooks historically | Keep K4 only as a mechanism bound ("a shared-codeword code can reach the coupling at 5.5k types"). The period-plausible entrant is homophonic + nulls + names, with the null-glyph mechanism untested. |
| v2 agent promotes hand-1 NMI (item 5) to a hard gate; C: it cannot clear multiplicity at the 1/55 floor; B: Schwartz found the tint weak | Settled by n4: it falls. It stays only as a gate on page-contiguity claims. |
| Peer's Phase 2 (2 vs 3 tournament, fixed in advance); C: uninterpretable; D: wait for U1/U2 | Do not build or fix Phase 2 entrants until the U1 and U2 controls exist. Then the pair is a period-plausible cipher twin vs a matched generator, both with stubs, scored all/A/B. |
| A: gibberish is low cost; v2 agent: too short for the extras | Both right. Gibberish ranges the seven v1 bands and position entropy per writer; extras only from the pooled file, flagged size-mismatched. |
| Baseline item 4 (A vs B) as a lead; C: partly pre-decided | A fails m_final in 40/40 draws. n6 reports it; the open questions are whether B alone passes and whether bands should be set per language. |
| TOP10-LEADS.md #1 (muse wonder (helper agent; self-identified 20:02 via Jon's paste); joint producer bake-off now) vs this synthesis (controls first) | The joint producer is the right Tier-2 experiment but, built now, it inherits Voynich's edge table and an unfixed unit, so a pass or fail is uninterpretable (C, D). It is step 5 here, after steps 1–3. |

## Surprises

- results_p1.txt was overwritten; the rerun did not reproduce the filed Part D interval.
- m1's column-copy negative is seed-unstable; hand-2 negatives (c1) are power failures. Five
  negatives in the registers need reclassifying from "fails" to "underpowered".
- n5 produced two new joint-anomaly targets instead of a family discriminator.
- The GPU is mostly occupied by other processes; the key search could not run tonight regardless.
- Timm's token bound (38k tokens vs 57–76k plaintext letters at 1.5–2 letters per token) has never
  been computed here; it constrains F3 and any verbose-cipher joint producer for free.
- Nothing content-side survives multiple-comparison correction; 291 sub-0.05 p-values were read as
  if each stood alone.

## The replacement: a sequence, not a list

> Superseded 2026-10-18 16:02 PDT: this was the adopted sequence of 2026-10-17; it is not the current queue (see D-066, PLAN.md `Current stage:`).

Each step names what it retires. Ceilings are the best Tier a step can reach.

0. **Done or running** (pre-registered by peers): n4 (done, falls), n5 (done, two targets), n6
   Currier A/B on v2 and n7 gibberish on v2 with the X ranges file (both waiting on Jon's go in the
   decryption session). Ceiling: Tier 3 each. Nothing in steps 1–4 waits on n6/n7.
1. **Retire U1 — real-line control.** Pre-test tonight from disk: gibberish real lines, Nibelungenlied
   real lines, RN-Top's -am odds ratio reproduced on ZL3b. Then CREMMA: download to a fresh directory,
   build a sidecar with real lines and paragraphs, score the edge bands, CHARWIN and Moran I on v2.
   Outcome A: scribal prose lines sit far below Voynich, so the edge bands become a real discriminator
   and the m5 target stands. Outcome B: they overlap, so the edge bands lose weight by v2's own in/out
   rule and "the only metric outside every family" dies. Either is Tier 3 and both re-rank everything
   after. Cost: low to medium.
2. **Retire U2 — coupling.** Position-stratified null, non-Voynich edge table (fit on A, score B; a
   Latin syllable table), and Timm's token bound. Decides whether +0.18 is ordering or position and
   whether a producer handed the table proves anything. Tier 3. Cost: low.
3. **Retire U3 — unit.** Re-derive h2, types and hapax on a fixed unit inventory (glyph+, v101, RF1b)
   and set the v2 bands from the 41-page within-manuscript widths C measured. If the edge or h2 bands
   move, that is a dated v2 amendment, not a silent edit. Tier 3. Cost: low.
4. **Power and multiplicity repair.** Reclassify c1 hand-2, m1, m6 Lc/Ls and a3/d6 as underpowered;
   adopt a per-round BH correction in v2 reporting; rerun m1 over 10 seeds to its own path. Tier 3.
   Cost: low.
5. **Entrants, only after 1–3.** (a) A period-plausible cipher twin: homophonic alphabet + nulls +
   small names list + m5 line-end draw, with the Zenodo workbook key as positive control. (b) A matched
   generator with the same edge table and the 7k budget. K4 kept as a bound. Each with a prereg stub,
   scored once on v2, all/A/B, 3 seeds, 41 held-out pages, now also against CHARWIN and Moran I.
   Ceiling: Tier 2 (a family favoured by a registered margin). Cost: medium.
6. **Key search.** Only if 5(a) wins and the GPU is free; positive control first on
   flow_cipher_layer. Ceiling: Tier 1, but Tier 1 also needs human-input evidence (physical and
   archival checks, item 10), which no computation here supplies.

Dropped from the baseline: item 1 (it is the target), item 2 as a period hypothesis, item 9 for now,
item 7 (done). Kept as gates, not leads: items 4 and 5. Promoted: item 8 (now step 1), the X ranges
file, U2, U3.

## What this does not settle

Whether the two-family framing is exhaustive (copied-without-understanding, liturgy, conlang, notation
untested; REDTEAM #6). Steps 1–4 are family-neutral, so this waits until step 5 is designed.

## Addendum 2026-10-17 19:52 (n6 landed after the gate)

- **n6 A/B** (`results_n6_ab_split.txt`): SAME family verdict on full-size ranges, SPLIT on matched-size ranges; Currier A sits inside the natural-language range on the coupling metrics (0.120 / 0.127) where B (0.232 / 0.240) and the whole text are outside, and A fails m_final ×6.21. The coupling anomaly is a B property; U2's control (s20) must stratify by language, and v2.1 needs a Currier-A rule.
- **n6 glyph-model generator** (`results_n6.txt`, prefix shared with the A/B run): with a generator that has power at 7k types (h2 2.14), the F1 residual is *not* matched on ZL3b/IT2a and hand-1 section NMI *holds* on all three transliterations. This reverses n4 (whose generator had h2 3.27 and no power) and reopens F1 as content-side evidence for manuscript-sized producers. The sequence stands; Phase 3's target set regains F1 and NMI-h1, with C-constraints' floor caveat.
- Prefix n6 was used by two scripts from two sessions (L-103). No overwrite, but the PLAN prefix table now governs.

