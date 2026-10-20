# Leaf contact / offset / stain map: Phase 7.4 part 1 (D-069)

Written 2026-10-18 17:17 PDT (clock read with `date`). **Design and prototype only.** No claim is filed and no register, graph, PLAN or TEAM-HANDOFF entry was edited. The lead freezes the full-run design in D-066 after reviewing this prototype; the draft is in section 6.

## 1. Question and why it matters

Which page surfaces touched each other in an earlier binding, judged from physical evidence alone? The method reads no text, no transliteration and no section labels. The physical order would then serve as an order-free reference for:
- the order-dependent findings (F-32, F-42, r9 drift);
- the subject-vs-writing-batch question that s111 left on HOLD, whose batch arm was underpowered at 19 different-subject same-quire pairs. Physical adjacency would give batch units that do not depend on the current quire assignment.

## 2. Data sources and licences

| Source | Use | Licence |
|---|---|---|
| Yale Beinecke MS 408 IIIF scans, `data/external/yale_scans/pages/` (204 JPEGs, sha256 in `MANIFEST.md`) | All image signals | Public domain (Yale catalogue). Untrusted download, so it is read only with `python -I`. |
| `data/vkb/vkb.sqlite`, table `folios` (folio, quire, bifolio, conjugate, image_path), opened read-only | Leaf identity, same-leaf exclusion, conjugate pairs, current facing pairs | Project-internal |
| Layfield, C. and Davis, L. F. (2026), "Singulion Structure and the Voynich Manuscript", *Digital Medievalist* 19, online 10 July 2026, doi:10.4000/16k0a, https://journals.openedition.org/digitalmedievalist/2331 | Known answers (the five contact links below) | Text is CC BY 4.0. Figures may carry other terms; Fig. 1 is credited to the Beinecke. |

The **five published contact links** were fetched from the article on 2026-10-18. Section numbers are the article's.

| Link | Evidence as described | Comment |
|---|---|---|
| 10v \| 15r | "the splashed stain" (sec. 7) | Inner faces of bifolio B-2 |
| 33v \| 40r | "the blue petals" (sec. 7) | Inner faces of E-1 (outermost bifolio of quire E) |
| 58v \| 65r | "a bit of green leaf" (sec. 7) | Inner faces of H-2. These two pages also face each other in the current binding, because ff59-64 are missing. |
| 76v \| 83r | "the nymph's right arm in the upper gutter" (sec. 7) | Inner faces of M-2. This is a drawing crossing the gutter, not a mirrored offset. |
| 78v \| 81r | "the two streams in the center gutter margin ... that cross the gutter" (sec. 6) | Inner faces of M-4. This is also a crossing drawing, not an offset. |

All five links are inner faces of a single bifolio. They show singulion contact (each bifolio decorated before nesting). They are therefore known-answer checks of a scorer, not a test of discovering unknown adjacency. The article gives no catalogue of stains or offsets (as the gap audit already noted). Other trivially known pairs are the conjugate bifolio pairs (folios table) and the current facing pages (consecutive surviving leaves Nv | next r).

## 3. Method (prototype, `tools/physical/contact_prototype.py`)

**Geometry.** Two facing surfaces touch mirror-wise about the fold. The contact transform is therefore a horizontal flip that brings gutter onto gutter, with a lag search of about ±10% of page width to absorb registration error. Show-through from the other side of the same leaf has the same mirror geometry. Same-leaf pairs are therefore never candidates; they are reported only as a show-through control.

**Per surface** (CPU, 1 thread):
1. JPEG draft downscale.
2. Trim the black background.
3. Cut at the gutter shadow, because the scans show the open book and the facing page often intrudes.
4. Resize to 192x272.
5. CIELAB chroma channels relative to the page's median parchment: green, blue, red/brown.

**Signals.** Each signal is scored for every ordered pair src → rcv on the GPU, with FFT cross-correlation over all lags in batches.
- **O, mirrored offset:** multichannel NCC of src's own strong paint, flipped, against rcv's faint "ghost" pigment. The ghost excludes rcv's own paint, ink and the same leaf's mirrored paint (show-through mask) and is high-passed.
- **C, coverage (v4):** the fraction of rcv's salient ghost mass that lands on src's mirrored paint footprint, minus the footprint's area fraction. This is a precision statistic rather than a correlation.
- **T, stain continuity:** NCC of band-passed parchment luminance. Text and paint are filled by masked blur and median, and the per-side (recto/verso) mean map is subtracted. Src is flipped.
- **U, gutter continuity:** 1-D NCC of the drawing (paint or ink) profile along the strip at each page's gutter edge.
- Pair score = s(a→b) + s(b→a). The combined score is the sum of z-scores over candidate pairs.

