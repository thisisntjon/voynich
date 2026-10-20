# Review: "Analyzing the Voynich Manuscript.docx" — verification + extension

Reviewed: 2026-10-17 15:00 (system clock). Source file (read-only, unmodified):
`<home>/Desktop/reverseengineer/Analyzing the Voynich Manuscript.docx`
(1,665,479 bytes). Extracted text: `docx_extract.txt` (215 paragraphs).
New tests: `b1_docx_tests.py` → `results_b1.txt` (stdlib only, seed 20261017),
run on `data/ZL3b-n.txt` paragraph text unless stated.

## Bottom line

**The document gets further than a decipherment claim — it correctly abandons
plaintext-hunting — but it overstates a synthesis as a solution.** Its
checkable section-level numbers mostly verify on local data (below). Its
headline conclusion ("decoded at the structural level" as a table +
self-citation notation system) remains an interpretation, not a demonstrated
result: the document presents no held-out test that separates it from the
rival families already standing in `README.md` / `FINDINGS.md`. My extension
(B1) adds one genuinely new measurement: previous-line copying is
*specifically column-aligned*, yet far too weak (~1.9 pp excess) to be the
dominant generator the document implies.

## What the document is

A long secondary synthesis (forensics, three-slot grammar, Currier/five
scribes, marginalia/cribs, falsifications of Bax/Cheshire, three surviving
model families, dual-mechanism synthesis). Provenance caution: most
quantitative claims cite a single web PDF ("BootLoops") and a 2026
ResearchGate structural analysis; the works-cited list mixes primary
literature (Bowern & Lindemann; Timm arXiv:1407.6639) with Wikipedia and
blogs. All equations were stripped in text extraction, so formula-level
claims (Bayesian evidence, entropy values with missing numerals) are
**unverified** here. Treat exact figures as claims to test, not facts.

## Claim-by-claim verdicts (B1, measured this run)

| Document claim | B1 measurement | Verdict |
|---|---|---|
| Pharma `-edy` ≈ 0.2%; Bio `-edy` dense | I=P 0.52% vs I=B 25.98%, I=S 13.68%, I=H 4.12% | **Verified** (direction + magnitude; 0.52 vs 0.2 = definition/sample gap) |
| Herbal-A Q1 `-edy` = 0.0% | 0.00% in 6 of 9 Herbal-A quires; max 0.23% | **Verified** |
| Herbal-A o-stem 0.69–0.81 early, drifting to e-form | o/(o+e): Q=A 0.733, B 0.899, C 0.798 … Q=O 0.556 | **Partial** — late-quire drop fits; early range exceeded, non-monotonic |
| Bio dominated by qok- + -edy | I=B qo 24.31%, qok 16.25% (both highest), edy 25.98% | **Verified** |
| qo- almost absent in Zodiac labels | Z labels qo 0.29% vs 9–24% in paragraph text | **Verified strongly** |
| Self-citation copies same horizontal position (~28%) | Same-column edit≤1 hit 10.69% vs off-column 8.79% vs far-line 8.80% (n≈31k) | **Effect real, size refuted** — column-specific excess only ~1.9 pp; off-column ≈ far proves alignment matters, not mere recency |
| f57v ring = 17 units × 4 | EVA-char best period 13 (match 0.174); repeated 16-char block exists | **Repetition verified; "17×4" unverified** in EVA terms (glyph units ≠ EVA chars; ring order mixes Cc/Ro units) |
| f49v single-glyph index column | L0 singletons alternate with P0 lines (f, o, r, y, e, k, s, p…) | **Consistent** (qualitative) |
| f116v hybrid charm readings | ZL transcribes only "oror sheey" on f116v | **Untestable** from this transcription |
| Slot inventories (181/175 prefixes…), Bayes factors, NMF alignment | Definitions/equations absent from extract | **Unverified** — what would refute: independent slot induction failing to recover comparable inventories; not run here |
| Under-paint rot/g/fo, Cod. Sang. 754 parallels | Paleographic claims, no image evidence in transcription | **Unverified** here (needs facsimile work) |

Consistent with prior local work (not new): low conditional entropy
(a1: h2 2.13 vs 3.11–3.30 controls), line-edge effects (a2: line-final m ×16,
g ×25; page-first gallows 86%), modest copy locality (a4b matched d=1 ratio
1.30), verbose-cipher word-length problem (a5), homophonic solver negative
with 100% positive control (a6). The document's Bax/Cheshire rebuttals match
the local failure pattern; its "verbose solvers fail held-out pages" claim
parallels a6's null result, though a6 tested a different solver family.

## Where B1 gets further

1. **Column specificity isolated.** a4 showed recent-word similarity; B1's
   off-column control (same previous line, shifted +4..+6 positions) landing
   exactly on the far-line baseline (8.79% vs 8.80%) shows the excess lives
   in vertical alignment. That is the sharpest local support yet for a
   Timm-style visual copying component — and simultaneously bounds it:
   at ~2 pp excess it cannot alone generate the text. Caveat: word-index
   column proxies ink x-position; a facsimile-coordinate test could shrink
   or grow the effect.
2. **Section signature table** (results_b1.txt) turns the document's prose
   table into reproducible local numbers, including the Herbal-A quire series.
3. **f57v quantified**: periodicity scan + repeated-block detection replace
   the bare "17×4" assertion with measurable (if differently-shaped) structure.

> Later files cover this list. f57v is `results_e3.txt` and `results_m1_coordinates.txt`. Slots are `results_d2.txt` and `results_m3_bakeoff_reconcile.txt`. Column position is `results_m1_coordinates.txt`. Topics are `results_c1.txt`. The queue is `TEAM-HANDOFF.md`.

## Highest-value next tests

1. Glyph-tokenized f57v scan (collapse ch/sh/cth… via `corpora.to_glyphs`)
   and per-ring (Cc vs Ro) separation — direct retest of "17×4".
2. Data-driven slot induction (e.g., prefix/core/suffix segmentation by
   positional entropy) with held-out perplexity vs Markov and vs a
   self-citation simulator — the missing bake-off that could actually
   separate "notation system" from "generated pseudo-text".
3. Facsimile x-coordinate column test to replace B1's word-index proxy.
4. Replicate NMF topic↔section alignment locally (needs a matrix library;
   a-scripts already use numpy outside the stdlib venv).

## Reproduce

```powershell
cd voynich
uv run python b1_docx_tests.py
```

Note: the multi-agent literature investigation launched earlier is still
running in the background; this review is independent of it and based only
on the .docx, local files read above, and B1 measurements.
