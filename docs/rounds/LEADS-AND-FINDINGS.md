> Current map: [TEAM-HANDOFF.md](TEAM-HANDOFF.md). Historical consolidation. The sentence "all rotation-null p=0.000" does not match `results_c1.txt`.

# Voynich manuscript — all leads and useful findings

Consolidated: 2026-10-17 15:17 (system clock). Source project (unchanged):
`.`. Data: ZL IVTFF EVA transliteration
v3b (`data/ZL3b-n.txt`, copied in this package); paragraph units (P*) unless
stated; 34,857 tokens / 7,025 types (analyze.py) or 25k-token samples (a/b
scripts). Controls: Gutenberg Latin/Italian/German/English (see README.md).
Status vocabulary: **Verified** = measured locally this project; **Literature**
= opened-source finding from multi-agent investigation; **Unverified** =
asserted but not opened/measured. Headline: **not deciphered.**

## Start here (reading order)

1. `README.md` — a1–a7 battery with controls (parallel session, complete).
2. `FINDINGS.md` — independent battery + simple-substitution falsification.
3. `INVESTIGATION.md` — how close others got and why (multi-agent, partial).
4. `DOCX_REVIEW.md` + `results_b1.txt` — audit of the .docx synthesis.
5. This file — every lead in one place, with next tests.

## A. Hard constraints (any theory must satisfy all)

| # | Finding | Evidence | Status |
|---|---|---|---|
| A1 | Char conditional entropy h2 ≈ 2.13 bits vs 3.11–3.30 (Latin/Italian/German/English); digraph collapse only 2.26–2.40 | results_a1.txt; FINDINGS H1 2.32 | Verified |
| A2 | Word-shuffling leaves h2 exactly unchanged; within-word char shuffle costs +1.48 bits vs +0.59–0.77 controls → anomaly lives inside words | results_b3.txt C4 | Verified |
| A3 | Line is a structural unit: first-glyph JSD 0.176 (null 0.002; verse 0.034); line-initial p ×17.9, t ×5.1; line-final m ×16, g ×25; page-first gallows 86% vs 19% | results_a2.txt | Verified |
| A4 | Currier A/B real: char JS 0.0168 vs 0.00019 split-half (~88×); vocab Jaccard 0.159 | FINDINGS; results_a1 (A/B rows) | Verified |
| A5 | Word-final restriction extreme: n 99%, m 97% word-final; controls max ~66% | results_b3.txt C3 | Verified |
| A6 | No function-word stratum: freq–length ρ −0.25 vs −0.34…−0.41; top-50 length ratio 0.82 vs 0.60–0.77 | results_a7.txt | Verified |
| A7 | Word lengths too uniform (SD 1.76 vs 1.95–2.91); immediate repeats 0.90% vs 0.00–0.16% | results_a1.txt | Verified |
| A8 | Zipf/vocab/hapax in natural range — but Markov gibberish matches too; proves little alone | FINDINGS; results_a1 | Verified |
| A9 | Radiocarbon parchment 1404–1438 CE; period inks; N. Italian / S. German-Alpine milieu | INVESTIGATION; DOCX_REVIEW | Literature |

## B. Dead ends (falsified — do not retry without new assumptions)

| # | Ruled out | How | Status |
|---|---|---|---|
| B1 | Monoalphabetic substitution, English-like plaintext (EVA 1-to-1) | Solver recovers control perfectly (−2.254 vs −2.261 identity); Voynich −2.482, gibberish | Verified (FINDINGS) |
| B2 | Homophonic letter substitution → Latin/Italian/German (BPE k=0/8/20, spacing kept) | 100% positive control; Voynich at wrong-language/null levels (−3.7…−4.2 vs ceilings −2.5…−3.1) | Verified (a6/a6b) |
| B3 | Polyalphabetic flattening | Char IC 0.0766 above English 0.0628 | Verified (FINDINGS) |
| B4 | Claimed readings: Newbold, Bax, Gibbs, Cheshire, Alberta-Hebrew, LLM claims | Fail blind fixed-key test; excess degrees of freedom | Literature (INVESTIGATION) |
| B5 | Letter-verbose cipher with Voynich words = plaintext words | Reaching Latin h2 needs ~53–57 units at 2.5 units/word → syllables/code fragments, not letters | Verified (a5) |

## C. Live leads (ranked by discriminating power)

### C1. Joint burden nobody meets: position + A/B + topics together ⭐ next test
Real text simultaneously shows A3 position effects, A4 dialect/hand split,
and NMF topic alignment NMI(illus) 0.379 / NMI(hand) 0.375 / NMI(lang) 0.346,
all rotation-null p=0.000, including *within-hand* section alignment
(hand 1: 0.275; hand 2: 0.333). Self-citation simulators reach only
0.05–0.13 and ~0.00–0.03 within hand 1; shuffled null ~0.01
(`results_b5.txt`). **Lead:** one pre-registered blind scoreboard on all
three families at once vs self-citation / gibberish / shuffled controls.
Caution: Augustine control shows contiguous-drift can inflate topic NMI
(rotation p=0.575) — rotation nulls are mandatory.