**Controls.**
- 180° rotation instead of the flip (U: one profile reversed). This geometry cannot arise from contact.
- Same-leaf show-through.
- Conjugate outer faces (Xr | Yv): the same sheet as each link, but never in contact as a singulion.
- Random candidate pairs.
- A rank null that draws random partners for the same five left pages (2,000 draws).

**Rank.** For a link X|Y, the rank of Y among X's 40 candidates and the rank of X among Y's 40 candidates. "Both ends" means the worse of the two ranks.

## 4. Prototype runs

There are 42 surfaces: quire B whole; f33/34/39/40; f57/58/65/66; f76/77/78/81/82/83. This covers all five links, their conjugate outer faces and 15 current facing pairs. Every run directory is new and holds `results.txt`, `results.json` and `matrices.npz`. The v1 script copy is kept in its run directory, and later runs record the script sha256.

| Run (`prototype/`) | Version | Change | Known links top-5 (both ends) |
|---|---|---|---|
| 20261018-171201 | v1 | baseline | O 0/5, T 1/5, U 0/5, combined 1/5 |
| 20261018-171336 | v2 | gutter crop, show-through mask, green+blue only, masked stain | O 0/5, **T 3/5 (p = 0.0065)**, U 0/5, combined 2/5 (p = 0.0145) |
| 20261018-171403 | v2, scale 2 | double resolution | O 0/5, T 2/5, combined 1/5 |
| 20261018-171532 | v3 | sparse salient ghost, blurred maps | O 0/5; T as v2 |
| 20261018-171641, -171654 | v4 (sha 3616d0cd...) | adds C coverage | C 0/5; T 3/5 (p = 0.007); combined 0/5 |

Best component, T stain (v2/v4). Ranks are from left / from right among 40 candidates; the 180° rotation control is in brackets.

| Link | T rank | rot180 | Offset O (v2) | Coverage C (v4) |
|---|---|---|---|---|
| 10v \| 15r | 11 / 12 | 21 / 24 | 20 / 9 | 13 / 9 |
| 33v \| 40r | 4 / 1 | 38 / 31 | 20 / 13 | 20 / 14 (rot 2 / 1) |
| 58v \| 65r | 31 / 27 | 27 / 19 | 34 / 38 | 26 / 30 |
| 76v \| 83r | 2 / 3 | 21 / 19 | 32 / 35 | 38 / 39 |
| 78v \| 81r | 1 / 1 | 1 / 1 | 6 / 21 | 21 / 29 |

- **Top-1, T:** 1/5 at both ends (2/5 at either end). **Top-5, T:** 3/5 at both ends against a random-partner null mean of 0.52 (p = 0.0065). Combined (v2): top-1 1/5, top-5 2/5. For 33v | 40r and 76v | 83r the stain match is geometry-specific: it collapses under rotation. For 78v | 81r it does not.
- **Current facing vs random pairs** (AUC, v2): T 0.667, O 0.566, U 0.595, combined 0.720. Score distributions for T: facing (n = 15) mean 0.269, median 0.233; random (n = 816) mean 0.209, median 0.197, p95 0.368. Retrieval of the current partner is at chance: 2/15 in the top 5 at both ends for T and 4/15 for combined, against about 1.9 expected.
- **Confound:** conjugate *outer* faces score as high as the inner links on T (AUC 0.774 against 0.780; 78r | 81v rank 1, 58r | 65v rank 3). The stain signal identifies the **same sheet, or a stain front through a stack**, not which faces touched. A water front through a folded sheet is mirror-consistent on all four faces, so this is expected physics, not a bug.
- **Offsets:** offsets are visible by eye; the 40r ghost map shows the ring of 33v's blue petals clearly. But neither whole-page statistic (O, C) ranks any link in the top 5. The large paint and layout mass of herbal pages swamps a small ghost. Show-through is detected (same-leaf O 0.111 against 0.054 random), so the ghost channel works and the aggregation is the weak part. The rotation control for C on 33v | 40r (rank 2 / 1 under rot180) is unexplained (unverified; possibly a coincidental bottom-margin ghost).
- **Gutter continuity** fails. The 78v streams are thin ink lines, and the trimmed gutter strip still mixes in neighbour-leaf material.
- **Compute:** about 10 s of features and under 3.5 s on the GPU for 42 surfaces, with peak GPU allocation 0.11 GB (0.43 GB at scale 2). Preflight: other processes held 6.0-8.7 GB of GPU memory; this run's cap was 3.5 GB.

