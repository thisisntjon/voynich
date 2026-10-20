# Transcription-free glyph units from the Yale scans (Phase 7.4 part 2, D-069)

Status: **design and prototype only**. Nothing here is a result. No claim is filed, no run id is taken, and no
register, graph, PLAN or TEAM-HANDOFF entry was edited. The lead freezes the design (section 4) in D-066 after
review, and only then does the full run start.

Written 2026-10-18 17:30 PDT (time from `date`). The prototype ran 17:24:29 to 17:29:34 PDT.

## 1. Question

Can the units of the script be decided from the images alone?
- X-01 (at-risk): are EVA's units, and the prefix/core/suffix slots built on them, units of the script?
- O-056: can a physical line discharge X-01 for F-34, F-39 and F-40?
- Gap 2 of `.inventory/runs/2026-10-18/audit-completeness_gap.md`, plus gap 5: do the Davis 2020 scribes
  separate by glyph shape alone (X-08, O-020)?

## 2. What is on disk

| Path | What |
|---|---|
| `tools/physical/glyph_prototype.py` | prototype pipeline (segmentation, labels, SimCLR embedding, k-means, gates) |
| `data/physical/glyphs/prototype/20261018T172429/` | the prototype run: `gate.txt` (printed gates), `params.json` (pages and parameters), `words.tsv` (per-word counts), `units_B.tsv` + `crops_B.npy` + `emb_B.npy` (16,816 level-B units, 48x48 crops and 64-d embeddings) |
| `data/physical/glyphs/prototype/20261018T172049/` | aborted start: the preflight stopped it because free RAM was 3.9 GB, below 4 GB. It holds only a one-line `gate.txt`. It is kept because files are never deleted. After this run, the preflight was moved ahead of the directory creation. |

The run used script sha256 `2ab4eac6...485ad343`. After the run, only the docstring was rewritten to describe the
s45-based geometry, which gives the current sha256 `11cf85a2...6e100933`. No code changed. The unused functions
`page_segment` and `label_words` (word geometry from the Rozanova boxes) are kept to show the path that failed.

Inputs: `data/external/yale_scans/pages/*.jpg` (public domain). `runs/s45/pages/*.json` provides kraken lines and
ink-gap words. `data/vkb/vkb.sqlite` provides the hands and ZL3b tokens, and vparse provides the loci that s45
aligned to. `tools/boxes.py` reads the Rozanova/voynichese boxes (MIT).

Rerun: `python -u tools/physical/glyph_prototype.py` from the project root. It uses about 5 minutes on 1 CPU
thread at BelowNormal priority, with a GPU peak of 2.94 GB under a 4 GB cap. It refuses to start if free RAM is
below 4 GB or free GPU memory is below 4.5 GB.

## 3. Prototype: method and printed numbers (prototype, unverified)

**Pages (20, fixed rule, seed 7069).** Held out: f42r, f3v (hand 1), f75r (hand 2), f105v (hand 3), f66r (hand 5).
Train: f30r, f22r, f54r, f29v, f54v, f87v, f24v (hand 1), f81v, f76v, f40v (hand 2), f105r, f112r, f103v (hand 3),
f48r, f57r (hand 5).

Hand 4 has no eligible page. Its text is circular or rotated, and s45 has almost no lines there. The three hand-4
slots went to hand 1.

**Geometry.** The Rozanova boxes were the planned seeds, but a global affine registration (FFT correlation of the
box mask with an ink map) fails on 10 of 20 pages. On those pages the median centre error is 3 to 25 line pitches.
On the other 10 pages the median error is 0.17 to 0.50 pitch, and the boxes are loose (median height 0.7 to 1.4
pitch).

The boxes were therefore not used for labels. Words come from the s45 ink tokens, which are themselves
transcription-free (kraken lines plus ink gaps). The known-answer labels come from s45 line groups whose ink-word
count equals the ZL3b word count and whose alignment confidence is at least 0.8, plus a width-per-character
sanity filter. That gives 879 labelled words: 704 on train pages and 175 held out.

**Units.**
- **A:** connected ink components.
- **B:** A, with components that overlap in x merged.
- **C:** B, with wide units split at thin ligature valleys.

### G-count: per-word unit count vs EVA count, held-out pages (175 words)

