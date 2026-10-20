> Round log, not the queue. The scoreboard was scored in `results_g0.txt`. The sentence that the evidence clearly sides with encoded text is stronger than `results_f3.txt`. Homophone classes are in `results_f4.txt`, which this file does not cover. Map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md).

# F-series results (2026-10-17 16:08 PDT)

Status: **not deciphered.** This round adds one new hard constraint (F1) and one mechanism that meets it together with the edge table (F3). Scripts: `f1_residual_order.py`, `f2_syllable_control.py`, `f3_flow_choice.py`. Outputs: `results_f1.txt` to `results_f3.txt`. Builds on C1–C4, D1–D6 and E1–E3 (`C_RESULTS.md`, `LEADS-CHASE.md`, `E_RESULTS.md`).


> **Superseded in part (2026-10-17 18:30 PDT).** The rebuttal flagged as untested under F3, a meaningless generator with a fixed word-pair habit table, has now been tested. The pre-registered N2 test (`n2_habit_fine.py`, `results_n2.txt`) passes it on residual. At p = 0.04 the residual is +0.038 to +0.046 on ZL3b, inside the manuscript's 95% CI, and likewise on RF1b and IT2a.
> - F1's residual and F3's "only the meaning-bearing producer keeps word order" therefore no longer discriminate meaning from generation.
> - The numbers below are unchanged.
> - F1's measurement of Voynich and F2's syllable result still stand.

## F1: word order beyond the edge table (new constraint)

The test is a held-out language model on adjacent tokens within lines. It compares predicting the next token from:
- the previous token's last two glyphs (the edge table), against
- the previous token itself.

**Residual excess** is the extra gain from knowing the previous token, minus the same quantity for the same text with each line shuffled. Results are for the top-300 vocabulary; whole words and top-100 agree.

| text | edge-gain excess | residual excess |
|---|---|---|
| Voynich (all / A / B) | +0.270 / +0.188 / +0.318 | **+0.042** / +0.052 / +0.048 |
| token-shuffled null | −0.001 | +0.002 |
| Naibbe (real verbose cipher) | +0.021 | **+0.036** |
| c2 section generator | +0.007 | +0.001 |
| prose controls (6) | +0.31 to +0.76 | +0.14 to +0.39 |

Voynich has prose-sized edge information but only cipher-sized word order beyond it: 3–9× below every prose control and clearly above the nulls.

Method disclosure: the first run used additive backoff, and every model, controls included, scored worse than unigram. I switched to Witten-Bell. Raw residuals were still negative on controls, so I added the shuffle calibration. The pre-registered thresholds did not change. The verdicts are INCONCLUSIVE for whole words and top-100, and "favours language" for top-300. Voynich sits at 0.23–0.30× the weakest prose control, right on the 0.25 threshold.

## F2: tokens are not plain syllables

I rewrote all six controls with a space at every syllable boundary, and again at every second boundary.
- Cross-space MI rises to +0.24–0.36 for single syllables and +0.10–0.22 for two-syllable chunks. Voynich is +0.18.
- Residual word order **rises** too, to +0.25–0.54, where Voynich has +0.04.
- Types fall to 1.1–2.6k, against Voynich's 7k.

Plain syllable spacing gives the edge coupling but not the weak word order. **Against** "Voynich is a syllabary of a known-type language written plainly".

## F3: a flow-choice cipher matches both; a flow-choice generator does not

Mechanism: whenever the producer has a free choice, it prefers candidates whose first glyph flows from the previous token's last glyph, with weight R(first | last)^β. R is Voynich's own edge table. That makes the test about whether the mechanism *can* carry the table, not where the table came from. Naibbe's tables have the same circularity.
- **CIPHER** re-encrypts Naibbe's 20,923 plaintext chunks. Its homophone sets are rebuilt from the workbook's encrypter sheet (median 6 homophones per letter).
- **GEN** is the c2 section generator, choosing among 8 candidates.

