# Big picture, MEANING lens (does the text carry content; best route to an anchor)

Written 2026-10-18 21:01 PDT (`date`). Read-only review. I did not open `data/anchor_A1/labels*.tsv`. Scratch numbers below are exploratory and not filed. Scripts and outputs are in `<home>/AppData/Local/Temp/claude/<agent-project>/<session>/scratchpad/bigpic/` (they import the frozen A0 script read-only and use `runs/s115_a0/*_embed.npz`).

## 1. Verdict

The link tests have not shown that the text has no meaning. After A0, almost every meaning null has no weight: F-33 and db-s100/s102 are page-level tests at N 119 (about 40 % power); db-s112 used 74 label loci; F-20 assumed pharma sketches redraw herbal plants, and A0 weakens that (Voynich 3/13 in the top 5 against a real-herbal median of 7/13).

What remains against content is structural: short-range core recurrence (F-13), no matching reference class (F-40), weak core order (F-12), and the page/quire locality of vocabulary (F-17, F-42). These findings argue against plain language and letter ciphers. They do not rule out a nomenclator or a notation (H-06/H-16/H-18).

**Net:** "no recoverable content" is somewhat more likely than it was a month ago, but because of the structural findings, not the link tests. A single result could settle it: the label-to-object test (lead 1) at power ≥ 0.9 against r 0.09.

## 2. Evidence ledger

| Item | Says | Weight now |
|---|---|---|
| F-33 (s78) | no picture-to-core link (r 0.007-0.053) | **none**: about 40 % power vs r 0.09 (L-330) |
| db-s100 / s102 | tail cores vs herbal picture or geometry: null | none: same N 119 page design |
| db-s112 | label text vs object crop: null (74 loci, 12 pages) | none: planted effect was mean z +1.1; below the A0 N |
| db-s113 / s122 | label form vs container/botanical class: AUC 0.41 (n 40); 0.62 p 0.108 (n 160); Edge2 0.66 p 0.040 | weak hint; one representation of several, not corrected for multiple tests |
| db-s114 / F-20 | repeated labels do not agree on object class (6/15, p 0.745); pharma labels share no text with herbal "partners" | weak: the partner premise is weakened by A0 (3/13 vs 7/13) |
| F-43 (db-s109) | label cores retrieve their own page's body (MRR 0.630 vs q99 0.588) | contested: holds only under Canon+Comp. Unverified whether the null held quire fixed; a local-pool generator (F-42) predicts the same thing |
| F-44 (s99) | rare label cores are not nearer their label (MDE 0.088) | uncalibrated against any real herbal |
| F-28; F-07, F-50 | no zodiac/antidotary order; section and quire drift | order only; drift fits content or re-set settings |
| Label inventory (VKB, ZL3b, checked) | 1029 label loci. Herbal **37 label tokens on 6 of 129 folios**; pharma 250 tokens, 235 types; zodiac 350 tokens, 285 types, of which only 38 types recur across zodiac panels | Real herbals caption every plant, so the herbal section lacks the best anchor unit. Zodiac labels are not repeated day numbers written as plain words |

## 3. Calibration on the real-herbal corpus (scratch, 820 captioned units from A0)

The noise model and partials are the A0 test-(a) code, unchanged. NPERM 199, 100 reps per N.

| N | 119 | 204 | 250 | 300 | 400 | 600 |
|---|---|---|---|---|---|---|
| Partial-Mantel power (picture vs caption) | 0.43 | 0.68 | 0.80 | 0.82 | 0.94 | 1.00 |
| 4-class picture category (k-means on embeddings, an A1 analogue) predicted from caption kNN | 0.10 | 0.17 | - | 0.13 | - | 0.68 (N 600) |

The N 119 value reproduces A0 (0.405). Two consequences:
1. Similarity designs need **N ≥ 250-300 units**.
2. **Coarse categories discard most of the signal.** Pooling A1 categories across all 204 images gives power of about 0.2 and is ruled out as the A2 response. Use A1 categories as strata or covariates, not as the outcome. (Caveat: k-means clusters are an analogue, not A1 itself.)

Duplicate pairs (scratch `dup_pairs.py`): among the **top 10 picture-matched cross-manuscript pairs, 4/10 share a caption token, against a 0.001 base rate**. The rate is 6/25 in the top 25 and 8/100 in the top 100. A design built on a few image-matched pairs therefore has a very large effect if the text names things, but it relies on precise image matches.

## 4. Ranked leads

