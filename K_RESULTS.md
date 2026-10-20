> **Historical (superseded 2026-10-17 23:33).** Current state: `README.md` → `workflow/FINDINGS-REPORT.md`. Findings from this file are in `.inventory/registers/`.

# K-series results: joint producers (2026-10-17 16:59 PDT)

Status: **not deciphered.** This round scores whole mechanisms on the whole benchmark at once:
- within-hand section NMI;
- line anatomy from M5;
- edge coupling from C3;
- residual word order from F1;
- h2, word types and hapax share.

Scripts: `k1_joint_producer.py`, `k2_nomenclator.py`, `k3_prefix_flow.py`. Outputs: `results_k1.txt` to `results_k3.txt`.

The line layer follows `results_m5_line_anatomy.txt` (session voynich-08):
- a paragraph-start word drawn from Voynich's paragraph-initial words;
- line-start and line-end preferences, plus a rising share of d-initial words toward line end, applied to whatever free choice the producer has.

Every table and ratio is measured on Voynich. That is circular in the same way as Naibbe's tables and F3's edge table: it tests what a mechanism can carry, not where its tables came from.


> **Superseded in part (2026-10-17 18:30 PDT): residual word order is no longer evidence for meaning.**
> The pre-registered N2 test (`n2_habit_fine.py`, `results_n2.txt`) removed this discriminator. A meaningless generator with a fixed random word-pair habit (p = 0.04) reaches residuals of +0.038 to +0.046 on ZL3b, +0.033 to +0.049 on RF1b and +0.035 on IT2a. That is inside the manuscript's 95% CI in each case, and edge coupling and repeats also pass.
> - The "first producer to hit NMI and residual together" claim (point 2 and the family reading below) therefore no longer counts for content on the residual side. The K2 rows still describe what a nomenclator does.
> - The numbers below are unchanged.
> - The type-budget constraint (point 3) is unaffected.
> - The N2 habit generator still has h2 of about 1.79 (Voynich 2.11) and about 1.8k types (Voynich 7k). N2's h2 check measured whether the gap narrowed relative to p = 0, not whether it matched the manuscript.

## Targets and results

| row | NMI h1/h2 | JSD first, para / other | JSD last | m-fin | cross MI | residual | h2 | types | hapax |
|---|---|---|---|---|---|---|---|---|---|
| **Voynich** | 0.275 / 0.333 | 0.549 / 0.147 | 0.082 | ×16.3 | +0.181 | +0.042 | 2.11 | 7,025 | 0.68 |
| K1 letter cipher (F3) + layer | 0.016 / 0.030 | 0.515 / 0.062 | 0.047 | ×4.7 | +0.217 | +0.065 | 2.12 | 4,971 | 0.50 |
| K1 letter cipher, **different Latin per section** | 0.008 / 0.007 | 0.515 / 0.059 | 0.044 | ×4.8 | +0.217 | +0.060 | 2.12 | 6,009 | 0.40 |
| K1 flow generator + layer (2 seeds) | 0.03–0.22 / 0.18–0.24 | 0.55 / 0.09 | 0.03 | ×4.5 | +0.23 | +0.008 | 1.76 | ~1,900 | 0.37 |
| plaintext Latin, same layout (sanity) | 0.448 / 0.303 | — | — | ×1.0 | +0.027 | +0.232 | 3.32 | 9,044 | 0.60 |
| **K2 nomenclator ×2** | **0.370 / 0.270** | 0.445 / 0.022 | 0.013 | ×2.3 | +0.069 | **+0.045** | 2.51 | 10,471 | 0.51 |
| K2 nomenclator ×8 | 0.135 / 0.042 | 0.431 / 0.097 | 0.079 | ×5.0 | +0.269 | +0.016 | 2.83 | 18,624 | 0.66 |
| K2 null, plaintext shuffled (×4) | 0.003 / 0.010 | 0.443 / 0.049 | 0.038 | ×3.6 | +0.136 | +0.011 | 2.69 | 14,491 | 0.58 |
| K3 stem ×2 + flow-chosen prefix | 0.013 / 0.015 | 0.486 / 0.314 | 0.001 | ×1.0 | +0.174 | +0.003 | 2.87 | 24,690 | 0.78 |
| K3, prefix not flow-chosen | 0.089 / 0.051 | 0.468 / 0.126 | 0.001 | ×1.0 | +0.001 | +0.001 | 2.86 | 24,626 | 0.78 |

## What this round established

1. **A letter-level verbose cipher cannot carry section vocabulary.** Even when each section encrypts different Latin, within-hand NMI is 0.008 / 0.007, because letter codes dilute the topic. The same Latin as plain words gives 0.448 / 0.303. Voynich's section signal therefore needs word-sized meaningful units, or a section-keyed generator. C1 still applies: hand 2's signal is not separable from quire drift, but hand 1 survives.
2. **The first producer to hit section NMI and residual word order together is a homophonic nomenclator.** This is a word codebook with a few codewords per word, chosen to flow from the previous glyph. At ×2 it gives NMI 0.370 / 0.270 and residual +0.045, against Voynich's 0.275 / 0.333 and +0.042. When the plaintext is shuffled, both go to zero, so both come from the meaning. Meaningless generators get the NMI but not the residual. Letter ciphers get the residual but not the NMI.
3. **The binding constraint is the type budget.** More homophones buy edge coupling and line effects (×8: +0.27, line-end JSD 0.079). The price is a vocabulary of 15–23k types, h2 of 2.7–2.95, and the loss of NMI and residual. Free prefix slots (K3) do the same, and worse. Voynich carries 0.18 bits of edge coupling, topical sections and diluted word order in **7k types with h2 2.11**. No tested mechanism does that.
4. **The line layer takes paragraph starts all the way, and line starts and ends only part way.** Paragraph-start JSD matches (0.43–0.56 against 0.549). Ordinary line starts and ends reach one third to one half of their targets, because a few homophones are not enough choice. That repeats point 3.

## Reading for the three families

- **Meaningless generation:** gets section NMI and edge coupling. It fails residual word order in every form tried: c2, flow, run-copy, now with a layer. The only escape left is a fixed habit table of word pairs shared across the book (untested), which works like a grammar.
- **Letter-level verbose cipher (Naibbe type):** gets h2, edge coupling with flow, and residual. It fails section NMI, even with topical plaintext.
- **Word-level code or language:** the nomenclator gets NMI and residual together, the only class to do so. It fails the type budget when asked to also carry the edge coupling.

The type budget points to a **many-to-one** code. Codewords would be *shared* between plaintext words, so ambiguity keeps the vocabulary small, and the edge-flow choice would fall among existing frequent types. That is the "natural language in a lossy script" family, in which several words collapse to one written form.

## Next

**K4: lossy (many-to-one) nomenclator.** Each plaintext word maps to several codewords taken from a small Voynich-like inventory, with codewords shared across plaintext words, chosen by flow and by the line layer. Sweep the sharing rate. Pass condition: within 25% of Voynich on NMI, residual, cross MI and the line-start JSD, with types at 7k ± 15% and h2 at 2.1 ± 0.15, all on one run. If no sharing rate passes, the type budget counts against every code-type mechanism tested here.
