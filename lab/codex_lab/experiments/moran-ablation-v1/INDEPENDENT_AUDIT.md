# Independent audit: Moran word-length ablation v1

**Audit date:** 2026-10-18 UTC  
**Audit mode:** read-only review, full snapshot rehash, exact replay, independent formula checks, and a no-write literal-seed sensitivity rerun  
**Scientific verdict:** **SUPPORTED WITH PROTOCOL DEVIATIONS.** The recorded values and the registered positive decision reproduce. The evidence supports the narrow statement that the positive lag-1 word-length autocorrelation is line-internal and robust to the two specified shuffles, page bootstrap, and identical-token-pair removal. It does not establish language, cipher, meaning, a key, or a generating mechanism.  
**Artifact verdict:** not fully clean: the implementation departs from the preregistration in two exact ways, and the result's provenance binding is incomplete. Neither departure changes the decision for this run.

## Exact identities verified

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `PREREG.md` | 3,156 | `e27fa209e282eae1465236cd4dfa862de4acf652175afcc463bda6bfe52e19b6` |
| `PREREG.sha256` | 160 | `e110440f64485fe761d07a298221116fe6c7a85a9ef0564477191e32e603f2be` |
| `moran_ablation.py` | 8,864 | `086cff8c993b5f157e6d5bdda7f932ed01a4e76d05fd96b7506957c9c7b38a41` |
| `result.json` | 9,225 | `359b3819c8424005833af9942d6eccc98022969534144e9898d0c9692f42dc47` |
| source snapshot `SNAPSHOT.json` | 99,942 | `fb7ff4abb33ce470ebb44b01b3a0a738d367e9834e8f5f9698bb16794fc8e3d9` |
| frozen `n5_signature_discrimination.py` | 14,394 | `9b9cd7ebb0e705d7bb9e31f60cba373a8a39ceca6c1bdced642e2142c806af8e` |
| frozen `scoreboard/metrics_new.py` | 38,109 | `a59c9c17f8abe4cc8e29347854b02304eaa6a13c90b32f1890c1b1a60e7b23ed` |

`PREREG.sha256` correctly binds the current `PREREG.md` and `moran_ablation.py`. The implementation hash recorded in `result.json` matches the current script, and the recorded snapshot-receipt hash matches the current receipt. I independently rehashed all 575 files listed in the snapshot receipt: 575 were present, with zero missing files and zero hash mismatches. The receipt records source-manifest SHA-256 `f1008e4c7add6e0539dfa2e6d82016d644c4389870796c8fcba70efab730f4ad`.

## Mathematical and computational checks

The implemented within-line statistic is

`I = (n / S0) * sum((x_i - mean(x)) * (x_j - mean(x))) / sum((x_i - mean(x))^2)`,

where `(i,j)` ranges over directed forward-adjacent token pairs inside a transcription line and `S0` is the number of those pairs. This agrees with the frozen `metrics_new` implementation. An independent implementation from the frozen pages reproduced the stored manuscript statistics.

The following details also check out:

- The whole-sequence version uses all adjacent positions and reproduces N5.
- Within-line shuffling independently permutes word lengths inside each line, preserving its multiset and length.
- Position-stratified shuffling pools by relative-position quintile and the four registered line-length bins, then independently permutes within each nonempty pool.
- The page bootstrap's sufficient-statistic reconstruction correctly recomputes the global mean, variance, adjacent-pair numerator, and `n/S0` factor after resampling pages.
- Removing identical adjacent token strings filters the intended pairs and recomputes `S0` consistently.
- The reported boundary numerator is the whole-sequence lag-product numerator minus the within-line numerator; its fraction is calculated against the whole-sequence numerator.

## Recorded and replayed results

An exact no-write replay under CPython 3.13.12 and NumPy 2.5.4 reproduced `result.json`, including every manuscript statistic, every `E`, `G`, `L`, and `X` control row, and the registered decision.

| Transcription | Whole-sequence I | Within-line I | Line-null q99 / p | Position-null q99 / p | Bootstrap q025 | Nonidentical retention | Boundary numerator fraction |
|---|---:|---:|---:|---:|---:|---:|---:|
| ZL3b | 0.140670039604 | 0.157243538737 | 0.080927322774 / 0.001 | 0.030580473273 / 0.001 | 0.141834317383 | 0.964794911170 | 0.014597152902 |
| RF1b | 0.140843670066 | 0.154867941124 | 0.081452010273 / 0.001 | 0.029931106330 / 0.001 | 0.139776649305 | 0.961362222640 | 0.031580113438 |
| IT2a | 0.141015522525 | 0.156594859651 | 0.081171860558 / 0.001 | 0.027531977709 / 0.001 | 0.140041180397 | 0.960040988291 | 0.022351970285 |
| ZL3b-25k diagnostic | 0.118674956599 | 0.135569151522 | 0.075833473266 / 0.001 | 0.031864251396 / 0.001 | 0.118513345452 | 0.954139615313 | 0.001362829083 |

