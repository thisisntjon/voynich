# Real-line Moran closer: checked result and team-claim review

## Verdict

The missing like-for-like comparison does **not** show that real-line human
gibberish reproduces the Daybreak result.

Native-line pooled Gaskell–Bowern human gibberish has within-line word-length
Moran's I `0.097973`. It is below the minimum full-transcription Voynich value
`0.154868` and below the prior registered-control maximum `0.128961`. More
decisively, it fails the same within-line shuffle test: observed `0.097973`
versus null median `0.102976`, q99 `0.120871`, one-sided `p=0.753`. It passes
the position-stratified null (`q99=0.054092`, `p=0.001`), but the registered
Daybreak conjunction requires both nulls.

The known s17 value `0.119430` is exactly reproduced as the whole concatenated
stream statistic. It is not the Daybreak within-line statistic. Cross-line
boundaries supply `31.19%` of the human-gibberish lag numerator, versus only
`1.46%` to `3.16%` in the three Voynich transcriptions. Re-cutting the same
gibberish stream into arbitrary eight-token lines raises its within-line value
to `0.122414`, still below `0.128961` and without evidentiary weight as a native
line effect.

The correct reading is therefore:

- the **whole-stream** N5 Moran value looks gibberish-like;
- the **line-internal excess over a line-preserving null** currently does not;
- the Daybreak ablation successfully separated those two statements.

This result preserves the Voynich constraint while narrowing its meaning. It
does not prove language, cipher, semantics, or any specific generator.

## Frozen closer

The experiment was frozen after the s17/s18 whole-stream results were known but
before any of these 64 sidecars was scored with the Daybreak within-line
formula. This makes it a post-hoc closer, not a blind confirmation.

- 73 input/provenance files were copied and bound by a manifest.
- All 64 s17/s18 sidecars were scored with the exact Daybreak statistic.
- The 25,000-token whole-line cap matches s17/s18.
- The primary eight native comparator rows received 999-draw within-line and
  position-stratified nulls.
- Every null starts from a fresh PCG64 seed `20261018`; no seed offsets are used.
- The decision code explicitly checks both q99 exceedance and `p <= .01`.
- A deterministic second run reproduced `result.json` byte for byte.

## Primary comparison

| Corpus | Whole-stream I | Within-line I | Line-shuffle q99 / p | Position-null q99 / p | Cross-line numerator share | Daybreak-style result |
|---|---:|---:|---:|---:|---:|---|
| Voynich ZL3b | 0.140670 | 0.157244 | 0.080927 / 0.001 | 0.030580 / 0.001 | 1.46% | passes both |
| Voynich RF1b | 0.140844 | 0.154868 | 0.081452 / 0.001 | 0.029931 / 0.001 | 3.16% | passes both |
| Voynich IT2a | 0.141016 | 0.156595 | 0.081172 / 0.001 | 0.027532 / 0.001 | 2.24% | passes both |
| Human gibberish, native lines | 0.119430 | 0.097973 | 0.120871 / 0.753 | 0.054092 / 0.001 | 31.19% | fails conjunction |
| CREMMA prose15 pool | -0.041523 | -0.033091 | 0.034764 / 1.000 | 0.065538 / 1.000 | 29.24% | fails conjunction |
| CREMMA c15 pool | -0.031553 | -0.019227 | 0.016698 / 0.956 | 0.053726 / 1.000 | 47.42% | fails conjunction |
| CREMMA all pool | -0.016942 | -0.018100 | 0.051392 / 1.000 | 0.066368 / 1.000 | 3.77% | fails conjunction |

Removing exact adjacent repeats retains `96.43%` of the human-gibberish
within-line value. Repetition is not the reason it fails. It fails because its
raw positive value is already expected when each real line keeps its own
word-length multiset. In other words, line-to-line composition can explain the
pooled gibberish value without a within-line ordering rule.

## All 64 sidecars

The maximum among all 64 new sidecars is `0.122414`, from the arbitrarily
eight-token-re-lined gibberish stream. The native human-gibberish row is
`0.097973`.

