# Phase 4 investigation: is EVA hiding the units a reading needs?

Stamped 2026-10-17 22:17 PDT (from `date`). Investigation only. No board, entrant or run_v2 runs, and nothing was downloaded.
The exploratory script and its output are in the session scratchpad:
`.../scratchpad/p4_units/units_check.py` and `units_check.out`. Those numbers are **exploratory, not pre-registered**.
Web pages were read as data only. Any claim I did not open the source for is marked *unverified*.

## 0. Short answer

**No: EVA is not what is hiding a reading.** The evidence:

1. Changing the alphabet only moves character-level metrics. On 131 common paragraph pages, h2 runs 2.09 (EVA), 2.29 (FSG), 2.34 (Currier), 2.35 (Rozanova–Temerev composite-collapsed EVA), 2.49 (v101) and 2.91 (an aggressive 49-unit verbose set). A Latin control on the same metric is 3.37. Word-level metrics are invariant by construction, because every alphabet keeps the same spaces. Zipf slope stays at −1.04 to −1.08, the hapax share at 0.67 to 0.70, and the coupling stays positive under every alphabet (+0.145 to +0.225).
2. The "0.158 to 0.493" swing is mostly an artefact of the split rule, not hidden structure. Splitting words raises the across-space coupling whatever the cut points are:

   | Split | Coupling before | Coupling after |
   |---|---|---|
   | s30 regex rule, Voynich | +0.173 | +0.450 |
   | Random cuts, same count, Voynich | +0.173 | +0.733 |
   | Random cuts, Latin Caesar | +0.046 | +0.143 |

   A split moves within-word glyph dependence across a "space", and the within-line shuffle then credits it as coupling. Also, `IntraWord_Lift_Split` in `s30_phase2_u2_u3_deltas.py` (lines 256–265) is a regex on EVA text: split before ch/sh/k/t/p/f after [aeiodylrn]. **It is not an ink measurement**, although the handoff calls it the "o1 ink" row. The same loader also deletes `{...}` ligature contents (line 236), while `vparse.py` keeps them. That is a small discrepancy between the board parser and s30.
3. The merge direction is the meaningful one, and it is small. Merging the commas lowers the coupling by about 16 % (+0.173 to +0.145 here; +0.192 to +0.158 in s30). It stays about 3× the Latin pseudo-line value.

**What could still change the picture** is the space layer, not the glyph layer: which "words" are really one word or two. That is a token-boundary question with a cheap, decisive test (§3). Ink-level stroke units are not measurable at the resolution held locally (§2).

## Ranked leads

| Rank | Lead | Why this rank |
|---|---|---|
| 1 | Spaces (§3) | Only lever that moves word-level metrics; decidable cheaply with data on disk |
| 2 | Alphabet bake-off (§1) | Fully offline, 1 session; bounds A9 but cannot rescue a letter reading |
| 3 | Davis hands (§4) | Already in the metadata; mostly done; one confound to report |
| 4 | Ink-derived units (§2) | Resolution floor locally; large human cost; lift ban only as bounded pilot |
| 5 (new) | Bounded BPE unit scale on board metrics (§5) | Rozanova–Temerev trough at 32–64 merges is the best-evidenced "verbose unit" inventory |

---

## 1. Alternative alphabets

**Prior art**
- Zandbergen's transcription overview and the IVTFF files: http://www.voynich.nu/transcr.html and http://www.voynich.nu/extra/sp_transcr.html. URLs are from the local `000_README.txt`; I did not open the pages.
- Lindemann & Bowern 2020/2021: local PDF at `data/external/bowern-lindemann-entropy/`. They compare a Maximal (≈EVA) and a Minimal (Currier-collapsed) transcription. Minimal h2 averages about 2.48, and they conclude that the low h2 is "not attributable to a particular script or transcription system" (local text, lines 30 and 863).
- Rozanova & Temerev 2026, https://arxiv.org/abs/2608.17096 (local copy: `data/external/papers/`):
  - Composite-collapsed EVA h2 is 2.69, against 3.45–3.52 for the controls, in their own metric (it differs from ours).
  - Within-token BPE has a dependence trough at 32–64 merges, about 88 units of mean span 2.4.
  - Early units are ol, ok, ar, ot, aiin, ch, qok. The units are stable across quires (median overlap 84 %).
  - All of the units are legal under Zattera's slot grammar, and a third of their occurrences cross Stolfi's layers.
- Bennett-style units and Cuva: not checked (*unverified*). No Cuva file is local.

**Prior evidence for a specific verbose mapping.** None independent. The only data-driven inventory is the R–T BPE set, and it is explicitly "not a privileged universal inventory". The aiin/ch/sh/qo-as-unit sets in the literature are paleographic conventions (Currier, Lindemann–Bowern Minimal), not results.

