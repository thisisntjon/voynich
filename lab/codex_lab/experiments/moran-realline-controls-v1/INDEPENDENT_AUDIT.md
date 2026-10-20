# Independent audit: real-line Moran controls v1

**Verdict:** CLEAN for the registered question. I found no hash, input,
implementation, result, or decision discrepancy. The result is a post-hoc
closer with the prior-exposure limits stated in `PREREG.md`; it is not an
independent blind confirmation.

## Sealed identities

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `PREREG.md` | 4,721 | `16801a0a8a209b8586423c55eddb29cb86932dd1346270737d1e69cd339f6d50` |
| `realline_closer.py` | 10,606 | `1c08c17d454facf70b4761dbf2071fa9d23a2d5404557233717cd5e595e46561` |
| `inputs/manifest.jsonl` | 10,224 | `e0eb444ff54a3eb1373dccaf308f316593cfbe23d8d5dd20b636eed7dbb6f560` |
| `result.json` | 25,593 | `c37a41770778022f935fd19ec0e5f4451bfe98d53f57603d08a8821f2d043d94` |

`PREREG.sha256` contains the first three identities exactly. It necessarily
does not contain the later result; this audit records the result identity.
The external Daybreak reference was also rehashed as
`359b3819c8424005833af9942d6eccc98022969534144e9898d0c9692f42dc47`,
the value fixed in the preregistration and implementation.

## Input and result audit

I independently parsed all 73 manifest records. Every record has exactly the
keys `path`, `bytes`, and `sha256`; all paths are distinct, relative, and free
of parent traversal. All 73 files have the declared byte count and SHA-256.
None is a link or reparse point. The set is exactly 64 sidecars plus nine
provenance/source artifacts. The only file under `inputs/` not listed is the
manifest itself.

`result.json` is strict finite canonical JSON with one terminal LF. It has 64
distinct named rows, one for each manifest sidecar. Exactly these eight native
rows have null results: `gib_realline_pooled`, `mhg_nibelungenlied`,
`oldfrench_roland`, `occitan_croisade`, `italian_dante`, `cremma_prose15`,
`cremma_c15`, and `cremma_all`. Each has both registered nulls and 999 draws.
The stored implementation, manifest, Daybreak, seed, draw-count, threshold,
and validation identities agree with the sealed inputs.

## Independent recomputation

I used a separate read-only implementation passed on standard input to the
locked interpreter with `-I -B`; it did not import `realline_closer.py` and
wrote no file. Runtime: CPython 3.13.12 and NumPy 2.5.4. It independently
loaded the sidecars, applied the whole-line cap, rebuilt pairs and strata,
and recomputed the statistics. Every non-null scalar field in all 64 rows
matched `result.json` exactly.

The cap admits a whole line whenever the pre-line count is below 25,000 and
then stops. The only overshoots were the registered consequences of that
rule: `cremma_all` +2, `cremma_all_marks` +2, `italian_dante` +1,
`occitan_croisade` +6, and `oldfrench_roland` +4 tokens.

I also independently regenerated all 999 values for both nulls on the primary
human-gibberish row and the three primary CREMMA pools. Every stored median,
q99, one-sided p-value, and pass boolean matched exactly:

| Row | Within-line I | Whole-stream I | Line shuffle median / q99 / p / pass | Position null median / q99 / p / pass |
|---|---:|---:|---|---|
| `gib_realline_pooled` | 0.0979731068999136 | 0.1194298116843237 | 0.10297573544609888 / 0.12087064808417762 / 0.753 / false | 0.027703451061192243 / 0.054092036974178186 / 0.001 / true |
| `cremma_prose15` | -0.03309063289076259 | -0.041522685817133566 | 0.01061663828018736 / 0.03476449605970695 / 1.000 / false | 0.03743825015922268 / 0.06553782129552245 / 1.000 / false |
| `cremma_c15` | -0.019227203793172543 | -0.03155294165419543 | -0.003474551220987456 / 0.016698216271721977 / 0.956 / false | 0.028445632209150883 / 0.053726171394497695 / 1.000 / false |
| `cremma_all` | -0.018100298414473404 | -0.01694227782996462 | 0.03697268888425097 / 0.05139189193499171 / 1.000 / false | 0.052606199042914366 / 0.06636801226335629 / 1.000 / false |

## Formula, randomization, and decision checks

The implementation uses the registered directed-pair statistic

`I = (n / W) * sum(z[left] * z[right]) / sum(z * z)`,

with the global mean, `W` equal to the retained within-line pair count, and no
cross-line pair. Whole-stream I uses `W = n - 1`. The nonidentical analysis
removes exactly equal token strings and recomputes `W` for the retained pairs.

Each null in each row constructs a fresh
`Generator(PCG64(20261018))`. The line null permutes observed lengths within
each original line. The position null restores the observed vector on every
draw and permutes within the sorted `(position_bin, line_length_bin)` strata.
The stored p-value is exactly
`(1 + count(null >= observed)) / 1000`. Unlike the earlier Daybreak runner,
the pass predicate here explicitly requires both `observed > q99` and
`p <= 0.01`.

The human-gibberish decision is therefore reproduced: 0.0979731 is below the
prior registered-control maximum 0.1289615, and only the position null passes;
`passes_both_fixed_nulls` is correctly false. The maximum of the three native
CREMMA pools is `cremma_all` at -0.0181003, also below that threshold.

## Interpretation and non-blocking limitations

The pooled gibberish result closes the earlier whole-stream/within-line metric
mismatch. Its within-line value is lower than its known whole-stream value,
and it does not exceed the prior registered maximum. Its failure against the
within-line shuffle is scientifically important: the positive value is not
evidence of local word-order structure beyond what remains when each line's
length multiset is permuted. Passing the position-stratified null instead
shows sensitivity to line-level composition that that null does not preserve.

Two diagnostic names need care. `boundary_numerator_fraction` divides signed
quantities, so it can be negative or exceed one when the whole-stream
numerator is small or opposing contributions cancel. Likewise,
`nonidentical_retention` is a signed-statistic ratio and can exceed one. The
primary decisions do not use either diagnostic.

The 73-file snapshot does not copy the sibling Daybreak result into
`inputs/`; it verifies that dependency by its fixed SHA-256 instead. The
result also does not serialize the Python/NumPy versions. These are
reproducibility/provenance limitations rather than observed result errors: the
locked runtime above reproduced every checked value exactly.
