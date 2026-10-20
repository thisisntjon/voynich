> Round log for G only. H1 is `results_h1.txt`. F4 is `results_f4.txt`. Map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md).

# G-round results (2026-10-17 16:08)

Executed `RESEARCH-PLAN.md`. Status: **not deciphered.** No config joint-passes
the frozen PREREG v1 bands. Generation is not retired: the best held-out run
clears both kill floors (cross-space excess above +0.05 and first-glyph JSD
above 0.05). A partial pass retires nothing, and no third rule was added.

`scoreboard/scoreboard.json` still has `reproduction_pass=true`. The original
Voynich row is unchanged (h2 2.1262).

## Filed streams on the frozen board (`results_g0.txt`)

All five fail. Bands: h2 1.98–2.28, length SD 1.41–2.11, first-glyph JSD ≥ 0.10,
p-initial ≥ ×8, m-final ≥ ×8, cross-space excess ≥ +0.09, repeats 0.4–1.8%.

| Entrant | h2 | SD | JSD | p | m | excess | redup % | Misses |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| C2 tuned L=200 post s4 | 1.805 | 1.640 | 0.036 | ×21.6 | ×16.8 | +0.001 | 1.50 | h2, JSD, excess |
| b4 SIMcal global | 1.892 | 1.704 | 0.001 | ×0.99 | ×0.91 | −0.001 | 2.24 | all but SD |
| b4 SIMcal seeded | 2.010 | 1.876 | 0.004 | ×1.58 | ×1.09 | −0.001 | 3.15 | JSD, p, m, excess, redup |
| Naibbe skeleton | 2.080 | 1.618 | 0.001 | ×0.90 | ×1.18 | +0.002 | 0.19 | JSD, p, m, excess, redup |
| D3 verbose seed 1 | 2.479 | 4.088 | 0.001 | ×0.97 | ×0.88 | +0.005 | 0.37 | all seven |

C2 still has the line-edge multipliers and none of the cross-space excess.
Naibbe still has the entropy and none of the position.

## F1 re-run (`results_f1.txt`)

The script on disk already scores a shuffle-corrected residual. The old
result file's "12.07×" and "FAVOURS EDGE-RULE" line were from the uncorrected
residual. The re-run, including the top-100 and top-300 class rows:

| Vocabulary | Voynich residual excess | Smallest prose excess | Verdict |
|---|---:|---:|---|
| Whole words | +0.041 | +0.167 (Augustine) | INCONCLUSIVE |
| Top 100, else `<first.last>` | +0.024 | +0.105 | INCONCLUSIVE |
| Top 300, else `<first.last>` | +0.042 | +0.141 | FAVOURS LANGUAGE |

On whole words the absolute previous-word model is still worse than the
unigram (10.386 vs 10.255 bits). The +0.041 is only how much less worse it is
than a shuffle. Alice's residual excess on the same definition is +0.417.
The top-300 language flag clears 0.25× the smallest prose residual by 0.007
bits. It is not a reading, and it was not used to change G1.

## G1 (`results_g1.txt`)

Nine configs, declared before the run. Edge table fit on 166 train pages
(23,165 pairs, 19 contexts with count ≥ 5, 213 cells). Rejection sampling,
0 fallbacks out of 34,857 draws. Line rules are C2's filed 0.088 and 0.148,
applied after the line. They do not edit the characters inside a within-line
edge pair.

Reported seed lexicon, L=200, seed 20261017, held-out (8,586 tokens):

| Band | Value | |
|---|---:|---|
| h2 | 1.595 | miss (below 1.98) |
| SD | 1.562 | pass |
| JSD | 0.080 | miss |
| p / m | ×541 / ×17.4 | pass |
| excess | +0.100 | pass |
| redup | 2.75% | miss |

The other five seed draws miss the same three bands. The edge filter is doing
its job. The 200-type list is too repetitive, and painting `p` on line starts
does not reproduce the rest of the line-start profile. Several seed draws
have no mid-line `p` at all, so the enrichment ratio is infinite while JSD
stays under 0.10.

Reported circular lexicon, same seed, held-out:

| Band | Value | |
|---|---:|---|
| h2 | 1.935 | miss (1.98) |
| SD | 1.734 | pass |
| JSD | 0.099 | miss (0.10) |
| p / m | ×118 / ×8.75 | pass |
| excess | +0.104 | pass |
| redup | 0.68% | pass |

The same run on the full skeleton passes h2 (2.030) and JSD (0.110) and
misses only m-final (×7.43 against ×8). The other two circular seeds do the
same: held-out misses h2 and JSD by a few hundredths; full misses only m-final.

## Branch

The circular list does not joint-pass. The bands that break are held-out h2
and held-out first-glyph JSD on an 8,586-token sample, and full-skeleton
m-final. The seed list also misses repeats. No external-index test: that
branch required the circular list to pass. No further rule in this round.
