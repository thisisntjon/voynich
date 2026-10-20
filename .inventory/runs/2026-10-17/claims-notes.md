# Claims register — run notes (2026-10-17 18:36 PDT, clock read with `date`)

Register: `.inventory/registers/CLAIMS.md` (286 rows, c-001…c-286; c-265–c-286 added 18:52 PDT for the K_RESULTS producer-table cells, the N1 "3%" and the j1 "2×" weight). Every number was checked against the named `results_*` / JSON / data file, never against another `.md`. No analysis was run; `results_d2.txt` was read through `iconv -f UTF-16`.

## Counts by status

| Status | Rows |
|---|---|
| VERIFIED | 229 |
| VERIFIED-LITERATURE (external text opened, figure found) | 8 |
| STALE (doc and source disagree, or a later source supersedes the doc) | 25 |
| UNSUPPORTED (no source file holds the number) | 13 |
| UNSUPPORTED-LITERATURE (research_notes cite it; primary not local or figure not found in the local text) | 10 |
| RESOLVED (was a contradiction at audit time; docs since corrected) | 1 |
| **Total** | **286** |

Eight VERIFIED rows carry a partial caveat inside the status cell: c-124 ("K=500" not in results_j2), c-131 (TEAM-HANDOFF:141 omits the line-final "BOTH"), c-134 (sd spread 0.086 not 0.07), c-155 (the 0.146 L-max is Macer Floridus, not Italian verse), c-160 (G1 page-shuffle range), c-232 (r/voynich "1 mention" not found), c-244 (README's "300 boundaries" vs o1's 283), c-262 (30-entry / 1011-word Lingua Ignota figures are literature).

## STALE / UNSUPPORTED rows (id, doc:line, what is wrong)

