# External-prediction test designs (research note, not a status file)

Written 2026-10-18 12:09 PDT (clock read with `date`). Read-only survey; no existing file was edited, no test was run.
Inputs: AGENTS.md, workflow/FINDINGS-MAP.md, workflow/PLAN.md, .inventory/registers/LEARNINGS.md, Daybreak synthesis
`codex_lab/reviews/voynich_top10_evidence_directions_2026-10-18.md` (read as data), the result files cited below.
Abbreviations: **V** = `.`, **C** = `lab/codex_lab`,
**RZ** = `V\data\external\word-coordinates\lrozanova-voynich-units-main\voynich-units-main\data`.

Why this note exists: the map's findings mostly lack an `external` axis (FINDINGS-MAP: F-03 and F-11 carry `external` only as
literature agreement; F-10 is literature-only). Every structural result describes *how* the text was produced. Only a correct
prediction of a held-out fact that the model never saw can move us toward *what* the text says.

## 1. External data on disk

Sizes come from the inventory sub-agent (du/ls, 2026-10-18). I opened only the s112 CSV header myself; the other rows are its report.

| Kind | Path | Size | What it is |
|---|---|---|---|
| Scans | V\data\external\yale_scans\pages\ | 204 jpg, 522 MB | Yale IIIF full-resolution scans, f1r–f116v (~2.6–3.0k x 3.7k px). Foldout panels are not split out. |
| Scans | V\data\facsimile\ (f1v, f57v, f68r, f75r, f99r, f116v) | 7 files, 7.5 MB | Single-page facsimiles. |
| Folio structure | V\data\folio_evidence_inventory.tsv | 22.5 KB, 227 folios | Quire, page-in-quire, bifolio, section, Currier language, hand, line, token and label counts. This is the codicology table. |
| Picture class per page | ZL3b `$I` page headers in V\data\ZL3b-n.txt | 412 KB | Illustration type for 228 pages (H 129, S 25, B 19, P 17, Z 12, C 11, A, T), plus quire `$Q`. |
| Label picture class | ZL3b label locus types | (same) | Lz 299, Lf 194, L 160, Ls 76, Ln 63, Lt 47, Lc 40, minor others. Ring and circle loci: Ri 75, Cc 72, Ro 67. |
| Label to object | C\acquisition\s112_object_label_registration.csv | 14.3 KB, 97 rows | Label loci with x/y, the nearest s48 crop and its distance, and a jar_like flag. |
| Stolfi classes | C\acquisition\s113_stolfi_label_attributes.csv; s114_stolfi_full_label_catalogue.csv | 14 KB / 18 KB | 84 and 239 loci. Classes are plant 168, root 46, container 25 on 14 pharma pages. There are no star or nymph classes. |
| Star/zodiac cribs | V\data\external\cribs\stolfi_f68r3*, stolfi_f70v2.htm, stolfi_f72v2_data.txt, voynich_nu_f07*_tr.txt | 2–17 KB each | Astronomical and zodiac label data. |
| Month names | V\research_notes\External anchors\zodiac_months.md; ZL3b `#` comments | 8 KB | Prose note only. **No structured month table.** |
| Plant IDs | V\data\external\cribs\sherwood_plant_list_p1–p14 (.html + .txt) | ~240 KB | Sherwood's proposed identifications per herbal folio. These are contested and not independent of each other. |
| Herbal crops | V\runs\s48\crops\ (123 H_ + 405 P_ part crops), crops.json | 102 MB | Text-masked whole-plant and object crops. **The full masked-page set for s78 was not saved; only 6 samples exist.** |
| Embeddings | V\runs\s78\embeddings.npz; s48\embeddings.npz; s53\embed.npz | 1.5 / 3.3 / 78 MB | DINOv2 and SigLIP vectors. Model weights are in V\data\external\models (1.1 GB). |
| Human labels | C\experiments\s101_annotation_sample.json | 4.6 KB | 24 pages, 4 booleans each. This is a validation sample, not training data. |
| Pixel geometry | C\experiments\s102_objective_geometry_metrics.csv | 10 KB | Six pixel metrics for each of the 119 herbal pages. |
| Lines and ink | V\runs\s45\pages\ (171 json); s47\positions.tsv, lines.tsv; RZ\...\voynichese_boxes\ (223 .js) | 8.8 MB / 2.6 MB / 2.1 MB | kraken baselines and ink-gap segmentation; ink width at each position; Rozanova word boxes. |
| Direct ink gaps | RZ\direct_pixel\results_unblinded.csv | 301 rows | 283 boundaries on 6 folios (the o1 input). |
| Antidotarium | C\acquisition\s115_antidotarium_nicolai_latin_recipes.csv; s119_*_recipes.csv | 233 KB; ~0.4 MB | 141 Latin recipes, plus Scribonius, Liber de coquina and CoReMA. |
| f57v / f116v / marginalia | f57v.jpg, RZ f57v.js; cribs\stolfi_f116v.htm, ciphermysteries_f116v*; research_notes\External anchors\multispectral_marginalia.md | small | Images and notes only. **No multispectral images were downloaded, and there is no marginalia data file.** |

