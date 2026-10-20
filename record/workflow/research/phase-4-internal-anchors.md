# Phase 4 investigation: can the manuscript supply its own anchors?

Stamped `Sat Oct 17 22:19:36 PDT 2026` (output of `date`). Read-only investigation; nothing under Phase 3 was run.
Exploratory scripts and their outputs are in the session scratchpad
(`<home>/AppData/Local/Temp/claude/<agent-project>/<session>/scratchpad/p4_anchors/`:
`x1_pharma_herbal.py`, `x3_ring.py`, `x4_zodiac_angle.py`, `*_output.txt`). **Every number below marked EXPLORATORY
is a feasibility check: not pre-registered, not hashed, not a result.** Web content was read as data; nothing was downloaded.

## 0. The question and the q1 trap

An internal anchor is a link between a word and a specific depicted thing that (a) beats a matched null and (b) predicts
material not used to find it. Q1 showed labels are image-class-specific (z=+5.2), and s29/s35 showed a class-conditioned
837-type generator reproduces that (results_s29_q1_controls.txt; results_s35 Part 3: within-illus z=+5.11). So any test
whose positive a **class-level or page-level** conditioned generator also produces is not an anchor. The test has to be
**pair-specific**: this word goes with this one plant (or slot), not with this section or page. Two further alternatives
must be named in each pre-registration:

- **Copy-from-source.** A scribe redrawing a plant from page X might copy a word from page X without any meaning. The
  manuscript already shows line-above copying (m1 recency z +8.82, results_s35). A pair-specific link is therefore
  "the scribe associated word with plant", which is a necessary condition for naming but not proof of it.
- **Locality.** Nearby pages share rare words (a3: adjacent/distant Jaccard 1.2 to 1.55). Nulls must match hand, Currier
  language and quire distance.

## 1. Ranking (P(reaches a real anchor) × 1/cost)

P values are this session's judgement, not measured. Cost: low = under 1 h agent time, no human; medium = needs a human
for an hour or two; high = days or a human expert.

| Rank | Lead | P(anchor) | Cost | Human? | Score |
|---|---|---|---|---|---|
| 1 | **Same-plant pairs**: pharma label to herbal text (lead 1), merged with herbal-to-herbal duplicate plants (new lead 6) | ~0.05 | medium | yes: freeze the pair list and point each pharma plant to its label on the scan | best |
| 2 | **Predict-the-partner** (new lead 7): from text alone, name the herbal page for pharma plants nobody has matched, then a blinded human judges the images | ~0.03, conditional on rank 1 being positive | medium | yes: blinded image judgment | runs only after 1 |
| 3 | Label to its own page's paragraph, spatial position (lead 2) | ~0.01 | low | no | low; copying confound |
| 4 | Duplicated illustrations: zodiac slots, rings, two-page months (lead 3) | ~0.005 | low | no | mostly done, null |
| 5 | Numerals from counted objects (lead 4) | <0.005 | medium to high | yes: counts from scans | lowest |

Lead 5 (2023 to 2026 literature) is folded into each lead's prior-art line. Short version: **nobody has run a
null-controlled, pair-specific test of the pharma-to-herbal label link.** The drawing correspondences were refreshed in
November 2025, and the text side was explicitly left undone.

## 2. Lead 1 (+ new lead 6): same-plant pairs

**Prior art.**

- **ZL3b carries the pairs.** `data/ZL3b-n.txt` has 14 `# Same plant as ...` comments (Petersen, Stolfi, FSG, GL): f1v,
  f3v (root), f18v, f19r, f23r, f32v, f37v, f47v, f48r, f90v1, f90v2 and f96v point to pharma f89v2, f99r, f100r, f100v,
  f102r1, f102r2 and f102v1. f39r points to herbal f95r2, and f48v to f89v. Nine of the 14 carry a "?".
