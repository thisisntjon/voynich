> **Historical (superseded 2026-10-17 23:33).** Current state: `README.md` → `workflow/FINDINGS-REPORT.md`. Findings from this file are in `.inventory/registers/`.

# Q-series results

## Q1 label ↔ image-class crib test (`q1_label_crib.py`, `results_q1.txt`)

Labels: 1,029 lines, 1,164 clean tokens, 837 types.
Image class proxy = IVTFF label unit (Lz zodiac, Lf, Ls, Ln, Lt, Lc, Lp, L0).

- A (repeat concentration): same-type label pairs share unit class 46.3%
  vs free-shuffle 22.2% (z=+13.9) and vs within-illustration shuffle
  36.2% (z=+5.2, p=0.005). Label vocabularies are image-class-specific
  beyond section vocabulary.
- B (held-out prediction): unit-from-word accuracy 0.166 vs majority
  0.134; seen-words only 0.338 (157/530 test tokens seen in train half).
  Association is real but sparse — most label types are hapax.
- C (zodiac positional crib): same-position repeat rate 0.0005 vs
  permuted 0.0018 (z=−1.4). **Null.** No evidence the same label word
  recurs at the same zodiac slot across the 12 zodiac pages.

Reading: labels behave like class-specific vocabularies (consistent with
meaning-bearing labels AND with class-conditioned generation), but offer
no positional crib of the sign-name kind. Combined with a3/D6 own-page
nulls, the label surface is exhausted at current power (837 types).
Caveat: unit classes are transcriber-assigned from images; Test A's
within-illus null controls section, not transcriber consistency.
