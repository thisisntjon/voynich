# MLC1: actual medieval line boundaries as a Voynich control

Protocol written before downloading/scoring the control XML. Exploratory follow-up to
the already-observed Voynich line anomaly; not a blind discovery or external registration.

## Question and prior art

Does the strong line-initial symbol distribution persist as an unusual feature when
compared with actual medieval Latin manuscript lines, preserving abbreviation signs?
The comparison is limited to this corpus, not all medieval writing or languages.

CREMMA-Medieval-LAT at Git commit `292525969ad98380b398e6606a9c2a36d51913ae`
provides 21 manuscripts. Fetch only original ALTO XML (exclude `.chocomufin.xml`),
README, data registry and htr-united metadata. Verify Git blob identities and save
SHA-256 hashes. No manuscript images are needed. Score each manuscript separately.
Keep MainZone / DefaultLine records only, and lines with at least three tokens.
All manuscripts with >=100 such lines are eligible; shorter ones are descriptive.
Dates and genres come from the registry; do not select them after scoring.

Prior art already includes CREMMA entropy measurement:
https://github.com/whitehatnetizen/voynich-investigation/blob/main/scripts/medieval_latin_h2.py
Its inspected script concatenates text to measure entropy, not ALTO line-position
effects. This experiment's candidate contribution is the original-line comparison
with two layout nulls and size-matched Voynich samples. No priority claim follows
from a search finding no identical study. Other reviewed sources:
https://doi.org/10.5334/johd.97
https://www.voynich.nu/transcr.html
https://ceur-ws.org/Vol-3313/paper12.pdf

## Frozen measurement choices

1. Primary normalization: lowercase NFD Unicode; retain letters, combining marks,
   private-use abbreviation characters and Tironian et (U+204A). Other characters
   delimit tokens. Group each base with following combining marks as one symbol.
   This is a specified base-plus-marks convention, not general Unicode grapheme
   segmentation. Never expand abbreviations or join words across lines.
2. Sensitivities: retain case; strip combining marks. Voynich ZL3b, RF1b and IT2a
   use their existing paragraph-text tokens and their EVA codepoint symbols.
3. Primary metric: base-2 Jensen-Shannon divergence (JSD) between first symbols
   of line-initial tokens and first symbols of interior tokens, pooled by manuscript.
   Secondary: final symbols of line-final tokens versus interior final symbols.
   Unlike EVA p/m enrichment, these statistics require no cross-script glyph mapping.
4. Null A: 999 independent within-line token permutations. Sampling the first and
   last distinct indices gives the exact edge/middle distribution of this null.
   Report observed minus null mean, null SD, and plus-one upper-tail p.
5. Null B: 199 within-page circular shifts of the entire token sequence, recut to
   the original line lengths. Preserves page vocabulary, token order except the
   wrap, and line-length sequence; randomizes alignment of text to line boundaries.
   Report observed minus null mean and plus-one upper-tail p. ALTO source order
   may not be actual multi-column reading order; this null is sensitivity only.
6. Sample-size check: for each eligible control, sample the same number of lines
   without replacement from each Voynich transliteration, 100 replicates. Each
   sample has 19 Null A draws. Report 2.5/50/97.5 percentiles of corrected JSD.
   These are sampling intervals, not manuscript-population confidence intervals;
   line lengths are NOT matched. They check gross finite-sample bias only.
7. Seed 20261017. No tuning. Case/mark sensitivities and final-symbol metrics are
   secondary. Apply Holm correction to Null A p-values across eligible Latin
   manuscripts separately for each metric; Voynich p-values are reported separately.

## Interpretation and gates

Reproduce ZL3b initial JSD 0.1759 within 0.0001 before interpretation. Unit tests
must cover punctuation/abbreviation tokenization, XML zone filtering, exclusion of
short lines, finite JSD, exact edge-permutation expectation on a toy example,
and sensitivity to a planted line marker. No family verdict or decipherment claim.

The target survives THIS comparison if all three Voynich samples have positive
Null A excess with p<=0.01 and every eligible Latin control's corrected initial
JSD falls below the 2.5th percentile of its size-matched Voynich samples in all
three transliterations. Otherwise report overlap / partial separation, naming
the controls. Even survival does not exclude other languages, genres, scripts,
hyphenation conventions, or alternative glyph models.

Save raw input provenance, eligible/excluded counts, all measured outputs,
protocol/code hashes, environment, and commands. Refuse to overwrite a result.