The highest native base CREMMA manuscript is `cremma_LaurPlut39.34` at
`0.102312`, but it contains only 770 tokens. The highest mark-preserving
CREMMA sensitivity is `cremma_LaurPlut33.31_marks` at `0.108057`, with 1,267
tokens. Every row with at least 5,000 tokens other than gibberish is negative;
the highest native individual CREMMA manuscript at that floor is BIS-193 at
`-0.043419`.

The 64 files are not 64 independent corpora: they include base/marks versions,
native/re-lined twins, pools, and their member manuscripts. They expand the
control coverage but should not be counted as independent replications.

## Review of the team interpretation

The following parts are supported:

1. `c-320` accurately records the Daybreak values and original 48 registered
   controls.
2. Daybreak supplies the strongest current evidence that the Voynich effect is
   inside lines, survives exact-repeat removal, and exceeds both fixed nulls.
3. Human gibberish was missing from the original Daybreak control set, so a
   like-for-like closer was required.
4. CREMMA and the s17 literary controls support the statement that the tested
   natural-language corpora do not reproduce this word-length pattern.
5. The signal is a useful constraint for any Phase 3 producer.

The following wording should change:

1. “Human gibberish gets most of the way there” compares s17's whole-stream
   `0.119` with Daybreak's within-line `0.155–0.157`. Under the matched
   statistic, native human gibberish is `0.098` and fails the line-preserving
   null at `p=0.753`.
2. “The signal is gibberish-like” is valid for the whole-stream N5 statistic
   and separately for CHARWIN. It is not supported for Daybreak's robust
   line-internal excess.
3. The two N5 signatures should not be bundled. CHARWIN remains strongly
   human-gibberish-like; the line-internal word-length constraint is presently
   unmatched by the tested human-gibberish pool.
4. “The line-initial profile is not prose layout” should be phrased as “it is
   not reproduced by the tested real-line medieval Latin prose controls.”
   Genre, scribal, and layout coverage is finite.
5. “The coupling is ordering, not position” should say it survives the tested
   coarse position-stratified null. Non-Voynich edge tables also regenerate it,
   so it is not currently family-diagnostic.
6. A verbose homophonic cipher and a disciplined human generator are a useful
   Phase 3 contrast, but they are not an exhaustive inference from these
   results. Either entrant must now reproduce the line-internal Moran excess;
   the s31 pre-test entrants do not.

## Recommended register correction

Keep `c-320` and add the present closer rather than rewriting its historical
record. Amend the interpretation attached to `L-111` along these lines:

> The real-line human-gibberish closer reproduces s17's whole-stream I=0.1194
> but gives native within-line I=0.0980. It fails the line-preserving shuffle
> (q99=0.1209, p=0.753), while Voynich gives I=0.1549–0.1572 and p=0.001.
> Cross-line boundaries contribute 31.2% of the gibberish numerator versus
> 1.5–3.2% for Voynich. Thus pooled human gibberish does not reproduce the
> robust line-internal constraint, although it remains a strong analogue for
> CHARWIN and the unablated whole-stream Moran statistic.

The next useful gibberish test is writer-level heterogeneity with a registered
minimum size, multiplicity rule, and writer-block bootstrap. The next mechanism
test should model line-specific length distributions and local length-state
transitions separately; a producer can match one without matching the other.

## Artifact identities

- `PREREG.md`: `16801a0a8a209b8586423c55eddb29cb86932dd1346270737d1e69cd339f6d50`
- `PREREG.sha256`: `c31c75b46bcf144bf4ee427cb61cf46ef20b3bb29b5ef6316f1a3fa140b323b1`
- `realline_closer.py`: `1c08c17d454facf70b4761dbf2071fa9d23a2d5404557233717cd5e595e46561`
- `inputs/manifest.jsonl`: `e0eb444ff54a3eb1373dccaf308f316593cfbe23d8d5dd20b636eed7dbb6f560`
- `result.json`: `c37a41770778022f935fd19ec0e5f4451bfe98d53f57603d08a8821f2d043d94`

