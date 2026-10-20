> **Historical (superseded 2026-10-17 23:33).** Current state: `README.md` → `workflow/FINDINGS-REPORT.md`. Findings from this file are in `.inventory/registers/`.

# J-series: powered homophone recovery → Voynich classes → collapse-solve

Session run under frozen PREREG v1 gates. Scripts: `j1_class_recovery2.py`,
`j2_voynich_classes.py`, `j3_collapse_solve.py` (+ g0 board earlier).
Import-only reuse of b4/c2/c4/d3/f3/f4/i1/a6; no builder files edited.

## Chain and verdicts

1. **J1 gate (controls only).** F4 context features collapse at Voynich-like
   inflation (m=3 truth ARI 0.036–0.039). J1 joint features: 0.101 (miss).
   Declared J1v2 (context + 2× spelling TF-IDF, no position): **0.171 at
   m=3 — gate PASS** (≥0.15). Caveat: I1 creates homophones by spelling
   alternation, so the spelling block may exploit control construction.
2. **J2 Voynich transfer.** J1v2 classes predict held-out Voynich pages:
   honest class-over-token +0.018 to +0.025 across K/seeds/splits, vs F4's
   −0.005. Largest classes are spelling families (daiin/odaiin, shedy
   variants, ol variants). Predictive ≠ homophonic — J3 decides.
3. **J3 crack attempt: FAILS cleanly.** Collapsing 244 classes to
   representatives (7,025 → 6,780 types) moves metrics away from language
   (excess +0.181 → +0.106, redup 0.90% → 1.66%) and the a6 homophonic
   solver scores collapsed text **worse** than raw (−4.114 vs −3.787
   bits/char, paired budget) and worse than pseudo-Voynich null (−4.014);
   Latin self-score −2.666. No readable output either way.

## Interpretation

J2's predictive classes capture spelling/morphological regularity (useful
compression structure), not plaintext-unit homophony usable for decipherment:
merging them destroys letter-level information a solver needs. Combined with
F4/I1, the homophone-class route at this granularity is retired unless a
recovery method passes the m=3 gate *without* spelling features (context-only
ARI remains ~0.04–0.10). This does not kill verbose/flow cipher family —
only this class-recovery path to a key. Status remains: **not deciphered.**
