# C — Constraints, pitfalls and power

Stamped 2026-10-17 19:26 PDT (clock read with `date`). Angle C of the top-10-leads investigation
(workflow/PLAN.md). Read-only outside this file and `workflow/research/C-helpers/`. Question:
what makes a lead unexecutable or its result uninterpretable here, and how much power do the
project's tests actually have?

Sources opened: `.inventory/registers/{METHODS,TOOLS,REDTEAM,OPEN}.md`, `results_{i1,c1,m1_coordinates,
m6_labels,a3,d6,m4_phase1_board,m7_board_translit,n2,n3,p1}.txt`, `m4_run2.log`, and the scripts
`c1_quire_null.py`, `m1_coordinates.py`, `m6_labels.py`, `scoreboard/score.py`, `corpora.py`, `vparse.py`,
`b5_nmf_topics.py`. Four helper scripts were written and run (each < 40 s, `python -I`):

| Helper (`workflow/research/C-helpers/`) | What it does | Imports project code unchanged? |
|---|---|---|
| `pw_c1_quire.py` | power curve for c1 test A (quire-block exact null) by injection | yes: `c1.chunks`, `c1.block_test`, `b5.topics`, `b4.pages`, `c2.WITHIN` |
| `pw_m1_column.py` | power curve for m1 column-specific excess by injection, plus far-line seed sensitivity on the real data | yes: `m1.build_pages/collect/boot/rates/nearest/ok_word` (real boxes) |
| `pw_m6_labels.py` | power curve for m6 §4 shared-2-char-prefix list test | **no** (m6 is module-level code; statistic and shuffle test re-implemented, same definitions, 200 shuffles, p=(k+1)/201) |
| `floors_v1_bands.py` | page-cluster bootstrap of the seven v1 bands at token budgets 2k..35k, Currier A only, 41-page subsets | yes: `score.py:profile_metrics/line_metrics/edge_metrics` (edge null nrep 5 instead of 20 per draw) |

Numbers below are from those runs (40 bootstrap draws or 10 injection seeds per cell unless stated). They were
not written to any `results_*.txt`. What would refute each is named in the row; "unverified" marks what was not run.

## 1. Power table (injection curves for the three negatives read as "favours meaningless")

