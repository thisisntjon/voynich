# Sprawl audit, voynich repo (read-only)

Stamped 2026-10-18 15:56 PDT (clock read with `date`). Auditor: subagent of voynich-08. Nothing in the repo was changed.

## 0. What `findings_graph.py sprawl` checks (tools/findings_graph.py:275-309)
1. claims c-300+ not linked to a finding; 2. root results_*.txt whose RUN PREFIX appears in none of CLAIMS/graph/TEAM-HANDOFF; 3. root *.md not declared in graph docs.
Today it prints 0 / 0 / 0. What it misses: coverage per file (it checks per run); results in runs/ and data/; .md files below the root; stale docs; numbers that disagree between docs; run-id collisions; how fresh the registers are; refs that point outside the repo.

## 1. Synthesis/status/summary docs outside the canonical homes
Declared in graph docs (FINDINGS-GRAPH.yaml:1067-1092): 6 canonical root docs, 13 superseded root docs (each has an in-file marker in its first 6 lines), 3 historical PREREGs, 8 workflow_views (only 2 of them in workflow/research/).

NOT declared anywhere in graph docs (status/synthesis-like):
- workflow/research/strategy-2026-10-17.md (README.md:13 calls it "What we do next"; written 2026-10-17 23:24)
- workflow/research/next-steps-gaps-2026-10-18.md (12:08; F-34 "CORROBORATED" at :29; line-held H-14 at :46, :86)
- workflow/research/next-steps-redteam-2026-10-18.md (12:11; line-held x3; referenced by nothing)
- workflow/research/next-steps-external-prediction-2026-10-18.md (12:11; referenced by nothing)
- workflow/research/learnings-audit-2026-10-18.md (AGENTS.md makes its section 3 "top 10 method lessons" binding, so it is a second home for methods beside METHODS.md)
- 26 more workflow/research files: A-lead-harvest, B-prior-art, C-constraints, D-stress-test, E-dependencies, phase-*, prereg-v2-freeze, public-baseline, replication-roach, support-phase1-audit
- workflow/phases/phase-1..3.md
- .inventory/INDEX.md (2026-10-17 21:09; README.md:15 start-here #5) and .inventory/INVENTORY.md (value-ranked, 2026-10-17): two more "maps" beside root INVENTORY.md
- docs/AUDIT-2026-10-17.md, docs/FOLIO-EVIDENCE-INVENTORY.md, docs/SCOUTED-EXTERNAL-HUBS-2026-10-17.md, docs/rounds/* (10 files; TEAM-HANDOFF.md:333 calls them historical, the graph does not)
- results/summary.md (analyze.py battery, 2026-10-17 14:23), reports/, research_notes/ (10), incoming/ten-theories/ (exploratory per D-048), codex_lab/reviews/s60_s63_evidence_audit_2026-10-18.md
- runs/*/README.md (10) and runs/s103/LEAD-READING.md

Workflow docs with no in-file supersession marker: synthesis-2026-10-18.md, SYNTHESIS.md, strategy-2026-10-17.md, FINDINGS-REPORT.md, CONSTRAINTS-MAP.md, .inventory/INDEX.md.

Stale against FINDINGS-MAP / LEARNINGS / DECISIONS (last write, then what it is missing):
- README.md (00:55; status line 2026-10-17 23:33). Start-here order: FINDINGS-REPORT, CONSTRAINTS-MAP, strategy-2026-10-17, PLAN, .inventory/INDEX, HANDOFF. It never names FINDINGS-MAP or D-066. Declared canonical.
- workflow/FINDINGS-REPORT.md (13:23): no D-067, D-068, r9-r11 or s101. :272 line-held table reproduces the prefix memory; :277 s93 "reaches the core signature"; :277/:281 s94 and s96 running.
- workflow/CONSTRAINTS-MAP.md (12:10): :227 F-34 CORROBORATED; :154 (dot 21) states the F-23 exclusion with no caveat; :123 A14 not flipped; :267-268 s94 and s96 running. Declared the "canonical narrative" in graph docs.
- TEAM-HANDOFF.md (canonical; written 15:48, but these sections were not updated): :177-181 "Next (single queue; rebuilt 19:35)" names SYNTHESIS.md as the adopted sequence; :173-175 "In flight" points to Phase 1; :208 s94/s96 "Running"; :306-325 a second Hypothesis Ledger; :325 F-23, F-30, F-31, F-34 and F-39 "all TRIANGULATED", with F-34 "discharging X-01"; :348 s94 "running, no result".
- workflow/PLAN.md:4 "Current stage" line (s103 running, s105 next, roach r6-r8): contradicted by the plan's own log at :239-256.
- FINDINGS-GRAPH.yaml:32 H-14 status "drifting affix state remains open (r9)", against L-217 (r9: drifting table 0/15). :321 still counts F-34 as "for H-14, moderate".
- FINDINGS-MAP section 1: F-23(s) and F-30(s) carry full strong weight against H-07 and H-05, with no * halving, although D-068 calls them uninformative. They are marked "at-risk" only in section 2.
- INVENTORY.md (12:18): lists workflow/comms as 11 files (it now has 16). "Read these first" lists the superseded root PLAN.md and leaves out FINDINGS-MAP and the registers.
- .inventory/registers/METHODS.md (2026-10-17 19:37) and TOOLS.md (18:41): about 20 h without an update. LOQO, Zattera, Seg_Affix2, matched-K and findings_graph.py have 0 hits in METHODS and TOOLS (LEARNINGS has LOQO x16, Zattera x8). None of the 16 tools/*.py files (incl. findings_graph.py and the s103/s105 fetchers) is in TOOLS.

## 2. Concrete disagreements (file:line)
1. F-34 grade: TEAM-HANDOFF.md:325 TRIANGULATED + "discharging X-01" | CONSTRAINTS-MAP.md:227 CORROBORATED | next-steps-gaps-2026-10-18.md:29 CORROBORATED | FINDINGS-MAP.md:88 CONTESTED, X-01 at risk (D-067, L-212).
2. F-23/F-30 exclusions: TEAM-HANDOFF.md:325 "all TRIANGULATED"; CONSTRAINTS-MAP.md:154 flat; FINDINGS-MAP.md section 1 (H-05 row F-30(s); H-07 row F-23(s)) full weight | DECISIONS.md:74 D-068, LEARNINGS.md:268 L-224, CLAIMS c-454 (planted recovery 0-4/15, UNINFORMATIVE).
3. H-14 drifting state: FINDINGS-GRAPH.yaml:32 "drifting affix state remains open (r9)" | LEARNINGS.md:261 L-217 (drifting table 0/15); PLAN.md:250 (D-067 amended to "multi-scale state").
4. s94: TEAM-HANDOFF.md:208 and :348 running; CONSTRAINTS-MAP.md:267 running; FINDINGS-REPORT.md:277 running | FINDINGS-GRAPH.yaml:1139 P-26 rejected at fixture; L-221; PLAN.md:4.
5. s96: TEAM-HANDOFF.md:208 "still being written"; CONSTRAINTS-MAP.md:268 running; FINDINGS-REPORT.md:281 running | FINDINGS-GRAPH.yaml:1141 rejected (D-065).
6. s93: FINDINGS-REPORT.md:277 "reaches the core signature" with no caveat | FINDINGS-GRAPH.yaml:1138 rejected (D-064); CONSTRAINTS-MAP.md:240 carries the bracketed rejection.
7. Within-line Moran I: CONSTRAINTS-MAP.md:156 "0.156" | CONSTRAINTS-MAP.md:74, FINDINGS-REPORT.md:42, FINDINGS-MAP.md:247 and CLAIMS c-328 (0.157244).
8. A14 core order: CONSTRAINTS-MAP.md:123 "Different cores do not follow each other in an ordered way" and synthesis-2026-10-18.md:27,39 | CONSTRAINTS-MAP.md:25 FLIPPED; CLAIMS.md:532 c-419 (+0.0452 at K=100).
9. s101 identity: LEARNINGS.md:242 L-199 "s101 tail, SigLIP" (this is Daybreak db-s101; the ref is in the yonichmanuscript tree) | LEARNINGS.md:268 L-224, CLAIMS c-454 and D-068 "S101 (Argon) LOQO power audit".
10. Current stage: PLAN.md:4 (s103 running, s105 next, roach r6-r8) | PLAN.md:239-256 (s103 INCONCLUSIVE 13:23, r9/r10 filed 14:06, D-068 at 15:43); OPEN.md O-062/O-063 (s105 HOLD, s108 not assessable).
11. Adopted sequence: TEAM-HANDOFF.md:178-180 "workflow/research/SYNTHESIS.md is the adopted sequence" | FINDINGS-GRAPH.yaml:1092 "phase-0 investigation synthesis (historical)".
12. F-12 impl line: FINDINGS-MAP.md:343 (+0.045 at K=100 headline) vs :349, where roach r4 is "null at K=100" yet filed as agrees:true. This is a judgment call; unverified whether the lead audit accepted it.
13. Start path: README.md:9-16 (FINDINGS-REPORT first, no FINDINGS-MAP) | AGENTS.md "Start here" (PLAN, FINDINGS-MAP, D-066, LEARNINGS, HANDOFF).

## 3. Results files vs claims
- Root results_*.txt: 352. Exact filename missing from CLAIMS.md: 180. Missing from CLAIMS, the graph and TEAM-HANDOFF: 171 (sprawl lets them through because it matches on run prefix).
  Families: n6_* 28, n7_* (ent/gib/voy/IT2a/RF1b) about 85, s18_cremma_* 48, s17_* 10, s20_* 6, plus the singles below.
  Singles that matter:
  - results_s93_frozen1.txt, results_s96_frozen1_1055.txt and results_s96_frozen2_1103.txt: the admissible frozen runs behind D-064/D-065, cited nowhere.
  - results_s89.txt: the pre-amend run; graph P-21 cites only s89_amend1.
  - results_p4d1_core_order.run1-crashed.txt, results_a6b_k20_latin.txt.
  - results_m4_phase1_board.prev.txt: cited in TOOLS only.
- Root results_*.json: 171. Sprawl does not check them at all.
- runs/ results files: 28. 16 have no CLAIMS row: all the roach fixture files (incl. fixture revisions r8/r9/r10/r11 rev0/rev1), the runs/s45 dry run and the runs/s82 crashed run.
- Claims pointing to missing files: 0 of the 183 distinct result filenames cited. Graph refs: 100 distinct, 0 missing. 7 graph refs, and 20 distinct register/graph paths in all, point outside the repo to lab (Daybreak's tree); all exist today.

## 4. Run-id collisions
Inside the lead tree (same prefix, different scripts):
- s63: s63_parisel_switch_within_hand.py and s63_rare_core_boundary_and_subglyph.py both reference results_s63.txt (the file now holds the rare-core run). A REAL collision on one output path.
- s66: s66_parisel_switch_within_hand.py and s66_scribal_corrections_and_quire_seams.py both reference results_s66.txt (the file holds the scribal-corrections run). A REAL collision; the Parisel switch result has no file of its own. Neither parisel script has a stub.
- Shared prefix, distinct outputs: s34, s35, s50 (s50_solver.py has no stub), s51, s52, s53, s54, n6 (n6_ab_split, n6_habit7k_glyph), p1 (p1_bifolio_null, p1_order_sensitivity). s33 was taken by a peer (per the s35 header).

Lead vs Daybreak db-sNN:
- s88-s99 (11 ids) are mapped at TEAM-HANDOFF.md:337-352.
- Unmapped: s101 (L-199 cites db-s101 with no prefix), s104, s105, s106 (graph :892 db-s106 vs lead s106 X2 HOLD), s109 and s111 (lead scripts created 15:54 today vs graph :903-912 db-s109/db-s111).
- db-s114, db-s118 and db-s120 have no lead twin yet.

Counts: 2 real output collisions (s63, s66); 9 shared-prefix script pairs; 17 cross-tree collisions (11 mapped + 6 unmapped).

## 5. Root clutter (non-recursive: 844 files + 14 dirs)
184 .py, 352 results_*.txt, 171 results_*.json, 107 *.prereg.sha256 stubs, 22 .md, 8 other (uv.lock, pyproject.toml, docx_extract.txt, register_extract.txt, m4_run2.log, f4_control_cache.json, s15_ranges.json, n7_gibberish_ranges.json).
s-series scripts with no stub at the root or in runs/: 6 (s109 and s111 are in flight; s50_solver, the s63/s66 parisel scripts, s94).

Proposed grouping, no moves:
- Generate a ROOT-INDEX section in INVENTORY (or in workflow/curation/FILES.md) keyed by series:
  - legacy a-r series (about 80 scripts, superseded);
  - s1-s57 (phases 1-4);
  - s58-s99 (phases 5-6);
  - s100+ (phase 7).
- List each results sidecar family (n6_*, n7_*, s17_*, s18_cremma_*, s20_*) as one row that points at its parent claim, and the json mirrors as one row.
- Declare the sidecar families under a graph docs key like orphan_results_ok (e.g. sidecars: {pattern: parent_claim}) so sprawl can check per file.

## 6. Data folders (data/*, 14 dirs)
| folder | files | README | refs |
|---|---|---|---|
| controls | 25 | no | 44 py, 185 results (covered by data/CONTROLS_MANIFEST.md) |
| controls_gibberish | 39 | no | not in CONTROLS_MANIFEST |
| controls_raw | 304 (33 MB) | no | only build_controls_ext.py; 0 results |
| controls_synthetic | 42 | no | manifest x4 |
| facsimile | 7 | no | not in manifest |
| naibbe_zenodo_17219445 | 2 | no | not in manifest |
| translit | 5 | no | 29 py, 78 results; not in manifest |
| controls_period, controls_realline, controls_tabular, controls_tabular_ruled, external, herbals_alchemical, herbals_period | - | yes | no doc refs for herbals_period and controls_period |

- No README: 7.
- Not referenced by any result: 1 (controls_raw, the raw inputs to controls/).
- Neither in CONTROLS_MANIFEST nor with a README: 4 (controls_gibberish, facsimile, naibbe_zenodo_17219445, translit).

## 7. Knowledge only in runs/ or comms
- runs/roach-r10/README.md:11: for an exchangeable line pool the within-line R_w baseline is invariant (R=1 at every d), so the baseline was moved to within-page. This bears on the R_within(1)>1 part of F-40. "exchangeable" has 0 hits in the registers, graph, PLAN and HANDOFF.
- runs/roach-r9/README.md:9-11 and results_fixture_run1_rev0.txt: the rev0 fixture fitted a drift scale of 10 against a planted 5, so there was one revision before the freeze. Not in L-217.
- runs/roach-r10/README.md:9-10: copy-recent also matched the planted pool (8/15) on two fixture runs before revision 2. Not in L-218.
- runs/roach-r6..r11 README.md: no register, graph, PLAN or HANDOFF references them (r3-r5 are referenced).
- workflow/comms/...TO-ROACH-VOYNICH91-QUEUE-20261018T202417Z.md:
  - roach worker cap of 12, the roach-offload-* folder rule, the 15-minute <team-comms> poll, and the r12 brief;
  - r12 is missing from TEAM-HANDOFF, PLAN and DECISIONS (graph P-41 only).
- workflow/comms/...ACK-DAYBREAK-S100-S106-AUDITS-...md item 2: the s104 fixture/stub/result timing (13:27:43 / 13:28:31 / 13:28:52 / 13:29:17), with the 13:28 edit unverified. The message says this is recorded on c-447; I did not check that c-447 carries all four times (unverified).
- workflow/comms has 16 files, against INVENTORY.md's 11. Registers reach comms only through Evidence lines.