| level | vs U1 (ch, sh, cth... single) | vs U0 (EVA characters) | vs U2 (iin, ee... also single) |
|---|---|---|---|
| A | exact 0.297, within ±1 0.629, rho 0.52 | 0.274 / 0.623 / 0.56 | 0.269 / 0.629 / 0.52 |
| B (chosen on train: 0.388) | **0.337 / 0.709 / 0.55** | 0.263 / 0.691 / 0.56 | 0.354 / 0.703 / 0.54 |
| C | 0.274 / 0.686 / 0.75 | 0.349 / 0.789 / 0.76 | 0.223 / 0.634 / 0.73 |

No level and no EVA unit system reproduces the per-word count well; exact agreement is at most about 0.35. Part
of the gap is label noise from the s45 alignment, which has not been measured.

### G-units: count ~ Σ beta_g × n_g(word)

All 821 labelled words with common units; bootstrap 95% CI. A beta of 1 means the image makes that EVA unit one
ink unit.

| EVA unit | level A (pure connectivity) | level B |
|---|---|---|
| ch | 1.66 [1.32, 2.03] | 1.35 [1.13, 1.58] |
| sh | 2.31 [1.97, 2.66] | 1.38 [1.10, 1.66] |
| cth | 2.10 [1.34, 2.91] | 1.51 [0.84, 2.22] |
| ckh | 1.97 [1.11, 2.91] | 1.63 [0.92, 2.22] |
| k / t | 1.28 / 1.26 | 0.94 / 0.82 |
| e | 0.36 [0.14, 0.54] | 0.41 [0.31, 0.54] |
| q | 0.02 [-0.35, 0.33] | -0.03 |
| i | 0.87 | 0.69 |
| o, y, d, a, r, l, s | 0.78 to 1.42 | 0.80 to 1.16 |

### G-purity: held-out units

230 held-out units in words whose B-count equals the U1 count, labelled by position; 18 label types; the majority
share is 0.122.

| embedding | K=24 | K=32 | K=48 |
|---|---|---|---|
| SimCLR CNN | purity 0.604 (null 0.251, max 0.287), NMI 0.547 | 0.613 (null 0.283), NMI 0.551 | 0.665 (null 0.328), NMI 0.589 |
| PCA of pixels | 0.604 (null 0.255), NMI 0.533 | 0.639 (null 0.275), NMI 0.571 | 0.670 (null 0.318), NMI 0.588 |

Clean clusters at K=32: l 0.86, y 0.82, a 0.82, r 0.86, o 0.83, d 0.75. The multi-stroke units are mixed:
- ch: 0.45 of ch falls in one cluster, which is 0.50 ch and also holds sh.
- sh: its modal cluster holds only 0.25 of sh.
- k: modal cluster share 0.40.
- t: shares a cluster with k.

### G-hand (descriptive)

Leave-one-page-out nearest-centroid classification of the Davis hand from per-page mean embeddings of 12 glyph
types: accuracy 0.650, permutation null 0.281, p = 0.010 (20 pages, hands 1/2/3/5).

The result is confounded: hand is entangled with section, with scan and ink conditions, and with page scale, and
hand 4 is missing.

### G-gap

Word-boundary agreement on held-out pages: kappa 0.713, recall 0.888, precision 0.617, threshold 0.73 x-height.
This is **circular** in the prototype, because the s45 words are themselves defined by ink gaps. It is reported
only as a check that the plumbing works.

### What the clusters say so far (prototype, unverified)

1. **Simple glyphs are real shape classes.** o, y, a, d, l and r each form clusters of 0.75 to 0.86 purity on
   held-out pages from images alone, about 2.4 times the permutation null. The pixel baseline does as well as
   the CNN, so the classes are plain in the ink and need no learned features.
2. **The ink does not agree with EVA's boundaries at the multi-stroke and bound glyphs.**
   - **ch:** beta 1.66 under connectivity, so the bar joins c+h only some of the time. In the clusters, ch
     mixes with sh.
   - **sh:** beta 2.31; the plume is usually a separate stroke, and merging overlaps (B) gives 1.38.
   - **Bench gallows (cth, ckh):** about 2 units, not 1. They are neither EVA's 1 nor its 3 letters.
   - **q:** beta about 0, so q is fused to the following o ("qo" is one ink unit).
   - **e:** beta 0.36 to 0.41, so e usually touches its neighbour.
   - **i:** minims behave like about one unit each.

   On ink connectivity alone, EVA's U1 is not the image's unit system for q, e, ch, sh or the bench gallows.
   Whether this reflects the script or the threshold and pen contact is the main open point. Nothing here
   discharges or flips X-01.
