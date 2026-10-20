> Round log for D. Map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md). Numbers live in `results_d1.txt` through `results_d6.txt`.

# Leads chase (multi-agent) — new tests D1–D6 + rambling verdict

Filed: 2026-10-17 15:34 (system clock); corrected same day against
results_d1/d2/d3.txt ground truth after a summary-filing error.
Method: 6 parallel agents (5 computational, 1 literature) + critic + synthesis.
Status: **partial** (rambling-literature structured result missing; substance
in agent note below). New code: `d1_edge_coupling.py`, `d2_slot_bakeoff.py`,
`d3_verbose_forward.py`, `d5_rambling.py`, `d6_ring_labels.py` (+ results_d*.txt).
Critic opened all five result files: no fabricated numbers; caveats at end.

## Could it just be the ramblings of a crazy person?

**Short answer: meaningless is still possible; a lone disordered rambler is
the weakest version of meaningless. Rambling survives only hybridized with a
workshop model** (dictated glossolalia, one inventor's exemplar copied by
scribes, or deliberate asemic production).

Testable rambling predictions (from glossolalia/asemic/psychosis literature,
7 URLs opened; Smarthistory 403 not cited) vs measurements (D5):

| Prediction | Measured | Verdict |
|---|---|---|
| Extreme perseveration | P(recur≤k) k1/k5/k20/k100 = 0.0084/0.0432/0.1275/0.3143; k1 = 16.3× max control, but k5 only 1.10× Augustine; excess vs shuffled 2.45×→1.41× localized | Supported only at immediate reduplication (k=1) |
| Saturating tiny vocabulary | Heaps β=0.724, late β=0.784 (fastest late); types 7,025 (Dante matched-N 6,503) | **Refuted** |
| Bursty, non-metronomic gaps | Top-50 gap CV 1.702 vs controls 1.055–1.253, shuffled 0.990 | Supported, but non-separating (topicality predicts it too) |
| No stable long-range topic structure | Rare-word page Jaccard decays 0.0205→0.0064 (ratio 3.18; within-A 2.24, within-B 2.34; null ratio 1.30) | **Refuted** |
| Single-producer idiolect | 5 scribes, shared positional grammar, 240 pp. on ~14–15 calves, workshop colour notes | **Refuted as lone production** (codicology, literature) |
| Labels not tied to referents | D6 primary: 12.1% own-page vs 10.6% null, p=0.0945 | Consistent with rambling (also with codebook) |

Glossolalia explains fluency + low entropy + meaninglessness; art-brut /
Serafini explain book scale; none alone explains 5-scribe shared script with
genre sections. Diagnosis from statistics alone remains impossible — claims
here are comparative, not clinical.

## New usable understanding

- **D1 Edge coupling confirmed at ~0.2 bits, with nuance.** Cross-space MI
  (Miller–Madow): Voynich EVA 0.172, glyph 0.176, full 0.185 vs permutation
  null ~0.012–0.017 and MM nulls 0.000 — real sequential signal, >10× bias
  floor. But not unique: Dante 0.140 is close (Caesar 0.036 far below);
  cross/within ratio Dante 0.171 actually exceeds Voynich 0.104–0.118.
  Within-word MI is the anomaly's other half: Voynich 1.655 vs controls
  0.74–0.82. Word-bigram gain (shuffle-corrected) Voynich 0.85% (full 0.72%)
  **confirms <1%** vs Caesar 2.46%, Dante 3.85%. Top contributor y→q alone
  = 47% of plug-in cross-MI — coupling is concentrated, not diffuse syntax.
- **D2 Slot bake-off: slots lose.** Held-out bits/token (7,332 test tokens):
  unigram 10.728 < char-trigram 11.279 < slot pref→core 13.136 <
  slot-independent 14.298. On unseen types, slot is worst (22.1–23.0 vs
  trigram 20.1, flat UNK 18.1) despite 98.7% segmentability. Under this
  (greedy, degenerate 1-char-core) induction, slot grammar redescribes /
  memorizes train vocabulary; it does not generalize. Curated/MDL induction
  untested — verdict conditional.
- **D3 Verbose cipher forward.** h2 reproduced (cipher 2.486 ± 0.041 vs
  Voynich 2.126, plain Latin 3.295) and Zipf slope reproduced (−0.985 vs
  −1.047). Fails: word-length SD 4.08 vs 1.76 (Bernoulli spaces; partly
  artifact), types 9,129 vs 5,417, adjacent repeats only ~40% of Voynich
  rate, line position totally (JSD excess +0.0002 vs +0.1739; p ×1.01,
  m ×1.04 vs ×17.9/×16.3). No position-blind enciphering creates line effects.
- **D6 Ring + labels.** f57v.3 *is* 17 words × 4 at word level
  (chunk agreement 17/16/15/15 of 17), but at glyph level the period is
  **18** (match 0.963; one cycle word spans 2 glyphs), longest repeated
  block 27 glyphs ×2, and whole-ring streams show no period-17 peak
  (0.077 vs 0.068 baseline). Cite as word-level f57v.3 fact only.
  Labels primary (exhaustive 40 pages with L*+P*, 778 tokens): **not**
  page-referential beyond section (p = 0.0945). Sensitivity including ring
  text (55 pp.) gives p = 0.0199 — secondary, different denominator.

## Strongest remaining lead

Joint scoreboard on held-out pages: D1 cross-MI (incl. y→q concentration)
+ B4 line JSD/enrichments + B5 within-hand NMI + D5 perseveration profile,
for C2 generator, D3 verbose output, self-citation, gibberish. Falsifier for
structured-generation/notation: one 15th-century-plausible mechanism matching
all without per-metric tuning — or a fixed-key blind reading
(INVESTIGATION.md proof standard).

## Critic flags (preserved)

- D2 verdict conditional on degenerate induction; D3 h1/Zipf partly circular
  (Voynich-derived fragment pool), SD failure partly space-model artifact;
  D1 controls not line-matched, Dante cross-MI mechanism uninvestigated.
- Unresolved: Caesar corpus (19,520 tok) shorter than Voynich N (Heaps
  matched-N uses Augustine+Dante); Heaps cross-language comparison
  approximate (surface forms, A→B turnover not decomposed);
  rambling-literature structured evidence missing (note preserved above).

## Reproduce

```powershell
cd voynich
uv run python d1_edge_coupling.py
uv run python d5_rambling.py
uv run python d6_ring_labels.py
```