| id | doc:line | what is wrong | which is right |
|---|---|---|---|
| c-066 | docs/rounds/LEADS-AND-FINDINGS.md:51 | "all rotation-null p=0.000, including within-hand" | results_b5.txt: hand 2 rotation p=0.048 |
| c-079 | PREREG.md:45; RESEARCH-PLAN.md:23,99 | "D2: 10.728" as the slot-model bar | results_m3: flat-UNK unigram is not a distribution over strings; renormalised bar ≈11.15–11.25 (frozen text needs v2) |
| c-093 | docs/rounds/E_RESULTS.md:56 | heading "17-glyph refrain" | results_e3/d6: 17 tokens, glyph period 18 |
| c-097 | docs/rounds/F_RESULTS.md:19 | "whole words and top-100 agree" | results_f1: INCONCLUSIVE / INCONCLUSIVE / FAVOURS LANGUAGE; top-100 residual +0.024 vs +0.042 |
| c-099 | docs/rounds/RESEARCH-PLAN.md:37-51 | F1 table (shuffle 10.383/10.636/10.800), "12.07 x", "FAVOURS EDGE-RULE", "only the whole-word block" | results_f1.txt re-run (3 blocks, INCONCLUSIVE, null row 10.428/10.724/10.915) |
| c-106 | docs/rounds/F_RESULTS.md:62 | "p ×1.07 against ×16" for the β=1.5 cipher | results_f3 prints ×1.07 for β=2; β=1.5 unruled is ×0.84 (results_h1) |
| c-107 | PLAN.md:247-248 (point 2), K_RESULTS.md:44,52, F_RESULTS.md:56-59,69-71 | F1/F3/K residual word order cited as evidence for meaning ("only the meaning-bearing one keeps Voynich's word order") | superseded by results_n2.txt: habit generator at p=0.04 gives +0.0423/+0.0389/+0.0346, inside the manuscript CI; PLAN 8a, K/F banners state this but point 2 and the K/F body text are not rewritten |
| c-110 | docs/rounds/F_RESULTS.md:103 | "without edge factoring type ARI 0.04 at MINC=5 vs 0.06" | no file holds it |
| c-116 | docs/rounds/G_RESULTS.md:66 | "The other five seed draws miss the same three bands" | results_g1: s1/s2 miss only h2+redup; s3 misses h2+cross_excess+redup |
| c-118 | PLAN.md:243 (audit-era wording) | "Generators miss cross-space coupling" | results_g1/f3: edge-table generators carry it; current PLAN:243-245 is already qualified |
| c-123 | TEAM-HANDOFF.md:152 | j1 "cot_gap = +0.025" | results_j1.txt has no cot column |
| c-135 | PLAN.md:299 | "bands are robust on EVA transcriptions" | results_m7: h2 past band edge for ZL3b_glyphplus (EVA-based) and GC2a; holds for ZL3b/RF1b/IT2a only |
| c-143 | PLAN.md:57 | "~70 % hapax … coinage signature" | results_m0/m4: controls 0.65–0.68 at 10k vs Voynich 0.686; hapax is an unweighted (overlapping) metric |
| c-144 | PREREG-v2-DRAFT.md:46 | "G predicts hapax 0.69–0.72 (m0, m2)" | 0.69–0.72 is Voynich across transliterations (m2); m4 generators span 0.41–0.83 |
| c-168 | docs/rounds/E_RESULTS.md:17 (quoting LEADS-CHASE first draft) | "0.387 glyph+ / 0.299 EVA" | results_d1: 0.172 / 0.176 / 0.185 (historical, already corrected in LEADS-CHASE) |
| c-169 | docs/rounds/E_RESULTS.md:23 | "C_RESULTS still says the Naibbe test was not run" | C_RESULTS has C4 |
| c-170 | docs/rounds/INVESTIGATION.md:93 | "no joint position + A/B + topic test has been run locally" | g0/g1/h1/m4 ran joint boards (historical) |
| c-185 | TEAM-HANDOFF.md:137 | codebooks "reproduce length SD" | results_ctl_nomen_numeric: SD 0.985/1.005/2.335; only nomen_word/lines (1.59/1.60) match |
| c-200 | K_RESULTS.md:45,52,54; PREREG-v2-DRAFT.md:51 (M19 G column) | "15–23k types, h2 2.7–2.95" / "every producer needs 15–25k types for +0.18 bits" | results_k4.txt: crossMI +0.215…+0.693 at 5,076–5,613 types, h2 2.23–2.31 (TEAM-HANDOFF:157 already states it) |
| c-206 | reports/Voynich decipherment attempts and failures.md:70 | "Timm-style generator JSD 0.0006–0.0010 … p only to ×1.5–1.8" | current results_b4: JSDfirst 0.0009–0.0052, seeded p ×1.16–1.89 (b4 is hash-seed nondeterministic) |
| c-209 | PREREG-v2-DRAFT.md:45 | "T&S 0.026" edge coupling | results_m4: timm_schinner 0.014/0.017; 0.026 is rugg_grille (the G-range max) |
| c-230 | data/external/README.md:76 | Timm–Schinner conf.properties defaults | log only; .properties on disk not opened |
| c-231 | docs/rounds/DOCX_REVIEW.md:40 | docx "~28% same horizontal position" | results_b1: 10.69 vs 8.79 (DOCX_REVIEW itself says size refuted) |
| c-233 | SCOUT-EXTERNAL.md:39-42; TEAM-HANDOFF.md:166 | TheVoynich.org 691 / 651 / 221 / 1,362 counts | web-only, no local file (the 7 status counts sum to 691) |
| c-234 | docs/rounds/README-a-series.md:12 | "5,385 lines, 39,020 tokens, 8,295 types" (vparse) | no results file; tool not run |
| c-235 | data/external/README.md:8 | ZL3b "pages=227 loci=5385 tokens=38255 types=8708" | log only; tools/ivtff_tokens.py not run |
| c-236 | data/external/README.md:30-40 | IVTFF per-file page/loci/token/type counts | log only; m7 confirms the files parse (34,411–36,385 paragraph tokens) |
| c-248 | PREREG.md:3 | "stamp in git/hg status" | not a git repo; only the SHA-256 exists |
| c-249 | docs/rounds/LEADS-AND-FINDINGS.md:130 | "MANIFEST.sha256 hashes every copied file" | no such file |
| c-250 | PLAN.md:312 | "130 entries: 15 summary markdowns, 51 scripts, 51 result files" | now 161 entries, 10 root .md, 66 .py, 66 results_*.txt |
| c-251 | PLAN.md:313; AUDIT §4 | "data/ is 1.6 GB" / "1,598 MB; external 1,516 MB" | du: data 393 MB, external 310 MB |
| c-252 | PLAN.md:326 | "data/external/ is 191 MB (was 1.3 GB)" | du: 310 MB (gaskell 78 MB and timm 74 MB trees remain) |
| c-253 | data/external/README.md:14 | "timm-schinner-generator/ 142 MB" | du: 74 MB after the README's own 18:10 prune note (line 145) |
| c-254 | AUDIT §4 | zip + tree duplicates for bowern, timm, gaskell, jre; .venv 204 MB | bowern clone/zip and jre deleted; gaskell zip + tree remain; .venv 206 MB |
| c-255 | AUDIT §4 | stray `.i1_stdout.txt`, `m4_run.log` | gone (m4_run2.log present) |
| c-285 | TEAM-HANDOFF.md:29 | N1 "around 3% of choices" | no file prints 3% (n1 grid is 0/0.1/0.25/0.5); n2 measured p=0.04 (RF1b also 0.03) |
| c-257 | TEAM-HANDOFF.md:112 | "Python 3.13.12 via uv" | system python is 3.11; uv 3.13 location unverified (`.uv-python` was empty) |
| c-261 | SCOUT-EXTERNAL.md:32-34 | "data/external/ still does not exist" | exists (fetched 16:15–16:30) |
| c-212–c-228 (10 rows) | reports/…failures.md; PLAN.md:50,55,98; INVESTIGATION.md:17 | literature figures (1404–1438, 294 languages, 1.95–2.50 / 0.27 / 2.16 / 29.5 %, 27 comparison texts, 93 %, Bennett 2.22, 65 threads, five scribes, 45 % Naibbe types, 102/116 folios) | research_notes opened for all but "45 %" and "102 of 116"; local paper texts confirm 2.85, 316, 0.2 bits, 2.7, AUC 0.905, 70 %, 86.6 %, 12 slots, F1 0.270, 42 volunteers, 41/42, 75 texts, 600–800 words, 864 labels, 0.130/0.243, 0.010/0.019, 22 statistics, 282 hypotheses, 0.2–0.3 bits/page |
| c-171 | AUDIT items 4, 25 | m4–m7 "running"/"not started" | RESOLVED: files on disk, TEAM-HANDOFF:3,79 and PLAN:297-300 say done |

