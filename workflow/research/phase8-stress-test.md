# Phase 8 angle: stress-test of Jon's hypothesis

Stamped 2026-10-19 09:31 PDT (clock read with `date`). Read-only investigation by a subagent of voynich-08 (<session>). This is the only file written.

Hypothesis under attack: "clean up this project and reduce sprawl and duplication as much as possible ... organized and as complete as humanly possible (literally) ... so we can triangulate."

**Verdict: REFINED.** "Organize so questions are answerable" survives. "Reduce sprawl by relocating files" is harmful here. "Complete, literally" has no stopping point. The refined form: make a fixed bank of researcher questions answerable in a bounded number of opens, using declarations, generated indexes and a fresh VKB, with almost no moves. Acquire external material only when it adds an independence axis to a load-bearing finding or to a D-066/D-073 gate.

## 1. What I found (paths, counts)

### 1a. Baseline: six real questions answered today
Each was answered from a cold start. "Calls" counts tool invocations; most calls opened several sources.

| # | Question | Calls | Sources opened | Result |
|---|---|---|---|---|
| Q1 | What is known about f68r1? | 6 | VKB `page_facts` (47 rows), `folio_features` (138), `claims`, `learnings`; grep over 6 registers, TEAM-HANDOFF, graph, map | Answered, but scattered. External facts come from 2 pulls (`astro-physical`, `catalogues`) with duplicate rows (the sun/moon illustration sentence appears twice) and two `fetched` date formats. The project's own knowledge sits in OPEN, REDTEAM, L-346 and `data/external/cribs/`, with no finding. No single query gives a folio dossier. |
| Q2 | Which results support F-20? | 3 | VKB `findings`, `finding_links`, `finding_lines` | Answered well. 6 evidence lines: s53 c-388, Argon s53 c-377, db-s114 external, s115-A0 and s54 controls. `finding_links` alone shows only D-053, so the reader must know to use `finding_lines`. |
| Q3 | Has a Naibbe cipher been tried? | 1 | VKB `claims` LIKE search | Answered in one call: yes, many times (f3, c4, ctl_naibbe, f4, g0, s27, s64; s71 per the file list). This fails if the question uses a synonym. |
| Q4 | What is the current status of H-14, and does it agree with L-217? | 1 | VKB `hypotheses` + LEARNINGS grep | Answered, and consistent. The drift that the 2026-10-18 15:56 sprawl audit found (graph:32 vs L-217) has been fixed in place. |
| Q5 | Which file holds the Parisel switch result? | 1 | grep registers + graph | `results_s68.txt` (c-408, L-161). The 10-18 sprawl audit (`.inventory/runs/2026-10-18/audit-sprawl_repo.md` §4) said "the Parisel switch result has no file of its own"; that was wrong, because s68 had run at 01:53 that day. An audit produced a false sprawl finding. |
| Q6 | What does Daybreak currently hold as its top leads or state? | 3 | grep our tree, then open `yonichmanuscript/codex_lab` | Not answerable from our tree. Only comms and run-notes mention the files. Daybreak's `CURRENT_STATE`, `EVIDENCE-INDEX`, `TOP-10-LIVE-LEADS` and `MEANING-RECOVERY-*` (written 2026-10-18 20:56 to 23:24) are not indexed. |

Reading of the baseline: 4 of 6 questions take 1 to 3 calls today, because the VKB and the registers already work. The costs are concentrated in three places:
- per-folio questions (scattered, duplicated external facts);
- team artefacts outside the tree (not indexed);
- staleness: the VKB was built 2026-10-19 00:57 and holds claims to c-587 and learnings to L-354, while the registers are at c-590 and L-359.

None of the six answers would get faster if root files were moved.