**Finding (exploratory, this session).** The local files are ZL3b, IT2a, CD2a (Currier), FG2a (FSG) and GC2a (v101). Only 131 paragraph pages are common to all five, because CD2a is partial. Of the five, only EVA, glyph+ and v101 were on the board in s30. Currier and FSG were never scored.

Raising h2 into the language range needs an inventory of about 50 or more units, with a mean of 2.8 units per word. That is the verbose-cipher hypothesis by construction, not evidence for it.

**Smallest pre-registerable test (P4-U2 (alphabet bake-off)).**
- Corpus: the 131 common pages.
- Alphabets, fixed in advance:

  | Alphabet | Units |
  |---|---|
  | EVA (ZL3b) | native |
  | FSG (FG2a) | native |
  | Currier (CD2a) | native |
  | v101 (GC2a) | native |
  | R–T composite-collapsed | cth, ckh, cph, cfh, ch, sh, iin, in, ee |
  | BPE-64 | merges learned on the odd quires, scored on the even quires |

- Metrics: h2, h3, mean and sd of word length in units, Zipf slope, coupling, JSDf and Moran I.
- Comparison: each value against the CREMMA and real-line control ranges already on disk.
- Decision rule, written before the run:

  > EVA is "hiding structure" only if some alphabet moves **two or more** of {coupling, JSDf, Moran} outside the s15 within-manuscript width, in the direction of the language range. Otherwise A9 stands as written ("units change entropy, not the anomalies").

  The prediction from this session's numbers is a null.

**Cost and what is human-only.** About 1 agent-hour, fully offline. Nothing is human-only.

## 2. Ink-derived units (pen-lift, stroke, gap)

**What is local** (`data/facsimile/MANIFEST.tsv`):

| Folio | Pixels | Resolution |
|---|---|---|
| f57v | 3028×3769 | native |
| f1v, f75r, f99r, f116v | 2000 px wide | downscaled |
| f68r | 2400×1150 | downscaled |

The o1 numbers imply a word box about 20 px tall: a certain space is 4.79 px at a normalised 0.240. At that scale the "intra-word lift" tier of 0.021–0.068 box heights is **0.4–1.4 px**, which is at or below the pixel floor on the 2000 px images. **Inference (unverified):** o1's three-tier hierarchy is real for the space tiers, but the lift tier cannot be measured reliably from the local files. The pixel scale is derived from o1's printed means, and I did not re-measure it. The 283 o1 Part A sites are R–T's archived `results_unblinded.csv`, not our own measurement.

Beinecke IIIF serves `full` native size per canvas (f57v proves it). Native scans are therefore about 1.5× the local 2000 px files, at roughly 400 ppi on the page. This ppi figure is an estimate from page size (*unverified*).

