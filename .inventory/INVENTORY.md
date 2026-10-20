# INVENTORY — Voynich research project (value-ranked)

Built 2026-10-17 from `.inventory/runs/2026-10-17/census.jsonl` (204 files) plus 5 bulk-directory rows, 3 post-census files, the 7 registers and the census run. Machine form: `.inventory/MANIFEST.jsonl` (210 rows). Read-only; nothing moved or deleted. Claims field is empty everywhere (CLAIMS.md not present at build time).

Paths are relative to `.`. Status words: canonical = the one source for a fact; evidence = a result file; derived = generated (generator recorded); superseded = replaced, read the successor; external = downloaded.

## A — load-bearing (lose it and the project goes back a day or more)

| id | path | what it is | why it matters | next action |
|---|---|---|---|---|
| v-001 | `.inventory/registers/DECISIONS.md` | DECISIONS register | Every kill, freeze and reversal (D-001..D-042) with the evidence file; the authority for the D-list and the do-not-start rules. | Append a decision when PREREG v2 is frozen; nothing else pending. |
| v-002 | `.inventory/registers/LEARNINGS.md` | LEARNINGS register | Every verified finding (L-001..L-095) with its source file; the only place a cold agent gets the measured facts without re-reading 60 result files. | Re-verify any L-row whose source file is re-run; add L-rows for k4 and o1 if missing. |
| v-003 | `.inventory/registers/METHODS.md` | METHODS register | Definitions of every metric and null with implementation pointers; needed to read any result file or write PREREG v2. | Fill §11 (formulas with no implementation pointer) before v2 cites them. |
| v-004 | `.inventory/registers/OPEN.md` | OPEN register | The open questions (O-001..O-043) with blockers and next step; this is the queue a new session should pull from. | O-003 is closed (`results_n5.txt`). Pull O-007 and O-043 from the handoff queue; close O-035/O-036 with one command each. |
| v-005 | `.inventory/registers/REDTEAM.md` | REDTEAM register | The adversarial reading of the headline claims (circularity of the F3 table, N2 lexicon size, l1 sample effect); prevents over-citing. | Turn attack rows 1-3 into O-039-style runs; keep the table current when claims change. |
| v-006 | `.inventory/registers/TOMBSTONES.md` | TOMBSTONES register | The record of every move, deletion and restoration today; the only proof nothing was lost in the docs move and the 1.1 GB prune. | Append on every future move or deletion; no other action. |
| v-007 | `.inventory/registers/TOOLS.md` | TOOLS register | Runtime, invocation, reads/writes and determinism per script, plus the docstring-vs-output disagreements. | Resolve §8 disagreements (ctl_generators overwrite, d1/d3/d5/d6 relative paths) or record them in the scripts. |
| v-026 | `c2_section_generator.py` | Section-aware generator c2 (frozen) | Frozen generation-family baseline used by c1, c3, f1, g1, k1 and the board; its tuned setting is filed as c2_best. | Keep frozen; do not nudge its two line rules (PLAN §6 stop list). |
| v-029 | `corpora.py` | Control-corpus loader (frozen) | Frozen loader that defines the six original controls and the glyph mapping the a-series and score.py depend on. | Keep frozen; extend only through corpora_ext.py. |
| v-045 | `data/controls` | Natural-language and constructed controls (25 texts) | The language side of every control family on the board; reader corpora.py (6 originals) and corpora_ext.py (section-marked builds). | Score the board on A-only and B-only skeletons (OPEN O-010); obtain a diplomatic Latin control (O-014). |
| v-046 | `data/CONTROLS_MANIFEST.md` | Controls manifest | Provenance, licence and caveat per control corpus; without it the 15-language board cannot be defended or rebuilt. | Add rows for any Gaskell-Bowern gibberish sidecars if O-031 is run. |
| v-048 | `data/controls_synthetic` | Synthetic producers with .meta.json sidecars (42 files) | The generation and code families on the m4 board (nomen_*, markov1, rugg_grille, naibbe_like, lull table, timm_schinner*, schwartz_reuse, c2_best, flow/nomen layers); the T-S rows cannot be regenerated without the pruned JRE. | Keep; add .meta.json sidecars for the 38 Gaskell-Bowern gibberish texts so the board gets a human-gibberish family (OPEN O-031). |
| v-060 | `data/translit` | Other transliterations as sidecars (RF1b, IT2a, GC2a, ZL3b_eva, ZL3b_glyphplus) | The robustness axis: m2, m7, n1 and n2 verdicts hold on every transliteration only because these five sidecars exist. | Decide in PREREG v2 whether bands are per-alphabet (OPEN O-022). |
| v-061 | `data/ZL3b-n.txt` | ZL3b-n IVTFF transcription (frozen) | The one transcription every test reads through vparse.py; every number on disk is a function of it. | Keep frozen; v2 must state whether ZL3b EVA stays the board transliteration (OPEN O-022). |
| v-102 | `PLAN.md` | Plan: proof bar (§0) and progress check (§6) | §0 is the only definition of cracked and §6 the current family verdict and stop list; the rest is historical narrative. | Keep §0 and §6 current; mark §1-§5 historical in-place rather than adding a summary file. |
| v-104 | `PREREG.md` | PREREG v1 (frozen seven bands) | The frozen benchmark: the only bands any producer is judged against, hash-anchored in scoreboard/PREREG.sha256. | Do not edit; freeze PREREG v2 beside it with the audit's corrections (OPEN O-007). |
| v-161 | `results_i1.txt` | i1 power of homophone-class recovery | Shows F4's procedure loses the known key once the control has Voynich-like type counts, so F4's negative does not decide the cipher family (D-010). | None: route closed; cite it whenever F4/J results are read as evidence against a cipher. |
| v-171 | `results_m0_newmetrics.txt` | m0 new metric families | Source of the three signatures (char model beats word list, position lock 1.661, Moran I +0.141) and the bigram-null 0.851 that v2 must beat. | O-003 is closed by `results_n5.txt` (D-044): do not cite the three as generation signatures. Carry the 0.851 premise-refuter threshold into v2 (O-007). |
| v-178 | `results_m4_phase1_board.txt` | m4 joint board over 43 corpora | The file behind the two anomalies no control family reaches (first-glyph line-edge JSD 0.176, word-boundary coupling 0.181) and the no-family-in verdict. | Do not re-run; use as the target list for the j producer once v2 is frozen (OPEN O-008). |
| v-179 | `results_m5_line_anatomy.txt` | m5 line-initial / line-final anatomy | Says what the universal line-edge failure is (paragraph-initial gallows, y/d/t/s starts, m/g ends, d-drift) and so defines the four draws any producer needs. | Give the j producer and the edge-table generator m5's four draws (OPEN O-008, O-038). |
| v-183 | `results_n2.txt` | n2 fine habit grid (F1 kill) | Pre-registered DIES on all three transliterations: a 4 % word-pair habit fakes the F1 residual, so transferable word order is withdrawn as content evidence (D-032). | Rerun at p=0.04 with a 7k-type lexicon to answer the red-team objection that the kill is shown only for a small-lexicon generator (OPEN O-039). |
| v-188 | `scoreboard/metrics_new.py` | m0 metric families | Implements the lexicon-growth, slot, MI-profile, bake-off and signature metrics that produced the two robust anomalies on the m4 board. | The three signatures were scored on cipher and generator output in `results_n5.txt` (D-044). Do not rerun O-003. |
| v-195 | `scoreboard/score.py` | Frozen v1 scorer | The hash-frozen implementation of the seven v1 bands; g0/g1/h1/l1/m4/m7 all load it by path. | Keep byte-frozen (hash 3a7b7c3e...); never run main() casually since it rewrites scoreboard/scoreboard.json. |
| v-200 | `TEAM-HANDOFF.md` | The map | The only file that says where each number lives, what was decided and what not to start; result files win over it on disagreement. | Add the n2 withdrawal of F1/F3/K residuals to every tier entry that cites them; update Prefixes to n3/o2/p (D-020). |
| v-210 | `vparse.py` | ZL3b parser (frozen) | Frozen reader of ZL3b-n.txt; defines which units count as text and how tokens are cut, so every count depends on it. | Keep frozen; tests/test_voynich.py guards it. |