Audit §2 items that the current docs have already fixed (not counted as STALE): item 2 (TEAM-HANDOFF:42 now reports line 5 P=0.020), item 3 (PLAN:243-245 qualified), items 11–13 in PREREG-v2 (M13 0.04–0.15, M6 refuter text with 0.85/1.18, M14 0.65–0.68), items 4/25. Item 23 inverts: the current PLAN:267-270 wording (starts = vocabulary, ends = both) matches results_m5's VERDICT; only TEAM-HANDOFF:141 still drops the line-final "BOTH".

## The 10 most-cited numbers and their definitional variants

| # | Number as usually quoted | Exact variants (id) | What changes it |
|---|---|---|---|
| 1 | h2 ≈ 2.1 | 2.126 a1 25k sample (c-001); 2.1262 score_v1 filed (c-004); 2.109 full 34,857 tokens (c-002); 2.093 b4.report lines 2+ (c-003); 2.048 held-out 41 pages (c-158); 2.135 RF1b, 2.128 IT2a (c-134); 2.263 glyph, 2.397 glyph+, 2.540 GC2a (c-007, c-134); analyze H1 2.3208 is a *different* statistic (no space symbol) (c-039) | sample size, line set, transliteration, alphabet collapse, whether the space is a symbol |
| 2 | ≈0.2 bits cross-space coupling | +0.1809 c3 excess / 0.1950 plug-in MI (c-072); +0.1899 glyph+; MM-corrected 0.1721 EVA, 0.1761 glyph, 0.1846 full (c-075); A +0.1203 / B +0.2321; uncertain spaces joined +0.1482; +0.1729 RF1b, +0.1660 IT2a (c-134); held-out +0.2023 (c-158); e2 0.1950 (c-090) | null subtraction vs plug-in, Miller–Madow correction, sample, Currier split, transliteration |
| 3 | ×16 line-edge enrichment | ×17.89 / ×16.31 all lines (c-015, c-016); ×15.97 / ×16.55 lines 2+ (c-019); ×19.4 / ×16.43 RF1b; ×18.95 / ×26.23 held-out 41 pages | page-first lines included or not; sample |
| 4 | first-glyph JSD 0.176 | 0.1759 all lines (c-012); 0.1722 lines 2+ (c-020); 0.1762 held-out; 0.1809 RF1b, 0.1748 IT2a, 0.2022 glyph+; paragraph-initial 0.5486 / other 0.1468 (c-127); attested-types only 0.1395 (c-129) | line set, transliteration, paragraph-initial split |
| 5 | +0.04 transferable word order | +0.042 top-300 page split (c-094); +0.041 whole words; +0.024 top-100; +0.039 reversed; +0.041 quire split (c-103); n1 quire-split +0.0461 [+0.0357, +0.0564] ZL3b, +0.0333 RF1b, +0.0410 IT2a (c-161); A +0.052 / B +0.048 (c-096) | vocabulary cut, split, transliteration, bootstrap |
| 6 | NMI 0.275 / 0.333 | b5 within-hand (c-065): rotation p 0.000 / 0.048; quire-block null means 0.067 / 0.209, p 0.018 / 0.133 (c-068); c2 perm p99 0.047 / 0.128 | which null |
| 7 | 7k types / 0.68 hapax | 7025 types, 0.680 full (c-040, c-010); 5417 / 0.679 at 25k (c-001); 0.686 at 10k (c-142); 2535 types on 41 held-out pages | sample size |
| 8 | SD 1.76 | 1.764 25k (c-005); 1.788 35k (c-002); 1.725 held-out; 1.777 RF1b, 1.691 IT2a; 1.435 glyph+ (c-134) | sample, alphabet |
| 9 | repeats 0.9 % | 0.896 % 25k (c-006); 0.87 % lines 2+ (c-021); 0.843 % full (294 doubles); 0.94 % n1/n2 MS rows; 0.80 % held-out | sample, line set, denominator |
| 10 | 10.728 bits/token (d2 unigram) | 10.728 flat-UNK seed-42 page split (c-078); m3 same split reproduced; proper-distribution unigram 11.632 (page) / 12.082 (quire); renormalised 11.245 / 11.645; char3-WB 11.151 / 11.556 (c-152); m0 quire 11.545 copy0.05+markov3 (c-141) | UNK handling, split, model |

