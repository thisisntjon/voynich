> Executed. Outcome is in `results_g0.txt`, `results_g1.txt`, and `results_f1.txt`. Do not run it again. Map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md).

# Research plan — next round (2026-10-17 16:00)

Status: **not deciphered.** This plan starts from the filed result files, not from
`PLAN.md` §1. That section's codebook ranking was written before the C1 quire
null and is superseded. Frozen numbers live in `PREREG.md`. Do not edit them.
A new threshold is PREREG v2, and every entrant is re-scored.

Proof bar, unchanged: a fixed key, a named language or code, a long continuous
reading, held-out folios, and failure on shuffled text (`PLAN.md` §0). This
round is not aimed at that bar. It is aimed at one Tier-2 decision: whether
one generator, with its parameters logged, can hit the joint board.

## What the other rounds already settled

| Round | Result to keep | What it removes |
|---|---|---|
| a6 / a6b | Homophonic letter substitution into Latin, Italian, or German, with Voynich spaces kept, lands at the null or at a wrong language. Positive control recovers a known cipher. | Another Latin/Italian/German letter solver |
| b4, c2 | Copying does not create line edges. Explicit `p`-start and `m`-end rules do. No single C2 seed hits NMI, both edge multipliers, h2, and the line-start profile together. | "Self-citation alone explains the page" |
| b5, c1 | Illustration/hand/language clusters are mostly section morphology. Hand 2's within-hand NMI fails a quire-block null (0.333 vs 0.209, p=0.133). | Topic models as the next experiment |
| c4, d3 | Real Naibbe ciphertext matches h2 (2.08 vs 2.09) and misses line position (JSD 0.0006 vs 0.172) and edge coupling (+0.002 vs +0.181). A Naibbe-like forward model also misses length SD (4.08 vs 1.76). | Position-blind verbose ciphers |
| d2 | Held-out bits/token: word unigram 10.728, char trigram 11.279, slot models 13.136 and 14.298. | This slot induction as a grammar. A later induction must beat 10.728 or it is retired (`PREREG.md`) |
| d5 | Vocabulary does not saturate (beta 0.724, late beta 0.784, the highest of the controls). Adjacent repeats are real; a lone rambler is not. | A small closed codebook, and glossolalia |
| d6, e3 | Labels match their own page at 12.1% vs a 10.6% null (p=0.09). f57v.3 is four copies of a 17-token glyph string, 15 positions fixed, glyph period 18. | Labels-as-names, and f57v as a period key |
| e1 | Joining `y–q`, the top-8 pairs, uncertain commas, or PMI>1 boundaries does not create word order. Best targeted excess is +0.012 bits. Dante inside a line is +0.536. Caesar is +0.239. | "The spaces are false word breaks at the coupled edges" |
| e2 | Cross-space MI is 0.195 bits. Deleting `n` removes 42%, `r` 28%, `y` 19%. | A one-pair `y→q` rule as the whole coupling |
| f1 | See the caveat below. Next-word models do not beat a unigram. | Word-order syntax of the Latin/English kind |
| scoreboard v1 | `score.py` reproduces a1/a2/c3 (`reproduction_pass=true`). Scored so far: Voynich, token-shuffle, Caesar, Dante. | Re-deriving those four rows |

`LEADS-CHASE.md` now matches the D-series files on the numbers that were wrong in its first draft. `C_RESULTS.md` now includes C4. `TEAM-HANDOFF.md` item "PREREG absent" is stale: `PREREG.md` and `scoreboard/` exist. Its open queue is otherwise the right one, and this plan is that queue with the F1 result folded in.

## How to read F1

`results_f1.txt`, whole words, held-out bits/token (lower is better):

| Text | Unigram | Edge (last two glyphs) | Previous word | Edge gain | Residual |
|---|---:|---:|---:|---:|---:|
| Voynich | 10.255 | 10.267 | 10.386 | −0.011 | −0.120 |
| Within-line shuffle | 10.383 | 10.636 | 10.800 | −0.253 | −0.163 |
| Dante, 9-word lines | 9.881 | 9.652 | 9.641 | +0.229 | +0.011 |
| Caesar | 10.969 | 10.903 | 10.854 | +0.066 | +0.049 |
| Alice | 8.756 | 8.162 | 7.903 | +0.594 | +0.259 |

The file's verdict line says "FAVOURS EDGE-RULE NOTATION/GENERATOR." Use the table, and treat that sentence carefully.

