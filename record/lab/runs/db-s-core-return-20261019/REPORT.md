# Cross-line core repetition under an edge-preserving comparison

Status: independently audited bounded result; canonical acceptance and scholarly novelty unresolved. No decipherment or semantic claim.

On the exact three 22,500-token inputs used by s87 amendment1, the reported deficit in identical-core repetition across line returns is not detected when complete lines are reordered within their original pages. The old token-shuffle comparison changes which tokens occupy line beginnings and endings; the new comparison preserves each line intact.

| Transcription | Actual repeated cores | Page-token shuffle mean | Whole-line shuffle mean | Whole-line lower-tail p |
|---|---:|---:|---:|---:|
| ZL3b |64|113.145|60.422|.729|
| RF1b |75|111.905|63.582|.966|
| IT2a |75|115.306|65.666|.911|

This shows that the original page-token deficit does not establish avoidance beyond the line-edge composition preserved by whole-line reordering. It does not establish equivalence, exclude every avoidance mechanism, or prove that line-start vocabulary alone causes the difference. Whole-line reordering preserves more than edge vocabulary. Within-line repetition is invariant under the new null and is not refuted.

The protocol, synthetic checks and inputs were frozen before scoring. One thousand permutations per null, one CPU, no acquisition. The independent audit reconstructs segmentation and counts separately and verifies all nine input/code hashes; it does not independently regenerate the Monte Carlo draws. See [PREREG.md](PREREG.md), [results.json](results.json), and [AUDIT.md](AUDIT.md).

The original inputs are reused research data, not an untouched discovery set. Three transcriptions represent one manuscript, not three independent samples. Learned cores remain operational units. The tested truncations end at f96r/f99r and do not constitute a whole-manuscript confirmation.

Prior art: [Jad Deeb's within-line repetition analysis](https://jad-deeb.github.io/voynich-findings/Voynich_Decoding_Attempt_3.html) already uses position-aware shuffles. The [antenore toolkit's cross-boundary test](https://raw.githubusercontent.com/antenore/voynich-toolkit/main/src/voynich_toolkit/currier_line_test.py) instead shuffles words throughout each folio, so it does not provide this edge-preserving comparison. Neither external result was independently reproduced here. First-ever status is not established.

Research implication: retain within-line reuse as a constraint; do not require an additional cross-line avoidance process solely to satisfy the old page-shuffle statistic. No automatic reversal of generator verdicts is justified because those involve other criteria.