**Honesty note.** Five script versions were looked at against the same five links, so the links are now *development* data. Any gate must use held-out known answers (section 6) with parameters frozen as they stand.

**Verdict on readiness:** the method **cannot pass a ≥ 4/5 top-5 gate** in its current form. It reaches 3/5 on one component, and that component does not distinguish touching faces from the same sheet. It should not go to a full run as is.

## 5. Recommended before freezing (one more prototype step, not a full run)

1. **Blob-level offset detector.** Use connected components of salient ghost and match each against the mirrored source paint components within the lag window, using shape (Hu moments or IoU after a local shift) and colour class. Score a pair by the best matched blob(s), not by whole-page correlation. This targets exactly what a codicologist sees (40r's petal ring).
2. **Face discrimination.** Use the two-sided test: an offset is present on one face of a sheet and absent from the other. Score inner (Xv | Yr) against outer (Xr | Yv) faces of the same sheet pair, and keep T only as a sheet-stack term.
3. **Gutter term.** Edge crop from the page boundary itself, not the shadow minimum; profile ink line endings at the edge only.
4. **Development and held-out split** fixed before step 1. Development uses the current subset and the five links. Held-out uses the current facing pairs in all other quires.

## 6. Draft frozen design for the full run (for the lead to freeze in D-066; not frozen here)

- **Question:** which surviving page surfaces were in contact (facing) in any earlier binding state, from physical evidence alone?
- **Units:** the 177 single-page surfaces with a scan in `folios.image_path`. Foldout panels are excluded until per-panel registration exists (gap map §2). Candidates for a surface are all other surfaces except itself and its own leaf's other side.
- **Statistic, frozen with code sha:** S(a,b) = z(blob-offset match, mirror geometry, both directions) + z(stain T). The blob-offset term must carry the face discrimination: z is over all candidate pairs. Parameters as in the version that passes the development check in §5; no tuning after the freeze.
- **Nulls:**
  - random pairs: 10,000 random candidate partners per evaluated surface, giving rank and top-k nulls;
  - rotation control: every evaluated pair re-scored under 180° rotation and under no flip. A contact call requires the mirror score to exceed both controls;
  - same-sheet control: conjugate outer faces must score below inner faces (Wilcoxon, one-sided p < 0.05).
- **Known-answer gate**, all three before any physical order is used downstream:
  - **K1:** at least 4/5 of the Layfield & Davis links in the top 5 at both ends among about 175 candidates. These are development data, so K1 is necessary but not sufficient.
  - **K2 (held-out):** current facing pairs outside the development quires, about 70 pairs. The true partner must be in the top 5 at both ends for at least 50%, against a null rate of about 3%, with a random-partner permutation p < 0.001.
  - **K3:** the same-sheet control as above.
  - If K1 or K2 fails: HOLD, record which signal failed, and make no physical-order claim.
- **Outputs**, written to new files under `data/physical/contact_map/<run-id>/`:
  - the N×N directed score matrices for each signal and each control;
  - the per-surface top-10 candidate lists;
  - the K1-K3 printed calls;
  - a contact-candidate table for pairs that are neither conjugate nor current-facing and score above the 99th percentile of the random-pair null (candidate earlier-binding adjacencies, unread until the lead files them).
  - Downstream (a separate frozen test): re-score F-32, F-42 and r9 drift with the physical order, and give s111's batch arm physically defined batches.
- **Compute:** from the prototype timing (scale 1: about 0.22 s/surface for features, N² GPU scoring at about 3 s for N = 42):
  - full run with N = 177, scale 1: about 1 min of features and about 1 min of GPU, plus the permutation nulls (vectorised, minutes);
  - scale 2: about 3 min of features and about 4 min of GPU;
  - peak GPU allocation under 1 GB (cap 3.5 GB);
  - 1 CPU worker at BelowNormal with a free-RAM check of at least 4 GB.
  - Budget: 30 min wall, 1 GPU-hour ceiling.

## 7. Run it

```
python -I tools/physical/contact_prototype.py            # 42-surface subset, scale 1
python -I tools/physical/contact_prototype.py --scale 2  # double resolution
```

The script aborts if free RAM is below 4 GB or if the GPU has less than 4.5 GB free. It never reuses an output directory.

## 8. Step 2 (lead instruction after the prototype report): blob-level matching. Frozen before any step-2 code was written or run

Written 2026-10-18 17:20 PDT. Sections 1-7 above are unchanged. This section was appended.

**Held-out answer set (K2), frozen first.**
- Rule: every current facing pair (Nv | r of the next surviving leaf, in folio order from the `folios` table, foldout sub-panels skipped) where both surfaces have a single-page scan (`image_path` not empty) and neither surface lies in a development quire (B, E, H, M: the quires used by the prototype subset).
- The rule gives **52 pairs**, not about 70. Many facing pairs touch foldouts that have no single-page scan, or touch a development quire.
- File: `step2/heldout_facing_pairs.tsv`, sha256 `0e1b64b2e09c01426d57502cab5cbd3f7bcf4dfdaf0c796083b76829b1fcd8be`.
- The pairs: f1v|f2r f2v|f3r f3v|f4r f4v|f5r f5v|f6r f6v|f7r f7v|f8r f17v|f18r f18v|f19r f19v|f20r f20v|f21r f21v|f22r f22v|f23r f23v|f24r f24v|f25r f25v|f26r f26v|f27r f27v|f28r f28v|f29r f29v|f30r f30v|f31r f31v|f32r f41v|f42r f42v|f43r f43v|f44r f44v|f45r f45v|f46r f46v|f47r f47v|f48r f48v|f49r f49v|f50r f50v|f51r f51v|f52r f52v|f53r f53v|f54r f54v|f55r f55v|f56r f87v|f88r f93v|f94r f96v|f99r f99v|f100r f103v|f104r f104v|f105r f105v|f106r f106v|f107r f107v|f108r f108v|f111r f111v|f112r f112v|f113r f113v|f114r f114v|f115r f115v|f116r.
- The five published links are **development data only**.

**Surfaces.** All 177 scanned single-page surfaces are scored. Each surface's candidates are all other surfaces except its own leaf's other side, which leaves 175.

**Features.** Working size 384 x 544 (scale 2). Background trim and gutter-shadow crop as in v4. Two colour classes, green and blue, are CIELAB channels relative to the page's median parchment.
- **Source footprint F_c:** pixels where the page's own strong paint (chroma distance > 16) has class channel c > 8, dilated by 2 px.
- **Ghost blobs for class c:**
  - Eligible pixels are not the page's own strong paint or ink (dilated by 6 px), not the mirrored strong paint of the same leaf's other side (show-through, dilated by 8 px), and have |L - L_median| < 8.
  - On these pixels, take the class channel high-passed (Gaussian sigma 40 px removed). Threshold at median + 4 MAD of the eligible pixels, and at least 1.5.
  - Keep connected components of 12 px or more.
  - **Leakage rule:** a component is dropped if its centroid lies within 6% of page width from the gutter edge, or within 3% of any other edge. The scans show the open book, so the facing page's real paint can sit in the gutter band.
  - Keep the 40 components of largest mass per surface (both classes together).

**Statistic (primary, B).** For a directed pair a → b and geometry G (hflip for contact; rot180 as the control):
- For each ghost blob g of b, in class c, compute IoU_g(t) between g's mask and G(F_a,c) inside g's bounding box, for every common lag t within ±40 px (about ±10% of width).
- B(a→b) = max over t of Σ_g w_g IoU_g(t) / Σ_g w_g, where w_g is the blob's mass. All blobs share one lag, which is the position-consistency requirement.
- Subtract the median over b's candidate sources.
- Pair score B(a,b) = B(a→b) + B(b→a).
- Secondary, descriptive only: the mirror excess B_hflip - B_rot180, and B + stain T.

**Gates. K1 to K3 are evaluated on primary B under hflip; nothing is tuned after this freeze.**
- **K1 (development):** at least 4 of the 5 published links in the top 5 at both ends (rank among 175 candidates).
- **K2 (held-out):** at least 50% of the 52 held-out pairs in the top 5 at both ends, AND permutation p < 0.001. The null is 10,000 draws; each draw gives every held-out pair a random partner from its left page's candidates and counts top-5 at both ends.
- **K3 (face contrast):** for every bifolio with all four faces scanned, inner B(Xv, Yr) > outer B(Xr, Yv) by Wilcoxon signed-rank, one-sided p < 0.05. Reported over all such bifolia, and separately over the held-out quires.
- **Rotation control:** reported for every K1 and K2 pair (rank under rot180) and as AUC(hflip) against AUC(rot180) for held-out pairs vs random pairs.
- **Stopping rule:** stop after this step. If K2 fails, report whether the signal is too weak at this scan resolution and whether higher-resolution tiles would help.

**Compute.** 1 CPU thread at BelowNormal, GPU memory capped at 1 GB, free RAM checked at 4 GB or more.

## 9. Step 2 result (run `step2/20261018-172434`, contact_blobs.py sha256 d7a523494681c5d0...; appended 2026-10-18 17:26 PDT)

Before the real run, a synthetic fixture was checked: a planted mirrored footprint, shifted (+7, -5) px, was recovered at rank 1 with IoU 1.00, and the rot180 control gave 0.29 (scratchpad check, not kept). The real run covered 177 surfaces with 175-176 candidates each. It took 74 s of features and 18 s on the GPU, with peak GPU allocation 0.51 GB.

| Score | K1 dev (top-5, both ends) | K2 held-out (n = 52) | K3 inner > outer (41 bifolia) | AUC held-out vs random |
|---|---|---|---|---|
| **B primary (blob, hflip)** | 0/5 (ranks 27, 44, 29, 53, 46) | 0/52, p = 1.0, median rank 102 | 17/41, p = 0.95 | 0.529 |
| B rot180 control | 0/5 | 1/52, p = 0.24 | 17/41, p = 0.93 | 0.543 |
| B mirror excess | 0/5 | 1/52, p = 0.32 | 23/41, p = 0.33 | 0.487 |
| B + T (secondary) | 1/5 | 5/52 (9.6%), p = 0.0005 | 23/41, p = 0.76 | 0.697 |
| T stain (secondary) | 2/5 | 5/52 (9.6%), p = 0.0003 | 22/41, p = 0.48 | 0.685 |

**Calls under the frozen rule: K1 FAIL, K2 FAIL, K3 FAIL.** Stop.

**Diagnosis.**
- Every surface reached the 40-blob cap. The ghost threshold (median + 4 MAD) is picking up parchment texture and tint noise, not offsets, so the blob statistic is at chance under both geometries.
- The stain term is real but weak: held-out facing pairs score above random pairs (AUC about 0.69; 5/52 in the top 5 against 0.6 expected, p < 0.001). It is far below the 50% bar, and it does not separate inner from outer faces.
- The physical offsets exist at this working scale: 40r shows 33v's petal ring by eye at 192 px width. The failure is detector specificity, not missing signal. Resolution is not the binding limit: the method used 384 x 544, about 1/7 of the native scan.

**Higher-resolution source.**
- The Yale IIIF service's maximum size is the native size already on disk. For example, info.json for canvas 1006078 gives 2691 x 3770, with 512-px tiles at scale factors 1-32, and `full/full` is that size. No higher-resolution tiles exist via IIIF.
- `/download/tiff/<id>` returns an HTML page, not a direct file. Whether the TIFF masters have more pixels than the JPEGs is unverified; they would at best remove JPEG compression.
- Better evidence for faint offsets would need other imaging: the Davis 2024 MSI stacks (10 folios, 16-bit; D-069 part 3) or raking light, which has no public source.

## 10. Native-resolution retry not run (2026-10-18)

The collection pass reached this file after K1, K2 and K3 had already failed. Section 9 records the stop, and it records that the working size was 384 x 544, about 1/7 of the native scan, and that resolution is not the binding limit. The Yale JPEGs already are the IIIF maximum. A second pass of the same blob detector at native size would rerun a stopped rule. It was not started. MSI stays parked.
