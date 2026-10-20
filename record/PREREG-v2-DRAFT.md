> **Historical (superseded 2026-10-17 23:33).** Current state: `README.md` → `workflow/FINDINGS-REPORT.md`. Findings from this file are in `.inventory/registers/`.

# Pre-registration: Phase 1 joint family discrimination

Drafted 2026-10-17 16:13 PDT (system clock). Status: **DRAFT** until Phase 0 reports land and the
critic signs; then a frozen hash is recorded at the bottom and the file is not edited again.
Any later change goes in an appendix with a date and reason.

## Hypothesis families

- **L**: a natural language written in an invented, possibly verbose or abjad-style script.
  Voynich words are plaintext words or fixed transforms of them.
- **C**: a codebook / nomenclator / non-syntactic notation. Voynich words index entries in a
  table or list; sequence carries little grammar; content varies by subject.
- **G**: generated text with no content: copy-and-mutate (Timm–Schinner), table-and-grille
  (Rugg), or a slot grammar, plus explicit line-edge rules.

Every corpus is scored by the same pipeline (`scoreboard/score.py` plus
`scoreboard/metrics_new.py`), 25,000-token samples unless a corpus is smaller, seed 20261017.

## Reference corpora

| Class | Corpora |
|---|---|
| Target | Voynich ZL3b EVA; Voynich glyph-collapsed; second transliteration if obtained (GC/IT) |
| L controls | Latin ×2, Italian, German ×2, English (existing); Hebrew, Arabic, Greek, Czech, Occitan, Old French, MHG, Catalan, Turkish, medieval Latin herbal (Phase 0) |
| C controls | nomen_word, nomen_syll, nomen_lines (synthetic nomenclator on a Latin herbal) |
| G controls | c2 section-seeded self-citation (best settings), rugg_grille, markov1, bigram-pseudo-Voynich |
| Other | Lingua Ignota, Enochian, Trithemius, Lullian tables, intuitive gibberish if obtained |

## Metrics and the predictions each family makes

| # | Metric | L predicts | C predicts | G predicts |
|---|---|---|---|---|
| M1 | h2 (char conditional entropy) | 2.8–4.0 | low, template-driven (≤2.5) | low (≤2.5) |
| M2 | Word-length SD | ≥1.9 | small (≤1.8) | small |
| M3 | Immediate word repeats | ≤0.2 % | low–moderate | high (≥1.5 %) |
| M4 | Line-edge JSD first / last | small (≤0.05 prose) | present only if layout rules exist | present only if rules added |
| M5 | Freq–length correlation; top-50 length ratio | ρ ≤ −0.34; ratio ≤0.77 | ρ weak; ratio ≈ 0.8–1.0 | ρ weak |
| M6 | Adjacent-word information (H(w) − H(w|prev)) with given boundaries AND after re-segmentation | high after re-segmentation (≥0.6 bits on top-500 vocabulary) | low at both (≤0.3) | moderate at adjacent, spike at previous line |
| M7 | Information profile shape (adjacent → line → prev-line column → page → section) | steep decay | flat, page/section-level | adjacent + prev-line-column spikes |
| M8 | Within-hand topic NMI vs section (rotation null) | significant | significant | not significant without seeding; with seeding fails M4/M3 jointly |
| M9 | Copy locality: same-column excess over far baseline | ≈0 | ≈0 | ≥5 pp |
| M10 | Lexicon growth: Heaps β; late/early new-type rate | β 0.5–0.7, no saturation | saturation: late/early ≤0.5 | steady β; most new types edit-1 of recent types (≥50 %) |
| M11 | Slot table: product-space occupancy; within-prefix core uniformity | sparse, Zipfian | high occupancy, near-uniform | crowded, edit-1 neighbourhoods ≥95 % |
| M12 | Held-out bake-off winner (bits/token) | Markov/word-unigram | slot model | copy model |
| M13 | Edge-coupling MI across spaces (last glyph → next first glyph) | 0.04–0.15 measured (Caesar 0.037, Dante 0.145; c3, m0); not ≈0 | ≈0 (independent entries; nomen_* 0.03) | ≈0 without an edge table (T&S 0.026); R&T report ~0.2 for Voynich |
| M14 | Hapax share at 10k tokens | 0.65–0.68 measured at matched size (m0); the published 40–60 % does not hold here | low (bounded book) | 0.69–0.72 (m0, m2); weak separator |
| M15 | Moran's I of word length, lag 1 | negative | ≈0 | positive (gibberish-like) |
| M16 | Within-word glyph position bias (mean normalised position entropy) | high entropy | low (slots) | low (slots); G&B: separates Voynich from human gibberish |
| M17 | L→R vs R→L held-out bits/char asymmetry | small | small | Parisel: R→L optimisation in Voynich |
| M18 | Montemurro–Zanette information-vs-scale peak | ~600–800 words | page/section scale | absent or at copy-window scale |
| M19 | **Type budget**: word types at 25k tokens scored jointly with cross-space edge-MI excess (K-round, 2026-10-17 17:02). Voynich: ~5.4k types at 25k (7.0k at 35k) with +0.18 bits. A producer that reaches the edge band only by exceeding the type band fails both. | types in the L control range | bounded by the book | every producer tested so far needs 15–25k types for +0.18 bits |

