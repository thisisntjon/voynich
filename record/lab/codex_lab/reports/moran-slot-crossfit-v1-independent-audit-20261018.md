# Independent audit: `moran-slot-crossfit-v1`

Date: 2026-10-18 UTC  
Auditor: independent Codex worker `/root/affix_crossfit_audit`  
Target: `codex_lab/experiments/moran-slot-crossfit-v1`  

## Verdict

**COMPUTATIONALLY CLEAN; the formal preregistered verdict `STRONG REPLICATION` is warranted. An interpretive correction is required for the exact-pair-retention statistic and has been supplied in a separate frozen addendum.**

The core result survives the intended out-of-quire test. I independently refitted all 15 fold-specific segmenters, reconstructed every held-out token segmentation, and recomputed all stored observed statistics and all 45 registered 999-draw null blocks without importing the target analysis or its bundled audit helper. The largest absolute discrepancy from `result.json` was `2.4869e-14`. All overall and Currier A/B gates recompute as passed.

The strongest evidential result is the learned-core ablation, including its covariance companion: the held-out operational cores retain only 3.37%–4.72% of the Moran excess and 2.66%–3.55% of the unnormalized adjacent-covariance excess. This is a strong out-of-quire localization result for the specified, manuscript-derived segmenter family.

The reported 90%–95% exact-pair retention must not be interpreted as the fraction of ordering explained by edge labels. Its within-line `(prefix,suffix)` cells are highly constrained and mostly singleton. That makes much of the shuffled vector immovable. This issue weakens the pair-retention component of the registered gate but does not affect the separately calculated core-length or covariance ablations.

## Frozen target and chronology

The following target hashes match the builder's sealed artifacts:

| Artifact | SHA-256 |
|---|---|
| `PREREG.md` | `921763da144d76b12dfbc2e5443b2ee269aeefa351282d0566b694199b5d0b5b` |
| `crossfit_moran.py` | `3895a354c67b511d3792e64f15ce3776aff2ab60f9f13f1a664b774f6f79e2af` |
| `result.json` | `f389aecae40e57a715b3777f34981a7c8d16bb08d7dd320cd365a1efb68c3999` |
| `replay-result.json` | `f389aecae40e57a715b3777f34981a7c8d16bb08d7dd320cd365a1efb68c3999` |
| `segmenter-models.json` | `fd431b072237b85a2bf3dc5b4366312a4c4919e028045c4036f04f28309707cb` |
| `replay-segmenter-models.json` | `fd431b072237b85a2bf3dc5b4366312a4c4919e028045c4036f04f28309707cb` |
| `REPORT.md` | `22bf10db940d0556ba0bb73341ce72169fcf860579182a063c56855b8500aeeb` |
| `RESULT.md` | `4eca013876ab6f81a4522e9cd9b42b257821416004e7fe8f44ff71f4437bc313` |
| `MANIFEST.sha256` | `44e9c787699a3fa376e6f96341be83d6953c3e3ec6048f4fe17e693912167abe` |

All eight entries in `INPUT_MANIFEST.json`, including `FOLDS.json`, match both their byte counts and hashes. Every entry in the final `MANIFEST.sha256` also verifies.

Local NTFS metadata records this order: `FOLDS.json` 05:13:07 UTC, `INPUT_MANIFEST.json` 05:13:14, `PREREG.md` 05:13:58, prereg hash stub 05:14:03, analysis code 05:16:17–05:16:57, result 05:17:34, replay 05:18:28, report 05:20:53, and final manifest 05:21:04. The analysis hard-codes and checks the preregistration hash. These facts support that the preregistration preceded target code and result generation.

One provenance limit remains: the preregistration names `INPUT_MANIFEST.json` but does not embed that manifest's hash in its own pre-run hash stub. The current files are internally consistent and their recorded times have the right order, but the input-manifest freeze is not backed by an external or cryptographic timestamp. This is not a detected mismatch and does not change the numerical verdict.

## Leakage and fold checks

I implemented the segmenter directly from the registered rule and did not import `crossfit_moran.py`, `reference/metrics_new.py`, or `independent_audit.py`.