Not on disk: annotations of recipe-section star markers, nymph attributes (tub, clothing, star held), a structured month table,
and multispectral marginalia.

## 2. What has already been tried

| Test | Result | Why it failed or stayed open |
|---|---|---|
| a3 / d6: labels name things on their own page | 0.121 vs a null of 0.107, p=0.106 (L-032) | Whole-word matching. Power curves later invalidated this as a negative (c-322/323). |
| m6: labels form a list or nomenclature | No list order; labels are o-initial and hapax-rich (L-033) | Descriptive only; no external target. |
| q1 / s29: label crib | Labels repeat within the same illustration unit (z=+13.9; +5.2 against a within-illustration shuffle). Same zodiac position: z=-1.4 (L-152). | A class-conditioned generator reproduces the clustering (O-044 closed). This is how labels are produced, not what they mean. |
| s52 T2a/T2b: zodiac 7-cycle and degree-position cores (350 Lz labels, 12 pages) | All null on 3 transcriptions, including the best circular offset with reflection. Power gates passed at 15% shared stems. (F-28; results_s52_p4comp1_antidotary_zodiac.txt) | **Closed at adequate power for strong effects.** Numbering by ring position is excluded. |
| s48 / s53 / s54: herbal and pharma same-plant anchor | Image matching works at part level (P=.0005). Pharma labels share no text with the partner page; the 13/13 control passed (F-20, L-147..149). | Only 13 pairs, so only a strong link was testable. |
| s78: picture similarity vs cores | Cores r=.007–.053 on 119 pages. Frames r=.077–.100, p≈.01. The C+ gate failed (17/20); MDE r≈.23 (results_s78.txt l.68–74). | **Underpowered and inconclusive.** The Mantel test on 7021 non-independent pairs makes the effective n page-scale. |
| s86 Part 2: frame–picture decomposition | The frame link follows page and obstacle layout (D_layout r=+.095, p=.0005) and is segmenter-dependent (results_s86.txt l.205). | The frame association is partly layout, so it is not semantic. |
| s99: label vs quire tail | 1 eligible page, 3 events (C\experiments\results_s99_*.txt) | Not a test; inadequate n. |
| s100 / s101 / s102: tail vocabulary vs picture | r=.04–.08 (detects about .30). Zero-shot vision failed validation (AUC .12–.59). No pixel metric replicates. | Only large generic effects are excluded. |
| s108: f57v as a Latin consonant key | 0/15 quires reach q99 | Direct substitution rejected. The meaning of the diagram is untested. |
| s109–s111: label tail cores retrieve own page body | MRR .630 vs q99 .588, p=.002 (22 pages, 173 events, 4 groups); holds leave-one-group-out. The strict representation gate fails. | **The only positive bridge.** It is representation-dependent and page-level, not object-level. |
| s112: label sharing vs object visual similarity | +.158 (p=.29); +.297 without containers (p=.131) | Generic similarity is closed. Specific attributes remain untested. |
| s113: container vs botanical label form | Page AUC .407 vs q99 .862 (5 pages, 8 positives) | **MDE AUC ≈.87 at 8 vs 32 (§4), so this could only detect near-perfect markers.** |
| s114: exact repeats share a Stolfi class | 20/31 agree, equal to the null median | 31 pairs: weak power. Redirects toward contents and preparations. |
| s116–s118: Antidotarium | A generic formula-graph resemblance (r=.108). The source-specificity check fails (p=.054); s116 is underpowered. | No token↔core pair is stable. Antidotarium is not identified. |
| Names and marginalia (O-029/O-030) | No marginalium is an anchor | n of 1–3 items; no statistical test is possible. |

