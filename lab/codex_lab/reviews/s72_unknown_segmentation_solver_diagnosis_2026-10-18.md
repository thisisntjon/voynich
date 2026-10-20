# s72 planted-control correction: simplified segmentation is not the full decoder

**Status:** provisional while `s72` is still running. This note diagnoses the visible planted-control failure and does not file a result.

## Corrected reading of the partial result

- The L4w construction can reproduce several registered surface bands, although its selected model still has the wrong `CHARWIN` sign and its target set uses the now-obsolete full-inventory `A14 <= 0` gate.
- When the true prefix/suffix inventories are supplied, the solver recovers Latin and Italian planted plaintext at `0.9958` and `0.9971` accuracy.
- In s72's **simplified** `unknown_seg` path, planted recovery falls to `0.1235` and `0.2145` on the same two languages.
- This does not establish that the project cannot infer boundaries. The earlier full `s50` solver included an MDL prefix/suffix search and recovered boundary-blind L4 planted controls at roughly `0.8815–0.9788` accuracy across the reported languages and keys. Most exceeded 0.90 and every language cell exceeded the registered 0.80 rule.
- A real-manuscript decode is still not licensed because L4w has not been tested with that full boundary search and the selected L4w producer retains the wrong `CHARWIN` sign.

## Code-path diagnosis

In `solve_l4w_inproc`, `known_pair` receives the true Voynich-derived prefix and suffix sets. The simplified `unknown_seg` path instead:

1. fits `SlotSegmenter` once on training-half ciphertext;
2. freezes that single segmentation;
3. chooses only among `pair`, `sep`, and `core` readings using a short solver run;
4. solves the substitution/null assignment without revisiting token boundaries.

The partial output shows the inferred prefix inventory shrinking from the true 28 to about 20–21 items while the suffix inventory remains 18. A boundary mistake changes the derived unit sequence before substitution search begins. This simplified path cannot repair that mistake. The full s50 implementation already contains a stronger alternative, `mdl_sets`, which searches candidate prefix and suffix inventories and was successful on the earlier planted L4 family.

## Required gate before a Voynich decode

Do not interpret or rank candidate Voynich plaintext until **L4w itself** passes the registered boundary-blind planted-control threshold across languages and keys under the full s50 segmentation search. Increasing restarts on s72's frozen greedy parse is not the appropriate repair.

Minimum next ladder:

1. Restore s50's `mdl_sets` candidate alongside the greedy `SlotSegmenter` candidate in the L4w planted-control path.
2. Use the same MDL-plus-language-model criterion that was validated on s50 L4, without exposing the true boundary inventory.
3. Measure boundary-set agreement and plaintext accuracy separately on untouched L4w languages and keys.
4. If MDL still fails on L4w, only then add a multi-parse lattice or alternating boundary/mapping updates.
5. Require stable language identification and plaintext recovery above the preregistered threshold before scoring Voynich.

This is the shortest evidence-backed route from the current statistical architecture to an honest decipherment attempt. The immediate issue is a removed validated search stage, not proof that a new decoder architecture is necessary.