For each of three transcription views and each of five folds:

- the independently reconstructed train and test quire sets were disjoint;
- train/test page counts, token counts, sorted page-ID hashes, and quire lists matched the frozen model records;
- the learned prefix and suffix inventories matched exactly;
- the canonical candidate-list hashes matched exactly;
- all observed pages appeared in exactly one test fold;
- every evaluated segmentation satisfied `word = prefix + core + suffix` with a nonempty core.

The implementation fits each model only from pages whose quire is outside that fold, then applies the model to the held-out quire group. I found no path by which held-out word counts, entropy values, vocabulary, target statistics, or null results influence the fitted inventory. The five-fold mapping is identical across views and covers every input page.

This excludes same-page, recto/verso, and same-quire fitting leakage. It does not make the segmenter family external to the manuscript: its algorithm and hyperparameters came from prior project work on Voynich data.

## Independent numerical reproduction

The independent checker uses a plain-loop observed-statistic calculation. For the nulls, it uses the registered SHA-256-derived seeds and PCG generator, but a different 17-draw batch size, stable sorting, and 1.5-spaced cell bands. The target uses 32-draw batches, quicksort, and 2.0-spaced bands. The two implementations produced every stored mean, median, standard deviation, 99th percentile, and one-sided p-value to a maximum absolute difference of `2.4869e-14`.

This covers:

- word, core, and affix line-null blocks for `ALL`, Currier A, and Currier B in all three views;
- the exact-pair-preserving word null for all nine learned rows;
- core and affix line nulls plus exact-pair nulls for all three fixed-comparator rows.

The seed formula, 999 draws, `(1 + count) / 1000` p-value, NumPy linear quantile, pooled global mean, and within-line-only adjacency definitions all match the preregistration. A second execution of the independent checker reproduced its output byte-for-byte.

### Primary `ALL` values

| View | Word Moran I / line-null median / p | Core Moran I / line-null median / p | Core excess retained: Moran / covariance | Exact-pair retention |
|---|---:|---:|---:|---:|
| ZL3b | 0.157244 / 0.070070 / .001 | 0.039524 / 0.035405 / .202 | 4.72% / 3.55% | 90.29% |
| RF1b | 0.154868 / 0.070409 / .001 | 0.044355 / 0.041509 / .293 | 3.37% / 2.66% | 90.20% |
| IT2a | 0.156595 / 0.071033 / .001 | 0.045671 / 0.042134 / .240 | 4.13% / 3.43% | 91.08% |

The covariance result is decisive for the normalization check. It operates in squared-character units and does not divide by the changed core-length variance, yet it shows the same collapse. The core result is therefore not an artifact of Moran's variance denominator.

### Currier scope gates

| View | Stratum | Core retained: Moran / covariance | Exact-pair retention | Scope gate |
|---|---|---:|---:|---:|
| ZL3b | A | 15.79% / 12.41% | 82.15% | pass |
| ZL3b | B | 1.83% / 1.36% | 92.96% | pass |
| RF1b | A | 15.56% / 12.92% | 84.20% | pass |
| RF1b | B | -0.72% / -0.56% | 92.04% | pass |
| IT2a | A | 4.21% / 3.64% | 83.32% | pass |
| IT2a | B | 3.71% / 3.04% | 93.62% | pass |

All six preregistered scope rows pass. Negative RF1b-B preservation means the core excess is slightly below its shuffled median; it is not negative mutual information and should not be interpreted as evidence that cores lack content.

## Exact-pair null degeneracy

The exact-pair null permutes word lengths only among tokens on the same line with the same exact operational `(prefix,suffix)` label. Independent reconstruction shows that most such cells contain one token and therefore cannot move.

| Scheme/view (`ALL`) | Singleton cells | Tokens locked in singleton cells | Tokens in cells containing multiple word lengths | Adjacencies with neither endpoint effectively mutable |
|---|---:|---:|---:|---:|
| Learned ZL3b | 88.57% | 77.73% | 12.97% | 76.79% |
| Learned RF1b | 88.96% | 78.38% | 12.79% | 77.13% |
| Learned IT2a | 89.24% | 78.92% | 12.37% | 77.88% |
| Fixed ZL3b | 89.70% | 80.02% | 9.79% | 81.91% |
| Fixed RF1b | 90.00% | 80.61% | 9.57% | 82.35% |
| Fixed IT2a | 90.18% | 80.91% | 9.58% | 82.24% |