Pattern: the external targets so far were either **coarse visible classes** (plant/root/container, picture embeddings), which
the text does not track, or **tiny n** (13 pairs, 5 pages, 1 page). The one positive result (s109) is page-local. It matches the
architecture, which says identity information lives in a page/quire-local tail inventory.

## 3. Designs that follow from the architecture

Shared rules for all designs:
- Pre-register with a sha256 stub.
- Score on 3 transcriptions (ZL3b, RF1b, IT2a).
- Use SlotSegmenter, with Canon+Comp or a fixed trim as a representation check.
- Include a planted positive control sized to the stated MDE. Treat a power-gate failure as **inconclusive**, never as null.
- The architecture has four claims. (a) Cores carry identity; frames carry line state and layout (F-11, F-15, s86). (b) Identity is local, concentrated in a quire/register tail pool (s95–s97). (c) The line is the production unit (F-01..F-04). (d) Labels draw on their own page's tail (s109).
- A design qualifies only if it predicts something that a frame-only or layout-only model does **not** predict.

### E1. Label → its physical neighbourhood in the page body (object-level extension of s109)
- **Prediction:** a label's tail core recurs in body lines that are physically *nearer* to that label than other body lines on the same page. The label's frame and the head cores show no such gradient.
- **Why the architecture implies it:** s109 puts the label–body link in tail cores, at page scale. If a core names or refers to the drawn thing, the text discussing that thing should sit next to it. If the tail is only a page-level pool, the link should have no spatial gradient. Frames are line-state/layout, so frames act as the built-in negative channel.
- **Held-out data:**
  - Label loci with x/y from s112 (97 rows), extended to all ZL label loci on herbal, pharma and astronomical pages via RZ boxes.
  - Body-line positions from s45 baselines.
  - Only events where the core occurs ≥1 time in the page body are used (s109's 173 events are the starting pool).
- **Statistic and null:**
  - Statistic: the normalized distance rank of the nearest matching body line among all body lines of the page. The null is uniform at 0.5.
  - Primary null: permute which body lines carry the core, within page and within line-position band (first/middle/last), so the core's line count is preserved.
- **Controls:**
  - Frame-only and head-core versions of the same statistic should show no gradient.
  - Planted fixture: insert the label core into the k nearest lines.
  - Layout control: labels in the left margin vs the right margin.
  - **Adversarial confound:** production recency. A label written right after its neighbouring lines would share cores through the in-line/recent-reuse mechanism, not through reference. To discriminate, require the gradient to hold for labels separated from text by a drawing (an obstacle) and for cores that do *not* occur in the immediately adjacent line.
- **Call:** support if the mean rank is below the q01 of the null on ≥2/3 transcriptions, the frame control is null, and the obstacle-separated subset keeps the sign.
- **Power:**
  - With 85–170 usable events, the MDE (one-sided α=.01, power .8) is a mean-rank shift of .10 to .07.
  - Page clustering on about 22 pages (deff ~2) makes it .10–.14, so only a moderate gradient is detectable.
  - n is adequate if ≥80 events survive the core-in-body filter. **Unverified** how many survive; count them first, before freezing the stub.
- **What a positive would mean:** high value. It would be the first object-level referential link, pointing to cores as names of drawn items.

### E2. Recipe-section star markers predicted from the paragraph's first line
- **Prediction:** an objective visual class of each paragraph's star marker can be predicted from that paragraph's first-line frame and core profile on held-out pages. Candidate classes: filled vs hollow, tailed vs plain, or colour fraction.
- **Why the architecture implies it:** the line is the production unit, and the first word carries a distinct start vocabulary (F-01/F-02). If paragraphs are typed entries, the typing should be visible in the start line. Typing that lives only in a page/quire pool would fail page-held-out prediction.
- **Held-out data:**
  - About 285 paragraphs on f103r–f116r (S52 corrected count, ZL3b), split by leave-one-page-out.
  - Star features are measured by pixel rules from the Yale scans at the paragraph-initial locus, located with s45 coordinates.
  - **No star annotation exists on disk.** The feature extractor must pass its own validation first, the s101 lesson: a 24-star sample, human-checked, before the text is touched.
- **Controls:**
  - Page-blocked permutation of star classes.
  - Line-length and position-only baseline.
  - The same test on the 2nd line of each paragraph should be weaker.
  - Planted class marker in frames.
- **Call:** support if held-out AUC beats the page-blocked q99 and the position-only baseline on ≥2/3 transcriptions.
- **Power:**
  - Independent n=285 (140/145) gives an MDE AUC of .61.
  - If star class is mostly constant within a page, the effective n falls toward about 23 pages (deff ~4) and the MDE becomes .72.
  - **Stop rule:** if the star class varies within fewer than 8 pages, do not run.
- **What a positive would mean:** medium-high value. Entries would carry a visible category that the text encodes, which is the first text→external-category mapping.

### E3. Leaf → its quire (codicological prediction from the tail pool)
- **Prediction:** hold out one leaf (both sides). Assign it to its physical quire, among quires of the same section and hand, using only tail-core recurrence learned from the other leaves. Then check whether leaves the codicological literature flags as possibly misbound are the ones assigned to another quire.
- **Why the architecture implies it:** s95–s97 say tail-repeat identity is a quire/register property, held across sheets within a quire but not across quires. The physical quire assignment was never used to fit a core.
- **Held-out data:**
  - folio_evidence_inventory.tsv quire and bifolio columns.
  - Strata with ≥3 quires sharing section and hand: Herbal-A (about 7 quires, about 56 leaves) and any B strata that qualify.
- **Controls:**
  - A head-only and frame-only classifier, which the architecture predicts will be near chance.
  - The conjoint-sheet shortcut must be removed: drop the held-out leaf's conjugate from training.
  - Permute quire labels within the stratum.
- **Call:** support if accuracy is above the permutation q99 on all 3 transcriptions and the frame-only classifier is not.
- **Power:**
  - Chance is 1/7 ≈ .14. At n≈56 leaves the MDE accuracy is ≈.29; at 100 leaves and 18 quires it is ≈.13 vs chance .056.
  - Each leaf aggregates roughly 100–300 tail opportunities, which turns s97's small per-token gain (+.005 bits) into about 0.5–1.5 bits per leaf. That is plausible but **unverified**. Run a planted check at s97's effect size first.
- **What a positive would mean:** low-moderate value. It is strong for the *how* (gives F-17/F-32 a physical-external axis) and useful for reconstructing the original order. It says nothing about meaning.

### E4. Within-page label picture class from core vs frame (ZL locus types)
- **Prediction:** on pages that carry ≥2 label classes, a label's picture class (ZL Lf / Lc / Ls / Ln / L, plus Stolfi classes) is predicted by its core on held-out pages, and not by its frame.
- **Why the architecture implies it:** cores carry identity and frames carry position. s113 tested raw forms on only 5 pages.
- **Data:** ZL locus types for about 900 labels, Stolfi s114 for 239. Restrict to mixed-class pages, an **unverified** count. Leave-one-page-out.
- **Controls:**
  - Within-page class permutation.
  - Frame-only model.
  - Locus-position-only model, to guard against layout leaks such as labels on the ring vs the centre.
- **Power:** at s113's scale (8 vs 32) the MDE AUC is about .87, which is hopeless. Run only if ≥50 minority-class labels exist on ≥10 mixed pages; at 50/50 the MDE AUC is .68.
- **What a positive would mean:** medium value. Note that s114 already makes coarse visible classes unlikely, so the prior is low.

### E5. Composition surprisal → physical hesitation in the ink
- **Prediction:** words whose core is a *new* tail core in the line or page (high surprisal under the quire pool model) are preceded by wider ink gaps or a longer pen-lift than predictable cores, after controlling for word length, initial glyph and line position.
- **Why the architecture implies it:** composition at the line with a locally activated pool (F-21 says errors look like composition) implies retrieval cost for new items. A copyist working from an exemplar would show no such relation.
- **Data:** s47 positions.tsv / lines.tsv and RZ boxes (about 223 pages); held-out quires (LOQO); ZL3b-aligned tokens.
- **Controls:**
  - Frame surprisal vs core surprisal.
  - A copied-Latin manuscript with gap measurements, if one is available. **Unverified** that one exists (CREMMA has no gaps).
  - Shuffled surprisal within line.
- **Power:** n is above 10⁴ tokens, so the MDE is a partial r of about .03 even with page clustering. Very high power.
- **What a positive would mean:** low value for meaning (*how*). It does add a physical-external axis and decides compose vs copy.

### E6 (not recommended now). Plant identity across quires (Sherwood IDs or the 13 known pairs)
Same-identity pages in different quires should share tail cores above the quire baseline. Noisy and contested labels attenuate any r. With 119 pages the MDE r is about .29, the same as s78 and s100, and only 13 known pairs exist. This was already underpowered (s54, s78, s100) and should not be repeated without a new, larger, validated identity set.

## 4. Power-adversarial ranking

MDE formulas: AUC SE = sqrt((n1+n2+1)/(12 n1 n2)); correlation via the Fisher z test; mean rank via SE = .289/sqrt(n). All at one-sided α=.01 and power .8; deff is the cluster inflation. These are my calculations, not measured fixture curves. Every design must still pass a planted gate at the stated MDE.

| Rank | Design | Effective n | MDE | Power verdict | Movement toward *what* |
|---|---|---|---|---|---|
| 1 | **E1 label → spatial neighbourhood** | 85–170 events / ~22 pages | Rank shift .07–.14 | Adequate for a moderate gradient; count events first | **High** (object-level reference) |
| 2 | **E2 star marker ← first line** | 285 paragraphs / ~23 pages | AUC .61–.72 | Adequate only if the class varies within pages; extractor gate first | **Medium-high** (entry typing) |
| 3 | E3 leaf → quire | ~56–100 leaves | Accuracy .29 vs .14 | Probably adequate; planted check at s97 effect size | Low-moderate (physical how) |
| 4 | E5 surprisal → ink hesitation | >10⁴ tokens | r ≈ .03 | Very high | Low (how; compose vs copy) |
| 5 | E4 label class ← core | 40–900 labels on mixed pages | AUC .68–.87 | Weak unless ≥50 minority labels | Medium, low prior after s114 |
| 6 | E6 plant identity across quires | 13 pairs / 119 pages | r ≈ .29 | Underpowered (repeat of s78/s100) | Medium if positive; not runnable |

**Order to run:**
- E3 and E5 first. They are cheap and high-powered, and they give F-17/F-32 and F-21 an external (physical) axis while the larger builds proceed.
- E1 is the main bet. It extends the only positive bridge and has a built-in negative channel (frames).
- E2 depends on a validated star extractor. Build it as a separate step with its own gate.

**Lessons that bind all six:**
- s78 failed on its control, not its effect. Size the planted control at the MDE the design claims.
- s95 showed that per-quire statistics lack power. Pool across quires, and report per-quire values only as descriptions.
- s113 showed that 8 positives can detect only a near-perfect marker. Refuse to run any design whose minority class has fewer than 30 events.
- Positives must survive the production-recency confound (E1) and layout leaks (E2, E4). Otherwise they are more *how*, not *what*.

File each result through workflow/TRIANGULATION.md with an `external` (or `physical`) line, so that the map's empty external axis is
actually exercised.
