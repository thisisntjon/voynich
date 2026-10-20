# Phase 8 angle: source of truth (where each kind of fact lives, and where it should live)

Date: 2026-10-19 09:33 PDT (from `date`). Author: Phase 8 source-of-truth agent. Read-only investigation; this is the only file written.
Brief: scratchpad `p8brief.txt` (binding). Scope: the voynich repo plus the outside homes it points at (<team-comms>, codex_lab, <home>/voynich-backups).

## 1. What I found

### 1.1 Homes per fact kind today

| Fact kind | Declared home (who declares it) | Other homes holding the same kind of fact (found) |
|---|---|---|
| Claims and measurements | `.inventory/registers/CLAIMS.md`, c-ids (TRIANGULATION.md table; README "One home per thing") | `results_*.txt` (365 .txt + 171 .json at root; "result file wins", AGENTS.md); TEAM-HANDOFF.md "Where a number lives" (AGENTS.md calls TEAM-HANDOFF "the measurement map"); VKB `claims` / `measurements` (derived); `data/external/library/unchecked_claims.tsv` (465 data rows, outside claims, not in VKB); `.inventory/INDEX.md` (says 332 claims) |
| Learnings | `LEARNINGS.md`, L-ids | VKB `learnings` (derived); `workflow/research/learnings-audit-2026-10-18.md` (top-10 method lessons, binding per AGENTS.md) |
| Decisions | `DECISIONS.md`, D-ids | TEAM-HANDOFF top section "2026-10-19 meaning-recovery pivot (D-072)"; <team-comms> comms (e.g. `<team-comms>`, cited by D-072); VKB `decisions` |
| Open questions / queue | `OPEN.md`, O-ids | D-066 (a decision row used as "single standing next-question entry", AGENTS.md); graph `pending:`; PLAN.md phase log; TEAM-HANDOFF "Next" (marked superseded); `data/external/library/GAPS.md`; VKB `sources.gap_note` |
| Findings, hypotheses, assumptions | `workflow/FINDINGS-GRAPH.yaml` (F-/H-/X-/P-); `FINDINGS-MAP.md` generated | `workflow/FINDINGS-MAP_X01-FIX-2026-10-19.md` (hand-edited copy of the generated map, disagrees, see 1.3); `workflow/CONSTRAINTS-MAP.md` (A-rows, a second taxonomy, declared canonical narrative); `workflow/FINDINGS-REPORT.md` (self-marked superseded but listed as a live view in the graph); TEAM-HANDOFF "Hypothesis Ledger" (marked superseded); PLAN.md "Assumption registry" (U-assumptions; TRIANGULATION says the assumption registry is PLAN.md while the X-ids live in the graph); `data/external/library/catalogue_to_findings.tsv` (270 rows); outside status files (VKB lists 18 `status-file` rows in <team-comms>, codex_lab, Argon brain dirs, e.g. `VOYNICH-EVIDENCE-INDEX.md`, `VOYNICH_MASTER_FINDINGS_INDEX.md`) |
| Runs and run ids | TEAM-HANDOFF.md "Prefixes" + free-text claim paragraphs + "Run-id alias map" | PLAN.md prefix table (16 rows, s1-s28 era only); `*.prereg.sha256` stubs (165 found); `runs/<id>/`; VKB `runs` (250 rows, built by parsing TEAM-HANDOFF prose plus file globs); codex_lab/experiments (Daybreak db-ids) |
| Page facts (published) | `data/external/page-facts/<pull>/facts.tsv` -> VKB `page_facts` (L-355, D-066 dd) | `page-facts/eyecheck/pairs.tsv` (not loaded: build globs only `*/facts.tsv`); `docs/FOLIO-EVIDENCE-INVENTORY.md` + `data/folio_evidence_inventory.tsv` (2026-10-17); VKB `folio_features` (computed) |
| External items and intake | VKB `external_items` (87 rows) | The rows are Python literals in `tools/vkb/world.py` (~lines 898-1003) plus audit snapshots in `.inventory/runs/2026-10-18/audit-*.md`; `data/external/README.md` fetch log; `data/external/library/catalogue_v2.tsv` (2,979 rows) and `primary_sources.tsv` (59), not read by the VKB; VKB `sources` (97 rows) from a scratchpad audit snapshot |
| Team comms | <team-comms> (426 file names containing "voynich", any case) via <team-comms> | `workflow/comms/` 28 files, 27 byte-identical to <team-comms> copies, 1 repo-only; codex_lab; roach bridge `<local-path>` |
| Methods | `METHODS.md` (stamped 2026-10-17; last mtime 10-18 16:06) | TRIANGULATION.md rules; learnings-audit top-10; `tools/vkb/README.md` canonical statistic names and folio-feature formulas; script docstrings |
| Tools | `TOOLS.md` (stamped 2026-10-17) | `workflow/curation/FILES.md` (curate, one line per file); script docstrings; `tools/vkb/README.md`. TOOLS.md names 85 scripts; 174 of the 247 scripts at root + `tools/` are not in it |
| Plan and status | `workflow/PLAN.md` (`Current stage:` line + phase log) | TEAM-HANDOFF top two sections (live pivot and intake status); README.md; root `PLAN.md` (graph: superseded, §0 still the proof bar); D-066; outside status files (above) |
| Inventory | root `INVENTORY.md` (curate-generated; AGENTS.md "read first") | `.inventory/INDEX.md` (graph: historical, but the file carries no banner and README's superseded start-here table still lists it); `.inventory/INVENTORY.md` (historical); `workflow/curation/*`; `.inventory/MANIFEST.jsonl`; a full register snapshot in `<home>/voynich-backups/2026-10-18_2214/.inventory/` |

### 1.2 What the VKB is derived from (tools/vkb/*.py, read)
- `manuscript.py`: folios, quires, loci, tokens, panel_images from `data/ZL3b-n.txt`, RF1b, IT2a IVTFF, `data/folio_evidence_inventory.tsv`, `runs/s100/star_classes.tsv`, `data/external/yale_scans/pages_index.json`.
- `features.py`: folio_features, finding_links (computed from tokens; links from the graph).
- `evidence.py`: runs (results globs + stubs + TEAM-HANDOFF prose), claims/measurements (CLAIMS.md + regex), findings/finding_lines/hypotheses/points/assumptions/pending (graph), learnings/decisions/open_questions (registers). Its docstring still says "s111 is running", a status frozen into code.
- `world.py`: corpora (data manifests and READMEs), corpus_stats (named results files), sources (snapshot `audit-completeness_gap.md`), external_items (literals + `audit-external-*.md` + `audit-intake.md`), page_facts (`page-facts/*/facts.tsv`).
- Last build: all four modules at 2026-10-19 00:57 (`build_log`). `data/vkb/` also holds 11 `vkb.sqlite.*.previous`, 5 `.failed`, 5 `test_*` and 1 `orig` copy of the database (22 files, about 300 MB).

### 1.3 Spot checks: 16 facts held in two or more homes

| # | Fact | Homes compared | Agree? |
|---|---|---|---|
| 1 | Claim count / last id | CLAIMS.md 547 rows, c-590 vs VKB 544, c-587 | No: VKB stale by 3 (built 00:57, register 09:08) |
| 2 | Learnings | LEARNINGS 290, L-359 vs VKB 285, L-354 | No: stale by 5 |
| 3 | Open questions | OPEN 72, O-072 vs VKB 71, O-071 | No: stale by 1 |
| 4 | Decisions | DECISIONS 73, D-073 vs VKB 73, D-073 | Yes |
| 5 | Finding status and grade, 51 findings | graph vs VKB `findings` | Yes, 0 differences (script compare) |
| 6 | X-01 on F-06, F-11..F-15, F-17, F-30, F-38 | `FINDINGS-MAP.md` (generated 09:08) strikes X-01 as discharged (graph lines still carry `discharges: [X-01]` from s76 Zattera) vs `FINDINGS-MAP_X01-FIX-2026-10-19.md` (hand-fixed copy) shows X-01 at risk after the vx01 A1 gate | **No**: the two maps contradict; the graph's assumption row says X-01 at-risk but its evidence lines still discharge it |
| 7 | c-588 (s122) numbers | CLAIMS vs `results_s122_20261019_011103.txt:9,16` (ZL3b word N_T 92 vs q99 30.01 quire; 60 vs 33.01 page) | Yes |
| 8 | c-590 (s128-p72) numbers | CLAIMS vs `results_s128_20261019T090659.txt:18,21` (MRR 0.0254, p 0.7202, power 0.958) | Yes |
| 9 | s124 status | TEAM-HANDOFF:9 "not yet filed or independently accepted" vs CLAIMS c-587, PLAN log 00:52 "s124 VERIFIED", VKB runs `admissible` | **No**: TEAM-HANDOFF stale |
| 10 | The 2026-10-19 pivot | DECISIONS D-072 (00:48) and D-073 (00:52), same pivot; TEAM-HANDOFF heading cites D-072; README cites D-073 | Duplicate decision under two ids; D-073's row admits the duplication |
| 11 | s128 owner | TEAM-HANDOFF: Grok Bot s128 (runs/s128) and lead s128-p72 (results_s128_20261019T090659.txt) vs VKB runs: one row `s128`, owner lead, results NULL | **No**: the collision collapsed into one wrong row |
| 12 | Id-band rule | README (D-054): other sessions use c-500+, L-300+, O-100+ vs registers: lead and Daybreak both file in c-5xx (c-550 db-s113, c-588 lead); L-230..L-299 and c-457..c-499 never used; no O-1xx exists, O-053..O-072 used by whoever filed | Rule not followed; dead |
| 13 | Where numbers live | README and TRIANGULATION: CLAIMS.md vs AGENTS.md: TEAM-HANDOFF is "the measurement map" | Two declared homes |
| 14 | Assumption registry | TRIANGULATION: PLAN.md vs X-ids in FINDINGS-GRAPH.yaml | Two registries (PLAN has U-assumptions, graph has X-01..X-09) |
| 15 | FINDINGS-REPORT.md status | own header "Superseded 2026-10-18 16:01" vs graph `workflow_views` "plain-language report" and graph `superseded:` naming it as successor of J/K/Q/R_RESULTS and BREWER-LEWIS-CHECK | **No**: supersession chain ends at a superseded file |
| 16 | Read-first list | root INVENTORY.md "Read these first" includes root `PLAN.md` vs graph: root PLAN.md superseded | **No** |
| 17 | page_facts pulls | L-355 "three pulls" vs VKB pulls astro-physical 349, catalogues 9,156, plants 656 | Yes |
| 18 | Repo comms vs <team-comms> | 28 files in workflow/comms vs <team-comms> | 27 byte-identical, 1 repo-only (`...REGISTER-ACK-SYLVIE-20261018T032251Z.md`) |
| 19 | vx01 files at root vs voynich-backups | 6 root vx01 .md + `FINDINGS-MAP_X01-FIX` vs `<home>/voynich-backups/` | All 7 byte-identical: root holds copies of the vx01 workstream's own home |

### 1.4 Id allocation and collisions
- Register scan (row-key regex over every register): **0 duplicate row ids** in CLAIMS (547), DECISIONS (73), LEARNINGS (290), OPEN (72). METHODS, TOOLS, REDTEAM and TOMBSTONES have no id-keyed rows. Gaps: c-457..c-499 and L-230..L-299 (the unused voynich-08 bands).
- Collisions are semantic, not textual: D-072/D-073 (one pivot, two ids, two sessions four minutes apart); s128 (lead and Grok Bot), s127 (lead `s127_facsimile_manifest.py`, no results, vs Daybreak db-S127 in codex_lab); s100-s111 lead/Daybreak twins (alias map, TEAM-HANDOFF:362-392); s63 and s66 each have two scripts writing one results file; lead r1/r2 vs roach r1/r2 (VKB renames to lead-r1); D-054 (c-366..c-381, L-133..L-142 duplicated by Argon and voynich-08, renumbered by hand).
- **D-067/D-073: not reproduced.** D-067 appears once (2026-10-18 13:25, affix-layer pivot) in the register, the backup snapshot (voynich-backups 2026-10-18_2214) and <team-comms>; I found no file using D-067 or D-073 for a different decision. Unverified: whether the brief meant D-072/D-073.
- Schema drift (a symptom of several writers): rows whose cell count differs from the header: DECISIONS 7 of 73 (D-043, D-044 have 4 cells; D-068..D-072 have 6), OPEN 21 of 72, LEARNINGS 10 of 290, CLAIMS 14 of 547 (some are pipes inside code spans). A blank line at DECISIONS.md:78 splits the table, so D-072 and D-073 sit outside it in a markdown renderer.
- Run-id allocation today: free-text claim paragraphs in TEAM-HANDOFF (one paragraph at line 356 is a single very long line), owner prefixes by convention (`db-`, `r`, `vx01_`, `lib01`), and "check the last id before appending" (README). Nothing is atomic, so two sessions reading the same last id both take it.

### 1.5 The 15 undeclared root .md (from `findings_graph.py sprawl`)
All 15 belong to the vx01 workstream (Voynich Analyst for Eve, X-01 segmenter tests; `vx01_` prefix reserved in TEAM-HANDOFF). No `*.prereg.sha256` names them by path (the vx01 stubs pin `plan_sha256`, scripts and seeds by hash). They cite each other by path and by sha256, so their bytes must not change. The 7 checked are copies of files in `<home>/voynich-backups/`; the IV review files they cite (`IV-RESCORE-X01-A1.md` and others) were not found in the repo, voynich-backups, <team-comms> or ~/.claude (depth 4): unverified where they live.

| File | Proposed status | Why |
|---|---|---|
| `PLAN-X01-B-FALLBACK-v6.md` | historical (hashed plan, master copy in voynich-backups) | cited by sha256 (dfc2e088...); title still reads v4; "no v7" ruling |
| `vx01_LEAD_DECISION_2026-10-18_no_A2_A3_A4.md` | historical (vx01 run record); its content needs a DECISIONS row or an L-row | a lead decision living outside DECISIONS.md |
| `vx01_a1_DISCLOSURE_1_dev_scores.md` | historical (vx01 run record) | append-only disclosure |
| `vx01_a1_DISCLOSURE_1_ADDENDUM_stdin_check_time.md` | historical | addendum, cites disclosure 1 by hash |
| `vx01_a1_DISCLOSURE_2_first_known_answer_version.md` | historical | disclosure |
| `vx01_a1_DISCLOSURE_3_small_inventory_books_dropped.md` | historical | deviation record |
| `vx01_a1_NOTE_why_rows_fail.md` | historical (UNVERIFIED until IV signs, per its header) | explains `results_vx01_a1.txt`, the one results file sprawl reports as unreferenced |
| `vx01_a1_RECORD_ADDENDUM_1_loaded_files.md` | historical | run record |
| `vx01_bf_CODE_DECISIONS_1.md` | historical | code record; CODE_DECISIONS_2 adds to it, does not replace it |
| `vx01_bf_CODE_DECISIONS_2.md` | historical | code record |
| `vx01_bf_DEVIATION_1_B2_dropped.md` | historical | deviation record |
| `vx01_bf_DISCLOSURE_1_incoming_slip.md` | historical | disclosure |
| `vx01_bf_DISCLOSURE_2_line167_time.md` | historical | disclosure |
| `vx01_bf_NAMES_1.md` | superseded: `vx01_bf_NAMES_2.md` | NAMES_2 is the corrected version (voynich-backups holds `vx01_bf_NAMES_1_to_2.diff`); NAMES_2 keeps the title "NAMES 1" |
| `vx01_bf_NAMES_2.md` | historical | current name map |

These are declarations in the graph's `docs:` block, not moves. The workstream may still be live (last file 02:14 today), so the files stay where they are until its owner closes it. Later destination: `runs/vx01/records/`, via curate archive with tombstones, after checking that no stub or IV file cites the root path.

### 1.6 Generated vs hand-edited

| File | Kind | Generator / note |
|---|---|---|
| `workflow/FINDINGS-MAP.md` | generated | `tools/findings_graph.py render`; header "do not edit" |
| `workflow/FINDINGS-MAP_X01-FIX-2026-10-19.md` (+ `.diff`) | **hand edit of a generated file** | breaks TRIANGULATION's rule; its header admits it |
| root `INVENTORY.md`, `workflow/curation/*` | generated | curate.py (scan of 2026-10-18; lists 805 root files, root now has 956) |
| `.inventory/INDEX.md`, `.inventory/INVENTORY.md`, `.inventory/MANIFEST.jsonl` | generated once by the inventory skill, then hand-patched | now historical |
| `data/vkb/vkb.sqlite` | generated | `tools/vkb/build.py` |
| `docs/FOLIO-EVIDENCE-INVENTORY.md` | generated | `tools/build_folio_inventory.py` (2026-10-17) |
| `data/external/page-facts/plants/facts.tsv` | generated | `build_plants.py` beside it; the other `facts.tsv` files are hand- or agent-pulled |
| `results_*.txt`, `runs/*/results*` | script output, immutable | never overwritten |
| Registers, FINDINGS-GRAPH.yaml, PLAN.md, TEAM-HANDOFF.md, TRIANGULATION.md, CONSTRAINTS-MAP.md, README/AGENTS | hand-edited | several writers each |
| `tools/vkb/world.py` external_items and sources literals | **hand-edited data inside code** | the only home of the 87 intake rows |

## 2. Verified vs inferred
Verified (command named):
- Register ids, duplicates, gaps, cell-count drift: Python regex scan of `.inventory/registers/*.md`.
- VKB counts, max ids, build time, findings compare, runs rows, page_facts pulls, external_items by class and location: `tools/vkb/query.py` and a sqlite3 + yaml script.
- X-01 contradiction: `diff` of FINDINGS-MAP.md vs the X01-FIX copy; `grep discharg` in the graph and in `tools/findings_graph.py:54-60,220`.
- c-588 and c-590 against their results files: `grep` of the named lines.
- Comms and vx01 copies: `cmp` against <team-comms> and voynich-backups.
- Undeclared root .md: `python tools/findings_graph.py sprawl`. Stub references: grep of all 165 `*.sha256` stubs for the .md names (0 hits).
- TOOLS coverage: regex of `*.py` names in TOOLS.md vs `glob('*.py') + glob('tools/*.py')`.
- 536 "results" = 365 `.txt` + 171 `.json` (`ls | grep ^results`).

Inferred, not checked:
- That the D-072/D-073 duplication came from two concurrent sessions. D-073's own row says so; I did not read session transcripts.
- That VKB parsers mis-assign columns on the drifted rows. I saw the cell counts but not the parsed values.
- The location of the IV-* review files.
- That the vx01 workstream is still live.

## 3. Surprises
1. The canonical generated map is wrong about X-01 and the only correct rendering is a hand-edited copy. The fix belongs in the graph: the s76 Zattera lines' `discharges: [X-01]` should be withdrawn or marked `unverified`. Re-rendering alone will not fix it.
2. The intake register (external_items) is Python literals in `world.py`, against D-070's "derived" rule. Re-running the build cannot recover a row that someone deletes from the code.
3. The VKB "runs" table takes run ownership from TEAM-HANDOFF prose and has already lost the s128 double.
4. The D-054 id bands are dead: two writers share c-5xx, L-3xx and O-0xx, while 113 ids sit unused.
5. The supersession chain for J/K/Q/R_RESULTS and BREWER-LEWIS-CHECK ends at FINDINGS-REPORT.md, which is itself superseded.
6. `data/external/library/` (lib01, Grok Bot) holds a second claims list (465 unchecked claims), a second findings crosswalk and a second gap list. None of it is in the VKB.
7. `data/vkb/` holds about 300 MB of `.previous`, `.failed` and test databases.

## 4. Assumption candidates (the cleanup would rest on these)
| # | Assumption | How to verify |
|---|---|---|
| A1 | Every VKB table can be rebuilt from files (D-070) | Check world.py for literals; after the move, rebuild into a temp path and diff row counts against the current DB |
| A2 | Registers have no duplicate ids | Done (0); rerun the scan as a check after every merge |
| A3 | Declaring the 15 vx01 .md in `docs:` drops sprawl's undeclared count to 0 without moving anything | Edit a copy of the graph, run `sprawl` against it |
| A4 | Root vx01 files are byte copies of voynich-backups, so the root copies can be retired later | `cmp` all vx01 files (7 of 15 checked, all identical); confirm with the owner |
| A5 | workflow/comms holds only mirrors of <team-comms> | `cmp` (27/28); file the 1 repo-only message to <team-comms> or declare it |
| A6 | Nothing reads TEAM-HANDOFF's free-text run claims except humans and evidence.py | `grep -rn TEAM-HANDOFF tools/ *.py` before restructuring that section |
| A7 | Owner-namespaced run ids would not break existing parsers | evidence.py:92 accepts `^(db-|lead-)?[a-z]+\d+`; test `gb-s1`, `vx-1` against it |
| A8 | Numeric register ids must stay numeric | findings_graph.py:66,70 and evidence.py match `c-\d+`, `D-\d+`; any new form needs those regexes widened |

## 5. Recommendations

### 5.1 The one-table canonical map (proposed for AGENTS.md, replacing TRIANGULATION's partial table)

| Fact kind | Single canonical home (hand-edited) | Derived views (never edit) | Retire or demote |
|---|---|---|---|
| Raw measurements | `results_*.txt`, `runs/<id>/results*` (immutable) | VKB `measurements`, `corpus_stats` | none |
| Cited numbers (claims) | `.inventory/registers/CLAIMS.md` (c-id) | VKB `claims` | TEAM-HANDOFF "Where a number lives" becomes pointers to c-ids only; AGENTS.md stops calling TEAM-HANDOFF the measurement map |
| Learnings | `LEARNINGS.md` (L-id) | VKB `learnings` | learnings-audit stays a method reference, cited by L-id |
| Decisions | `DECISIONS.md` (D-id) | VKB `decisions` | TEAM-HANDOFF pivot section becomes a one-line pointer to D-073; mark D-072 "merged into D-073" in place, no delete |
| Open questions, gaps, next queue | `OPEN.md` (O-id, with a state column) | VKB `open_questions` | D-066 points to O-ids instead of holding the queue; library GAPS.md rows are intaken as O-rows; graph `pending:` holds runs in flight only |
| Findings, hypotheses, assumptions (X) | `workflow/FINDINGS-GRAPH.yaml` | `FINDINGS-MAP.md`, VKB findings tables | X01-FIX copy declared superseded once the graph is fixed; PLAN "Assumption registry" renamed "plan assumptions (U)"; CONSTRAINTS-MAP declared narrative-only (cites F-ids) |
| Runs and run ids | TEAM-HANDOFF "Run ledger" section, one table row per id (id, owner, claimed-at from `date`, stub, results, state) | VKB `runs` | PLAN prefix table and the free-text claim paragraphs marked historical |
| Page facts | `data/external/page-facts/<pull>/facts.tsv` | VKB `page_facts` | load `eyecheck/pairs.tsv` or declare it data-only |
| External items, intake, sources | one TSV under `data/external/` (moved out of `world.py` literals; a data file, not a status file) plus `library/catalogue_v2.tsv` | VKB `external_items`, `sources` | `.inventory/runs/2026-10-18/audit-*` stay frozen evidence |
| Team comms | <team-comms> (<team-comms>) | none | `workflow/comms/` declared mirror (or tombstoned) |
| Methods | `METHODS.md` (definitions) + TRIANGULATION.md (filing rules) | `tools/vkb/README.md` statistic names cite METHODS | none |
| Tools | script docstrings | curate `FILES.md`; TOOLS.md demoted to runtime notes | TOOLS.md marked historical for per-script rows (85 of 247 covered) |
| Plan and status | `workflow/PLAN.md` (`Current stage:` line + phase log) | none | TEAM-HANDOFF top sections, README status lines, root PLAN.md (§0 proof bar moves or is cited) |
| Inventory | root `INVENTORY.md` (curate) | `workflow/curation/*` | `.inventory/INDEX.md` gets a superseded banner (it has none); README start-here table removed in favour of AGENTS.md |

### 5.2 Collision-proof id rule (proposed for AGENTS.md and TEAM-HANDOFF)
1. **Run ids: each owner has its own namespace and counter.** lead `sNNN`, Daybreak `db-sNNN`, roach `rNN`, Grok Bot `gb-sNNN`, Argon `ag-sNNN`, Voynich Analyst `vx01_*`. Nobody takes a number from another owner's counter. A new agent registers a prefix once, in the run ledger, before its first run. Collisions become impossible by construction, with no locking. Existing ids stay as they are; the alias map covers the old ones.
2. **Register ids (c/L/O/D): one writer.** Only the session holding the lead token (named in TEAM-HANDOFF) appends rows. Other sessions send proposed rows through <team-comms> with a local tag (`db:L-1`); the lead assigns the number and records the tag in the row. Ids stay numeric, so parsers (A8) keep working.
3. **If two sessions must both write, claim the id with an atomic marker first.** `mkdir .inventory/ids/c-591` either succeeds or fails, which is atomic on NTFS. Only after it succeeds is the row written. A failed mkdir means the id is taken; take the next one. The marker is an empty directory, not a status file.
4. **Gate.** Add a duplicate-id check and a cell-count check to `findings_graph.py sprawl` or `tools/vkb/check.py`, plus a "same title within 1 hour" check for D-rows. Retire the D-054 bands with a DECISIONS row.

### 5.3 Actions
| # | Action | Effort | Risk |
|---|---|---|---|
| R1 | Declare the 15 vx01 .md in graph `docs:` (14 historical, NAMES_1 superseded by NAMES_2); no moves | low | low |
| R2 | Fix X-01 in the graph: withdraw or mark `unverified` the s76 `discharges: [X-01]` lines, re-render, declare the X01-FIX copy superseded | low | medium (changes the grades of 9 findings; needs the lead audit) |
| R3 | Rebuild the VKB after every register write (it is 3 claims, 5 learnings and 1 open row behind), and make sprawl warn when `build_log.built_at` is older than any register's mtime | low | low |
| R4 | Mark D-072 merged into D-073 in place; repair DECISIONS.md:78 (blank line) and the 6-cell rows | low | low |
| R5 | Adopt the canonical map (5.1) in AGENTS.md; fix the three conflicting statements (AGENTS "measurement map", TRIANGULATION "assumption registry", README start-here) | low | low |
| R6 | Adopt the id rule (5.2); add the duplicate, cell-count and same-title checks | medium | low |
| R7 | Replace the TEAM-HANDOFF run claims with a one-row-per-id run ledger; teach evidence.py to read it; split the s128 VKB row into lead and gb | medium | medium (evidence.py parses the current prose) |
| R8 | Move external_items and sources literals from world.py into a TSV under data/external; load library catalogue, unchecked_claims and GAPS into the VKB or intake them as rows | medium | medium (D-071 does not apply because world.py is not stub-named; check that first) |
| R9 | Declare workflow/comms a <team-comms> mirror; copy the one repo-only message to <team-comms> | low | low |
| R10 | Give `.inventory/INDEX.md` a superseded banner; point FINDINGS-REPORT's supersession successors at FINDINGS-MAP | low | low |
| R11 | Archive the 22 old VKB databases (`.previous`, `.failed`, `test_*`, `orig`) with curate archive (about 300 MB) | low | low |
| R12 | Re-run curate so INVENTORY.md matches the 956 root files, and drop superseded root PLAN.md from "Read these first" | low | low |