There is a precedent bar: `.inventory/runs/2026-10-17/cold-start.md` scored 5/5 using INDEX plus at most two register opens. The 10-18 curate run, by contrast, graded itself PASS 100/100 with `question_bank_score 0/0 (no bank committed)`, and its onboarding bytes rose from 29,816 to 75,300 (`workflow/curation/SCORECARD.md`). That is the cleanup-theatre failure mode, already observed once: the grade passed without measuring a single answer, and the reading load more than doubled.

### 1b. Breakage surface if root files move
- **Stubs.** 142 `*.prereg.sha256` files exist (126 at the root). Together they pin **2,627 distinct paths**:
  - 161 root files (153 `.py`);
  - about 2,149 under `data/`;
  - 116 under `runs/`;
  - 25 under `tools/`;
  - 135 written as `../` relative paths.
- **Scripts reading results as inputs.** 193 distinct `results_*` names appear in root/tools `.py` files, and 78 of them are referenced by 2 or more scripts (so they are probably consumed as inputs). For example, `results_m4_phase1_board.json` appears in 11 scripts and `results_s18_cremma_all.json` in 7. Those scripts are frozen (D-071), so a moved input breaks reproduction with no permitted repair.
- **VKB builder** (`tools/vkb/evidence.py`). It globs `ROOT/results_*.txt`, `ROOT/*.py` and `ROOT/*.prereg.sha256`. A moved results file is dropped from the `runs` table **silently**, with no error.
- **findings_graph.** It checks `os.path.exists(ROOT/ref)` (`tools/findings_graph.py:77,139`). A move fails **loudly** across 83 distinct graph result refs; the graph has 235 `ref:` lines.
- **Documents citing bare root filenames.** Registers cite 228 distinct results filenames and TEAM-HANDOFF cites 137.
- **Downstream site.** The public site (simoneresearch.com) displays graph grades and weights. `grokactivity101926.txt:15,113` reports 15 findings already graded differently on the site. How the site ingests the graph was not checked (unverified). Renaming ids or paths widens that drift.
- **Concurrent writers right now.**
  - 38 root files changed since 00:00 today.
  - s128 wrote `results_s128_20261019T090659.txt` at 09:06, and its script lives in `tools/`, not the root.
  - vx01 (Eve) has 40+ root files, the last written at 02:14, plus 14 of the 15 undeclared root `.md` files.
  - Daybreak's tree has 4,272 files modified today.
  - <team-comms> has 1,203 files newer than 10-18.

### 1c. Provenance lessons from earlier curation (TOMBSTONES, `.inventory/runs`, LEARNINGS)
- **The only relocation round** (2026-10-17 17:20: 10 round logs moved to `docs/rounds/`) worked, because it moved closed narrative docs that nothing executed. Every other TOMBSTONES row is a collision, overwrite or renumbering caused by **concurrency**, not by clutter:
  - PREREG.md and score.py overwritten by another session;
  - `results_p1.txt` overwritten (12 minutes with no copy on disk);
  - prefix collisions on n6, s1/s2, s33, s34/35, s51-54, s63/66;
  - D-054 renumbering.