**Tools and prior art**
- kraken: https://github.com/mittagessen/kraken. It is line-level, segmentation-free recognition, so it learns to transcribe and does not give stroke boundaries.
- eScriptorium: https://gitlab.com/scripta/escriptorium. A ground-truth and line-segmentation front end.
- CREMMA shows the ALTO export path (`workflow/research/phase-1-cremma.md`).
- Bernasconi & Ferilli, CNN glyph classification on about 6k extracted symbols (IRCDL 2024; https://www.mdpi.com/2078-2489/16/2/119). Seen in search results only, not opened (*unverified*).
- R–T's blind direct-pixel pipeline (local: `word-coordinates/lrozanova-voynich-units-main/.../analysis/direct_pixel/`, OpenCV).
- A published Voynich kraken/HTR model: **none found** in two searches (*unverified absence*). I found nothing that matches a "2024–2026 Voynich OCR" effort with released models.

**Smallest pre-registerable test (pilot).** One question: are ZL `,` separators physically intermediate, and does a pixel-derived boundary class re-split tokens differently from ZL?
- 30 folios, chosen in advance and stratified by Davis hand × section. Use the native IIIF `full` size.
- Reuse R–T `measure_direct_pixels.py` blind, at the word-box boundaries already in `word-coordinates`.
- Outcome: the gap distribution per boundary, then a 2-component mixture.
- Kill rule:

  > If the pixel classes agree with ZL `.`/`,` at κ ≥ 0.6 and the re-tokenised stream moves no board metric outside s15 widths, close O-048.

- Intra-word stroke and lift segmentation is excluded from the pilot (resolution floor above).

**Cost**
- Download: 30 × about 3–4 MB, about 120 MB. It needs Jon's go-ahead, because the handoff forbids downloads unless a measurement names the folio. The pre-registration would name them.
- About 1 agent-day for the pipeline and QC.
- **Human-only:** about 2–3 h of blind spot-labelling of about 300 boundaries, so the classifier has independent ground truth. The download approval is also human-only.
- A full HTR model (kraken), with about 30 pages of line ground truth at about 1 h per page, is human-heavy and **not recommended**. It would reproduce EVA's own unit decisions.

## 3. Spaces (`.` vs `,`, and "two words written as one")

**Best evidence**
- R–T 2026: uncertain separators behave like word-internal junctures (internality 0.494 against 0.029 for certain separators). They are physically narrower (AUC 0.905 from independent coordinates, with a blind ink audit of the same sign). ZL and v101 agree on 93.1 % of separator labels (κ 0.31). Merging all uncertain spaces does not repair the low token order (0.79 % → 0.54 %).
- Our o1: the `,` gap is 0.163 against 0.240 for `.` (n = 21 only).
- This session: merging the commas costs 16 % of the coupling, and every anomaly survives.
- Line-length and justification: R–T report that gradients by line length disappear on middle-length lines. A voynich.ninja claim says spaces after r/s compress near line end (forum, *unverified*; e.g. https://www.voynich.ninja/archive/index.php/thread-5612.html).

**Decisive test (P4-U1 (space regimes)).** Pre-register two predictions that separate "a `,` is a word-internal juncture" from "a `,` is a real space squeezed by justification".
- **P1 (justification).** If commas are compressed real spaces, their rate rises over the last 25 % of the line, adjusted for line length and position. The comparison is the same position on lines that end in a long final word. If commas are junctures, their rate is flat in position.
- **P2 (lexical).** For each `A,B` pair, check whether the joined `AB` occurs elsewhere as an ordinary space-free token, and whether `A` and `B` occur alone. Count each case at a rate above a frequency-matched null.
- Verdict:

  | Result | Meaning |
  |---|---|
  | P2 high, P1 flat | junctures, so merge |
  | P1 positive, P2 at null | real spaces, so split |

- Run the board metrics under the winning convention only.

Cost is about 1 agent-hour, using ZL3b and GC2a on disk. Nothing is human-only.

## 4. Davis's five scribes instead of Currier A/B

**Prior art.** Davis 2020/2021, *Manuscript Studies* 5(1): https://repository.upenn.edu/mss_sims/vol5/iss1/6. I saw this in search results and did not open it. Commentary reports five scribes, with Scribe 1 writing 113 pages.

**Metadata.** The per-folio list **is already in the transliterations**: IVTFF page variable `$H`, with Currier's hands in `$C` (`000_README.txt`). The ZL3b page counts by `$H` value are:

| `$H` | Pages |
|---|---|
| 1 | 113 |
| 2 | 46 |
| 3 | 33 |
| 4 | 27 |
| 5 | 7 |

`vparse.py` already reads it, and s33 and s35 already stratify by hand. "Use Davis hands" is therefore mostly done.

**Does it matter? (exploratory)** The coupling by hand is:

| Hand | Currier language | Coupling |
|---|---|---|
| 1 | A | +0.120 |
| 2 | B | +0.242 |
| 3 | B | +0.238 |

The A/B coupling split is a hand-1 versus hands-2/3 split. Hand and language are confounded for the main hands. Hands 4 and 5 fall below 1.5k paragraph tokens.

**Smallest test.** A crossed design in s20 style, coupling and JSDf by (`$H` × `$L`), keeping only cells with more than 1.5k tokens. The question is whether any hand has both A and B pages and, if so, whether its coupling follows the hand or the language. If no such cell exists, report "A/B and Davis hands not separable for A3" and stop.

Cost is about 30 minutes, offline. Nothing is human-only.

## 5. New lead: BPE unit scale on our metrics

The R–T BPE-32/64 inventory is the best-evidenced verbose-unit set: data-driven, quire-stable and cross-fitted. It is already folded into the §1 bake-off as the sixth alphabet. No separate project is needed.

## 6. The "glyph-segmentation" ban

**Where it comes from.** The ban is D-017 (16:58), a list of scope guards against open-ended side projects with no evidence row. It conflicts with FINDINGS §6 and CONSTRAINTS-MAP §C, which list O-048 (an ink-driven token stream) and the pixel-derived boundary test as open.

**Recommendation.**
- **Keep the ban** on any glyph or stroke segmentation project, HTR model training, or new alphabet design.
- **Lift it narrowly** for three bounded, pre-registered checks:
  - P4-U2, the alphabet bake-off on existing files (§1);
  - P4-U1, the space-regime test on existing files (§3);
  - only if P4-U1 is inconclusive, the 30-folio boundary-gap pilot (§2). The pilot measures only space and boundary gaps at existing word-box edges, needs Jon's go-ahead for about 120 MB of named IIIF downloads, and has the κ kill rule.
- Reword D-017 to "no open-ended glyph/stroke segmentation; boundary-gap pilots under a named prereg are allowed".
- Separately, fix the handoff label: s30's `IntraWord_Lift_Split` is a text regex, not an ink row. Its +0.493 should not be cited as evidence that segmentation hides structure.
