> Round log for C. Map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md). Numbers live in `results_c1.txt` through `results_c4.txt`.

# C-series results (2026-10-17)

Tests 1 to 4 come from the conclusion of `reports/Voynich decipherment attempts and failures.md`. Each script reuses vparse, corpora, a2, b4 and b5. Each one runs Voynich against a natural-language control and a null. Full output is in `results_c1.txt` to `results_c4.txt`. The three families are **NL** (a natural language in a lossy script), **cipher** (a verbose cipher such as Naibbe) and **meaningless** (structured generation with no message).

## C1: quire-aligned null for the B5 within-scribe signal (`c1_quire_null.py`)

The test permutes section labels among quire-section blocks, using exact enumeration. A second test uses only the quires where a hand writes two sections, with a page-permutation null.

| | hand 1 (H vs P) | hand 2 (B/H/T) |
|---|---|---|
| Voynich, quire-block null | NMI 0.275 vs 0.067, **p = 0.018** (the floor, 1/55) | NMI 0.333 vs 0.209, **p = 0.133** |
| Voynich, inside one quire | quire O: 0.060 vs 0.062, p = 0.36 | quire M: 0.049 vs 0.040, p = 0.38 |
| Section-seeded generator (has a true section effect) | p = 0.018; quire O p = 0.006 | p = 0.010; quire M p = 0.053 |
| Drift generator (null: vocabulary follows page order) | p = 0.22 | p = 0.029 |
| Token-shuffled null | p = 0.53 | p = 0.76 |
| Augustine I–IX vs X–XIII (NL control) | all 84 blocks p < 0.0002; at hand-1 size (11 blocks) p = 0.09 | |

**Favours: meaningless (weakly).** Hand 2's section signal does not survive the quire null. Inside the shared quires, neither hand separates its sections, even though the same test finds a real section-keyed generator (p = 0.006). Hand 1 survives across quires at the minimum attainable p, so this result rests on a single quire boundary pattern. The test is weak at Voynich's size: a real topic change in Augustine reaches only p = 0.09. The result therefore removes evidence for meaning rather than adding evidence against it. The B5 section signal is not separable from quire-level drift.

## C2: section-seeded copy-and-mutate generator plus two line rules (`c2_section_generator.py`)

Generator design:
- Each (hand, section) gets a seed lexicon of L random Voynich types.
- Each word is drawn fresh from the lexicon with probability p_seed. Otherwise it copies a word from the page so far and then mutates it.
- Two explicit line rules apply: p at line start and m at line end.

Targets: NMI 0.275/0.333, p-initial ×15.97 and m-final ×16.55.

| run | NMI h1 / h2 | p-init / m-final | h2 | repeat |
|---|---|---|---|---|
| Voynich | 0.275 / 0.333 | ×16.0 / ×16.6 | 2.09 | 0.87% |
| section ps=0.8 s2 | **0.291 / 0.327** | ×18.7 / ×10.1 | 1.80 | 1.19% |
| TUNED L=200 post s4 | 0.419 / **0.322** | **×20.6 / ×17.0** | 1.82 | 1.43% |
| TUNED s5 / s6 | 0.42 / 0.51, 0.40 / 0.51 | ×16.4 / ×18.9, ×19.2 / ×18.5 | 1.76–1.79 | 1.5% |
| circular (lexicon = real section text) ps=0.6 | 0.319 / 0.304 | ×6.6 / ×5.1 | 2.02 | 0.97% |
| null: global lexicon, no rules | 0.040 / 0.050 | ×1.0 / ×0.9 | 1.72 | 1.86% |
| null: drift lexicon | 0.022 / 0.098 | ×12.4 / ×8.5 | 1.78 | 1.40% |
| NL control: Augustine book NMI 0.155; Dante p ×1.23, m ×0.00 | | | | |

**Favours: meaningless, but only on these two targets.** One run lands on the NMI target and another on the ×16 target. No single run hits all four numbers, and the same settings vary a lot by seed (hand-1 NMI 0.17–0.32). The edge effect appears only because of the explicit rules. With the section lexicon on and the rules off, p-initial is ×0.7 and m-final ×1.05. The generator also misses several things:
- **Line-start profile:** JSD(first, mid) is 0.03–0.04 against 0.17, because the rule enriches p and nothing else, while real lines also enrich y, t and d.
- **h2:** 1.76–1.82 against 2.09.
- **Immediate repeats:** 1.2–1.6% against 0.87%.

Copying spreads rule-made words to mid-line unless the rules are applied after the page is generated.

## C3: cross-space edge coupling (`c3_edge_coupling.py`)

The measure is MI between the last glyph of token i and the first glyph of token i+1, in bits. The null shuffles tokens within each line. Our definition is a reimplementation from the abstract and has not been checked against the paper's method.