Also with ≥3 variants: label hit rate (0.121 vs 0.107±0.010 p=0.106 in a3; 0.1208 vs 0.1060 p=0.0945 in d6; 0.1441 p=0.0199 with ring text), Heaps β (0.724 d5 vs 0.741 m0), f57v period (17 tokens / 18 glyphs / 13 by box angle), column copying (1.9 pp word-index vs +0.41 pp coordinates; same/far 1.21 vs 1.23).

## Numbers that appear in one doc with two different values

| Doc | Values | Rows |
|---|---|---|
| TEAM-HANDOFF.md | N2 generator "about 1.6k types" (line 30) vs K_RESULTS:24 "about 1.8k": 1.6k is the p=0 baseline, 1.8k the p=0.04 entrant | c-203, c-205 |
| TEAM-HANDOFF.md | m-series sd spread "0.07" (line 143) vs m7's plain-EVA spread 0.086 | c-134 |
| PLAN.md | point 2 (line 247) "matches … held-out word order together" vs 8a (line 275) "dead as a discriminator" | c-107 |
| PLAN.md | "data/ is 1.6 GB" (line 313) vs "data/external/ is 191 MB" (line 326); neither matches du (393 / 310 MB) | c-251, c-252 |
| PLAN.md | hapax "~70 %" coinage signature (line 57) vs PREREG-v2 M14 "0.65–0.68 measured … does not hold here" | c-143 |
| K_RESULTS.md | "15–23k types" (line 45) vs TEAM-HANDOFF:157 K4 5,613 types with +0.215 | c-200 |
| C_RESULTS.md | "0.130 and 0.243 … whether those figures are for A and B is unverified" — Schwartz text gives them per scribe, not per Currier language | c-218 |
| data/external/README.md | timm-schinner 142 MB (line 14) vs its own prune note (line 145); "300 boundaries" (line 94) vs o1's 283 | c-253, c-244 |
| docs/rounds/F_RESULTS.md | banner line 1 "F4 … which this file does not cover" vs F4/I1 sections at lines 83-134 | audit item 7 |
| docs/rounds/E_RESULTS.md | heading "17-glyph refrain" (line 56) vs body "four copies of 17 tokens … glyph period is 18" (line 62) | c-093 |
| docs/rounds/RESEARCH-PLAN.md | F1 whole-word residual "−0.120 … FAVOURS EDGE-RULE" (lines 39-50) vs line 28 "See the caveat below" and the current results_f1 INCONCLUSIVE | c-099 |
| scoreboard / PREREG | "2.126" (PREREG:23) vs "2.1262" (G_RESULTS:11) — same value, printed precision | c-004 |

## Method notes

- Line numbers are from the files as they stood 18:30–18:36 PDT. TEAM-HANDOFF, K_RESULTS, PLAN, PREREG-v2-DRAFT and F_RESULTS were re-saved at 18:30 (N2/K4/O1 banners); the audit's line numbers for those docs are shifted (K_RESULTS +8, F_RESULTS +6, PLAN +1 after line 275).
- Counts that only a tool run would verify (vparse / ivtff token counts) are UNSUPPORTED, not STALE: nothing contradicts them, but no results file holds them.
- `du` figures are MB on disk at 18:36; data/external is 310 MB, not the 191 MB PLAN:326 states.
- Citation counts in SCOUT-EXTERNAL (73 / 136 / 0 / 3 / 19) reproduce exactly by per-file `grep -o`; "r/voynich: 1" does not.
- Nothing outside `.inventory/` was written.