- **Stolfi's 2025 refresh.** On 16 Nov 2025 Stolfi posted seven strong pairs, all onto f102r1 and f102r2 except f19r, and
  said each pharma sketch is "a proper subset" of the herbal figure. Two of his cells differ from ZL: f19r is f102v-2.3
  against ZL [2,2], and f23r is 3.2 against ZL [3,1]. Bernd started the thread, and asked about the text side he chose to
  "leave text analysis to others" (quote unverified beyond the archive page). Source:
  [voynich.ninja thread 4067 p19, "Matching Plant Images Internally"](https://www.voynich.ninja/archive/index.php/thread-4067-19.html).
- **Older unnulled checks.**
  - Oocephalus (Feb 2016) checked rare pharma labels such as `otory` (f102v2) and `opchor`, found only vague look-alikes,
    and used no null ([thread 196](https://www.voynich.ninja/archive/index.php/thread-196.html)).
  - A 2017 check of more than 200 pharma labels found "only a few close matches" (search summary only, **unverified**;
    [printthread 2013](https://www.voynich.ninja/printthread.php?tid=2013)).
- **Zandbergen's label article.** Pharma labels are 234 tokens, 89 % hapax, and Currier A-like. Zodiac and pharma labels
  share only 13 types ([voynich.nu/extra/labels.html](https://mail.voynich.nu/extra/labels.html)).
- **Pharma layout.** Zandbergen (Aug 2025) lists the bifolios as f88+f89, f99+f102 and f100+f101, and argues the f88r
  top-left label is misplaced ([thread 4853](https://www.voynich.ninja/archive/index.php/thread-4853.html)).
- **On disk.** `data/external/papers/rozanova_2608.17096_src/.../decipherment_attack/plant_crib_attack.py` (Rozanova
  2026 bundle) already reads the ZL "Same plant as" comments and ranks the labels. It has **no null** and no output on
  disk; its results are unknown.
- **Project files.** a3 and d6 tested labels against the page's own text only, never the cross-page pair.

**EXPLORATORY check (x1).** For each ZL pair, the referenced pharma labels were scored against every herbal page with
more than 30 paragraph tokens (128 pages). The score is exact or edit-1 matches over sqrt(text length). The statistic is
the rank of the true herbal page.

- Page-level label sets: mean percentile 0.566 over 12 pairs, P 0.215 against a uniform null. Row-level: 0.541, P 0.315.
  **No strong link.**
- **Feasibility problems found:**
  1. The approximated rows are unreliable. Each Lc (container label) was taken to start a row, and f102r1 has only one
     Lf label for several plants.
  2. Many redrawn plants appear to carry **no label of their own**: f1v and f37v both point to f102r1 row 3, whose only
     label is a container label. This is unverified on the scan.
  3. Two herbal pages point to the same cell: f18v and f23r both go to f102r2[3,1] in ZL.

  The testable N is therefore about 5 to 10 label-to-plant pairs, which only has power for a strong effect.
- An eyeball check of the herbal first words (for example `told`, `pydchdom`, `psheot`) against the partner labels shows
  nothing obvious.

**Smallest pre-registerable test.**

- **Freeze the pair set first:** the ZL strong set, Stolfi's 2025 seven, and the herbal-to-herbal duplicates from thread
  4067. A human then marks on the scan which label (if any) sits on each pharma plant. That is about 1 to 2 h, from the
  Beinecke images or Stolfi's posted clips.
- **Statistic A (label to page).** For each labelled pair, take the rank of the true herbal page among all herbal pages
  of the same Currier language and hand, by best label-to-text similarity. Use three fixed tiers: exact; edit distance 1;
  same core under the project's SlotSegmenter. The first paragraph word gets a pre-stated weight, because a medieval herbal
  normally opens with the plant name.
- **Statistic B (herbal to herbal, new lead 6).** For duplicate-plant herbal page pairs, measure rare-word overlap (types
  with fewer than 5 occurrences) against all page pairs matched on hand, language and quire distance. This gives far more
  tokens than a single label.
- **Nulls.**
  1. Rank uniform over matched pages.
  2. Decoy labels: other labels from the same pharma page.
  3. A generator control: the s35 `G_unit_cond_837_matched` labels, conditioned on section. They give uniform ranks by
     construction; run it to show the pipeline yields no false positive.
- **Anchor criterion.** The mean rank percentile beats both nulls at a pre-stated alpha after the round correction, AND
  the effect holds on the held-out half of the pairs (split by a fixed seed before looking).
- **What a positive is and is not.** A positive would be pair-specific and beyond any class-conditioned generator. It
  would still be compatible with copy-from-source. It counts as a proto-anchor (Tier 3+), and becomes Tier-1-directed
  only through lead 7.

**Cost.** Compute is low: one CPU script, minutes. The human time, 1 to 2 h to freeze pairs and label positions from
scans, is the gate.

## 3. New lead 7: predict the partner (the predictive half of lead 1)

Pharma plants with no published herbal match are the untouched material. From labels alone, the lead 1 scorer emits a
ranked herbal page for each one. A human who does not see the ranking then judges the image similarity of the top
candidate against a decoy. A hit rate above the decoy rate is the first thing in the project that would predict content
from text. Even then it is "words point to plants", not a reading.

- **Cost:** medium (blinded human session of about 1 to 2 h).
- **When:** only if lead 1 is positive; otherwise it is underpowered noise.

## 4. Lead 2: label word in its own page's paragraph, and where

**Prior art.**

- a3 found a hit rate of 0.121 against 0.107 (p 0.106).
- d6, the powered version (results_d6.txt B), found 12.1 % against a section-permuted 10.6 % (p 0.0945): null.
- d6's sensitivity run, which counts any non-label unit as page text (so zodiac circle text is included), reached p 0.02
  (14.4 % against 11.8 %). That positive is page-level and therefore inside the q1 trap.
- Forum readers noticed the labels "apparently don't" return in their paragraph
  ([thread 2862 p8](https://www.voynich.ninja/archive/index.php/thread-2862-8.html), search summary, **unverified**).

**EXPLORATORY checks.**

- **x1/X2.** 51 of 622 labels of at least 4 glyphs recur in their own page's paragraph text. The hits sit early: median
  line fraction 0.26, and 10 of 51 are the first word of their line. There is no null, so it is uninterpretable as it
  stands.
- **x4, zodiac.** ZL gives clock positions for the Lz labels and the Cc ring starts. 25 of 282 labels recur in their own
  page's ring text, mostly common words (`otar`, `oteey`, `daiin`). The mean angular distance to the nearest recurrence
  is 0.221 turns against 0.237 under random angles (P 0.288): **null.** The ring angles are approximated from word index,
  which is crude.

**Smallest test.** Spatial version: is a label word closer (on the page) to its recurrence in the paragraph than a
within-page rotated null predicts? Use the coordinate boxes behind `m1_coordinates.py`; whether they cover labels is
**unverified** (O-019 notes they come from voynichese.com and are 3-px snapped).

- **What a positive would mean.** It would beat a page-conditioned generator, but the m1 line-recency copying habit
  predicts it too. It is not an anchor unless the recurring word is rare and its position is not the line just above or
  below.
- **Cost:** low. **P(anchor):** low.

## 5. Lead 3: duplicated or near-duplicated illustrations

**Prior art (project).**

- **Two-page months.** In `research_notes/External anchors/zodiac_months.md`, the two Aries pages (f70v1 and f71r) share
  0 month-unique tokens. The two Taurus pages share only `chal` (49 occurrences manuscript-wide) and `okeodaly`, and not
  in the same slot. Best zodiac slot 9/10 against shuffle P 0.35.
- **Same nymph slot.** Q1 test C found no same-position repeat across the 12 zodiac pages (z -1.4). The s29 planted-crib
  power curve has power 1.00 at exact-token and core-stem level, and the manuscript's stem z is -0.00. **Same-slot
  nymph labels are dead at tested encodings, with power.**
- **f57v ring.** e3 shows a 17-word block repeated 4 times, with 15 of 17 positions stable. It is internal repetition,
  but nothing points outside it.

**EXPLORATORY check (x3).**

- **Without ring identity.** A naive check of the first two glyphs against the label's position index gave P 0.000.
- **With ring identity.** Once ring identity is respected (each `@Lz` block is a ring, and the rotation stays within
  rings), it is null: P 0.864 at bin 3 and P 0.369 at bin 5.
- **Reading.** The naive signal was outer-against-inner ring composition (MI(ring; first2) = 0.19 bits): a class effect,
  which is exactly the q1 trap.

**What remains.** Bath figures and star rings are not true duplicates, so there is no pair to test. Bernd's 2025 thread
lists herbal-to-herbal duplicates, and those belong in lead 1 / statistic B. **Cost:** low. **P(anchor):** very low.

## 6. Lead 4: numerals from counted objects

**Prior art.**

- ZL comments give counts, for example f70v2 has 19 + 10 nymphs, "NOT 20".
- Stolfi's Note 040 tables give nymph position, star and decoration.
- Forum work: 30-nymph signs such as Gemini have 28 left arms and 29 stars, and Pisces omits a nymph; these are read as
  scribal error ([thread 5160 p24](https://www.voynich.ninja/archive/index.php/thread-5160-24.html), search summary,
  **unverified**).
- A 2025 thread proposes reading the nymphs as zodiac degrees (same source, **unverified**).
- On disk: `data/external/cribs/stolfi_f68r3_data.txt` and the Bax f68r pages.
- If nymph labels were degree ordinals (1 to 30), the same label, stem or prefix would recur at the same ordinal across
  signs. The s29 power curve and x3 rule this out at exact, stem and first-two-glyph level.

**Smallest test.**

- A human counts objects (stars per f68r cluster, petals and roots per pharma plant, nymphs per ring) from the scans.
  Pre-register one candidate numeral feature: the count of `i` strokes in `-aiin`/`-aiiin`, or word length.
- Test rank correlation against the counts, with a null that permutes counts within section.
- n is small (12 zodiac pages, about 30 star clusters), and the multiplicity is high.
- **Generator note.** A count-conditioned generator is implausible, so a positive would be strong evidence. But P is very
  low, because label hapax rates (80 to 89 %) leave no closed numeral inventory.

**Cost:** medium to high (human counting).

## 7. What would move Tier 1, and what would not

- **Would move it.** Only lead 1 followed by lead 7 can produce something that predicts untouched material from text.
- **Gate.** Both need a human hour to freeze the pair list and label positions before any script runs. Run lead 1 first
  as a pre-registered test.
- **Stop rule.** If its held-out half is null, stop the internal-anchor line and record it as a powered negative: state N
  and the minimum detectable effect.
- **Would not move it.** Leads 2 to 4 are cheap but already null or confounded. They are worth at most one bundled
  low-cost script, scored as Tier 3 negatives.