3. **The hand signal is above chance by shape** but is not separable from section and scan in this design.

## 4. Draft frozen design for the full run (for the lead to edit and freeze in D-066)

**Question.** From the scans alone: (Q1) what is the inventory of ink units, and does it coincide with EVA U1, U0
or U2? (Q2) Do the Davis 2020 hands separate by glyph shape within glyph type, beyond section and scan? (Q3) Do
ink word boundaries agree with transcribers' spaces when they are measured independently of s45?

**Rivals.**
- (R1) EVA U1 units are the script's units: images split ch, sh and the gallows as U1 does, and the slot results
  (F-34, F-39, F-40) stand on X-01.
- (R2) The script's units are finer or coarser than U1. The pairs qo and e+neighbour fuse, and the bench gallows
  split into 2. The slot analyses must be rerun on image units.
- (R3) The image units are threshold artefacts: the betas move with the binarization threshold, so connectivity
  cannot decide.

**Evidence and representation.**
- All single-folio Yale canvases with s45 lines: about 170 pages.
- Hand 4 and the circular text are a separate arm that needs rotation-normalised line finding. It is excluded
  from the primary analysis and stated.
- Units at levels A, B and C, as in the prototype, with parameters frozen at the prototype values (`params.json`).
- Embeddings: SimCLR CNN (primary) and pixel PCA (second representation).
- Words: s45 ink tokens.
- Labels: s45 counts-equal groups (conf >= 0.8, width filter), and additionally Rozanova boxes on pages where a
  per-line re-registration reaches a median centre error below 0.3 pitch. Box labels serve as a second, partly
  independent label source.

**Gates, in order. A failed gate is a HOLD with no Q1 to Q3 call.**
- **G0, label quality.** Read 100 random s45-labelled words against the image; this is a hand check by the lead
  or an independent agent, not the runner. At least 90% must be correctly paired. If not, use box labels only.
