# Addendum: exact edge-pair null is highly constrained

Date: 2026-10-18 UTC  
Applies to: `codex_lab/experiments/moran-slot-crossfit-v1`  
Sealed registered result SHA-256: `f389aecae40e57a715b3777f34981a7c8d16bb08d7dd320cd365a1efb68c3999`

## Correction

The registered numeric result is reproducible, but the `exact_pair_retention` percentage must not be read as the share of word-length ordering explained by the operational prefix/suffix sequence.

That null shuffles word lengths only among tokens that share the same exact `(prefix,suffix)` pair **inside the same line**. Most such cells contain one token, so most positions cannot move. A token is *effectively mutable* here only when its cell contains at least two tokens with at least two different word lengths.

### Learned, quire-cross-fitted segmenter (`ALL`)

| View | Singleton cells | Tokens locked in singleton cells | Effectively mutable tokens | Adjacencies with neither endpoint effectively mutable | Reported pair retention |
|---|---:|---:|---:|---:|---:|
| ZL3b | 88.57% | 77.73% | 12.97% | 76.79% | 90.29% |
| RF1b | 88.96% | 78.38% | 12.79% | 77.13% | 90.20% |
| IT2a | 89.24% | 78.92% | 12.37% | 77.88% | 91.08% |

### Training-free fixed comparator (`ALL`)

| View | Singleton cells | Tokens locked in singleton cells | Effectively mutable tokens | Adjacencies with neither endpoint effectively mutable | Reported pair retention |
|---|---:|---:|---:|---:|---:|
| ZL3b | 89.70% | 80.02% | 9.79% | 81.91% | 94.76% |
| RF1b | 90.00% | 80.61% | 9.57% | 82.35% | 94.97% |
| IT2a | 90.18% | 80.91% | 9.58% | 82.24% | 93.53% |

The fixed rule's even higher retention, despite failing the core-collapse gate, confirms that a high value is partly a mechanical consequence of low permutation freedom. The pair-preserving component is therefore under-informative. It establishes neither 90% explanatory power nor a causal edge mechanism.

## What remains intact

The core-length ablation uses a different line-shuffle null and does not depend on exact-pair cell mobility. Its cross-fitted result remains strong:

| View | Core Moran excess retained | Core covariance excess retained | Core line-null p |
|---|---:|---:|---:|
| ZL3b | 4.72% | 3.55% | 0.202 |
| RF1b | 3.37% | 2.66% | 0.293 |
| IT2a | 4.13% | 3.43% | 0.240 |

An independent auditor refitted the fold models and reproduced all 45 randomization blocks, with maximum absolute numeric difference `2.49e-14`. The formal preregistered verdict remains **STRONG REPLICATION** because its frozen gates were met. The scientifically defensible wording is narrower:

> The learned operational segmentation's core-collapse survives quire-level cross-fitting and the covariance check. The exact-pair shuffle cannot quantify how much of the ordering is explained by edge-label sequence because most of its cells cannot change the length arrangement.

The training-free comparator remains non-corroborating for the strongest core-collapse claim, retaining 48.8%–54.1% of Moran excess in its cores. Cross-fitting removes held-out page and quire leakage; it does not make the algorithm or its hyperparameters independent of manuscript-specific development, and it does not turn operational segments into linguistic morphology.