| producer | cross MI excess | residual excess (page split / reversed / quire split) | h2 | types | hapax |
|---|---|---|---|---|---|
| Voynich | +0.181 | **+0.042 / +0.039 / +0.041** | 2.11 | 7,025 | 0.68 |
| CIPHER flow β=1.5 | +0.224 | **+0.049 / +0.042 / +0.049** | 2.09 | 4,703 | 0.49 |
| GEN flow (β = 1–2; splits at β=1.5) | +0.12–0.39 | page split +0.009 to +0.017 (β 1–2); at β=1.5: +0.011 / +0.012 / −0.001 | 1.75 | ~1,600 | 0.35 |
| GEN flow β=1.5 + run-copying (p = 0.1–0.5) | +0.26–0.31 | −0.014 to +0.006 | 1.75 | ~1,600 | 0.35 |
| CIPHER β=0 (plain Naibbe) | +0.001 | +0.033 | 2.09 | 4,650 | 0.48 |

**Favours the encoded-text family: a verbose homophonic cipher of a real language, with a scribe who chooses homophones that flow from the previous glyph.**
- Both producers can carry the edge table.
- Only the meaning-bearing one keeps Voynich's word order across pages and across quires.
- Copying runs of earlier words does not fake it: the copied pairs stay on their page and don't carry over to held-out pages.
- The flow cipher also matches h2 (2.09 against 2.11). The generator does not (1.75).

What it still misses: line effects (no producer has line rules; p ×1.07 against ×16), type count (4.7k against 7k), hapax share (0.49 against 0.68) and immediate repeats (0.13% against 0.87%).

Rebuttal not yet tested: a meaningless generator with a fixed word-pair habit table shared across the whole book would pass F1. Such a table is, in effect, a grammar, so this test cannot separate it from language.

## Progress, honestly

Earlier rounds narrowed the families. This round gives the first test where Voynich clearly sides with one mechanism class:
- **Meaning-bearing producers** (Naibbe, prose, flow-cipher) leave word order that carries over across pages.
- **Meaningless producers built from copying** (b4, c2, run-copy) do not.

It is a constraint, not a reading. No key, no language.

> Superseded. Item 1 is `results_f4.txt`. The inflation check is finished in `results_i1.txt`. Item 2's line rules are `results_h1.txt` and do not joint-pass. Item 4 is false: the board is `results_g0.txt`. The queue is `TEAM-HANDOFF.md`.

## Next high-value steps (ranked)

1. **Homophone-class recovery, with the F3 cipher as a positive control.** If tokens are homophones chosen by flow, the tokens that encode the same plaintext unit should share their right-hand contexts once the edge glyph is factored out. Cluster on F3 cipher output, where the ground truth is known, until it recovers the classes. Then apply the same frozen procedure to Voynich and pass the class sequence to the a6 solver. This is the shortest path from "family" to "key", and it fails cleanly if the classes don't form.
2. **Joint producer.** Add c2's line rules and a larger, more hapax-heavy table (7k types, 0.68 hapax) to the flow cipher, then score it on the whole benchmark: C3, F1, a2/b4, h2, types, B5 within-hand NMI. One mechanism hitting everything without tuning each metric separately would be a Tier-2 result.
3. **Kill the remaining rebuttal.** Test a generator with a global word-pair habit table in F1, to measure how much habit gives the same transferable residual.
4. **Phase 0 scoreboard** (TEAM-HANDOFF queue item 1) is still unowned. F1's residual and C3's coupling belong in it.

## F4: homophone-class recovery (2026-10-17 16:34 PDT)

Script `f4_homophone_classes.py`, output `results_f4.txt`. The procedure was frozen in the docstring on the control before any Voynich run:
- **Units:** types seen at least 10 times.
- **Contexts:** ±1 neighbours. Each neighbour count is weighted by the text's own R(first|last)^−1, which removes the flow effect.
- **Vectors:** Hellinger vectors reduced to 60 dimensions by SVD, then KMeans with three refinement passes in which neighbours are replaced by their current classes.
- **K:** a truth-blind rule. K = f·types, with f taken from {0.1, 0.2, 0.33, 0.5} by the best held-out gain on the even→odd pages.

**Held-out test.** The F1 Witten-Bell chain gets a class context. "Class-over-token" (cot) is what the class of the previous token adds on top of the token model, on held-out pages. It is calibrated against a line shuffle. Classes are fit on training pages only. The honest direction is odd→even.