- **G1, planted recovery.**
  - Synthetic fixture: render known strings in an EVA-like stroke font (Voynich glyph outlines drawn from the
    prototype's cluster medoids), with known fusions (qo fused, ch joined, sh with a separate plume). The beta fit
    must recover the planted betas to within ±0.15 on at least 90% of units.
  - Positive control on real text: a Latin page from a 15th-century Gothic cursive scan already on disk (or the
    s103 herbal controls). Here connectivity units vs known letter counts must give beta within 1 ± 0.2 for at
    least 70% of letters, so that the method can see one letter as one unit when that is the truth.
- **G2, threshold stability (R3).** Recompute the betas at C = 10, 15 and 20, and with the s45 Gaussian adaptive
  binarization. A unit's beta call (≈1, ≈2, ≈0) is stable only if all four settings agree. Unstable units are
  reported as UNDECIDED, not as evidence.
- **G3, held-out purity.** Held out by bifolio (both leaves of a bifolio held out together; about 25%). SimCLR
  purity at K=32 must exceed the 99th percentile of the label-permutation null on held-out units, and the
  per-label recall of o, y, a, d must be at least 0.6. If this fails, the embedding is not trusted for Q2.

**Statistics and calls.**
- **Q1 unit inventory.**
  - For each EVA unit g with at least 200 tokens, beta_g at levels A and B, with a word-cluster bootstrap 95% CI
    (resampled by page).
  - CALL_UNIT_g = SINGLE if the CI lies inside [0.8, 1.2] at level B; DOUBLE if it is inside [1.7, 2.3] at
    level A; FUSED if the CI upper bound is below 0.5 at level A; otherwise UNDECIDED.
  - The cluster inventory is the number of k-means clusters (K chosen by held-out silhouette in 16 to 64) holding
    at least 0.5% of units, with each cluster's majority U1 label and purity.
  - **X-01 call:** IMAGE_UNITS_MATCH_U1 if SINGLE holds for at least 80% of U1 units by token mass and for ch and
    sh both. IMAGE_UNITS_DIFFER if any unit with at least 2% token mass is FUSED or DOUBLE, stably under G2.
    Otherwise UNDECIDED.
- **Q2 hands by shape.**
  - Per glyph type (o, y, a, d, e, ch, k, t, l, r, i, n, at least 20 tokens per page), take the per-page mean
    embedding after removing per-page scale and stroke width.
  - Classifier: leave-one-bifolio-out nearest centroid over hands 1, 2, 3 and 5 (4 if its arm passes).
  - Null 1: 10,000 permutations of hand labels across bifolios.
  - Null 2 (the confound control): permutation of hand labels within section, keeping each section's hand
    counts. Hand 1 vs 2 within herbal is the key cell, since both write herbal pages.
  - CALL_HAND_SHAPE = accuracy above the 99th percentile of both nulls. Report the confusion matrix against Davis
    2020, and list the pages Davis marks ambiguous (f115r and others from the MUSE article; fetch the article
    first) with their predicted hand. No call on a single page.
- **Q3 word boundaries.**
  - Run an independent gap detector on the image units: a 2-component mixture on unit gaps per page, fitted on
    train bifolios.
  - Its boundaries are compared with Rozanova box edges (the second source) and with ZL3b spaces, scored by kappa
    on held-out bifolios. Comparing with s45 boundaries is not allowed: it is circular.
  - CALL_SPACES_AGREE = kappa >= 0.75 against both sources.

**Nulls.** For purity, labels are permuted among held-out units, 1,000 times. For the hand calls, labels are
permuted across bifolios and within section, 10,000 times each. For the betas, a shuffle control: the U1 counts
are permuted among words of the same character length, and every beta must then collapse toward the mean count
per character.

**Power, from the prototype.** With 821 labelled words, the beta CIs for ch, sh and e are about ±0.3 to 0.35. The
full run expects about 7,000 labelled words (about 8.5 times as many), which gives CIs of about ±0.12. That is
enough to separate 1 from 2 and from 0 for any unit with at least 200 tokens. cth and ckh, at about 30 tokens per
20 pages, get CIs of about ±0.3 and may stay UNDECIDED; this is stated in advance. For Q2, 4 hands on about 85
bifolios gives a MDE of about +0.15 accuracy over the within-section null; compute this exactly from the null
spread before scoring.

**Stopping rule.**
- IMAGE_UNITS_MATCH_U1: record that X-01 is discharged by image units on these 170 pages, and stop.
- IMAGE_UNITS_DIFFER: rerun the F-34, F-39 and F-40 slot calls on image-unit tokenizations. This is a separately
  frozen run that does not vary unit levels.
- UNDECIDED or any G2 instability: record that connectivity cannot decide the units, and stop the connectivity
  line. The next physical evidence would be stroke-order or pen-lift evidence (MSI, O-060). No parameter sweep.
- Q2 positive against both nulls: shape supports the Davis hands; O-020 gets a shape line. Negative at adequate
  power: record it, and keep the hands as palaeography only (X-08 stays unverified).

**Compute (estimated from the prototype at 11 s/page and 74 s for 11k units × 40 epochs).**
- Segmentation of about 170 pages: about 35 CPU-minutes, 1 worker, BelowNormal.
- SimCLR on about 140k units: about 15 GPU-minutes; the peak of 2.9 GB stays under the 4 GB cap at batch 512.
- k-means, bootstrap and permutation nulls: about 30 CPU-minutes.
- Box re-registration and the G1 fixture and control: about 30 CPU-minutes.
- Total about 2 CPU-hours and 0.5 GPU-hour, 1 worker. Free RAM of at least 4 GB is checked; peak resident memory
  is about 1 GB per page.

## 5. Known limits of the prototype

- The labels come from the s45 length alignment, and their error rate is not measured (G0 will measure it).
- Purity is scored only on words whose unit count already equals the U1 count, which favours units that agree
  with U1. Purity therefore overstates agreement; the betas are the unbiased part.
- The Rozanova boxes need per-line registration before they can serve as labels or seeds. The global fit failed
  on half the pages.
- Hand 4 and all rotated or circular text are absent.
- The hand result is not separated from section, scan or page scale.
