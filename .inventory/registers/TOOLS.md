# TOOLS register — Voynich project (.)

Stamped 2026-10-17 18:32 PDT (clock read with `date`). Built read-only: every script's module
docstring and its output/seed lines were extracted (`ast.get_docstring` + grep); nothing was run.
"Results on disk" was checked with `ls` at 18:29. Runtimes are those printed in result files or
docs; "n/r" = not recorded anywhere I found.

## 0. Two runtimes (read before invoking anything)

| Runtime | How | Used by | Notes |
|---|---|---|---|
| system `python` 3.11 (3.11.9 per REPRODUCTION.md; numpy 2.4.6, scipy 1.17.0, scikit-learn 1.8.0) | `cd .; python <script>.py` | scoreboard/*, tests, m-series, ctl_*, tools/*, n1/n2, o1 (TEAM-HANDOFF "Runtime note") | REPRODUCTION.md and the 18 tests were stamped on this interpreter. |
| uv env, Python 3.13.12 (`.venv`, `.uv-python`, `.uv-cache`; `pyproject.toml` requires >= 3.11, numpy >= 2.4.6, openpyxl >= 3.1.5, scikit-learn >= 1.9.1, scipy >= 1.17.1) | PowerShell: `$env:UV_CACHE_DIR=...\.uv-cache; $env:UV_PYTHON_INSTALL_DIR=...\.uv-python; $env:TMP=...\.tmp; $env:TEMP=$env:TMP; Set-Location ...; uv run python <script>.py` (TEAM-HANDOFF "Run") | a-/b-series docstrings say `uv run python ...`; j1-j3 say `uv run`; analyze.py; test_voynich | "Python 3.11.9" in PLAN.md is historical (TEAM-HANDOFF). openpyxl (c4, f3, f4, i1, j*, k*, h1, l1) is only declared in the uv env; whether the system python has it is **unverified**. |

Other caveats carried over from TEAM-HANDOFF: `results_d2.txt` is UTF-16 LE (PowerShell `>`
redirect); import `c2_section_generator` only after any b4 SIMcal generation in the same process
(c2 patches `b4.build_neighbours`; b4's own neighbour lists come from set iteration and change with
PYTHONHASHSEED, so b4 generators are **not reproducible across processes** unless PYTHONHASHSEED is
fixed; c2's `sorted_neighbours` is deterministic); `scoreboard/score.py:main()` overwrites
`scoreboard/scoreboard.json` down to the original four rows.

Frozen files (`scoreboard/PREREG.sha256`, both lines re-verified 2026-10-17 18:30 with `sha256sum`):

| File | sha256 | Status |
|---|---|---|
| PREREG.md | 1fcf9c17e91e0cdd3d6536710ec0f24a00d47b506765b9c278c45b863529ca5c | matches |
| scoreboard/score.py | 3a7b7c3efea13b884362f9f7f07551835bab8ca158ecdb43b946c96a8b3fbf1d | matches; `scoreboard/score_v1.py` has the same hash (byte-identical copy) |

Also frozen by convention (TEAM-HANDOFF "Data the tests read"): `data/ZL3b-n.txt` (sha256
bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc, read 18:30; recorded by
`scoreboard/run.py` provenance), `corpora.py`, `c2_section_generator.py`. Pre-registered scripts
with hash files: `n1_habit_table.py` a40137f5... (`n1_habit_table.prereg.sha256`),
`n2_habit_fine.py` 13058a76... (`n2_habit_fine.prereg.sha256`, which also lists n1) — both verified.

Owner prefixes: `a`-`k`, `l1`, `m0`-`m7`, `n1`-`n2` taken; `o1` present on disk (not listed in
TEAM-HANDOFF "Prefixes"); next free is `n3`/`o2` onward. Sessions named in docs: scoreboard v2 +
m-series = "voynich-08"; ctl_* = "controls-builder agent"; data/external = "data agent".

Status key: **frozen** = hash-pinned or declared not to be edited; **live** = current pipeline or
queue item; **historical** = filed, superseded or one-off.

## 1. Library modules (imported, not run)

| Module | Invocation | Reads | Writes | Seed / determinism | Owner | Status |
|---|---|---|---|---|---|---|
| `vparse.py` | `python vparse.py` prints line/token/type counts and label tallies; otherwise imported | `data/ZL3b-n.txt` (ascii) | nothing | deterministic | a-series | frozen-by-use (tests read it) |
| `corpora.py` | import only; `corpora.voynich()`, `voynich_lines()`, `control(name, n)`, `to_glyphs` | ZL3b via vparse; `data/controls/<name>.txt` (Gutenberg) | nothing | deterministic | a-series | frozen (TEAM-HANDOFF) |
| `corpora_ext.py` | import only; `control_ext`, `control_ext_lines`, `control_ext_pages`; lists `NATURAL`, `CONSTRUCTED`, `SYNTHETIC` | `data/controls/*.txt` (## section markers), `data/controls_synthetic/*.txt` + `.meta.json` | nothing | deterministic | controls-builder | live |
| `scoreboard/corpus.py` | import; `Corpus.from_voynich / from_control / from_control_sections / from_wordlist / from_meta_json` | ZL3b, controls, sidecars | nothing | deterministic | voynich-08 | live |
| `scoreboard/score.py` (= `score_v1.py`) | `python scoreboard/score.py` (docstring: `uv run python scoreboard/score.py`) runs `main()`; `score_corpus(name, words, lines)` is the v1 API used by g0/g1/h1/l1/m4/m7 | ZL3b, latin_caesar, italian_dante | **`scoreboard/scoreboard.json`** (main() rewrites it to the 4 v1 entrants + `reproduction_pass`; do not run casually) | SEED 20261017 for the shuffled null; edge null `Random(0)`; deterministic | PREREG v1 | **frozen** (hash) |
| `scoreboard/score_v2.py` | import; `score(corpus, n_tokens=25000, seed=20261017, skip_nmf=False)`, `flatten` | via Corpus | nothing | pinned per-metric seeds (a2 0..29, a4 0, b3 7, b5 rng 0/NMF 0, b1 20261017); deterministic | voynich-08 | live |
| `scoreboard/metrics_new.py` | import; `lexicon_growth`, `slot_structure`, `information_profile`, `heldout_bakeoff`, `extra_signatures`, `bigram_pseudo_pages`, loaders | ZL3b via vparse; sidecars | nothing | SEED 20261017 (`Random` + `default_rng`); deterministic | voynich-08 | live |
| `ctl_common.py` | import; `voynich_pages`, `write_control`, `ctl_stats` | ZL3b | `data/controls_synthetic/<name>.txt` + `.meta.json` (via `write_control`) | — | controls-builder | live |
| `b4_selfcite_sim.py`, `c2_section_generator.py`, `c4_naibbe_lines.py`, `f1`, `f2`, `f3`, `f4`, `k1`, `k2` | also imported as libraries by later scripts (see rows below) | | | | | |

## 2. Scoreboard CLIs

| Script | Invocation (project root, system python) | Reads | Writes | Runtime | Seed / determinism | Status |
|---|---|---|---|---|---|---|
| `scoreboard/run.py` | `python -m scoreboard.run --corpus voynich` / `--corpus voynich:glyph` / `--control latin_caesar[:verse\|:linesN]` / `--sections latin_augustine` / `--meta path.meta.json` ; flags `--name`, `--n-tokens 25000`, `--seed 20261017`, `--skip-nmf`, `--out`, `--print`, `--dry-run` | ZL3b, controls, sidecars | `scoreboard/scoreboard.json["v2"][name]` (metrics, params, corpus summary, source, timestamp, provenance sha256 of score_v2/corpus/score_v1/ZL3b + lib versions). Current v2 keys: voynich, voynich:glyph, latin_caesar, nomen_k2_x2 | ~11-15 s per Voynich corpus (NMF ~2 s) | deterministic (pinned seeds) | live |
| `scoreboard/run_new.py` | `python -m scoreboard.run_new --voynich` (`--quick` = 5 shuffles) | ZL3b, latin_caesar, italian_dante (25k, 8x20), bigram null | `results_m0_newmetrics.txt` + `.json` | ~35 s Voynich block (timing line: lex 14.7, bake 9.9, extra 6.3 s) | 20261017; deterministic | live. **Docstring/output mismatch**: the file on disk is headed `# results_d1_newmetrics` (older name). |
| `scoreboard/run_robust.py` | `python -m scoreboard.run_robust` (`--fast` = 25k subsample, 5 shuffles) | `results_m0_newmetrics.json` (or `results_d1_newmetrics.json`) baseline; `data/translit/{ZL3b_glyphplus,RF1b,IT2a,GC2a}.meta.json` | `results_m2_robustness.txt` + `.json` | ~2.5 min (timing line) | 20261017; deterministic | live |
| `tests/test_score.py` | `python -m unittest tests.test_score -v` | ZL3b, latin_caesar, italian_dante, latin_augustine | nothing | 26-33 s (18 tests) | deterministic | live |
| `tests/test_voynich.py` | `uv run python -m unittest discover -s tests` (docstring) or `python -m unittest tests.test_voynich` | ZL3b; `analyze.english_control()` reads workspace docs | nothing | n/r (5 tests; solver test runs 3 restarts x 1500 iters) | analyze SEED 20261017 | live (historical battery) |

## 3. Experiment scripts (root), by prefix

Column "Writes" names the exact results file. "print" = console only; the filed `results_<x>.txt`
for those was produced by shell redirect (a-series) — so for a1-a7 the file name is a convention,
not in code.

| Script | Invocation | Reads | Writes | Runtime | Seed / determinism | Status |
|---|---|---|---|---|---|---|
| `analyze.py` | `uv run python analyze.py` | ZL3b; English workspace docs; | `results/results.json`, `results/summary.md` | n/r | SEED 20261017; deterministic | historical |
| `a1_profile.py` | `python a1_profile.py > results_a1.txt` | ZL3b (eva/glyph/glyph+, lang A/B), 6 controls | print (results_a1.txt) | seconds | `Random(0..2)` shuffles; deterministic | historical (frozen numbers reproduced by score_v2) |
| `a2_position.py` | `python a2_position.py > results_a2.txt` | ZL3b lines; dante/faust verse | print (results_a2.txt) | ~1 min (30-draw nulls) | `Random(i)`; deterministic | historical (reproduced) |
| `a3_labels.py` | `python a3_labels.py > results_a3.txt` | ZL3b L*/P* | print (results_a3.txt) | n/r | `Random(i)`, 500 draws | historical |
| `a4_selfcite.py` | `python a4_selfcite.py > results_a4.txt` | ZL3b, controls | print (results_a4.txt) | minutes (Levenshtein, W=40, 12k tokens) | `Random(0)` | historical |
| `a4b_selfcite_matched.py` | `python a4b_selfcite_matched.py > results_a4b.txt` | ZL3b with (lang, illus, hand) | print (results_a4b.txt) | minutes | `Random(0)` | historical (reproduced) |
| `a5_verbose.py` | `python a5_verbose.py > results_a5.txt` | ZL3b | print (results_a5.txt) | n/r | `Random(1)` | historical |
| `a6_solver.py` | `python a6_solver.py [k]` (k = BPE merges, default 8) `> results_a6_k0.txt` | ZL3b units, latin_caesar | print (results_a6_k0.txt on disk) | long (40000 iters x 4 restarts, numpy) | `default_rng(seed)`, POS seed 3, nulls s/s+10 | historical |
| `a6b_calibrate.py` | `python a6b_calibrate.py <k> <lang>` (k in 0/8/20; lang latin/italian/german) `> results_a6b_k<k>_<lang>.txt` | ZL3b, controls | print (9 files results_a6b_k{0,8,20}_{german,italian,latin}.txt) | long | seed 5 for homophonic control | historical |
| `a7_abbrev.py` | `python a7_abbrev.py > results_a7.txt` (module-level code, no main) | ZL3b, controls | print (results_a7.txt) | seconds | deterministic | historical (reproduced) |
| `b1_docx_tests.py` | `uv run python b1_docx_tests.py` | ZL3b | `results_b1.txt` | n/r | SEED 20261017 (far line) | historical (T2 reproduced) |
| `b2_hmm_sukhotin.py` | `python b2_hmm_sukhotin.py` | ZL3b, 6 controls | `results_b2.txt` | long (20 restarts x 120 iters x 7 corpora x 2 variants) | `default_rng(seed0+r)`; `Random(1)` | historical |
| `b3_slot_claims.py` | `python b3_slot_claims.py` | ZL3b, controls, a6 pseudo null | `results_b3.txt` | n/r | one `Random(7)` shared across corpora (order-dependent) | historical (C3/C4 reproduced) |
| `b4_selfcite_sim.py` | `python b4_selfcite_sim.py` | ZL3b, dante verse | `results_b4.txt` | n/r | `Random(seed)` 1/2/3 BUT `build_neighbours` iterates sets -> **output depends on PYTHONHASHSEED** (c2 docstring); VOYNICH/CTRL rows deterministic | historical (VOYNICH/CTRL rows reproduced) |
| `b5_nmf_topics.py` | `python b5_nmf_topics.py` | ZL3b, dante, augustine, b4 generator | `results_b5.txt` | n/r (NMF 200 perms x 6 blocks) | `default_rng(0)` shared; NMF rs 0; `Random(5)` shuffle; b4 rows hash-dependent | historical (Voynich/CTRL reproduced) |
| `c1_quire_null.py` | `python c1_quire_null.py` | ZL3b, c2 generator, augustine | `results_c1.txt` | n/r (exact enumeration, MC cap 5000) | `default_rng(0)`, `Random(5)` | historical |
| `c2_section_generator.py` | `python c2_section_generator.py` | ZL3b, b4 | `results_c2.txt` | n/r (NMF per run, ~20 runs) | `Random(seed)` per run; deterministic (sorted neighbours) | **frozen** (TEAM-HANDOFF; PREREG "do not edit c2") |
| `c3_edge_coupling.py` | `python c3_edge_coupling.py` | ZL3b, b4/c2 generators, 6 controls | `results_c3.txt` | n/r | `Random(0)` null; b4 rows hash-dependent | historical (v1 edge metric source) |
| `c4_naibbe_lines.py` | `python c4_naibbe_lines.py` | `data/naibbe_zenodo_17219445/Naibbe_Cipher.xlsx` (openpyxl, values only), ZL3b skeleton | `results_c4.txt` | n/r | `Random(7)` shuffle | historical |
| `d1_edge_coupling.py` | `python d1_edge_coupling.py` | ZL3b, caesar, dante | `results_d1.txt` (via `open(..., "w")`, relative path -> must run from root) | n/r | SEED 7 | historical |
| `d2_slot_bakeoff.py` | `python d2_slot_bakeoff.py > results_d2.txt` (module-level code, prints only) | ZL3b | print; on disk `results_d2.txt` is **UTF-16 LE with CRLF** (PowerShell redirect) | n/r | SEED 42 page split | historical (reconciled by m3) |
| `d3_verbose_forward.py` | `python d3_verbose_forward.py` | latin_caesar, ZL3b line lengths | `results_d3.txt` (relative path) | n/r | SEEDS [1,2,3] | historical |
| `d5_rambling.py` | `python d5_rambling.py` | ZL3b, caesar/augustine/dante | `results_d5.txt` (relative path) | n/r | `Random(42)`, `Random(100+s)` | historical |
| `d6_ring_labels.py` | `python d6_ring_labels.py` | ZL3b all units | `results_d6.txt` (relative path) | n/r | part b `Random(12345)` | historical |
| `e1_resegment.py` | `python e1_resegment.py` | ZL3b (BASE and strict_spaces), caesar, dante | `results_e1.txt` | n/r | SEED 20261017 | historical (pre-registered; thresholds frozen in docstring) |
| `e2_edge_ablation.py` | `python e2_edge_ablation.py` | ZL3b | `results_e2.txt` | seconds | none needed | historical |
| `e3_f57v_cycle.py` | `python e3_f57v_cycle.py` | ZL3b f57v | `results_e3.txt` | seconds | none | historical (superseded by m1 period 13) |
| `f1_residual_order.py` | `python f1_residual_order.py` | ZL3b, naibbe (c4), c2, controls | `results_f1.txt` | n/r | shuffle seed 3; `Random(5)` | historical; **superseded as a meaning test by n2** |
| `f2_syllable_control.py` | `python f2_syllable_control.py` | controls (syllabified), ZL3b, naibbe | `results_f2.txt` | n/r | `Random(5)` | historical |
| `f3_flow_choice.py` | `python f3_flow_choice.py` | Naibbe workbook `encrypter` sheet, ZL3b, c2 | `results_f3.txt` | n/r | cipher seeds 1/2, gen seeds 1/2 | historical (BETA=1.5 chosen post hoc) |
| `f4_homophone_classes.py` | `python f4_homophone_classes.py` | f3 control (cached in `f4_control_cache.json`, 634 KB), ZL3b, caesar, dante | `results_f4.txt`; creates `f4_control_cache.json` if absent | n/r (KMeans x 3 seeds x 4 fracs x texts) | KMeans random_state 0/1/2; `Random(5)` null | historical (procedure frozen; no DECISION line) |
| `g0_score_filed.py` | `python g0_score_filed.py` | b4 SIMcal, c2 tuned, d3 seed 1, c4 naibbe skeleton; loads `scoreboard/score.py` by path | `results_g0.txt`; **appends** rows to `scoreboard/scoreboard.json["entrants"]` (now 9 rows) | n/r | b4 SIMcal rows hash-dependent | historical |
| `g1_edge_joint.py` | `python g1_edge_joint.py` | ZL3b, c2 lexicon | `results_g1.txt` | n/r | SEED 20261017 split; configs 9 | historical (pre-registered) |
| `h1_flow_lines.py` | `python h1_flow_lines.py` | Naibbe workbook, ZL3b skeleton | `results_h1.txt` | n/r | CIPHER_SEED 1, RULE_SEED 20261017 | historical (pre-registered) |
| `i1_power_inflation.py` | `python i1_power_inflation.py [m ...]` (default 1 2 3 5 8; filed m=1,2,3,5) | f3/f4 control | `results_i1.txt` (rewritten after each m) | long (F4 per m) | inflate `Random(0)`; cipher seed 2 | historical (finished) |
| `j1_class_recovery2.py` | `uv run python j1_class_recovery2.py` | i1 control at m=3 | `results_j1.txt` | n/r | KMeans rs 0 | historical. **Name mismatch**: TEAM-HANDOFF calls it `j1_hybrid_dist.py` (not on disk). |
| `j2_voynich_classes.py` | `uv run python j2_voynich_classes.py` | ZL3b, f4 | `results_j2.txt` | n/r | KMeans rs 0 | historical. TEAM-HANDOFF calls it `j2_voynich_hybrid.py` (not on disk). |
| `j3_collapse_solve.py` | `uv run python j3_collapse_solve.py` | j2 classes, a6 solver, score.py | `results_j3.txt` | long (a6 solve 15000 iters x 2) | solver seed 0 | historical |
| `k1_joint_producer.py` | `python k1_joint_producer.py` | Naibbe workbook, ZL3b, c2, m5 tables (recomputed) | `results_k1.txt` | n/r (NMF per row) | `default_rng(0)`, `Random(9)`, gen seeds 1/2 | historical |
| `k2_nomenclator.py` | `python k2_nomenclator.py` | ZL3b, caesar/augustine plaintext, k1 layer | `results_k2.txt` | n/r | `Random(4)` shuffle, encrypt seed | historical |
| `k3_prefix_flow.py` | `python k3_prefix_flow.py` | k2 codebook, ZL3b | `results_k3.txt` | n/r | — | historical |
| `k4_lossy_nomenclator.py` | `python k4_lossy_nomenclator.py` | k1/k2 machinery | `results_k4.txt` (filed 18:30, after this register's first pass) | n/r | codebook seed 20261017, encrypt seed 1 | filed; shared-codeword code reaches cross excess at 5.4–5.6k types, misses hand-2 NMI and line edges |
| `k5_export_entrants.py` | `python k5_export_entrants.py` | k1/k2 producers regenerated | `data/controls_synthetic/{flow_cipher_layer,flow_gen_layer,nomen_k2_x2,nomen_k2_x8}.meta.json` (present) | n/r | same seeds as k1/k2 | historical (no results file by design) |
| `l1_heldout_g1_split.py` | `python l1_heldout_g1_split.py` | ZL3b, g1, h1, k2, score.py | `results_l1.txt` | "<15 s" claimed in docstring (unverified; 200 splits + 2000 perms) | SEED 20261017; splits 1000..1199 | historical (confirmatory, done) |
| `m1_coordinates.py` | `python m1_coordinates.py` | `tools/boxes.py` over `data/external/word-coordinates/lrozanova-voynich-units-main/voynich-units-main/data/voynich-units/morphometry_voynichese/voynichese_boxes/<folio>.js` (223 folios), ZL3b | `results_m1_coordinates.txt` | n/r (N_BOOT=1000) | SEED 20261017 (+offsets) | historical (done) |
| `m3_bakeoff_reconcile.py` | `python m3_bakeoff_reconcile.py` | ZL3b, italian_dante | `results_m3_bakeoff_reconcile.txt` | n/r | 20261017 page split; d2 seed 42 reproduction | historical (done) |
| `m4_phase1_board.py` | `python m4_phase1_board.py` | ZL3b; all `data/controls/*` (corpora + corpora_ext), all `data/controls_synthetic/*.meta.json` (glob), score.py by path, metrics_new | `results_m4_phase1_board.txt` + `.json`; previous run kept as `results_m4_phase1_board.prev.txt`; `m4_run2.log` is a console log | **703 s** (printed) | 20261017; 5 lexicon shuffles | draft board (decision rule is PREREG-v2-DRAFT, not the bar) |
| `m5_line_anatomy.py` | `python m5_line_anatomy.py` | ZL3b (own IVTFF reader for `<%>` paragraph marks) | `results_m5_line_anatomy.txt` | **18.9 s** (printed) | 20261017, NREP 100 | historical (done; feeds K layer) |
| `m6_labels.py` | `python m6_labels.py` (module-level code, no main) | ZL3b all units | `results_m6_labels.txt` | n/r (NSHUF 200) | 20261017 | historical (done) |
| `m7_board_translit.py` | `python m7_board_translit.py` | `data/translit/*.meta.json` (5), score.py by path, `results_g0.txt`, scoreboard.json (read only) | `results_m7_board_translit.txt` | n/r | scorer's fixed seeds | historical (done) |
| `n1_habit_table.py` | `python n1_habit_table.py` | `data/translit/{ZL3b_eva,RF1b,IT2a}.meta.json`, f1/f3/c2/c3 | `results_n1.txt` | n/r (B=1000 bootstrap x 3 translits x 12 runs) | TABLE_SEED 20261017; seeds 1-3; `Random(3)`, `default_rng(7)` | **frozen** (prereg hash) |
| `n2_habit_fine.py` | `python n2_habit_fine.py` | same, imports n1 unchanged | `results_n2.txt` | n/r | same | **frozen** (prereg hash); current verdict source (F1 DIES) |
| `o1_direct_pixel_and_ink_spacing.py` | `python o1_direct_pixel_and_ink_spacing.py` | `.../voynich-units-main/data/direct_pixel/results_unblinded.csv`, `data/facsimile/*.jpg` (PIL) | `results_o1.txt` | "<15 s" claimed | 20261017 | filed (not in TEAM-HANDOFF prefix list) |

## 4. Control builders (`ctl_*`, `build_controls_ext.py`)

| Script | Invocation | Reads | Writes | Seed | Status |
|---|---|---|---|---|---|
| `build_controls_ext.py` | `python build_controls_ext.py` | `data/controls_raw/*` (untrusted, read as data) | `data/controls/*.txt` (15 natural + constructed; `## ` section markers) | — | live (rebuild) |
| `ctl_nomenclator.py` | `python ctl_nomenclator.py` | `data/controls/latin_macer_floridus.txt`, `latin_pliny_herbal.txt` | `data/controls_synthetic/nomen_{word,syll,lines}.txt/.meta.json/.key.json`; `results_ctl_nomenclator.txt` | 20261017 (+1, +2) | live |
| `ctl_nomen_numeric.py` | `python ctl_nomen_numeric.py` | same plaintext | `nomen_numeric{,_lines,_sylls}.*`; `results_ctl_nomen_numeric.txt` | 20261017 (+1, +2) | live |
| `ctl_naibbe.py` | `python ctl_naibbe.py` | same plaintext | `naibbe_like.txt/.meta.json/.key.json`; `results_ctl_naibbe.txt` | 20261017 (+100+k tables) | live |
| `ctl_generators.py` | `python ctl_generators.py` | ZL3b, latin_augustine | `markov1`, `rugg_grille` (+key), `latin_merged`, `lull_ars_brevis_table` sidecars; `results_ctl_generators.txt` (**overwritten by ctl_report.py** with the T-S/Schwartz/c2_best table; the file on disk is ctl_report's) | 20261017 (+10, +20) | live. Docstring says this script writes results_ctl_generators.txt; so does ctl_report.py — two writers, one file. |
| `ctl_timm_schinner.py` | `python ctl_timm_schinner.py` (needs `data/external/jre/` Java 21 — **deleted 2026-10-17 18:10**, re-download per data/external/README.md "Pruned") | `.../executable/text-generator.jar` + conf | `timm_schinner.java_output.txt`, `timm_schinner.conf.properties`, `timm_schinner.txt/.meta.json`, `timm_schinner_ownlines.meta.json` | jar seed 19 | historical (cannot rerun without JRE) |
| `ctl_schwartz.py` | `python ctl_schwartz.py` | ZL3b per hand; preprint text for citations | `schwartz_reuse.txt/.meta.json` | 20261017 | live |
| `ctl_c2_best.py` | `python ctl_c2_best.py` | `results_c2.txt` (parsed), c2 Gen | `c2_best.txt/.meta.json` (sidecar carries setting + deviation table) | c2 seeds | live |
| `ctl_report.py` | `python ctl_report.py` | `timm_schinner`, `schwartz_reuse`, `c2_best` sidecars | `results_ctl_generators.txt` | — | live |

## 5. tools/

| Tool | Invocation | Reads | Writes | Notes |
|---|---|---|---|---|
| `tools/ivtff_tokens.py` | `python -I tools/ivtff_tokens.py FILE...` | IVTFF files (untrusted) | print: pages, loci, tokens, types, top-10 | used for data/external/README counts |
| `tools/ivtff_to_meta.py` | `python -I tools/ivtff_to_meta.py IN.txt OUT.meta.json [--collapse glyph\|glyph+] [--check] [--force]` | `data/external/voynich-nu-ivtff/*.txt` | `data/translit/<name>.meta.json` (refuses to overwrite without --force) | mirrors vparse.clean; produced the 5 translit sidecars |
| `tools/boxes.py` | import (`python tools/boxes.py` runs a self-check) | voynichese `<folio>.js` box files (json.loads only), ZL3b | nothing | alignment rule in docstring (difflib on collapsed forms; ALIGNED if abs(n_zl - n_box) <= 1 and >= half matched) |
| `tools/pdf2text.py` | `python -I tools/pdf2text.py in.pdf out.txt` | PDF (pypdf from user site) | text file with `===== page n =====` markers | |
| `tools/html2text.py` | `python -I tools/html2text.py FILE...` | saved HTML | sibling `.txt` | |
| `tools/build_folio_inventory.py` | `python tools/build_folio_inventory.py` | ZL3b, boxes, `results_unblinded.csv`, facsimile, cribs | `data/folio_evidence_inventory.tsv`, `docs/FOLIO-EVIDENCE-INVENTORY.md` | not in the task list; present on disk |
| `tools/findings_graph.py` (added 2026-10-18 16:05 PDT) | `python tools/findings_graph.py check` (integrity + triangulation rules; exit 1 on error) / `render` (check, then write workflow/FINDINGS-MAP.md) / `gaps` / `sprawl` (claims c-300+ not linked, root results_*.txt whose run is unreferenced, root *.md not declared in graph docs) | `workflow/FINDINGS-GRAPH.yaml`, `.inventory/registers/CLAIMS.md`, `DECISIONS.md`, `workflow/CONSTRAINTS-MAP.md` (A-rows, dots), `TEAM-HANDOFF.md` | `workflow/FINDINGS-MAP.md` (render only; never edit by hand) | module docstring; TRIANGULATION.md; AGENTS.md (run render and sprawl before reporting). sprawl checks per run prefix, not per file |
| stub verify (command, not a script; added 2026-10-18 16:05 PDT) | `grep -v "^#" STUB \| tr -d '' \| sha256sum -c -` (Git Bash) | a `*.prereg.sha256` stub (LF, frozen before real data) | nothing | TRIANGULATION.md step 1; AGENTS.md binding rules. A failing stub or a script modified after its run makes the result `unverified: true` |

## 6. Data assets used as inputs

| Asset | Role | Format / provenance | Status |
|---|---|---|---|
| `data/ZL3b-n.txt` | the manuscript (ZL IVTFF EVA) | ascii IVTFF; sha256 bf5b6d4a... (above); 227 pages / 5385 loci / 38,255 tokens by ivtff_tokens; 207 P* pages / 34,857 tokens after vparse + `?` drop | **frozen** |
| `data/translit/{ZL3b_eva,ZL3b_glyphplus,RF1b,IT2a,GC2a}.meta.json` | other transliterations in sidecar form | top keys `source, alphabet, collapse, units ("P*"), dropped_unreadable_tokens, pages`; page keys `id, section, hand, lang, quire, lines`; 207/207/207/206/207 pages, 34,857/34,857/34,618/34,411/36,385 tokens | live (m2, m7, n1, n2) |
| `data/controls_synthetic/*.meta.json` | synthetic controls | **two sidecar dialects**: ctl_nomenclator/naibbe/generators write `{name, seed, note, pages:[{page, section, lines}]}` (no `id`; `Corpus.from_meta_json` falls back to `p0000`-style ids; `metrics_new.meta_json_pages` requires `p["id"]`; m4 uses its own `load_meta`, which accepts `id` or `page` — verified); ctl_common / k5 / c2_best write `{name, ..., pages:[{id, section, hand, lang, quire, lines}]}` (+ `illus`, `para_start` for k5). Companion `.txt` (one line per line, `## section`), `.key.json` (codebooks), `timm_schinner.conf.properties`, `timm_schinner.java_output.txt` | live |
| `data/controls/*.txt` | 25 natural / constructed controls | Gutenberg originals (6, read by `corpora.control`) and builder output with `## ` markers (read by `corpora_ext`); manifest `data/CONTROLS_MANIFEST.md` | live |
| `data/external/word-coordinates/` | word bounding boxes (223 folios), `yale_folio_to_iiif.tsv`, `yale_manifest.json`, `direct_pixel/results_unblinded.csv` | Rozanova-Temerev voynich-units repo zip + unpacked dir (untrusted) | live (m1, o1, folio inventory) |
| `data/facsimile/{f1v,f57v,f68r,f75r,f99r,f116v}.jpg` + `MANIFEST.tsv` | six Yale IIIF JPEGs with sha256 and reason | public domain per Yale catalog (manifest) | live (o1) |
| `data/naibbe_zenodo_17219445/Naibbe_Cipher.xlsx` | Greshko Naibbe workbook (sheets `analysis`, `encrypter`) | read with openpyxl values-only | live (c4, f3, f4, h1, i1, k1, l1) |
| `data/external/voynich-nu-ivtff/`, `schwartz-2026-preprint/`, `timm-schinner-generator/`, `bowern-lindemann-entropy/`, `gaskell-bowern-gibberish/`, `cribs/`, `nomenclators/`, `papers/`, `naibbe-greshko/` | reference downloads; fetch log in `data/external/README.md` | untrusted; never executed; JRE pruned | reference |
| `f4_control_cache.json` | cached F3 control for f4/i1 | 634 KB JSON | live cache (delete to regenerate) |
| `docx_extract.txt` | text of the user's .docx audited by b1-b5 | 50 KB | historical |
| `scoreboard/scoreboard.json` | v1 entrants (9 rows incl. g0 appends) + `reproduction_pass=true` + `v2` dict | JSON | live; **rewritten by score.py main()** |
| `scoreboard/entrants_g0.json` | g0 entrant list | JSON (not opened) | historical |

## 7. Scripts with no results file on disk

- `k4_lossy_nomenclator.py` -> `results_k4.txt` filed at 18:30 (was missing at this register's first pass).
- `k5_export_entrants.py`, `ctl_c2_best.py`, `ctl_schwartz.py`, `ctl_timm_schinner.py`,
  `build_controls_ext.py`, `tools/*` — write data/sidecars only (no results file by design).
- `analyze.py` writes `results/results.json` + `results/summary.md` (present), not a `results_*.txt`.
- `a1`-`a7`, `a6b`, `d2` print only; their `results_*.txt` exist via shell redirect (not in code).

## 8. Docstring vs output-file disagreements

| Script | Docstring / doc says | On disk |
|---|---|---|
| `scoreboard/run_new.py` | writes `results_m0_newmetrics.txt` | file exists but its header reads `# results_d1_newmetrics` (produced under the earlier name; run_robust accepts both) |
| `ctl_generators.py` | "Run: python ctl_generators.py" -> `results_ctl_generators.txt` | `ctl_report.py` also writes `results_ctl_generators.txt`; the on-disk file is ctl_report's table ("written ... by ctl_report.py") |
| `scoreboard/README.md`, `REPRODUCTION.md` | `score.py` "imports and re-exports" `score_v1.py` | `score.py` is byte-identical to `score_v1.py` (hash 3a7b7c3e...); the re-export is in `score_v2.py` |
| TEAM-HANDOFF "Latest Completed Rounds" | `j1_hybrid_dist.py`, `j2_voynich_hybrid.py` | files are `j1_class_recovery2.py`, `j2_voynich_classes.py` (J_RESULTS.md has the right names) |
| `scoreboard/score.py` docstring | "Run: uv run python scoreboard/score.py" | REPRODUCTION/handoff run everything scoreboard-side on system python 3.11 |
| `d1`, `d3`, `d5`, `d6` | open `results_dN.txt` by relative path | correct only when run from the project root (no `__file__` anchoring) |
| `o1_direct_pixel_and_ink_spacing.py` | prefix `o1` | TEAM-HANDOFF "Prefixes" stops at n2 |