For each manuscript and both nulls, zero of the 999 null draws reached the observed value, giving the minimum registered Monte Carlo p-value `(1 + 0) / 1000 = 0.001`.

The exact N5 control-family maxima are `E = 0.041132628588`, `G = 0.128961482589`, and `L = 0.042798996825`. Each full transcription exceeds the largest of these, the `G` maximum, by:

| Transcription | Margin above G maximum |
|---|---:|
| ZL3b | 0.028282056148 |
| RF1b | 0.025906458535 |
| IT2a | 0.027633377062 |

The preregistered diagnostic ZL3b-25k value also exceeds the `G` maximum by `0.006607668933`. The family-range comparison is descriptive under the preregistration and is not needed to pass the primary decision.

## Two preregistration/implementation deviations

1. **Random-seed schedule.** `PREREG.md` line 37 specifies NumPy PCG64 seed `20261018` “for each test.” The implementation instead initializes the line null at `SEED + seed_offset` (line 132), the position null at `SEED + 10_000 + seed_offset` (line 140), and the page bootstrap at `SEED + 20_000 + seed_offset` (line 148). This is a literal preregistration deviation, although it is a deterministic and transparent seed schedule.

2. **Decision predicate omits the explicit p-value check.** `PREREG.md` line 57 requires the observed statistic to exceed each null's 99th percentile **and** have `p <= .01`. The decision flags at implementation lines 208 and 210 test only observed `> q99`; they do not test the stored Monte Carlo p-value. For these data all six primary p-values are `0.001`, so adding the omitted check leaves the recorded decision unchanged. The implementation would not enforce the complete registered rule in a tied or borderline future case.

## Literal-seed rerun

To test the first deviation directly, I loaded the sealed module from its verified path, saved NumPy's original `default_rng`, and temporarily replaced the module's generator factory with a wrapper returning a fresh `Generator(PCG64(20261018))` for every call. I then invoked `analyze_pages` over the exact frozen N5 manuscript iterator. This causes the line null, position null, and page bootstrap for every row to start separately from the literal registered seed. The run used CPython 3.13.12 and NumPy 2.5.4, wrote no output file, and created no rerun artifact.

| Row | Line-null median / q99 / p | Position-null median / q99 / p | Bootstrap median / q025 / q975 |
|---|---:|---:|---:|
| ZL3b | 0.069368011074 / 0.080927322774 / 0.001 | 0.017023709124 / 0.028921908743 / 0.001 | 0.157321810378 / 0.142176273492 / 0.171457831596 |
| RF1b | 0.070541225365 / 0.081946180094 / 0.001 | 0.018618374157 / 0.031655798679 / 0.001 | 0.155191280246 / 0.140497707828 / 0.167993977427 |
| IT2a | 0.070777730138 / 0.082223576728 / 0.001 | 0.015687586223 / 0.027292198919 / 0.001 | 0.156112874749 / 0.139897816570 / 0.171680409928 |
| ZL3b-25k diagnostic | 0.062317533263 / 0.076039694639 / 0.001 | 0.016939112014 / 0.031774649627 / 0.001 | 0.135716723331 / 0.120563722109 / 0.151103330317 |

All three primary transcriptions still pass both nulls at `p = 0.001`, retain a bootstrap lower limit above zero, and retain more than 96% of the within-line statistic after identical pairs are removed. The diagnostic also remains positive and separated from both nulls. The seed-schedule deviation therefore does not explain or reverse the result.

## Provenance and design limitations

- `result.json` binds the implementation and snapshot-receipt hashes, but it does not bind the preregistration hash, `PREREG.sha256`, the N5 script hash, `metrics_new.py`, the Python version, or the NumPy version. This audit supplies those current identities but cannot retroactively make them part of the result's signed dependency graph.
- The experiment script hashes `SNAPSHOT.json` but does not validate its 575 file entries before importing and reading snapshot dependencies. The current closure passed this audit's independent rehash; the script itself does not enforce that condition.
- Local NTFS times are consistent with sealing before result generation: `PREREG.md` was last written at `2026-10-18T03:20:55.0008701Z`, the hash file at `2026-10-18T03:21:17.7501575Z`, and `result.json` at `2026-10-18T03:23:56.3467669Z`. There is no repository commit or external immutable timestamp anchoring that chronology, so it remains locally attested.
- The design defines 20 possible position-by-line-length strata, but only 19 are nonempty in these inputs: lines of length 1–4 cannot populate the fifth relative-position quintile under the stated integer binning. Empty strata are naturally absent and this has no numerical effect, but “20 fixed strata” is conceptual rather than 20 operational shuffle pools.

The warranted interpretation is a stable local ordering constraint in word lengths, internal to transcription lines and not reproduced by the exact tested control families. The experiment narrows the mechanism search; it does not identify the source of the constraint.