| Test | Effect injected (definition) | Smallest effect detected (power >= 0.8 at p < 0.05) | Where the manuscript sits | Reading |
|---|---|---|---|---|
| **c1 test A, hand 1** (11 blocks HHHHHHHHPHP, 55 assignments, floor p = 0.018) | s = share of tokens of a token-shuffled Voynich replaced by a draw from the real (hand, section) unigram bag; s = 1 is the bag-level section vocabulary | **s = 0.35** (0.8), s = 0.40 (0.9), s = 0.45 (1.0). NMI at s = 0.35 is only 0.04; NMI is near zero up to s = 0.3 (NMF hard-assignment threshold) | MS NMI 0.275 ~ s 0.50–0.55 (NMI 0.22–0.30), well inside the detected zone | hand 1 "survives" with power ~1 **but only reaches the floor**: the test cannot distinguish NMI 0.18 from 0.52 (both p = 0.018). It is a yes/no at a 2-vs-9 block split, not a measurement. |
| **c1 test A, hand 2** (7 blocks HHHHBTT, 105 assignments, floor 0.0095) | same | **s = 0.60** (0.8), s = 0.70 (0.9); at s = 0.50 (NMI 0.20) power 0.6; at s = 0.45 power 0.5 | MS NMI 0.333 ~ s 0.60–0.65 (injection NMI 0.27 at 0.60, 0.39 at 0.70) | **hand 2's p = 0.133 is a coin flip, not a negative.** At the manuscript's own effect size the test misses 20–40 % of the time; c1 "MG weakly" for hand 2 is a power failure of the F4 kind (REDTEAM #21). |
| **m1 column-specific excess** (22,046 same-column pairs; page-cluster bootstrap, P(diff <= 0) < 0.05) | r = per-token probability that a token on line n is an exact copy of its nearest line n-1 token within 0.5 W, on top of m1 null 1 (within-line shuffle, boxes fixed) | **r = 0.005** gives power 0.7 (+0.51 pp); **r = 0.010** power 1.0 (+1.00 pp). Threshold ~ r = 0.006–0.007 | filed excess +0.41 pp ~ r = 0.004, i.e. **below the detection threshold** | The filed "P = 0.068" is at the edge of what the design can see. Worse: see §5 pitfall 1 — the P-value is a function of the far-line random draw (0.003–0.093 across 10 seeds, 7/10 < 0.05). |
| **m6 list order, ALL label pages** (1,107 adjacent pairs) | r = probability that the second label of an adjacent pair takes the first's 2-char prefix, applied to a within-page-shuffled order | **r = 0.05** (excess +0.041, power 1.0); r = 0.02–0.03 unverified (not on the grid) | observed excess +0.013 (p 0.050 filed / 0.075 here with a different shuffle seed) ~ r = 0.015 | a 1.5 % prefix-sharing habit is below power at 1,107 pairs; the ALL p = 0.015 (ned) / 0.050 (pre2) are what a marginal effect at the edge of power looks like, not "no list order". |
| m6 list order, ZODIAC (332 pairs) | same | r = 0.05 (1.0) | obs 0.157 vs null 0.164 (negative) | readable: a 5 % effect would show; none does. |
| m6 list order, PHARMA Lf (190 pairs) | same | r = 0.10 (0.9); r = 0.05 power 0.7 | obs +0.018 excess, p 0.21 | marginal power. |
| m6 list order, STARS Ls (64 pairs) | same | r = 0.15 (1.0); r = 0.10 power 0.6 | obs -0.008 | only a 15 % effect is readable; "no list order in the star labels" means "no effect >= 15 %". |
| m6 list order, PHARMA Lc (24 pairs) | same | **not detectable**: r = 0.50 gives power 0.6 | obs +0.05, p 0.20 | the jar-label list test has no power at any plausible effect size. |

Refuters: c1 — a different injection (disjoint synthetic marker vocabulary per section) would detect smaller s
because it is a stronger per-token signal; the bag injection is the one that interpolates to the manuscript's own
bag-level statistic, so it is the fair one. m1 — the injected copies are exact; an edit-1 "copy" injection would
need a larger r for the same edit<=1 excess. m6 — a prefix-copy is one list structure; alphabetical order would
show on `first` not `pre2` (both tested by m6; only pre2 curved here).

Other filed negatives not curved (unverified power): a3/d6 own-page label hit (p = 0.09–0.11, 40 pages, 778
tokens; d6's SENSITIVITY row on 55 pages already gives p = 0.020, so the 40-page negative is a sample-size
negative), c1 test B within-quire (12 and 20 pages), c1 test C centroid (same floor as A).

## 2. Sample-size floors for the seven v1 bands (page-cluster bootstrap of Voynich)

Readable = 95 % interval narrower than the band (two-sided bands) or interval excludes the floor (one-sided).

| Band (pass) | n = 2k | 5k | 8.6k | 11.2k (A size) | 17k | 25k | 35k | 41 pages (6.8k tok, no replacement) | Currier A only (114 p, 11.2k) |
|---|---|---|---|---|---|---|---|---|---|
| h2 [1.98, 2.28] | 2.00–2.20 (w 0.20) | 2.05–2.14 | 2.04–2.14 | 2.06–2.14 | 2.08–2.13 | 2.08–2.14 | 2.08–2.13 | 2.07–2.16 (w 0.10) | 2.12–2.16 |
| sd_len [1.41, 2.11] | w 0.17 | 0.11 | 0.08 | 0.08 | 0.06 | 0.04 | 0.05 | 1.75–1.83 | 1.77–1.80 |
| redup % [0.4, 1.8] | 0.55–1.10 | 0.68–1.08 | 0.63–1.08 | 0.68–1.04 | 0.68–1.00 | 0.70–0.98 | 0.75–0.96 | 0.63–0.98 | 0.76–1.01 |
| jsd_first_fg >= 0.10 | 0.14–0.28 | 0.13–0.26 | 0.16–0.22 | 0.16–0.21 | 0.16–0.20 | 0.15–0.19 | 0.16–0.20 | **0.149–0.220** | 0.136–0.146 |
| p_init_enrich >= 8 | 7.7–31 **UNREADABLE** | 9.8–29 | 12.9–31.7 | 13.2–27.3 | 13.9–23.0 | 14.5–20.3 | 15.6–21.1 | 11.1–22.8 | 10.2–13.5 |
| m_final_enrich >= 8 | 7.1–71 **UNREADABLE** | 8.9–27.7 | 11.0–24.6 | 11.6–26.0 | 12.6–20.6 | 13.0–22.1 | 13.7–20.2 | 10.4–24.6 | **5.8–6.8 FAILS in 40/40 draws** |
| cross_excess_eva >= 0.09 | 0.12–0.23 | 0.16–0.21 | 0.16–0.22 | 0.16–0.21 | 0.16–0.20 | 0.16–0.20 | 0.17–0.20 | 0.149–0.202 | 0.131–0.139 |

Findings.
- Every band is readable as a pass/fail gate on the Voynich side from ~5k tokens; the two enrichment ratios
  are the noisy ones (width 14–19x at 8–11k tokens, 5–6x at 35k) because they are ratios of two small counts.
- **The 41-page held-out split (g1/l1) has jsd_first_fg spread 0.149–0.220 and cross-excess 0.149–0.202.**
  Any entrant-vs-entrant comparison on 41 pages must beat those widths: h2 +-0.05, jsd +-0.036, cross +-0.027,
  enrichments +-6–7x. The G1 circular "miss" of jsd by 0.0006 (REDTEAM #4) is 60x inside this width.
- **Currier A alone is not a sample-size problem; it is a real band failure.** m_final_enrich on A pages is
  5.8–6.8 in every bootstrap draw (band >= 8), and jsd_first_fg sits at 0.136–0.146 (above floor but a third
  below the whole-manuscript 0.176). The v1 bands therefore do not describe A; an A-only board must either
  re-derive bands from A or drop the m band (lead 4 "A vs B separate systems" is scored on bands that already
  fail A, so a separate-systems verdict is partly by construction).
- Bands derived as "Voynich +- 0.15" (h2) are 3–6x wider than Voynich's own sampling width at 25k (0.057),
  so an entrant can sit 0.1 bits off the target and still "pass"; the bands are gates, not measurements.

## 3. Multiplicity

Count (regex over all `results_*.txt`, see helper command in the run log): **582 printed p-values** (560 by
the stricter pattern), 131 z-scores, 193 verdict/PASS/FAIL/DIES/HOLDS tokens; 291 of 582 p-values are < 0.05.
Per file: m1 86, n2 87, n3b 159, n1 48, c2 47, b5 32, m6 30 (25 list tests + 5), c1 28, l1 20, n3 18.

| Marginal result | raw p | Bonferroni at m = 10 (the ten leads) a = 0.005 | m = 25–30 (its own file) a = 0.0017–0.002 | m = 582 (today) a = 0.00009 | BH(0.05) over all 582 (cutoff 0.018) | BH(0.10) (cutoff 0.05) |
|---|---|---|---|---|---|---|
| m1 column-specific P = 0.068 (and 0.003–0.093 by far-line seed) | 0.068 | no | no | no | no | no |
| m6 ALL shared-2-prefix p = 0.050 / ned p = 0.005 | 0.005 | **no** (0.005 = a, not <) | no | no | yes (0.005 <= 0.018) | yes |
| c1 hand 1 p = 0.018 (floor 1/55) | 0.018 | no | no | no | borderline (= cutoff) | yes |
| n3 hand-1 NMI margins 0.013 (ZL3b) / 0.005 (IT2a) — these are NMI margins over the generator's seed mean, **not p-values**; the only p is the floor 0.018 | 0.018 | no | no | no | borderline | yes |
| a3/d6 labels p = 0.0945 (40 pages) | 0.0945 | no | no | no | no | no |
| c1 hand 2 p = 0.133 | 0.133 | no | no | no | no | no |

Statement. None of today's marginal results survives a Bonferroni correction at any family size from 10 upward,
and c1 hand 1 / n3 cannot survive one by construction: an exact null with 55 assignments has a floor of
0.018 > 0.005. Under BH at 5 % across everything printed today the cutoff is 0.018, so the floor results sit
exactly on the line and m6's ned p = 0.005 passes, the pre2 p = 0.050 does not. The honest summary: **the
content side's remaining discriminator (hand-1 NMI) is a floor p-value from a 2-vs-9 block pattern, held by an
NMI margin of 0.005–0.013 against a generator whose own seeds span 0.14–0.31 (n3) — a margin smaller than
the generator's seed spread.** That is not a multiplicity survivor; it is a result awaiting a null with more
than 55 distinct assignments (the bifolio null, p1, adds assignments only if the bifolio map differs from
the quire-section blocks; unverified).

Also: 291/582 printed p-values < 0.05 is the base rate at which this project calls something significant;
with that many looks, a top-10 list that cites any single sub-0.05 p-value without a pre-registered family
is citing noise at ~50 % prior.

## 4. Execution constraints

Environment read 19:26 PDT: system `python` 3.11.9, numpy 2.4.6, scipy 1.17.0, scikit-learn 1.8.0, openpyxl
3.1.5 (**present on system python**, resolving TOOLS "unverified"); `torch 2.11.0.dev20260115+cu128`,
`cuda.is_available() = True`, RTX 5080 reported 16.3 GB total, **13.2–13.3 GB in use by other processes at
19:19 and 19:26 (nvidia-smi; `torch.cuda.mem_get_info` returned 15.7 GB free at 19:20 — the two disagree,
unverified which is right for an allocation)**; RAM 32 GB total, **3.6 GB free** (vmmemWSL, ChatGPT, claude,
Memory Compression at the top; 20 python processes using 1.4 GB together). uv: `.uv-python` is empty; uv
resolves 3.13.12 from `<local-path>` (closes OPEN O-035).

| Family of test | Script(s) | Runtime (measured or filed) | Peak memory (estimate) | GPU | Under 4 sessions at 3.6 GB free |
|---|---|---|---|---|---|
| v1 board on one corpus | `score.py:score_corpus` | 1–2 s | < 200 MB | no | fine |
| full m4 board (47 corpora x v1 + metrics_new) | `m4_phase1_board.py` | **703 s** filed; rerun killed today under 4 sessions (m4_run2.log stops at corpus 32/47, 497 s) | per corpus the `bake` step builds char 2–3-gram tables on 25k tokens; cumulative JSON kept in memory; ~1–2 GB (unverified) | no | **not safe**; run alone or with `--`-style per-family splits (none exist: m4 has no resume) |
| metrics_new on Voynich (run_new) | `scoreboard/run_new.py` | ~35 s/corpus (lex 15, bake 10, extra 6) | < 1 GB | no | fine singly |
| run_robust (4 translits) | `run_robust.py` | ~2.5 min | < 1 GB | no | fine singly |
| c1 quire null | `c1_quire_null.py` / helper | 14 s for 2 hands x 8 s-values x 5 seeds (NMF on ~260 chunks) | < 300 MB | no | fine |
| m1 coordinates | `m1_coordinates.py` | build_pages 0.2–2.3 s, collect 0.2 s, boot 1000 ~0.5 s; full script with 2 nulls x 20 reps + f57v: ~1 min (unverified) | < 300 MB | no | fine |
| m6 labels | `m6_labels.py` | ~1 min (200 shuffles x 8 blocks; unverified) | small | no | fine |
| n1/n2/n3 habit generator (3 translits x 3 seeds x B=1000 bootstrap) | `n*_*.py` | n/r; n3b prints none; estimated 5–15 min | < 1 GB | no | fine singly |
| a6/a6b/j3 solvers | 40,000 iters x 4 restarts numpy | "long" (tens of minutes to hours) | small | no (numpy) | CPU-bound, 4 sessions share cores |
| K4 / K-series producers + NMF | `k4_lossy_nomenclator.py` | n/r; NMF per row | < 1 GB | no | fine |
| b2 HMM (20 restarts x 120 iters x 7 corpora x 2) | `b2_hmm_sukhotin.py` | long | small | no | fine |
| **O-009 GPU noisy-channel key search** | none exists | unknown | needs the GPU with > 3 GB free; **today 13.2 GB of 16.3 is held by other processes** | yes | **not executable until the GPU is freed; no script, no positive control** |
| Timm–Schinner regeneration | `ctl_timm_schinner.py` | — | — | — | **blocked**: JRE deleted 18:10 |

Two runtimes: a-/b-/j-series docstrings say `uv run` (3.13.12), m-/n-/ctl-/scoreboard run on system 3.11
(TEAM-HANDOFF "Runtime note"). Both have numpy >= 2.4.6; `__pycache__` holds cpython-311 and -313 pyc. The
risk is not import failure but **non-identical floating results across runtimes for KMeans/NMF/SVD paths**
(sklearn 1.8.0 on 3.11 vs >= 1.9.1 pinned for uv; unverified whether seeds reproduce across the two). Any lead
whose kill rule is a 3rd-decimal margin (n3: 0.005) must name its interpreter and sklearn version in the result
header.

'?' and uncertain-space policies (counted on `data/ZL3b-n.txt`, 4,130 P loci): 212 tokens contain `?`
(dropped everywhere; 108 pages touched); **2,464 uncertain spaces `,`** (treated as word breaks by default;
`strict_spaces=True` joins them and drops the token count from 35,069 to 32,606, i.e. 7 % of tokens);
746 `<->` drawing breaks (always a break); 131 `@nnn;` rare glyphs (collapsed to `?`, so dropped with
their token); 656 `[a:b]` alternatives (first reading taken). Sensitive leads: edge coupling and every
edge-table producer (c3: +0.181 -> +0.148 when uncertain spaces are joined; 7 % of the pairs change),
h2 (a 7 % token change moves the 25k window), m1 (`ok_word` drops `?`; boxes are matched to ZL strings
so `[a:b]` choice changes alignment), m5/line anatomy (line-final `m` is often before `,`?: unverified),
labels (m6 drops `?` words; d6 shows the f57v ring's rare glyphs are `@169;`–`@172;`), F1/n2 residual
(TOPN-300 vocabulary shifts). Insensitive: NMI/section tests (bag-level), Heaps.

## 5. Pitfall list (ways a lead's result is an artefact here)

1. **Random far-line draw decides m1's verdict.** Re-running `m1.collect` on the real data with far-line
   seeds 0–9 gives P(column-specific <= 0) = 0.073, 0.007, 0.007, 0.033, 0.003, 0.093, 0.073, 0.030, 0.003,
   0.027 (filed 0.068 at seed 20261017). Seven of ten would have been read as "column copying detected".
   Any lead that re-tests same-column copying must average over far-line draws or use all far lines.
2. **Floor p-values from exact enumeration** (c1 A/C: 55 and 105 assignments; n3 inherits): p = 0.018 is
   both "the strongest possible" and "one quire boundary". Reported as "survives", it cannot be corrected,
   ranked, or compared with the generator's p (also 0.018 in 3/3 seeds).
3. **Circular tables**: F3/G1/H1/K1–K4/N1–N3 carry Voynich's own P(first | last) edge table and c2's
   section lexicons; c2_best's lexicon *is* the real tokens per (hand, section). Any "entrant matches the
   edge band / NMI" is a capacity statement (REDTEAM #1, #5, #13).
4. **Pseudo-line controls**: every L control is wrapped into 9-word lines; jsd_first_fg / p / m for L are the
   shuffle null (0.001–0.003). "Outside every family" on edge metrics is by construction (REDTEAM #7).
5. **Alphabet-specific bands**: h2 2.13 (EVA) / 2.40 (glyph+) / 2.54 (GC2a); sd_len likewise. A producer
   built in EVA strings is scored on the EVA band; one built on glyphs fails it (m7, O-022).
6. **Hash-seed nondeterminism**: `b4.build_neighbours` iterates sets; b4 SIMcal rows (b4, b5, c3, g0) change
   with PYTHONHASHSEED; c2's `sorted_neighbours` is deterministic only if c2 is imported after b4 generation.
7. **Shared RNG across corpora** (b3 `Random(7)`, b5 `default_rng(0)`): a row's value depends on which
   corpora ran before it in the same process.
8. **UTF-16 outputs**: `results_d2.txt` (PowerShell `>`); any grep/parse that assumes UTF-8 reads it as
   empty (my p-value count had to fall back to utf-16). New sessions redirecting with PowerShell will
   produce more of these.
9. **Sidecar dialects**: `pages[].id` (ctl_common/k5/c2_best) vs `pages[].page` (ctl_nomenclator/naibbe/
   generators); `metrics_new.meta_json_pages` requires `id`, `Corpus.from_meta_json` falls back to p0000
   ids, m4's `load_meta` accepts both. A lead scored through metrics_new on a `page`-dialect sidecar
   silently loses page identity (page MI, same-page far, bifolio nulls).
10. **Two writers, one file**: `results_ctl_generators.txt` is overwritten by `ctl_report.py`;
    `score.py:main()` rewrites `scoreboard.json`; `g0` appends to it. Relative-path writers (d1, d3, d5,
    d6) land wherever the cwd is.
11. **Plug-in entropy bias at small n**: h2 at 2k tokens is 0.03 lower on average than at 35k (bootstrap
    means 2.09 vs 2.11); any A/B or per-section h2 comparison across unequal n inherits this.
12. **25k cap vs all-tokens definitions**: four filed "Voynich h2" values (2.126 / 2.109 / 2.093 / 2.397,
    METHODS 1.1); redup N vs N-1; JSD all lines vs lines 2+. A lead quoting one number against a band
    derived from another is off by more than the band's sampling width.
13. **Undefined metrics counted as outs**: abjad controls print `inf` for p/m enrichment (no p/m glyphs)
    and are counted as L "out" (REDTEAM #20); 3 corpora errored in m4 and are silently absent.
14. **Range-overlap weighting set after the control families were chosen** (m4: 14 of 23 metrics zeroed);
    the "G favoured, margin 2" verdict moves with any added control.
15. **Four sessions, no VCS, no ledger**: three result files and three docs changed during the inventory
    read; a lead ranked from a doc number can be ranked from a superseded number (REDTEAM #23).
16. **Dropped `?` tokens and 2,464 uncertain spaces** (above): any edge or boundary statistic has a 7 %
    tokenisation lever that nobody pre-registers.
17. **Word-box provenance**: m1's boxes are a voynichese.com scrape on a 3-px grid; 26 % of zero-gap sites
    disagree with ink (o1); 9 folios < 60 % matched. Column leads inherit a transcriber's reading.
18. **Bootstrap draws reuse the null's RNG** (m1 `boot(res, rng)` continues the same generator that chose
    far lines; c1 passes `default_rng(0)` through all four corpora): seed-level reproduction of a single
    block requires rerunning everything before it.

## 6. Stress test of the peer baseline (coordinator request, 19:2x)

Baseline: 1 joint anomaly as target; 2 K4 lossy code + rare codewords + m5 line-end draws; 3 matched edge-table
generator, same type budget; 4 A vs B separate systems; 5 hand-1 NMI vs 7k habit generator + bifolio null (n4);
6 gibberish fourth family (n7); 7 generation signatures on cipher output (n5); 8 diplomatic Latin line-break
control; 9 planted-key search only if 2 passes; 10 physical/external checks. Phases: 0 freeze v2; 1 = 4–7;
2 = paired tournament 2 vs 3 with 8 as control, 3 seeds, 41 held-out pages; 3 = 9 gated.

**Does Phase 2 have the power to separate 2 from 3 on 41 pages (~6.8k tokens here, not 8.6k: 41 random pages
average 6,849 tokens; 8.6k is the l1 split's particular draw)?** Partly. The 41-page sampling widths measured
above are h2 +-0.05, sd_len +-0.04, redup +-0.18 pp, jsd +-0.036, cross-excess +-0.027, p/m enrichment +-6–7x.
Entrants 2 and 3 differ by construction on **h2 and types** (K4 2.23–2.27 and 5.4–5.6k types vs every
generator 1.6–1.9k types, h2 1.75–1.81): that gap (0.4 bits, 3.5k types) is 8x the 41-page width, so a
tournament separates them on h2/types with 3 seeds easily — but it is the same separation already on file
(k4 vs n2), and K4 wins it by default because the generator has never been given a 7k lexicon (O-039). On
the metrics the tournament is *meant* to decide — edge coupling, jsd, NMI, page MI — **both entrants carry
Voynich's own edge table and c2's section lexicons, so their expected values are equal by construction and
their difference is seed noise inside +-0.03.** Three seeds do not resolve a difference whose expectation is
zero. The p/m enrichment bands cannot separate anything on 41 pages (width 12–14x). Verdict: Phase 2 as
specified has power only on the dimension that was not in dispute, and none on the ones that were.

**Is item 8 a control or the load-bearing unknown?** Load-bearing, and it must precede Phase 2. The line-edge
bands (jsd, p, m, m5 anatomy) are the only metrics on which the families still differ (REDTEAM §2.3), every L
control is pseudo-lined, and the Voynich line layer is handed to every entrant. Until one real scribal
transcription with line breaks is scored, nobody knows whether jsd 0.176 / m x16 are "anomalies" or what any
15th-century scribe does; if a real scribe gives jsd >= 0.10, the edge bands stop discriminating families and
Phase 2's control is the result. Scheduling 8 as a Phase-2 control reverses the dependency: it is the test
whose outcome decides what Phase 2 can mean. It should run in Phase 1 (cost: one transcription with line
breaks, O-014/O-026; score with `score.py:line_metrics` and m5, < 1 min).

**Is item 1 a lead or the scoring target?** The target. "Joint anomaly" is the conjunction of seven bands
derived from Voynich's own values; it has no refuter (Voynich passes its own bands in 200/200 splits, l1),
no cost, and no tier it can reach on its own. Listing it as lead 1 spends a slot on the definition of the
scoreboard. What *would* be a lead is the within-Voynich failure of the target: Currier A fails m_final in
40/40 bootstrap draws (§2), so the "joint anomaly" is not a property of the whole manuscript. That belongs
under item 4, and it means item 4 is partly pre-decided by the bands (pitfall: A "separate system" verdict
scored on bands fitted to B-heavy totals).

**What does "2 beats 3" license?** Only this: a word-sized shared-codeword code can carry h2 ~2.2 and 5–6k
types while a 1.7k-type habit generator cannot — a granularity statement (REDTEAM #13), not a content
statement. Because both carry the same edge table and section lexicons, a win on edge/jsd/NMI is seed
luck; a win on h2/types is the lexicon-size confound (O-039) unless 3 is given the same 7k budget, which
the baseline says it is ("same type budget") — then the generator's h2 will rise toward the band (hapax-heavy
tables raise h2) and the h2 separation shrinks to an unverified margin. It does **not** license Phase 3: a
planted-key search under the F3 model is gated on a cipher producer passing the *v2* board, and the GPU it
needs is 13 GB occupied today with no script and no positive control. "2 beats 3" would license at most
"build the non-Voynich-table versions of 2 and 3" (REDTEAM #1), which is the test that actually bears on
family.

Other attacks on the baseline: (i) items 5 and 6 are cheap and good, but 5's bifolio null (p1 exists:
`results_p1.txt` reports quire-permuted ranges, not a p-value) adds no assignments above 55 unless the
bifolio map splits the HHHHHHHHPHP blocks — check the map before promising a "stronger null"; (ii) item 7
(n5) is the only Phase-1 item with an existing pre-registration hash and a clear kill (`n5_signature_
discrimination.prereg.sha256` is on disk); (iii) item 10 has no statistic and no refuter in the baseline;
(iv) Phase 0 "freeze v2" must fix an alphabet (O-022) and an uncertain-space policy (§4) or every later
margin is inside the tokenisation lever; (v) with 291/582 p < 0.05 today and a floor-bound content
discriminator, a ten-item list that includes four content-side items (4, 5, 7, 8) and one target (1) has
at most three items (2, 3, 6) that can reach Tier 2, and two of those are the same tournament.

## 7. Infeasible or uninterpretable as specified

| Lead (baseline #) | Status | Why |
|---|---|---|
| 9 GPU key search | **infeasible now** | no script, no positive control, GPU 13.2/16.3 GB held by other processes, 3.6 GB RAM free; gated on 2 passing a board that is not frozen |
| 2 vs 3 tournament on edge/jsd/NMI (Phase 2) | **uninterpretable** | both carry Voynich's table; expected difference zero; 3 seeds inside +-0.03 noise |
| 4 A vs B on the v1 bands | **partly pre-decided** | A fails m_final in every draw; bands fitted to the whole |
| 1 joint anomaly | **not a lead** | it is the target; no refuter |
| m4-style full board reruns under 4 sessions | **infeasible concurrently** | 703 s, killed at 497 s today; no resume |
| any lead re-using m1's column test as filed | **uninterpretable** | far-line seed decides P (0.003–0.093) |
| any lead using c1/n3 hand-2 negatives as evidence | **uninterpretable** | power 0.6–0.8 at the manuscript's own effect size |
| m6 Lc/Ls list tests | **no power** | 24 / 64 pairs; detect only >= 50 % / 15 % effects |
| Timm–Schinner regeneration | blocked | JRE deleted |
| anything scored through `metrics_new` on a `page`-dialect sidecar | silent loss of page identity | pitfall 9 |

## 8. Assumption candidates (for the PLAN registry)

- The c1 exact-enumeration null's floor (1/55) is acceptable as "survives"; a null with >= 1,000 distinct
  assignments (bifolio or page-within-block) is needed before hand-1 NMI can be ranked against anything.
- m1's filed P = 0.068 is a single far-line draw; the column-copy question is open at r ~ 0.4 %, below the
  design's 0.6–0.7 % threshold; a lead on it must use all far lines.
- The v1 bands are gates 3–6x wider than Voynich's own sampling width; entrant-vs-entrant comparisons need
  the 41-page widths in §2, not the bands.
- The v1 bands do not hold on Currier A (m_final); any A-specific lead needs A-derived bands.
- Edge-band leads are uninterpretable until one real-line scribal control exists (item 8 before Phase 2).
- Multiplicity: nothing marginal today survives Bonferroni at m = 10; BH(0.05) cutoff is 0.018; results at
  the enumeration floor cannot be corrected and should be reported as floor-bound, not as p-values.
- Tokenisation lever (2,464 uncertain spaces, 212 `?` tokens, 656 alternatives) must be frozen in v2.
- GPU work is not available this round; plan CPU-only.
- Runtime/sklearn version must be in every result header for margins < 0.02.
