# Moran word-length ablation v1: checked result

## Verdict

This experiment supports one narrow positive finding: the Voynich transcription
has a stable, positive, line-internal lag-1 association in token length that is
not explained by line/page concatenation, exact adjacent token repetition, the
two fixed formatting-preserving nulls, or any registered N5 encoded,
meaningless-producer, or natural-language control.

The finding is a constraint on viable explanations. It is not a reading,
language identification, cipher identification, or key.

The implementation contains two disclosed departures from the literal
preregistration. An independent audit reran the affected tests with the literal
seed and the registered conclusion still passed. The result is therefore
reported as **supported with disclosed implementation deviations**, rather
than as a perfectly executed preregistration.

## What was newly done

The preceding N5 experiment reported whole-sequence word-length Moran's I near
`0.141`. This v1 experiment was designed to test whether that observation was a
concatenation artifact or a trivial repetition/formatting effect.

Before the first computation, the question, inputs, metrics, two null models,
bootstrap, seed, draw count, and conjunction rule were written to `PREREG.md`.
The preregistration and implementation were then bound in `PREREG.sha256`.
The run used a frozen 575-file source snapshot. A deterministic replay produced
the same `result.json` byte for byte. A separate agent then independently
rehash-checked all 575 snapshot entries, recomputed all manuscript and control
statistics without writing into the experiment, inspected the statistic and
bootstrap algebra, and reran the affected tests using the literal preregistered
seed.

## Registered result

| Transcription | Within-line I | Line-shuffle q99 | Position-null q99 | Monte Carlo p, each null | Page-bootstrap 95% lower | Value retained after exact repeats removed | Cross-line share of positive numerator |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b | 0.157244 | 0.080927 | 0.030580 | 0.001 | 0.141834 | 96.48% | 1.46% |
| RF1b | 0.154868 | 0.081452 | 0.029931 | 0.001 | 0.139777 | 96.14% | 3.16% |
| IT2a | 0.156595 | 0.081172 | 0.027532 | 0.001 | 0.140041 | 96.00% | 2.24% |

None of the 999 draws in either null reached the observed value for any full
transcription. All four preregistered conditions passed for all three full
transcriptions. The 25,007-token ZL3b size diagnostic also passed, with
within-line I `0.135569`.

The full-transcription values exceed the nearest registered N5 control,
`schwartz_reuse` at `0.128961`, by `0.025906` to `0.028282`. The registered
control maxima were:

| Family | Runs scored | Maximum within-line I |
|---|---:|---:|
| Encoded producers (E) | 17 | 0.041133 |
| Meaningless producers (G) | 10 | 0.128961 |
| Natural-language controls (L) | 21 | 0.042799 |

That comparison is finite: it rejects the tested producers, not every possible
generator. Ten context-only rows were also recomputed, but they do not enter the
registered-family verdict.

## What the ablations establish

The effect is mainly within transcription lines. Only 1.46% to 3.16% of the
whole-sequence positive lag-product numerator comes from cross-line boundaries.
It is not carried by exact adjacent repeats: removing those pairs retains about
96% of the statistic. It is much larger than null distributions that preserve
each line's length multiset or preserve coarse relative-position and line-length
strata. Whole-page resampling keeps the lower 95% limit well above zero.

The evidence therefore points to a local token-length ordering rule or process
that the present control models do not reproduce. Candidate causes still
include linguistic dependencies, copying/editing habits, cipher mechanics,
layout-conditioned generation, transcription conventions, or a mixture.

## Audit findings and limits

1. `moran_ablation.py` used deterministic dataset/test seed offsets, although
   `PREREG.md` specified PCG64 seed `20261018` for each test. The independent
   literal-seed rerun left both null p-values at `0.001` for all three full
   transcriptions. Its page-bootstrap lower limits were `0.142176` (ZL3b),
   `0.140498` (RF1b), and `0.139898` (IT2a), so the conclusion is unchanged.
2. The stored decision checks observed values against each q99 but does not
   separately enforce the preregistered `p <= .01` condition. The recorded
   p-values are all `0.001`, so this omission cannot change this result.
3. `result.json` binds the implementation and snapshot-receipt hashes but does
   not bind the preregistration, N5 implementation, interpreter, or dependency
   closure. The independent audit supplied those checks for the present files.
4. The snapshot receipt was not validated by the experiment code before use.
   The independent audit rehashed all 575 files and found zero missing, size,
   or hash mismatches.
5. The local freeze chronology is self-attested by file times and hashes; it has
   no external immutable timestamp or repository commit.
6. Nineteen of the 20 conceptual position/line-length cells are nonempty in the
   data. Calling the operational null “20 fixed strata” is slightly imprecise.
7. ZL3b, RF1b, and IT2a encode the same manuscript. Agreement among them shows
   transcription robustness, not three independent manuscript replications.
8. Page, quire, section, scribal, and layout clustering remain possible sources
   of heterogeneity. The current tests do not identify a mechanism.
9. Token length depends on transcription alphabet and tokenization. Pixel-level
   checks and alternative unit systems are needed before treating the magnitude
   as a property of the physical writing itself.

No v1 source or result file was silently corrected after seeing the outcome.
The deviations remain visible and should be fixed in a separately frozen
successor experiment.

## Why this merits continuation

The result is large enough to survive two stringent fixed nulls, page
resampling, removal of exact repeats, three transcription systems, a 25k-token
size check, deterministic replay, and independent recomputation. It is also
discriminating: every registered control family falls below it. This gives the
investigation a concrete target rather than a general impression that the text
is unusual.

The next decisive experiment should localize the mechanism. It should freeze a
hierarchical spatial-block analysis that matches or conditions on folio, quire,
section, layout, line length, relative position, and transcription system; map
the association by token distance; test leave-one-block-out prediction; and
compare against stronger manuscript-like and historically matched controls.
The separate pixel-registration pilot should test whether the effect persists
under glyph measurements derived from scans rather than transcription token
lengths.

## Bound artifacts

- `PREREG.md`: `e27fa209e282eae1465236cd4dfa862de4acf652175afcc463bda6bfe52e19b6`
- `PREREG.sha256`: `e110440f64485fe761d07a298221116fe6c7a85a9ef0564477191e32e603f2be`
- `moran_ablation.py`: `086cff8c993b5f157e6d5bdda7f932ed01a4e76d05fd96b7506957c9c7b38a41`
- `result.json`: `359b3819c8424005833af9942d6eccc98022969534144e9898d0c9692f42dc47`
- frozen snapshot receipt: `fb7ff4abb33ce470ebb44b01b3a0a738d367e9834e8f5f9698bb16794fc8e3d9`
- N5 implementation: `9b9cd7ebb0e705d7bb9e31f60cba373a8a39ceca6c1bdced642e2142c806af8e`