Note on M6/M7 (added after the research-notes audit; N2 at 18:24 then showed a 4 % word-pair habit reproduces the manuscript's held-out word-order residual, so M6/M7 carry no weight as content evidence): weak adjacent-word information is
reproduced by Naibbe ciphertext, self-citation output and human gibberish, so M6 cannot on its
own separate C from G. It keeps its role as the check on the plan's premise (below) and as an L
discriminator only.

Numeric thresholds above are the planning values. **Before freezing**, each is re-set to the
range actually produced by that family's Phase 0 controls (e.g. L range = min/max over the
natural-language controls; C range = the three nomen_* variants; G range = the generators).
A metric where the three control ranges overlap is retained for reporting but carries no weight.

## Decision rule

For each family F and each weighted metric, Voynich scores **in** if it lies inside F's control
range (extended by 10 % of the range width), **out** otherwise. The critic reports, per family,
the count of in/out and the list of out-metrics.

- **Kill**: a family is retired if Voynich is **out** on ≥3 weighted metrics where that family's
  controls are tight (range width < half the spread across all corpora), and no single parameter
  change in the family's generator/control brings those metrics in without pushing another out.
- **Favoured**: a family is favoured if it has strictly fewer outs than each rival and the margin
  is ≥2 metrics.
- Otherwise: undecided; Phase 2 budget split by (1 / outs).

## Robustness checks required before any verdict

1. Repeat on the glyph-collapsed tokenization and, if available, a second transliteration. A
   metric whose in/out flips between tokenizations is downweighted to zero.
2. Repeat on Currier A and B separately. A verdict must hold in both or be stated as A-only/B-only.
3. Rotation nulls for every page-contiguous label (section, hand, quire), plus quire-aligned
   and bifolio-aligned nulls (Schwartz; Layfield & Davis: one scribe per bifolio, original
   binding was the misbinding). A topic result that dies under the bifolio null is reported as
   physical-neighbourhood similarity, not topic.
4. Labels scored separately from running text (Lindemann & Bowern: labels have higher h2).

## What refutes the plan's premise (PLAN §1)

If M6 after re-segmentation exceeds the bigram-pseudo-Voynich null by the margin that
separates the language controls from that null, the premise that sequence carries little
information is wrong and L becomes primary. An absolute threshold is useless here: after BPE
re-segmentation the null itself scores 0.85 bits (m0), Voynich 1.18, Latin 0.95, Italian 0.90,
so the excess is within-word structure, not word order; the refuter did not fire (m0, e1, f1).

## Freeze record

(To be filled: SHA-256 of this file at freeze, date from the clock, critic's name/run id.)