- **The 10-17 20:11 curate run** by an unidentified session wrote root `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and `INVENTORY.md`, which collided with `.inventory/INVENTORY.md`. Three "maps" still coexist: root INVENTORY.md, `.inventory/INVENTORY.md` and `.inventory/INDEX.md`. Root INVENTORY.md (12:18 on 10-18) still says "newest in-scope file 2026-10-18" and lists comms as 11 files (there are 28 now).
- **Curate labels go stale within minutes.** 224 of the 872 ARCHIVE-CANDIDATE files in `workflow/curation/labels.csv` (10-18 12:18) are now stub-pinned: `s99_label_nearby_lines.prereg.sha256` (12:23, five minutes later) pins 223, and `s102_period_ciphers_recipes.prereg.sha256` pins 1. Archiving from that label set would have violated D-071 on 224 files.
- **Banners in place work, but leave stale text readable.** The 10-18 16:01 superseded banners (README, CONSTRAINTS-MAP, TEAM-HANDOFF ledger and s94/s96 lines) fixed most of the audit's 13 disagreements without moving anything. A cold reader still reads the old tables below the banner.
- **Hand-kept indexes decay.** The LEARNINGS navigation index omits 66 of 290 L-ids (23%).
- **Asking other sessions to comply has not worked.** On 10-18 22:59Z, b379 asked Daybreak (`workflow/comms/<team-comms>`) to banner its status files "Not canonical" and to stop issuing new status or top-10 files. Today none of `codex_lab/AGENT-START.md`, `CURRENT_STATE_2026-10-18.md`, `EVIDENCE-INDEX.md`, `BIG-PICTURE-EVIDENCE-SYNTHESIS-2026-10-18.md` or `MEANING-RECOVERY-STRATEGY-2026-10-19.md` contains "not canonical" or a pointer to this tree (grep, 0 hits). MEANING-RECOVERY-STRATEGY was written after the request. Daybreak's db-S127 to db-S132 numbering also overlaps the lead's s127/s128.

### 1d. The "30 orphan claims" overstate the filing debt
Of c-561 to c-587 in the VKB, about 21 are literature, data or inventory facts with no run id:
- literature: Hodgins radiocarbon, Greshko, Chang, Koshy, Lux, Helton and others;
- data and inventory: wave-5 fetch, "VKB rebuilt" (c-575), LSI loci count, Fontana control acquired.

By the CLAIMS id-band convention these belong in c-2xx/c-3xx; that convention has lapsed. Only about 6 are run results needing a finding link: s115, s117, s123, s124, s125, s126. c-588 to c-590 are not in the VKB yet. The `sprawl` check counts every c-300+ claim without a finding link, so it inflates the number.

## 2. Verified vs inferred
Verified, with the command or check:
- the six-question baseline: VKB queries via `tools/vkb/query.py` plus grep;
- `findings_graph.py sprawl` output: 30 / 1 / 15;
- root counts: `ls` gives 956 files, 536 `results_*` (365 txt + 171 json), 205 `.py`;
- stub pin set: Python parse of every stub, 2,627 paths;
- the 224 archive candidates now pinned, and which two stubs pin them (mtime check);
- VKB staleness: `build_log` 00:57, max ids c-587 and L-354 against the registers;
- VKB and graph path handling: read `evidence.py` glob lines and `findings_graph.py:77,139`;
- LEARNINGS index coverage: `comm` of index ids against row ids gives 66 missing;
- Daybreak's non-compliance: grep for "not canonical" / "Python/voynich" across 5 files gives 0;
- curate scorecard numbers: read `SCORECARD.md`.

Inferred, not verified:
- that the 78 multiply-referenced results files are read as inputs rather than written (name co-occurrence only);
- how the public site ingests the graph;
- that no other tool globs root paths (only vkb and findings_graph were read);
- the D-067/D-073 and s127/s128 collisions are taken from the brief; I saw D-072/D-073 as near-duplicate pivots 4 minutes apart but did not trace D-067.

## 3. Surprises
1. **The prior curate run is a worked example of cleanup theatre.** It graded PASS 100/100 with no question bank, its onboarding bytes rose 2.5x, and 224 of its archive candidates became pinned within five minutes.
2. **An earlier sprawl audit made a false finding** (Parisel has no file). Audits of sprawl need the same "file the printed check" discipline as experiments.
3. **The VKB `runs` table would lose moved results silently.** The graph check would fail loudly. These are asymmetric failure modes.
4. **14 of the 15 undeclared root `.md` files are vx01's live disclosure trail** (Eve, last written 02:14). Declaring them is safe; moving them would break another session's live protocol.
5. **The hypothesis competes with D-072/D-073.** Those decisions stop structural accumulation in favour of external validation. A large organization effort is the same kind of non-gate work those decisions park, unless it is tied to the gates.

## 4. Assumption candidates the cleanup plan would rest on
| # | Assumption | How to verify |
|---|---|---|
| A1 | Organizing will make answers faster | Commit a question bank of 20 or more real questions (Q1-Q6 above plus folio, "tried?", "supports F-x", "who owns run id") with a call/open budget. Measure before and after. The plan passes only if the score rises. |
| A2 | Root files can be moved safely | At action time (not from cached labels), recompute the stub pin set, script-input references, register/graph/HANDOFF mentions and VKB glob coverage. Movable means "in none of these". Expect almost no results or `.py` files to qualify. |
| A3 | Other sessions will honour declarations or banners | Already falsified once (Daybreak, 10-18 22:59Z). Verify by grep after 24 h, and plan for pull-side indexing instead. |
| A4 | The 30 orphan claims are filing debt | Classify each by run_id. Expect about 6 that are truly run claims; the rest need a literature/data exemption in `sprawl`. |
| A5 | The VKB is the source a cold agent uses | Check the `build_log` age against register mtimes. It was stale by 5 claims and 5 learnings at 09:26. |
| A6 | Completeness raises triangulation | For each acquisition, name the finding/axis or gate it could change. If none can be named, the assumption fails for that item. |

## 5. Recommendations (effort / risk)
1. **Question bank as the acceptance test** (low / low). Extend `cold-start.md` to 20 or more questions, with a budget of 3 calls and 5 opens each, and record the baseline above. No Phase 8 step counts as done unless it raises this score. That is the stopping rule for "organized".
2. **No relocation of results, `.py` or stubs** (zero effort / it removes the high risk). Allowed moves: only closed narrative docs that pass A2 at action time, via `curate.py archive` with tombstones, and never from an existing `labels.csv`.
3. **Declare instead of move** (low / low). Add the 15 root `.md` files to graph docs. vx01's files go in as "team-owned, live" and are not touched. Add a `sprawl` exemption for literature/data claims (or a `kind` column), so the orphan count measures real debt.
4. **Session-namespaced ids, not an allocator** (low / low). Collisions come from sessions that do not read the claim board, so a shared counter fails the same way. Require the prefix by session for runs (`db-`, `vx01_`, `argon-`), as D-054 did for register bands. Extend the D-054 bands to every live session and to D-ids. `sprawl` flags any unprefixed new id. A lock-file allocator is medium effort and still depends on compliance.
5. **Pull-side team index** (medium / low). Extend the VKB with a read-only `team_artefacts` table: path, owner, mtime, sha256 and a self-declared status line, harvested from codex_lab, <team-comms> voynich files, `workflow/comms`, `incoming/` and the roach bridge. Copy nothing and edit nothing. This answers Q6 without depending on compliance.
6. **VKB freshness gate** (low / low). `findings_graph.py sprawl`, or the VKB `check.py`, should fail when `build_log` is older than the newest register row. Rebuilding is cheap (about 21 s).
7. **Folio dossier view** (low / low). Add one VKB query or view joining `page_facts` (deduplicated across pulls), `folio_features`, `claims`/`learnings`/`open_questions` text mentions and crib files. This answers Q1 in one call.
8. **Generate the LEARNINGS index, don't hand-keep it** (low / low). 23% of rows are already missing from it.
9. **Stopping rule for "complete"** (policy, low). Acquire an external item only when all three conditions hold:
   - it is named as an input by an open pending test (graph `pending`), a D-066/D-073 gate, or an OPEN row;
   - it could add an axis (data/impl/external/control) to a load-bearing finding;
   - it fits a stated budget.

   Stop a gap-filling batch when two consecutive batches change no FINDINGS-MAP grade and do not raise the question-bank score. Everything else goes in a "known, not acquired" list (in a register, not a new file), with the reason.

Conditions the refined hypothesis depends on: the question bank exists and is scored before and after (A1); moves are checked live against pins and references (A2); team integration is by pull, not by asking (A3); acquisition is gated by triangulation value (A6), consistent with D-072/D-073.
