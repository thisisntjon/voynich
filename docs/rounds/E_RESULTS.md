> Round log for E. Map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md). Numbers live in `results_e1.txt` through `results_e3.txt`.

# E-series results (2026-10-17 15:40)

Status after C1–C4 and D1–D6, plus the three tests below: **not deciphered.**
No fixed key, no named language, no continuous reading.

The new scripts are `e1_resegment.py`, `e2_edge_ablation.py`, `e3_f57v_cycle.py`.
Thresholds in `e1_resegment.py` were written before `results_e1.txt`.

## Which earlier summary to trust

`LEADS-CHASE.md` disagrees with the result files it cites. Use the files.

| Claim in LEADS-CHASE | Result file |
|---|---|
| D1 cross-space MI 0.387 glyph+ / 0.299 EVA | `results_d1.txt`: EVA 0.191, glyph 0.206. `results_c4.txt`: EVA 0.195 |
| D2 char-trigram wins at 8.915; slot bits missing | `results_d2.txt` (UTF-16): word unigram **10.728** beats trigram 11.279, slot-indep 14.298, prefix→core 13.136 |
| D3 h2 2.044 vs 2.016, Zipf −0.47 vs −0.94 | `results_d3.txt`: h2 2.126 vs cipher 2.486 ± 0.041; Zipf −1.047 vs −0.985 |
| D5 growth exponent 0.61, adjacent/far 1.27 | `results_d5.txt`: beta 0.724, beta_late 0.784, adjacent/far 3.18 |
| D6 longest repeat 4 glyphs; labels 105 pages, hit 15.2%, p=0.02 | `results_d6.txt`: f57v.3 glyph period 18 and a 27-glyph repeat; labels 40 pages, 778 tokens, hit 12.1%, p=0.0945 |

`C_RESULTS.md` still says the Naibbe test was not run. `results_c4.txt` is that test. Real Naibbe ciphertext (Zenodo sampler, laid onto Voynich line lengths) has first-glyph JSD 0.0006 against Voynich 0.172, p-initial ×0.89 against ×15.97, and cross-space MI 0.008 against 0.195.

`PLAN.md` promoted a codebook because within-hand topic NMI looked strong. `C_RESULTS.md` C1 then found hand 2's section signal fails a quire-block null (NMI 0.333 vs 0.209, p=0.133), and inside a shared quire neither hand separates its sections.

## E1. Joining the coupled boundaries does not create word order

Paragraph tokens, '?' dropped, 30,727 within-line boundaries. `tok_excess` is bits of adjacent-token information above a within-line shuffle.

| Policy | Tokens | Length SD | h2 | Cross MI | Token excess |
|---|---:|---:|---:|---:|---:|
| BASE | 34,830 | 1.79 | 2.109 | 0.195 | +0.028 |
| STRICT (commas kept inside words) | 32,368 | 1.85 | 2.123 | 0.163 | −0.049 |
| J1 join every y–q | 31,365 | 3.14 | 2.144 | 0.187 | +0.012 |
| J2 join the d1 top-8 pairs (33% of boundaries) | 24,690 | 4.81 | 2.209 | 0.359 | −0.025 |
| Random joins, same count as J2, 20 reps | | | 2.278 | 0.196 | frac −0.005 |
| PMI>1 bit, fit on even folios, scored on odd | 16,517 | 1.85 | 2.088 | 0.152 | −0.042 |
| Dante, 9-word lines | 97,002 | 2.26 | 3.109 | 0.143 | +0.536 |
| Caesar, 9-word lines | 19,512 | 2.90 | 3.294 | 0.050 | +0.239 |

Pre-registered decision: **INCONCLUSIVE** (neither FAVOUR_RESEGMENT nor FAVOUR_RULE). The direction is against resegmentation. Token excess had to rise by 0.02 of token entropy and h2 had to beat the random-join null by 0.15 bits. The best targeted policy, J1, moved excess from +0.028 bits to +0.012. Dante inside a line is +0.536 bits. Joining the top 8 pairs makes the remaining boundaries more coupled (cross MI 0.359), not less, and pushes length SD to 4.81, which is the verbose-cipher failure already measured in `results_d3.txt`.

## E2. The coupling is a table, not the pair y→q

Plug-in MI is 0.195 bits on the same 30,727 pairs (`results_e2.txt`). Deleting one left-edge context, by replacing its conditional with the marginal:

| Left edge | Share of tokens | MI left after deleting it | Share of the 0.195 |
|---|---:|---:|---:|
| n | 0.166 | 0.114 | 0.418 |
| r | 0.157 | 0.140 | 0.282 |
| y | 0.410 | 0.158 | 0.191 |

y→q is the most common single pair (3,465, 27.5% of words that end in y). It is not most of the information. n prefers c or o (0.292 / 0.291). r prefers o, c, a (0.261 / 0.235 / 0.181). A generator that emits each word on its own still cannot meet this. A generator that stores P(first character | last character) can. That table has not been added to the C2 generator.

## E3. f57v.3 is a 17-glyph refrain

The 68-token circular line is four copies of 17 tokens. Fifteen positions are identical. The raw transcription (`data/ZL3b-n.txt`) is:

`o.l.[d:j].r.v.x.k.m.f.@169;v.t.r.@170;.@171;.y.I.@172;`

and the same string with `f`→`p` and `I`→`c` in the later copies. Position 8 is f, f, p, p. Position 15 is I, c, c, c. None of the 68 tokens matches `qo*edy`. The capital I is in the transcription; this note does not identify the glyph. `results_d6.txt` already showed the glyph period is 18, because `@169;v` is two glyphs inside one token. The "17×4" claim is this one line's tokenisation, not a key for the page.

> Later: the edge table was added in `results_g1.txt` and did not joint-pass. The word-list win in d2 is reconciled in `results_m3_bakeoff_reconcile.txt`. The queue is `TEAM-HANDOFF.md`.

## Best leads after this round

1. **Whole-token lexicon, plus line-edge rules, plus the edge table in E2.** Held-out word unigram beats the induced slot grammar (`results_d2.txt`). Real Naibbe and the copy generators miss the line edges and the edge table (`results_c4.txt`, `results_b4.txt`). Joining tokens does not turn the lexicon into syntactic words (E1). A crack of this lead is an external index that names the frequent types and predicts a held-out quire. Labels do not (`results_d6.txt`, p=0.0945). No such index was tested here.
2. **Generation is still the null, and it is not yet joint.** C2 can be tuned onto within-hand NMI and the ×16 edge multipliers, on separate runs, and still misses h2, the full line-start profile, length SD, and every bit of cross-space MI. E2 says the missing piece is an explicit P(first | last) table. Adding it is the next generator test. It would not be a reading.
3. **Do not spend the next round on topic models or on f57v as a cipher period.** C1's quire null accounts for the hand-2 section score. E3 accounts for the 17×4 claim.

What would revive resegmentation: a join rule, fixed before seeing the score, that lifts within-line token excess from 0.028 bits toward Caesar's 0.239 while holding length SD near 1.8 and h2 near 2.1. J1, J2, comma-joining, and PMI>1 all failed that.
