# Big picture, physical and material lens

Written Sun Oct 18 20:53:33 PDT 2026 (from `date`). Read-only review; nothing filed. Numbers come from the files cited next to them. Anything not checked is marked "unverified".

## Underused assets on disk

- **Glyph prototype units** (`data/physical/glyphs/prototype/20261018T172429/`): 16,816 units with crops and embeddings. Only gate statistics exist. **No sequence statistic (h2) has been computed on image units.**
- **MSI stacks**: f1r is in `data/msi/`; f17r and f116v are in `<local-path>` (85 files, MANIFEST checks; f116v includes 8 transmitted bands and a true-colour TIFF). f1r has had a first look only (O-069). f17r and f116v have not been opened.
- **Bifolio and conjugate columns** (VKB `folios`, 52 bifolia): used as a null block (F-07, F-09), never as a production unit.
- **Gothic-hand manuscript images**: bsb_clm5905 (399), bl_add41623 (331), sloane4016 (235), ljs419 (205), bodleian_canon_misc_408 (166). None has gone through the glyph or ink pipeline.
- **CREMMA HTR ground truth** (202 XML): unused. The images are not on disk; whether they can be fetched is unverified.
- **s45 lines and ink-gap words** (about 170 pages): never used for ink density.

**VKB gaps:**
- `folios.msi` = 1 only for f116v, although f1r and f17r are on disk.
- `quires.collation` is NULL for all 18 quires.

Fix both at the source before lead 1.

## What failed, plainly

- **Contact map (L-324, O-068).**
  - Prototype v1-v4, then a step-2 blob matcher against 52 held-out facing pairs (frozen by hash): 0/5 dev, 0/52 held out, inner over outer faces 17/41 (p 0.95), AUC 0.53. Every surface hit the 40-blob cap, so the matcher was picking up parchment texture.
  - The stain term is real but weak (5/52, p 0.0003), and it finds the same *sheet*, not which faces touched (outer 0.774 vs inner 0.780).
  - The five published links are now development data. The offsets are visible by eye (33v on 40r): what failed is the detector, not the evidence.
- **Glyph prototype (L-325).**
  - Only 0.337 exact count agreement with EVA. Rozanova boxes failed registration on 10 of 20 pages.
  - The label error rate has not been measured. Purity is biased toward U1. The hand signal is confounded with section and scan.
  - The betas (ch 1.66, sh 2.31, q about 0, e about 0.4) may be binarization artefacts; G2 has not run.

## Ranked leads

### 1. Conjugate leaves as the production unit (cheapest; splits F-32 and F-50)

- **Evidence.**
  - Layfield and Davis (2026): bifolia were decorated singly before nesting; all five published links are inner faces of one bifolio. So a sheet is plausibly one production batch, and its two leaves sit far apart in bound order (leaf k and leaf 9-k).
  - VKB: about 42 conjugate leaf pairs, all same hand, 38 also same section. My grouping was rough, so these counts are approximate.
  - A grep for "conjugate" in `results_*.txt`, `runs/*/*.txt`, CLAIMS and LEARNINGS found no test of this. Other folders were not searched.
- **Test.**
  - Distance between conjugate leaves on the s114 affix and word-length features (VKB `folio_features`), against non-conjugate same-quire pairs matched on bound distance.
  - Permutation within hand x section; ZL3b, RF1b and IT2a.
  - Frozen stub; a synthetic fixture with a planted sheet effect first.
- **Opposite predictions.** If F-32's drift follows the order of writing, conjugates should be *less* alike than neighbours. If sheets are batches, they should be *more* alike.
- **Refuted if** conjugates are no closer than matched pairs, at an MDE the fixture shows is reachable.
- **Cost.** Minutes of CPU, no images. The risk is power (about 40 pairs); compute the MDE first.
- **Splits.**
  - H-05/H-14 (a procedure or state re-set per batch) against H-06 (drift follows content).
  - It gives s111's batch arm physically defined batches (L-318: only 19 crossing pairs).
  - On "one system, five hands": VKB puts f57v (hand 1) on sheet H-1, which is otherwise hand 5, and fRos (hand 4) on N-1, which is hand 2. If Davis 2020 confirms these (unverified), hands shared sheets, which points to one workshop at one time.