### Lead 1: label-to-object similarity over every label in the book (recommended A2)
- **Evidence.** There are 1029 label loci. A0 captions are labels, so the A0 corpus is the right positive control. Every past label test was underpowered (db-s112 used 74 loci).
- **Design.**
  - Register each label locus to the drawn object it sits on or beside. Word boxes are available for 223 folios (`tools/boxes.py`).
  - Crop each object with the writing masked and embed it (DINOv2 + SigLIP on the RTX 5080).
  - Statistic: a partial Mantel of crop similarity against label-core tf-idf similarity, with the A0 code.
  - Partial out same page, same bifolio, same quire (F-50 drift), adjacency, section, hand, label length difference and crop size difference.
  - Permute within quire x section strata. Run ZL3b, then RF1b and IT2a, with two segmenters.
  - Drop identical star glyphs (no picture variance). Expect about 600 or more eligible units: pharma, zodiac, bath and cosmological figures.
- **Power.** 0.94 at N 400 and 1.00 at N 600 against r 0.09 (calibrated above).
- **Before freezing:** recompute power on A0 subsamples whose caption lengths match the Voynich labels (about 1.17 tokens per label), and on a within-page-clustered A0 subsample.
- **Refuted if:** the matched-power check reaches at least 0.9 and the Voynich r is at most the null q95 on all three transliterations, with the CI upper bound below 0.05. That would mean the labels do not name their objects. A positive result fails if it disappears when same-quire pairs are removed or appears under only one segmenter.
- **Cost.** Registration plus a 50-label audit about half a day; embedding minutes on the GPU; test under 1 CPU-hour; fixture and A0 control already built.

### Lead 2: image-matched duplicate objects, then label identity
- **Evidence.** On real herbals, the top image matches share a name 40 % of the time against a 0.001 base rate. The Voynich pharma pages repeat jars and fragments across quires O and S.
- **Design.**
  1. Blind picture step first: find cross-quire top-K duplicate crops among pharma fragments, jars and herbal plants, with no text. Freeze K and the pair list.
  2. Count pairs whose labels share an exact word or core. Compare against a null of pairs matched for quire and hand.
- **Power.** At base rate 0.003: K 10 at the real-herbal rate 0.4 gives P(X ≥ 2) = 0.95 (null 4e-4); at rate 0.1, K 25 gives 0.46. So power rests on how many duplicates the picture step finds (A0 suggests few pharma-herbal, maybe more within pharma).
- **Refuted if:** at least 10 high-confidence duplicates are found and sharing is at most the base rate. If the picture step finds fewer than 10, record UNINFORMATIVE.
- **Cost:** about 2-3 hours on top of the lead 1 crops.

### Lead 3: calibrate F-43 (label to own-page body)
- **Evidence.** F-43 is the only positive link. It is also exactly what a quire-local core pool would produce (F-13, F-42).
- **Design.** Find a transcribed herbal with captions and body text (Macer or Circa instans editions; usable form unverified) so A0's test C can run; rerun db-s109 there at Voynich size, and on the Voynich with decoy pages drawn from the same quire and hand, under three representations.
- **Power.** Unknown until the real corpus is found.
- **Refuted if:** the Voynich MRR falls to the same-quire null, or the real-herbal power is below 0.8.
- **Cost:** finding the text is the bottleneck (hours to days). The runs take under an hour.

### Lead 4: zodiac (referent known: sign, later-hand month names)
- **Evidence.** 299 nymph labels, 12 panels, 10 signs (standard attribution, unverified here); Aries and Taurus have two half-panels; 38 of 285 label types recur across panels.
- **Design.** (a) Lead 1 restricted to zodiac, same panel partialled: N about 300, power about 0.82 at r 0.09, probably lower since the crops vary little. (b) The 2 same-sign half-panel pairs against about 10 adjacent different-sign pairs: best p 1/55 = 0.018, needs d ≥ 1.8. If labels name days, halves need not share words, so (b) is ill-defined.
- **Positive control:** none found. **Cost:** about 1 hour; low value; run inside lead 1.

### Ruled out
- Page-level body vocabulary against pictures (N ≤ 125; power ≤ 0.45).
- A1 categories as the A2 outcome, pooled or not (category power 0.1-0.2 at N 119-300).

## 5. What would settle "no recoverable content"

**No anchor.** Lead 1 a powered null (matched power ≥ 0.9, CI below 0.05), lead 2 at least 10 duplicates with no name sharing, and F-43 dissolving under the same-quire null. That would show that the labels do not name what they are attached to. It would close the cheapest route to an anchor and, given F-13/F-40, make "no recoverable content" the working position. Body-text content would remain formally untested.

**Anchor exists.** Lead 1 replicates on all three transliterations and two segmenters with quire partialled out, and lead 2 agrees.

Before any A2 freeze, the A1b cross-model kappa must be done, and power must be shown at the real Voynich label length.
