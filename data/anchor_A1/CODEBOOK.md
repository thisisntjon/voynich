# s115-A1 image-category codebook (frozen before any classification)

Written Sun Oct 18 2026, before any image was classified. Run s115-A1 (D-066 entry (t)). Any change
after the freeze is a new file with a new name; this file is never edited.

## Blindness

Classifiers see only: this codebook, a list of image stems, and the masked images in
`data/anchor_A1/masked/<stem>.png`. They never see a transliteration, label list, token table,
results file, section name, folio number or the other pass. Masking (`s115_a1_mask.py`) paints out
glyph-sized ink not touching paint (policy M1); circular-diagram scans keep their text (policy M0,
downscale only) because their figures and circles are unpainted outlines drawn with the same pen as
the writing, and erasing glyph-sized ink removes them. Classifiers judge the drawing only and ignore
any writing or writing-like marks, including where text lies.

## Unit

One scan image (one file stem). A foldout scan with several panels is one unit. Page-level counts
cover the whole image. Where a category says "principal", it means the largest drawing of the
relevant kind (largest by drawn area); ties go to the leftmost, then the topmost.

## Output row

One tab-separated row per image, columns in this order, no header inside part files:

`stem PT P_plants P_root P_leafshape P_leafcount P_flower P_habit J_shape J_count J_fragcount J_fragtype C_centre C_animal C_figures C_rings C_diagrams C_rays B_pools B_figures B_tubes note`

Every column uses exactly one level token from the lists below. `NA` means the category does not
apply (wrong page type, or a condition stated below is not met). `note` is free text, at most 12
words, no tabs, `-` if empty.

## C0. PT, page type (every image)

Apply the rules in order; the first that fits wins.

1. `CIRCLE`: one or more circular diagrams (a figure organised around a centre with a circular
   outline, rings, rays or a circle of figures) that together cover at least a quarter of the image.
2. `BATH`: two or more human figures standing or sitting in pools, basins, tubes or flowing liquid.
3. `PHARMA`: one or more containers (jars, vessels, tubes standing upright as vessels), or four or
   more separate small plant parts (roots, leaves, sprigs) set out side by side in rows.
4. `PLANT`: at least one plant whose drawing is at least 30% of the page height.
5. `MARGINAL`: only small drawings (stars, small marks, small figures or objects) each under 15% of
   the page height.
6. `NONE`: no drawing at all (writing only, or blank).
7. `OTHER`: a drawing that fits none of the above.

## Plant categories (only when PT = PLANT, else NA)

Principal plant = the tallest plant.

- **P_plants** (separate plants, counted by separate roots or bases, each at least 30% of the height of
  the tallest): `1`, `2`, `3+`.