| text | K | type ARI vs truth | class gain | token gain | cot (seeds 0/1/2 mean) | seed ARI | page-split ARI |
|---|---|---|---|---|---|---|---|
| CONTROL, F3 flow cipher β=1.5 | 96 | **0.19** (0.15–0.23) | +0.024 | +0.042 | **+0.014** | 0.20 | 0.04 |
| CONTROL-NULL (tokens shuffled) | 96 | 0.04 | +0.006 | −0.003 | +0.003 | 0.09 | 0.08 |
| CONTROL β=0 (plain Naibbe) | 103 | 0.26 | +0.036 | +0.035 | +0.027 | 0.28 | 0.12 |
| **VOYNICH** | 244 | — | +0.009 | +0.039 | **−0.005** | **0.11** | **0.06** |
| VOYNICH-NULL (tokens shuffled) | 49 | — | +0.003 | −0.000 | −0.004 | 0.09 | 0.04 |
| prose: Caesar | 154 | — | +0.080 | +0.168 | +0.037 | 0.14 | 0.03 |
| prose: Dante | 78 | — | +0.059 | +0.219 | +0.011 | 0.22 | 0.14 |

**Control: the classes partly recover.** Type ARI is 0.19 against 0.04 for the null. Classes add +0.014 bits held-out beyond the token model, against +0.003 for the null. Seed agreement is 0.20 against 0.09. Edge factoring matters: without it, type ARI was 0.04 at MINC=5 against 0.06 with it.

The recovery is only partial. Page-split agreement is at null level even on the control. With roughly 10–40 tokens per type, the context evidence is thin. Token-weighted ARI is misleading here, because frequent types sitting alone score about 0.32 even on the null, so the table reports type-level ARI.

**Voynich: no comparable class structure.**
- The class context adds nothing over the token context: −0.005 bits mean, the same as its token-shuffled null (−0.004). The control gives +0.014 and Caesar +0.037.
- Seed agreement (0.11) and page-split agreement (0.06) are at null level (0.09 / 0.04).
- Voynich keeps cipher-sized token-context information (+0.039, as in F1). Only 24% of it survives pooling into classes: the class gain is +0.009. Pooling keeps 58% on the control, about 100% on plain Naibbe, 48% on Caesar and 27% on Dante.
- The "classes" it does form are spelling families such as chedy/shedy/otedy/sheedy and qokain/qokaiin/qokey. They do not generalise.

**Step 4 (a6 solver on class sequences) was not run.** Its precondition, stable Voynich classes, failed. Running the solver on unstable classes would only measure noise.

**Reading.** If Voynich were a flow-choice homophonic cipher with Naibbe-like homophone sets, this procedure should find classes. It finds them, partly, in the F3 control. In Voynich it finds none that predict held-out text. That counts against F3's mechanism as the whole story, at least with few homophones per unit at this sample size. It does not exclude a cipher with many more, rarer homophones: Voynich has 7k types against the control's 4.7k, and there are 489 types of 10+ tokens against 191. The present control has no power in that regime.

That re-run is the I1 section below. It is finished. Do not start it again.

## I1: power check for F4 under Voynich-like type inflation (2026-10-17 16:45 PDT)

Script `i1_power_inflation.py`, output `results_i1.txt`. This runs the F3 flow cipher (β=1.5) with each Naibbe piece given m spelling-variant homophones (ch↔sh, e↔ee, i↔ii, k↔t, …, weighted Zipf 1/(r+1)^1.2). It then applies the F4 procedure unchanged (imported, not edited).

| m | types | hapax | truth type ARI | cot (3 seeds) | null cot |
|---|---|---|---|---|---|
| 1 (= F4 control) | 4703 | 0.49 | 0.190 | +0.014 | +0.003 |
| 2 | 6541 | 0.63 | 0.073 | +0.003 | −0.001 |
| **3 (Voynich-like)** | **7610** | **0.70** | **0.044** | **+0.004** | **+0.000** |
| 5 | 8316 | 0.75 | 0.010 | +0.010 | +0.003 |

For reference, Voynich has 7025 types and a hapax share of 0.68.

**Reading: F4's power collapses at Voynich-like inflation.** At m=3, truth ARI falls to 0.04, the F4 null level. The cot gap over its null (+0.004) is inside the F4 seed spread (~0.006). At m=5, cot rises while truth ARI is about 0. That shows cot can be lifted by something other than real classes once types multiply.

**Consequence:** F4's Voynich negative does not count against a flow-choice homophonic cipher with Voynich-like homophone richness. The cipher family is neither supported nor excluded by class recovery at this sample size. Caveat: the control has 20.9k tokens against Voynich's 34.9k, so Voynich offers somewhat more evidence per type than the m=3 control.