For the learned rows, 61.25%–63.09% of adjacent pairs have both endpoints in singleton cells. Even more pairs have no endpoint in a cell containing multiple observed word lengths. High retention is consequently expected from the null's low mobility, regardless of how much causal or generative information the labels carry.

The Moran and covariance exact-pair-retention ratios are also algebraically identical for a fixed word-length vector: Moran is a constant rescaling of the same adjacent dot product. Their two registered thresholds are duplicate checks, not independent confirmations.

The formal pair-retention gates pass exactly as preregistered, so this does not alter the rule-based verdict. It does alter the scientific reading. The safe statement is: **under a highly constrained exact-label-within-line shuffle, the statistic retains 90%–95% of the word-length excess.** It is not safe to call that number the proportion of ordering explained, reproduced, or localized by edge labels without a less degenerate comparator. The separate correction addendum records this boundary at SHA-256 `989dc9c6e273f2fc646cc21520592ac370788599ff45db00378eb304b5cec3fc`.

## Fixed-rule comparator

The fixed comparator is correctly classified as **non-corroborating** under the preregistration:

| View | Fixed core retained: Moran / covariance | Exact-pair retention | Failed condition |
|---|---:|---:|---|
| ZL3b | 48.82% / 28.25% | 94.76% | Moran core > 25% |
| RF1b | 50.69% / 30.90% | 94.97% | Moran core > 25% |
| IT2a | 54.08% / 34.38% | 93.53% | Moran core > 25% |

The fixed rule's even higher pair retention, despite failing the core-collapse gate, reinforces that pair retention is not the discriminating evidence. The strong core collapse belongs to the manuscript-trained entropy/frequency representation and does not generalize to this frozen conventional edge list.

## Registered decision

Independent gate arithmetic gives:

- three of three learned `ALL` overall passes;
- six of six Currier A/B scope-direction passes;
- core preservation at or below 10% for both Moran and covariance in all three `ALL` rows;
- fixed comparator: zero of three overall-like passes.

Therefore `STRONG REPLICATION` is the correct formal registered verdict. In scientific prose it should be qualified as **strong cross-fitted replication of the learned operational core-collapse**, not as independent validation of morphology, a causal mechanism, or the 90% edge-label explanatory claim.

## Claim-to-evidence map

- **Completed:** frozen input/final manifest verification; exact replay hashes; all 15 fold-model refits; quire/page leakage checks; candidate-list hashes; all learned and fixed observed statistics; all 45 null blocks; registered gates; pair-null degeneracy diagnostic.
- **Supported:** same-page and same-quire fitting do not explain the learned core collapse; the result survives a covariance measure that removes Moran denominator concerns; the localization spans the registered A and B strata.
- **Failed comparator:** the fixed training-free rule fails the normalized core-collapse gate in every view.
- **Correction supplied:** `moran-slot-crossfit-v1-pair-null-addendum-20261018.md` describes pair retention as the outcome of a highly constrained null, rather than as a percentage of ordering explained by edge labels.
- **Not established:** linguistic morphology, historical production method, semantic content, plaintext, or decipherment.

## Independent audit artifacts

| Artifact | SHA-256 |
|---|---|
| `codex_lab/reproductions/moran_slot_crossfit_independent_recheck.py` | `ed2c75a08bf84195139f46b90c795065dd98e1ee02815735c72f1ffa5c0f9426` |
| `codex_lab/reproductions/moran_slot_crossfit_independent_recheck.json` | `54d7b274fc39dab2681c7f475261d60e4bf52be98960588b2a49a4b0bfbeec99` |
| `codex_lab/reports/moran-slot-crossfit-v1-pair-null-addendum-20261018.md` | `989dc9c6e273f2fc646cc21520592ac370788599ff45db00378eb304b5cec3fc` |