- **P_root** (principal plant's underground part). Decide in this order:
  - Is there a swollen part (a mass at least twice the stem width that is not just a tangle of thin
    lines)? If one smooth, rounded, roughly onion- or ball-shaped mass (height/width 0.5 to 2), with or
    without rootlets hanging from it: `BULB`. If swollen but irregular, lumpy, several lobes,
    knobbly fingers, or an elongated horizontal mass: `TUBER`.
  - Not swollen: one main root axis clearly longer and thicker than every side root: `TAPROOT`;
    two or more roots of comparable thickness diverging, forked or fibrous, no single dominant axis:
    `BRANCHING`.
  - No root drawn (stem ends, cut, or hidden): `NONE`.
- **P_leafshape** (the leaf type covering the largest area on the principal plant). First, if leaves
  are deeply toothed or lobed (incisions reaching at least a quarter of the way to the midrib) or
  compound (separate leaflets on one stalk, pinnate or palmate): `DIVIDED`. Otherwise by length to
  width ratio of a typical leaf: under 1.5 `ROUND`; 1.5 to 3 `ELLIPTIC`; over 3 (strap, grass,
  needle, narrow lance) `LINEAR`. No leaves: `NONE`.
- **P_leafcount** (separately drawn leaves on the principal plant; a compound leaf counts once):
  `0`, `1-4`, `5-10`, `11-20`, `21+`.
- **P_flower** (flowers, fruit or seed heads on the principal plant: a terminal or side structure
  that is not leaf-like: petals, a coloured head, cup, bell, spike, berry or cluster): `0`, `1`,
  `2-4`, `5+`.
- **P_habit** (principal plant): `ROSETTE` if leaves rise directly from the base with no visible
  stem, or every stem is shorter than the longest leaf; else `SINGLE` if one stem leaves the
  root/base (branching higher up is still SINGLE); else `MULTI` (two or more stems leave the
  root/base).

## Container / pharma categories (only when PT = PHARMA, else NA)

- **J_shape** (shape held by the majority of containers; tie goes to the larger containers): `CYLINDER`
  (straight, roughly parallel sides, may have lid, rim bands or feet); `VASE` (curved or bulging
  profile, neck, waist, goblet or pedestal form); `OTHER`; `NONE` (no containers).
- **J_count** (containers in the image): `0`, `1-2`, `3-4`, `5+`.
- **J_fragcount** (separate plant parts drawn outside containers: roots, leaves, sprigs, small whole
  plants): `0`, `1-5`, `6-15`, `16+`.
- **J_fragtype** (what most fragments are): `ROOTS` (at least two thirds are roots or underground
  parts with no leaves), `LEAVES` (at least two thirds are leaves or leafy sprigs without roots),
  `MIXED` (anything else, including small whole plants), `NONE` (no fragments).

## Circular-diagram categories (only when PT = CIRCLE, else NA)

Principal diagram = the largest circular diagram.

- **C_centre** (what fills the centre of the principal diagram): `ANIMAL` (any beast, fish, bird,
  scorpion, lizard, crab), `HUMAN` (one or more human figures), `FACE` (a sun, moon or star with a
  drawn face), `GEOMETRIC` (star, rosette, wheel, spokes, flower-like pattern, dots, without a face,
  animal or human), `EMPTY` (blank, or writing only).
- **C_animal** (only if C_centre = ANIMAL, else NA): `FISH`; `HORNED` (quadruped with horns);
  `HORNLESS` (quadruped without horns); `CRAWLER` (scorpion, lizard, crab, crayfish or other
  many-legged or reptile-like creature); `BIRD`; `OTHER`.
- **C_figures** (human figures anywhere in the image): `0`, `1-9`, `10-19`, `20+`.
- **C_rings** (concentric rings of the principal diagram: count the drawn circles around the centre
  disc, not counting the centre disc's own outline, then map): 0 or 1 circle `0-1`; 2 circles `2`;
  3 circles `3`; 4 or more `4+`. Bands of writing without drawn circles do not count.
- **C_diagrams** (separate circular diagrams in the image): `1`, `2-3`, `4+`.
- **C_rays** (straight radial spokes, rays, petals or wedge segments in the principal diagram):
  `PRESENT`, `ABSENT`.

## Bath categories (only when PT = BATH, else NA)

- **B_pools** (distinct basins: enclosed areas of liquid, painted, hatched or outlined, or tubs;
  a pool split by a drawn wall counts as two): `1`, `2`, `3+`.
- **B_figures** (human figures anywhere in the image): `1-5`, `6-10`, `11+`.
- **B_tubes** (pipes, tubes, conduits or channels drawn as objects): `PRESENT`, `ABSENT`.

## Agreement and keep rules (fixed before the pilot)

- Two independent passes (separate agents, no access to each other's output) label each image.
- Cohen's kappa (unweighted) per category. PT over all images. Every other category over the images
  where both passes gave a level other than `NA` (n reported); disagreement about applicability is
  carried by PT.
- Pilot (15 images, chosen by seed 115 by image group before any viewing): a category is kept if
  kappa >= 0.6. If n < 4 applicable pilot images, or kappa is undefined (both passes used a single
  level), the category is carried to the full run undecided.
- Full run (every image): labels are reported for every carried category, but only categories with
  full-run kappa >= 0.6 and n >= 10 are KEPT as frozen referents for A2; the rest are marked DROPPED
  in kappa.txt and must not be used by A2.
- Consensus `labels.tsv`: where the passes agree, the level; where they disagree,
  `DISAGREE:<pass1>|<pass2>`. Disagreements are never resolved by looking at text.