| text | EVA MI | excess over null |
|---|---|---|
| Voynich, all | **0.195** | +0.181 |
| Voynich, Currier A / B | 0.146 / 0.249 | +0.120 / +0.232 |
| Voynich, uncertain spaces joined | 0.163 | +0.148 |
| token-shuffled null | 0.006 | −0.001 |
| b4 self-citation (4 variants) | 0.011–0.022 | −0.003 to +0.002 |
| c2 generators (5 variants, incl. TUNED and circular) | 0.005–0.007 | −0.001 to +0.001 |
| prose controls: Latin ×2, German ×2, English | 0.049–0.125 | +0.036 to +0.106 |
| Dante (Italian verse) | 0.156 | +0.145 |

**Favours: NL or cipher, against every meaningless generator tested.** Voynich reproduces the published figure of about 0.2 bits. Its A and B values are close to the 0.130 and 0.243 figures in our notes, though whether those figures are for A and B is unverified. Voynich is above every prose control. Every copy-and-mutate generator gives zero, including the one that passed C2, because it picks each word without regard to its neighbour's edge. Joining uncertain spaces lowers the coupling, but it stays at the top of the control range. A generator with an explicit rule linking each word to the previous word's last glyph might close the gap. None has been tested. So the gap points to structure across spaces, such as tokens that are not words, or syllable or cipher groups.

## C4: Naibbe ciphertext through a2, B4 and C3 (`c4_naibbe_lines.py`)

Source: Greshko's supplementary files, [Zenodo 17219445](https://zenodo.org/records/17219445). Only `Naibbe Cipher.xlsx` (17.1 MB) and the Supplementary Materials PDF (2.6 MB) were downloaded, both md5-checked against Zenodo, into `data/naibbe_zenodo_17219445/`. The macro-enabled `Voynichesque.xlsm` was skipped. The input is the workbook's cached run: 20,923 tokens and 4,733 types, encrypted from the "Four-Text Sampler" plaintext (Dante, Pliny, alchemical herbal, De sphaera). Naibbe outputs an unbroken stream, so the script imposes lines two ways:
- poured into Voynich's real page and line lengths;
- wrapped at 50 characters, Voynich's mean line length.

| text | JSD first-glyph (first vs mid) | JSD last-glyph (last vs mid) | p-init | m-final | h2 | repeat | edge-coupling excess |
|---|---|---|---|---|---|---|---|
| Voynich | 0.176 | 0.082 | ×16.0 | ×16.6 | 2.09 | 0.87% | +0.181 |
| Naibbe, page skeleton | 0.0007 (null 0.0012) | 0.0011 (null 0.0009) | ×0.89 | ×1.14 | 2.08 | 0.18% | +0.002 |
| Naibbe, 50-char wrap | 0.0032 (null 0.0011) | 0.0009 (null 0.0010) | ×0.77 | ×0.96 | 2.08 | 0.19% | +0.002 |
| null: Naibbe tokens shuffled | 0.0006 | 0.0010 | ×1.01 | ×1.17 | 2.08 | 0.39% | −0.001 |
| NL control: Dante (verse) | 0.034 | 0.167 | ×1.23 | ×0.00 | 3.11 | 0.05% | +0.145 |

**Favours: nothing for the cipher family as Naibbe stands; against Naibbe as the mechanism.**
- Naibbe matches Voynich's h2 (2.08 against 2.09).
- It shows no line-edge effect in either layout: p and m stay at ×0.8–1.2, and glyph JSDs sit at null level.
- Its edge coupling is detectable (z ≈ 5) but about 1% of Voynich's, so it fails C3 like every meaningless generator.
- Its immediate-repeat rate is a quarter of Voynich's.
- Side finding: wrapping at a fixed width alone gives a line-initial *length* JSD of 0.019, close to Voynich's 0.022. So the a2 length effect is not evidence of anything beyond layout, while the glyph effects are.

This matches the published criticism that Naibbe "does not produce line effects". To reach the benchmark, Naibbe would need explicit line rules, as the C2 generators do, plus whatever produces the C3 coupling.

## Net

- **C1 and C2** make meaningless generation more economical for section vocabulary and line edges, though only with explicit line rules and a lot of tuning.
- **C4:** Naibbe gets h2 right and nothing else on the line tests.
- **C3** is the hardest target. Voynich's tokens share about 0.2 bits across each space, more than any prose control. No meaningless generator produces this, and neither does the one available verbose cipher (Naibbe reaches about 1% of it).

So no tested mechanism, meaningless or cipher, matches the whole benchmark. The test that separates the families best is edge coupling, and the natural-language controls are the only texts that come close on it: Dante +0.145 against Voynich +0.181. That favours a natural language in a lossy script, or some encoding in which spaces fall inside the units of meaning. It does not supply a key.

Caveats:
- C1 has low power.
- The C3 definition is our own reimplementation.
- All results rest on the ZL transcription's word boundaries and the current folio order.
- b4's generators vary between runs because of hash-seed ordering. The c-scripts sort the neighbour lists in-process, so their numbers repeat; b4 itself is unchanged.
- B5's Augustine control included the table of contents and about 875 chunks of end-notes labelled as book XIII. C1 uses only the main text. B5 was not re-run.