### 2. h2 on image units against the same pipeline on a real Gothic hand (H-17's core question)

- **Evidence.** F-08: h2 moves with the alphabet and the boundary rule. L-321: low h2 is one of two signature anomalies (z -4 to -8). The prototype shows that ink does not cut ch, sh, the bench gallows, q or e as EVA does. The units needed to test this are already cut.
- **Test.**
  1. Run the frozen G2 (four binarization settings) and G0 (100 labels checked by someone other than the runner).
  2. Cluster at K = 16, 24, 32 and 48.
  3. Compute conditional entropy within s45 lines.
  4. Run the identical pipeline on bsb_clm5905 or Sloane 4016 (and CREMMA, if its images can be fetched, as the G1 letter ground truth).
  5. Report Voynich h2 minus control h2 at each K, against the EVA-based gap.
- **Refuted (low h2 is real)** if Voynich stays well below the control at every K and every stable setting. If the gap closes, low h2 is a transcription artefact and L-321 loses one of its two anomalies.
- **Cost.** About 2 CPU-hours and 0.5 GPU-hour (glyph README, section 4), plus about 1 hour for the control. A 20-page pre-check on the existing embeddings takes minutes; it is a fixture, not a result.
- **Splits.** H-17, H-02 and H-03 (which fail on h2, per F-25) against H-05/H-19 (a procedure makes the low h2). It also settles X-01 for F-39, F-40, F-41, F-46 and F-48, and gives O-020/X-08 a shape line (Q2, within-section null).

### 3. Ink fade and pen-dip cycles (cheap, novel, may die at the fixture)

- **Evidence.** A dip pen fades between dips and jumps darker at each re-dip. The s45 words give stroke pixels on about 170 pages. This has never been measured.
- **Test.** Median stroke L* per word gives a dip sawtooth; its fade direction gives writing direction. Use a left-to-right period manuscript as the positive control. Then ask:
  - (a) Does the fade run left to right? That would be a physical line for X-05.
  - (b) Do F-04's rhythm or F-13's in-line repeats lock to the dip phase (within-line shift null)?
  - (c) Do paragraphs start on a fresh dip?
- **Dead if** the control shows no sawtooth in the JPEGs. The fallback is the 16-bit MSI bands on 3 folios.
- **Refuted for (b)** if the rhythm and repeats are independent of the dip phase.
- **Cost.** 1-2 CPU-hours.
- **Splits.**
  - Rhythm locked to dips makes F-04 partly a motor artefact (H-11, for that finding only).
  - Repeats clustered within one dip suggest burst generation or copying (H-05/H-07/H-08) rather than composition (H-01/H-17).

### 4. MSI ink identity and layer order, f116v and f17r (moderate, history-grade)

- **Test.** Calibrate to the Spectralon patches in the frame. Then classify ink pixels by spectrum, comparing f116v marginal ink with main-text ink and the drawing outline with the text. Decide which layer is on top at crossings (Schwartz's text-over-drawing claim, on these folios only).
- **Uninformative if** iron-gall inks are spectrally indistinguishable (unverified, plausible). Same ink does not prove same time; different ink refutes the same campaign.
- **Cost.** About a day of design plus GPU hours. f1r's erased alphabets are probably a later reader's (unverified), so f1r has more historical than hypothesis value.
- **Splits.** Weakly. A f116v marginal in the main-text ink would be the author's only plaintext-like writing (H-01/H-17/H-06).

### 5. Contact map at native resolution (expensive, speculative; keep parked)

- **Test.** A new offset detector at native 2691x3770, against the same frozen 52-pair K2 gate and the K3 face contrast. IIIF has nothing larger, and the MSI covers too few folios for contact.
- **Refuted if** K2 fails again. Then close O-068.
- **Cost.** Days, with contaminated development data.
- **Splits.** X-04 and F-32/F-36 reading order. Run it only if lead 1 shows sheets are batches, so that the binding order matters.

## Recommendation

1. Lead 1 now: minutes, no images.
2. Then G0/G2 and lead 2. It is the one physical test that could remove half of L-321's signature.
3. Lead 3's control as a one-hour fixture.
4. Lead 4 after leads 1 and 2.
5. Lead 5 stays parked.