## B — evidence and scaffolding behind an A row

| id | path / group | what it is | why it matters / why not | next action |
|---|---|---|---|---|
| 12 rows, v-116..v-131 (non-contiguous; see MANIFEST) | results_a1, a2, a4b, a6b_k{0,8,20}_{german,italian,latin} (9) | a-series evidence (profile, line position, matched self-citation, letter-solver calibration) | Band sources for PREREG v1 and the letter-solver kill (D-005) | none; reproduced by tests/test_score.py |
| v-133 v-135 v-136 v-137 | results_b1, b3, b4, b5 | b-series evidence (docx checks, slot claims, SIMcal, NMF) | Cited by D-002/D-036/D-037/D-041; b5 is cited only to say c1 replaces it | none |
| v-138..v-141 | results_c1..c4 | c-series evidence (quire null, c2 grid, edge coupling, Naibbe lines) | c1 corrects the topic claim; c3 is the cross_excess band source; c2/c4 feed the stop list | none |
| v-142..v-145 | results_ctl_generators, ctl_naibbe, ctl_nomen_numeric, ctl_nomenclator | profiles of the synthetic controls | The codebook kill (h2 3.2-3.7) and the T-S / Schwartz edge figures (D-011) | none |
| v-146 v-147 v-148 v-150 | results_d1, d2, d3, d6 | d-series evidence | d2 holds the 10.728 figure m3 corrected; d6 is the f57v kill; d1/d3 cited by D-033 | none; d2 is UTF-16 LE |
| v-151 v-153 | results_e1, e3 | e-series evidence | e1 inconclusive resegmentation; e3's 17-token cut superseded by m1 | none |
| v-154..v-157 | results_f1..f4 | f-series evidence | f1/f3 residual rows withdrawn by n2 (D-032); f2 syllabary verdict; f4 closed by i1 | cite only with the n2 caveat |
| v-158 v-159 v-160 v-162 v-164 | results_g0, g1, h1, j1, j3 | joint-board and J-series evidence | No joint pass (D-007); J kill (D-023) | none |
| v-166 v-168 | results_k2, k4 | K-series evidence (k4 post-census) | k4 reversed the type-budget reading (D-025) | OPEN O-040 extends k4 |
| v-169 | results_l1 | held-out split diagnostic | Manuscript passes all 7 bands on G1's pages; leaf locality | bifolio null (O-004) |
| v-170 v-173 v-176 | results_m0_newmetrics.json, m2_robustness.json, m4_phase1_board.json | machine forms of m0/m2/m4 | per-corpus values behind the text files; m4's are the v2 range source |  |
| v-172 v-174 v-175 v-180 v-181 | results_m1, m2, m3, m6, m7 | m-series evidence | Column-copying kill, robustness, bar correction, labels register, bands on other transliterations | none |
| v-182 v-184 | results_n1, o1 | n1 coarse habit grid; o1 ink geometry | n1 is the predecessor of the F1 kill; o1 refutes box-interpolated spacing | none |
| 12 rows, v-185..v-198 (non-contiguous; see MANIFEST) | scoreboard/* (score_v2, corpus, run*, README, REPRODUCTION, PREREG.sha256, scoreboard.json, entrants_g0.json, score_v1.py) | the v2 scorer, loaders, CLIs and records | Everything the board runs on apart from the frozen score.py and metrics_new.py; score_v1.py is a by-design byte duplicate of score.py | resolve the TOOLS §8 docstring disagreements |
| v-105 v-201 v-202 v-209 | tests/*, pyproject.toml, uv.lock | tests and runtime | 18 exact reproductions guard the scorer; runtime split is OPEN O-034/O-035 |  |
| v-203..v-208 | tools/* (boxes, build_folio_inventory, html2text, ivtff_to_meta, ivtff_tokens, pdf2text) | python -I readers for untrusted downloads | The only sanctioned way to read data/external (D-022); ivtff_tokens.py's secret flag is a filename false positive |  |
| v-024 v-030 v-032 v-033 v-037 v-038 v-039 | ctl_common, ctl_generators, ctl_report, ctl_schwartz, ctl_timm_schinner, build_controls_ext, corpora_ext | control builders and loaders | Regenerate data/controls and the synthetic sidecars; ctl_timm_schinner needs the pruned JRE |  |
| 36 rows, v-009..v-101 (non-contiguous; see MANIFEST) | a1, a2, a4, a4b, a7, b3, b4, c1, c3, c4, d1, d2, d3, e1, f1, f2, f3, g0, g1, h1, i1, k1..k5, l1, m1, m3..m7, n1, n2, o1 scripts | live experiment scripts | Method of record for the B-list evidence files; n1/n2 are hash pre-registered | none; use prefixes n3/o2/p for new work |
| v-047 v-049 | data/external, data/controls_raw | untrusted downloads (1,592 + 304 files) | Sources of the translit sidecars, word boxes, cribs, papers; read only via tools/ | OPEN O-031 (gibberish sidecars), O-037 (edge-coupling definition) |
| 9 rows, v-050..v-059 (non-contiguous; see MANIFEST) | data/facsimile/*.jpg + MANIFEST.tsv, data/naibbe_zenodo_17219445/* | six page images; the Naibbe workbook and supplement | o1 and the f57v glyph check read the images; the workbook is the known-key positive control | OPEN O-021 glyph check on f57v |
| v-057 v-062 v-063 v-065 v-199 | docs/AUDIT, docs/SCOUTED-EXTERNAL-HUBS, docs/FOLIO-EVIDENCE-INVENTORY (+tsv), SCOUT-EXTERNAL.md | audit, scouting and folio inventory | The audit rebuilt the queue; the folio inventory is the lookup for any folio-named measurement | OPEN O-032 TheVoynich.org diff |
| v-008 v-082 v-088 v-093 v-097 v-099 v-103 v-106 | J_RESULTS, K_RESULTS, m4_run2.log, n1/n2 prereg hashes, PREREG-v2-DRAFT, README.md, .inventory/runs | round logs, pre-registration hashes, the v2 draft, entry point, census | Logs narrate B-list numbers; the hashes prove n1/n2 were fixed in advance; v2 draft is the next freeze | freeze v2 (O-007) |

## C — archive candidates (historic; stop loading)

| id | path / group | what it is | why it matters / why not | next action |
|---|---|---|---|---|
| v-064 | docs/rounds (11 files) | closed round logs | Contradict their result files in places (audit); LEARNINGS.md replaces them | stop loading |
| 11 rows, v-118..v-167 (non-contiguous; see MANIFEST) | results_a3, a4, a5, a6_k0, a7, b2, d5, e2, j2, k1, k3 | evidence no decision cites | Answered questions with no downstream use; keep for the record | stop loading |
| v-177 | results_m4_phase1_board.prev.txt | byte-identical backup of the m4 board | duplicate cluster; main file is canonical evidence | drop on the user's word |
| v-014 v-018 v-020 v-043 v-068 | analyze.py, a5, b2, d5, e2 scripts | scripts whose results are C | Still runnable; nothing cites their output | stop loading |
| v-114..v-115 | results/results.json, results/summary.md | analyze.py output | historical a-series battery | stop loading |
| v-107..v-113 | reports/*.md, research_notes/* (6) | literature review and its notes | Drove D-003; the map lists them historical | stop loading; cite LEARNINGS |
| v-066 | docx_extract.txt | text of the user's .docx | b1 checks are filed; the extract is no longer needed | stop loading |

## D — do not resume (question closed)

| id | path | what it is | why killed | successor |
|---|---|---|---|---|
| v-011 | `a3_labels.py` | a3 labels-in-page permutation | Another label-in-page permutation is on the do-not-run list (D-005); m6 characterised labels as a register and replaced it. | results_m6_labels.txt |
| v-015 | `a6_solver.py` | a6 letter-substitution solver | Latin/Italian/German letter solvers with spaces kept land at the null (a6b calibration); closed by D-005/D-012/D-017. | results_a6b_*.txt; OPEN O-025 (abjad/transposition) is a different design |
| v-016 | `a6b_calibrate.py` | a6b solver calibration on L/I/G | Showed the solver cannot separate language from null at k=0/8/20; the letter-solver family is on the do-not-start list. | results_a6b_*.txt |
| v-019 | `b1_docx_tests.py` | b1 .docx test battery (T2 column copying by word index) | Its column-copying test indexed words, which m1 replaced with real coordinates; the other b1 checks are filed in results_b1.txt and need no rerun (D-041). | results_m1_coordinates.txt |
| v-023 | `b5_nmf_topics.py` | b5 NMF topics | Topic NMF as a discriminator is closed (D-012, D-034); its Augustine control included the TOC; c1's quire null is the row to cite (D-037). | c1_quire_null.py / results_c1.txt |
| v-031 | `ctl_c2_best.py` | c2 line-rule tuning selector | Parameter nudges on c2's two line rules are closed (D-012, D-017); c2_best is filed as a sidecar and should not be re-tuned. | data/controls_synthetic/c2_best.* |
| v-034 | `ctl_naibbe.py` | ctl Naibbe-like randomiser | Naibbe as-is is closed (D-012); c4/h1/f3 already use the real workbook; naibbe_like sidecar is filed. | data/controls_synthetic/naibbe_like.* |
| v-035 | `ctl_nomen_numeric.py` | ctl positional-numeral codebook builder | Numeral codebooks closed with the random-core ones (D-012); sidecars filed. | data/controls_synthetic/nomen_numeric* |
| v-036 | `ctl_nomenclator.py` | ctl random-core nomenclator builder | Random-core codebooks sit at h2 3.2-3.7 against 2.1 and are closed (D-011/D-012); the nomen_* sidecars are filed and stay on the board. | data/controls_synthetic/nomen_*; k4_lossy_nomenclator.py |
| v-044 | `d6_ring_labels.py` | d6 f57v ring labels | f57v as a period key is closed (D-012); the box-based period reading in results_m1_coordinates.txt replaces the 17-token cut. | results_m1_coordinates.txt |
| v-069 | `e3_f57v_cycle.py` | e3 f57v cycle | Same closed question as d6; the 17-token cut is superseded by the angle-ordered box reading. | results_m1_coordinates.txt |
| v-073 | `f4_control_cache.json` | f4 control cache (634 KB) | Cache for the closed f4/i1 route; regenerable, do not load. | results_i1.txt |
| v-074 | `f4_homophone_classes.py` | f4 homophone-class recovery | Homophone-class recovery is closed (D-010): i1 showed the procedure has no power at Voynich-like type counts; rerun forbidden. | results_i1.txt |
| v-079 | `j1_class_recovery2.py` | j1 class recovery with spelling features | J-series killed (D-023): passing the m=3 gate needed spelling features, which is the circularity the gate forbids. | results_j1.txt |
| v-080 | `j2_voynich_classes.py` | j2 Voynich classes | Found predictive classes that are morphology, not homophones (J_RESULTS); route retired with D-023. | results_j2.txt |
| v-081 | `j3_collapse_solve.py` | j3 collapse-and-solve | Collapsing j2 classes made the solver worse than the pseudo-Voynich null; the kill that closed the J series. | results_j3.txt |

## Counts

210 rows: A 25 · B 141 · C 28 · D 16. Status: canonical 88 · derived 12 · evidence 83 · external 10 · superseded 17.

## D-list rationale

Every D row is a script whose question DECISIONS.md records as closed, with the closing evidence on disk and a successor row named: the a6/a6b Latin-Italian-German letter solvers (D-005, D-012, D-017: they land at the null and the family is on the do-not-start list), b5 topic NMF (D-012, D-034, D-037: c1's quire null is the row to cite), the d6/e3 f57v period (D-012: m1's box reading replaces the 17-token cut), f4 and the j1-j3 class recovery with its cache (D-010, D-023: i1 showed no power at Voynich-like type counts and the J gate was passed only with spelling features), a3 labels-in-page (D-005: m6 characterised labels instead), b1's T2 column copying by word index (m1 used real coordinates), the nomen_* codebook builders and the Naibbe-like randomiser (D-011, D-012: their sidecars stay on the board as the code family, the builders need no rerun), and ctl_c2_best's line-rule tuning (D-012, D-017: no parameter nudges). Their result files are kept as B or C evidence; nothing is deleted. Reopening any of them requires a new assumption written as a decision first, and OPEN O-024/O-025 (transposition, nulls, abjad) are different designs, not reruns.

## Notes for the reader

- Derived rows name their generator in `produced_by`; the bulk rows (`data/external`, `data/controls`, `data/controls_raw`, `data/controls_synthetic`, `data/translit`, `docs/rounds`) describe what is inside and the reader to use in `notes`.
- `tools/ivtff_tokens.py` was flagged secret-suspect by the census because its filename contains `token` (census.py `SECRET_HINTS` path-substring rule); the file was opened and holds only IVTFF tag regexes, so its class is `code`.
- Two duplicate clusters: `results_m4_phase1_board.prev.txt` (backup, C) and `scoreboard/score_v1.py` (by-design copy of the frozen scorer, B derived).
- `results_k4.txt`, `docs/FOLIO-EVIDENCE-INVENTORY.md` and `data/folio_evidence_inventory.tsv` were written 18:28-18:30, after the 18:27 census; they are rowed from the map's description and a direct open.