### C2. Pure self-citation is insufficient (needs extra machinery)
Simulators without positional rules produce JSDfirst ≈ 0.001–0.005 vs real
0.172, p-initial ×~1 vs ×16.0, m-final ×~1 vs ×16.6, while over-repeating
words (2.2–6.0% vs 0.87%) (`results_b4.txt`). Any generation story must add
explicit line-edge rules — at which point it starts resembling a notation
system. **Lead:** minimal added rules that jointly fit B4 + B5 metrics;
count free parameters against fit gain.

### C3. Column-aligned copying (small but specific)
Same-column previous-line edit≤1 hits 10.69% vs off-column 8.79% vs far-line
8.80% (n≈31k; `results_b1.txt` T2). Off-column = far baseline proves vertical
alignment, not recency. Excess only ~1.9 pp — a component, not the engine.
Local near-copy ratios (a4b matched d=1 1.30, W=10; shrinks to 1.08 at W=40)
agree. **Lead:** facsimile x-coordinate version (word-index is a proxy).

### C4. Second-order slot grammar (beyond bigrams)
P(gallows|qo-)=0.841 vs P(gallows|o-)=0.565 in real text; bigram pseudo-text
0.403 vs 0.417 — the prefix class carries information bigrams cannot
(`results_b3.txt` C2). q→o binding 0.977 is bigram-trivial (null identical).
Edit-1 neighbourhoods: 97.2% of top types have a neighbour (null 84.1%).
**Lead:** data-driven slot induction + held-out perplexity bake-off:
slot model vs Markov vs self-citation simulator (the missing separator).

### C5. Vowel/consonant structure does not emerge
2-state HMM recovers vowels perfectly on Latin (acc 1.000); on Voynich
partitions are unstable (6–11/20 restarts) and final/non-final-flavoured
(AUC 0.58–0.67 EVA); Sukhotin vowel sets flip with/without spaces
(`results_b2.txt`). Supports non-phonemic or heavily templated encoding.
**Lead:** repeat on glyph+ tokenization with stability selection; compare
against syllabic-script controls (none tested yet — gap).

### C6. Section signatures (docx claims mostly verified)
Pharma -edy 0.52% vs Bio 25.98%; Herbal-A -edy 0.00% in 6/9 quires; Bio
qo 24.31%/qok 16.25% highest; Zodiac-label qo 0.29% vs 9–24% prose
(`results_b1.txt` T1). o→e quire drift only partial. **Lead:** test whether
prefix classes (qo-/ot-/ol-) behave as section operators vs topic vocabulary
via within-hand, cross-section migration analysis.

### C7. Labels and key-like pages
Label-in-own-page hit 12.1% vs null 10.7±1.0% (p≈0.11, only 40 pages —
underpowered; `results_a3.txt`). f57v: EVA-char best period 13 + repeated
16-char block; "17×4" unverified in EVA terms. f49v single-glyph column
consistent qualitatively. f116v charm untestable in ZL (only "oror sheey").
**Leads:** glyph-level per-ring f57v retest; larger label test; facsimile
work on f49v/f57v/f66r/f116v marginalia (rot/g/fo, Cod. Sang. 754 — all
**Unverified** locally).

## D. Open families (all still standing)

1. Unknown natural language in invented/non-phonemic script (syllabic,
   abbreviation-based, abjad readings untested).
2. Codebook/nomenclator or verbose encoding where Voynich words ≠ plaintext
   words (removes letter statistics by design; hardest to refute).
3. Generated templated pseudo-text (slot table + copying + line rules).
Languages untested by solvers: Hebrew, Arabic, Czech, Occitan, Greek.
Cipher families untested: transposition, nulls, broken word spacing.

## E. Proof standard (what "cracked" must mean)

Fixed key + named language reading long continuous text (formulation: 10
consecutive pages), manuscript-wide across A/B, hands, sections, labels;
fails on shuffled/gibberish controls; held-out prediction; shared code/data;
expert sign-off (`INVESTIGATION.md`). Nothing published or local meets it.

## F. Package inventory

Reports: README.md, FINDINGS.md, INVESTIGATION.md, DOCX_REVIEW.md, this file.
Code: vparse.py, corpora.py, analyze.py, a1–a7 (+a4b/a6b), b1–b5,
tests/test_voynich.py, pyproject.toml. Results: results_a*.txt,
results_b*.txt, results/results.json + summary.md. Data: data/ZL3b-n.txt
(controls are Gutenberg texts listed in README.md, not copied).
`MANIFEST.sha256` hashes every copied file; source folder left unchanged.
Run (stdlib parts): `uv run python analyze.py`, `uv run python b1_docx_tests.py`;
a/b scripts need numpy (`python aN_*.py` per README.md).