- Residual = (edge-2 bits) − (previous-word bits). Negative means the previous word made prediction worse.
- Voynich's residual (−0.120) sits next to the shuffle (−0.163), not next to Alice (+0.259). There is no usable word-order syntax past the unigram.
- The edge gain is also negative (−0.011). Knowing the previous word's last glyphs does **not** identify the next word. E2's 0.195 bits is about the next **character**. F1 and E2 are different targets. F1 does not show that an edge table generates the text.
- The printed "12.07 x" divides Voynich's residual by Augustine's residual of −0.010. It is not "12 times more structure." The branch that fired treats any non-positive residual as the edge-rule verdict (`v <= 2 * max(null, 0)`). Augustine itself would pass that branch.
- The script on disk also loops a top-100 and top-300 class collapse. `results_f1.txt` contains only the whole-word block. Those two rows are unrun.

What F1 is good for: the generator must not be a word-bigram model. Draw a word from a list, then accept or reject it so the first character matches P(first | last). Predicting the whole word from the previous word is the model that already lost.

## The experiment

One new script, `g1_edge_joint.py`. Do not edit `c2_section_generator.py` (its filed numbers are cited by C2 and F1). New prefix is `g`: `f1` is taken.

### Entrant

On each held-out page skeleton:

1. Draw a candidate word from that page's section lexicon (the C2 section seed).
2. Accept or reject so the first EVA character follows P(first character | previous word's last character). Estimate that table on **train pages only**. Page split 80/20, seed 20261017, the split in `PREREG.md`. Contexts with train count under 5 fall back to the marginal. Report the number of contexts kept.
3. Apply the two line rules after the draw, as C2 does when the rules are on: line-initial `p`, line-final `m`. Report whether a rule can override the edge table. If it can, that override is a parameter and it is logged.
4. Also run the circular upper bound: the lexicon is the real section vocabulary, same filter and same line rules. This is not a theory of authorship. It asks whether a real word list plus the two filters is even capable of the joint board.

Log every config. Cap 20. One config is the reported score. The others are the stability check. Fitting the edge table on test pages voids the run.

### Score

Run `scoreboard/score.py` on the held-out skeleton and on the full skeleton. A joint pass is all seven frozen bands at once (`PREREG.md`):

| Metric | Pass |
|---|---|
| h2 | 1.98–2.28 |
| sd_len | 1.41–2.11 |
| jsd_first_fg | ≥ 0.10 |
| p_init_enrich | ≥ ×8 |
| m_final_enrich | ≥ ×8 |
| cross_excess_eva | ≥ +0.09 |
| redup_pct | 0.4–1.8% |

Generation is favoured, Tier-2, only if one documented config joint-passes. It is killed as a complete explanation if the best edge-augmented run still has cross_excess under +0.05 or first-glyph JSD under 0.05. A partial pass retires nothing.

Before building `g1`, add the already-filed streams to the same board so the gap is one table: best filed C2 config, D3 verbose output, the C4 Naibbe skeleton, b4 SIMcal. No new theory in that step. `PREREG.md` already lists them as unscored.

### How to read the outcome

- **Circular list passes and the small seed lexicon passes.** A word list plus an edge filter plus two line rules is enough. Generation stays the economical account. The following round counts parameters against the seven constraints and stops adding machinery.
- **Circular list passes and the seed lexicon fails.** The load-bearing object is the vocabulary itself, not the filter. Only then open an external-index test: a mapping from frequent types to named items that predicts a quire held out of the mapping. A handful of plant-name hits does not count. Labels already failed that kind of test.
- **Circular list fails.** The edge filter and the line rules fight each other, or they distort length and entropy. Report which band broke. That conflict is the next measurement. Do not add a third rule in the same run.

## Do not run

- Topic models, NMF, or another within-hand cluster. C1 closed that use of them.
- f57v as a cipher period, or another label-in-page permutation. d6 and e3 closed both.
- A new language solver that keeps EVA letters and Voynich spaces. a6b closed Latin, Italian, and German. F1 says resegmentation will not reveal English-like word order; e1 already tried the coupled boundaries.
- Another prefix/core/suffix induction, unless the held-out score beats 10.728 bits/token on the d2 page split.
- A word-bigram or "P(next word | last glyphs)" generator. F1 says that model loses to the unigram.
- Edits to `PREREG.md`, `vparse.py`, `corpora.py`, or `data/ZL3b-n.txt`.

## One audit, not a new line of work

Re-run `f1_residual_order.py` so `results_f1.txt` matches the script now on disk, including the top-100 and top-300 rows. In the same note, replace the "12.07 x" sentence with the residual table. Do this before anyone cites the verdict line. It does not change what `g1` should test.

## Order

1. Score the four filed streams on the frozen board.
2. Audit F1 so the result file matches the script.
3. Build and score `g1`, circular and seed-lexicon, train-only edge table, at most 20 logged configs.
4. Branch on the three outcomes above. Stop the round if `g1` returns no joint pass and no clean band-level failure. A partial pass is not a reason to add rules.
