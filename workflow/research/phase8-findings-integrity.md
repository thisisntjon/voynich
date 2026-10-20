# Phase 8 investigation: findings integrity

Date: 2026-10-19 09:33 PDT (from `date`). Author: findings-integrity subagent of the lead session (<session>). Read-only investigation; this is the only file written in the repo.
Question: is every result filed, every claim linked, and every load-bearing fact verified?

## 1. What I found

### 1.1 The highest-priority finding: roach r15 contradicts F-50 and has not been taken in

- roach delivered r15 (a blind replication of s114 / F-50) on 2026-10-18 at 20:47. The files are in `<local-path>`, and `sha256sum -c MANIFEST.sha256` passes. There is no `runs/roach-r15/`, no CLAIMS row and no graph line for it.
- The printed call is `CALL Test A: NO DRIFT`.
  - ZL p 0.0009: HIT.
  - IT p 0.0006: HIT.
  - RF p 0.0545: MISS (79 folios kept, MDE 1.0 SD).
- Lead s114 (c-558) printed DRIFT_ONLY.
- The graph still lists the run as `P-56 r15 state: rejected, "withdrawn by D-066 (w)"`. A lead brief for r15 was nonetheless sent at 19:54 (`<team-comms>`).
- Under TRIANGULATION, filing the printed call means an impl line with `agrees: false`, which makes F-50 CONTESTED. Two of three transliterations do agree in direction. That belongs in a note; it does not change the call.

### 1.2 The 30 unlinked claims (sprawl list: c-559 and c-561..c-589)

I read every row. I opened the results header or CALL lines for each run claim (s115-A0, s117, s122, s123, s124, s125, s126), and checked that every cited evidence file exists. All 30 sources are present. Each printed CALL matches its claim text.

Dispositions (L = add as a line or claims entry to an existing finding; N = new finding; S = `standalone_claims` with a reason):

| claim | content | proposed disposition |
|---|---|---|
| c-559 | s115-A0 known-answer control: vocabulary test power 0.405, image test 0.995 | **L: F-33 `controls`** (and F-20). F-33's "no strong link" is underpowered for vocabulary at Voynich size. The row already says "F-33, F-20", and P-57 cites it, but neither finding lists it. |
| c-561 | Hodgins 2009 C14 interval | S: dating context, not a manuscript measurement |
| c-562 | Greshko supplement statistics | S: guard ("not h2/hapax"); related to F-24 only as context |
| c-563 | Guzy 2022 Widemann purchase | S: provenance note |
| c-564 | Chang 2026 bigram entropy vs shuffle | S (guard). Optional: F-12 external line, `unverified: true` until the unit scope (whole words vs cores) is mapped |
| c-565 | Koshy 2026 MDS / h2 2.112 | S: guard |
| c-566 | Signorino height-transition entropy | S: guard |
| c-567 | Amador: H vs F differ on 20% of words, 29% of line word counts | **N (with c-576, c-568)**: see below |
| c-568 | Lux: h2 range 0.58 bit across transliteration files | **N (with c-576)**: external line |
| c-569 | Kinnison BPC rates | S: guard |
| c-570 | Helton "decipherment" | S: outside claim (also a REDTEAM candidate) |
| c-571 | wave-5 fetch manifest | S: data inventory |
| c-572 | Beasley census | S: input to O-062/s105 |
| c-573 | Segre 98 herbs | S: input to s105 |
| c-574 | CEUR 3313 inventory | S: data inventory |
| c-575 | VKB rebuild 2026-10-18 | S, and mark **STALE**: it says findings 51 / claims 520. The DB was rebuilt at 00:57 and now holds claims 544 |
| c-576 | LSI loci: all primary readers agree on 22% of loci; H vs F token agreement 0.33 | **N: a new finding on transliteration disagreement**, resting on X-09. X-09 is marked `verified` ("agree on glyph identity well enough"), but whole-locus agreement is 0.22-0.34. X-09 should be re-graded or scoped, and every `data`-axis line inherits this |
| c-577 | s117 within-line co-occurrence, CALL overall T | **L: F-42**, marked superseded at word level by c-588 |
| c-578 | s125 NO_CONTROL | S: rejected run (P-70); method lesson only |
| c-579 | s123 NOT_MEASURABLE | S: rejected run (P-68) |
| c-580 | s126 NOT_MEASURABLE | S: rejected run (P-71); descriptive only |
| c-581 | D'Imperio/Panofsky programme | S: prior for H-20; cite it in the H-20 row basis |
| c-582 | Brewer: Berlin Lat. fol. 88 concealment | S: historical context (H-16 background) |
| c-583 | Painter and Bowern: hands close, no script tradition | L option: F-16 external line, `unverified: true` until scope-checked; otherwise S |
| c-584 | Fontana known-answer images acquired | S: data acquisition |
| c-585 | TrOCR preflight unusable | S: method lesson |
| c-586 | db-S141 Penn/Sloane graph positive control | S: calibration for s105 only (narrow scope as filed) |
| c-587 | s124 pharma drawings: weak page grouping, below the real-herbal range | **N (at-risk) or point**: the first filed result bearing on H-20 (P-69 `filed`, H-20 has 0 points). A weak "against" point is warranted |
| c-588 | s122: word and core recurrences are page-local; only gallows trigrams pass | **L: F-42**. It refines "quire/register-local" to page-local, and also fixes F-42's empty `claims: []` |
| c-589 | Gisclon 2026, outside claim, UNVERIFIED | S: pending check, linked to O-058 |

Net effect: 5 additions to existing findings (F-33 x1, F-42 x2, plus optional F-12/F-16), 2 new findings (transliteration disagreement; H-20 picture-programme evidence), and 21 standalone entries.

### 1.3 Results files

- Total `results*.txt` in the tree: 413 (365 at the root, 37 in runs/, 7 in data/, 4 in incoming/). sprawl counts unreferenced files by run id and finds 1 (`results_vx01_a1.txt`).
- Matching on the exact file name against CLAIMS, the graph and TEAM-HANDOFF, 202 are unreferenced. All but a few are family members of referenced runs:
  - root: n6/n7/s17/s18/s20 per-corpus outputs (161).
  - `results_p4d1_core_order.run1-crashed.txt`, `results_m4_phase1_board.prev.txt`, `results_a6b_k20_latin.txt`.
  - `results_s89.txt`: the pre-amendment output. P-21 uses `results_s89_amend1.txt`.
  - runs/: roach `results_fixture*.txt` (17), `runs/s82/results_run1-crashed.txt`, `runs/s45/results_s45.dryrun-unregistered.txt`, `runs/s128/results_s128_f0n2_calibration.txt`, `runs/vx01_a1_dev/.../results_path_test.txt`.
  - `data/physical/contact_map/*/results.txt` (7, Phase 7.4 prototypes).
  - `incoming/ten-theories/` (4, exploratory, D-048).
- **`results_vx01_a1.txt` is a real unfiled outcome.** Its plan text (`vx01_LEAD_DECISION_2026-10-18_no_A2_A3_A4.md`) says the A1 gate found **no segmenter ADEQUATE on planted books**. That bears directly on X-01 (SlotSegmenter units), on F-11 and on F-40. It is owned by another session (Voynich Analyst; header "UNVERIFIED, not yet seen by the Independent Verifier"). I could not find `IV-RESCORE-X01-A1.md` within depth 4 of the Desktop or `<team-comms>`, so the IV acceptance is unverified.
- **No cited results file is missing.** 15 claims (c-544..c-555) cite `.../results_*.txt`, and all 15 exist in `lab/codex_lab/experiments/`. F-42 (2 lines), F-43 (3 lines) and db-s88 also depend on codex_lab, which is **outside the repo**.
- **Unfiled returns outside the repo:** roach r15 (section 1.1).

### 1.4 Stubs: pre-move baseline (binding command, run from each stub's folder)

- 142 `*.prereg.sha256` files.
- **Strict command: 111 OK, 31 FAILED.** The 111 that pass are listed at the end of this file. 5 of them (`runs/s128/*_v1..v5`) pass **only from the project root**. Their header says so, but the AGENTS.md rule says to run from the stub's folder.
- Of the 31 failures, 24 pass under `tools/vkb/evidence.py::stub_check` (read and imported, not edited):
  - Superseded duplicate lines: n5, n6, s40.
  - Restored `.orig-<hex>` copies:
    - s23, s35, s47, s65.
    - s69, plus 14 later stubs that pin `s69_prefix_stream_memory.py`: s76, s79-s84, s87, s89-s91, s95, s96.
  - Relocated copies: roach r10, r13.
  - s114, whose DB snapshot is `vkb.orig-6615aa.sqlite`.
- **7 still fail: roach r6, r7, r8, r9, r11, r12, and s125.** These are the VKB's 7.
  - Roach r6-r12: every missing input (Gutenberg texts, ZL/IT files) is mirrored at `<local-path>`. I hashed every entry. All lines resolve: 6 stubs, 291 entries, 0 unresolved, counting the local relocated `runs/roach-r7/r7.py` and `r11.py`. They are verifiable, but not inside the repo.
  - s125: pins `data/vkb/vkb.sqlite` (4ed3497c...). The live DB was rebuilt at 00:57. The pinned snapshot survives as `data/vkb/vkb.sqlite.20261019-004344.previous` (sha256 prefix 4ed3497cfd73 matches), but stub_check only looks for `.orig-<hex>` names.
- **The live VKB is a stub-pinned file.** s114 and s125 pin `data/vkb/vkb.sqlite`, and every rebuild breaks them. D-071 ("no file named in any stub may move") conflicts with routine rebuilds.
- Pinned-file footprint (relevant to any move): root stubs name 2,386 distinct paths.
  - Root-level: 150 (142 .py, plus `PREREG-v2.md`, `results_s97.txt`, `results_s98.txt`, `results_s107.txt`, `results_m4_phase1_board.json`, `vx01_gate_seeds.json`, a stub).
  - data/: herbals_alchemical 731, herbals_period 442, external 299, anchor_A1/A1b/A0 604.
  - runs/s45, plus `runs/*/fit_*.json` and `cells.json`.
- VKB `runs` table: 250 runs, 123 with no stub. Of those with c-400+ claims: s105 (stage-1 HOLD) and db-s100 have none. s115 has three stubs (`s115_a0/a1/a1b`), but `evidence.py` does not map them to run id `s115`. That is a tool mapping gap.

### 1.5 VKB check (`python tools/vkb/check.py`: PASS, 0 fail, 10 warn)

| WARN | detail | class |
|---|---|---|
| folios without image_path: 50 | acquisition gap | acceptable (gap list) |
| quires without collation: 18 | Phase 7.4 gap | acceptable (gap list) |
| stub does not verify: 7 | r6-r9, r11, r12 (inputs on the V: mirror); s125 (snapshot under a `.previous` name) | **needs-fix** (copy inputs or teach stub_check; both are recoverable) |
| stub newer than results creation: 28 | 26 of 28: the results file was created, then the script was edited and re-hashed, and the results were **overwritten in place** by a rerun (results mtime > stub mtime). Examples: s70 created 02:55, stub and script 03:37, results rewritten 03:43; s72; s74; s85; s86; s88; s92. s87 and s89 are documented amendments (results finished before the stub was re-stamped). s93 and s96 were already rejected (D-064/D-065). Only some stubs carry AMENDMENT text: p4d1, s51, s52, s54, s69, s82, s83, s87, s89, s96 | **needs-fix (audit)**. This is the D-064/D-065 pattern on about 16 more runs, mostly Argon s70-s92. The "never overwrite" rule is broken. stub_ok does not prove freeze-before-data for these |
| runs with results but no claim: 10 | j4 (`orphan_results_ok`), n3b, n4b, s1, s25, s26, s29, s31 (historical series), vx01 (live, other session), db-s88 (Daybreak) | acceptable for the historical runs; **needs-fix** for vx01 (owner files it) and db-s88 (intake) |
| load-bearing F-04, F-06, F-34, F-40 unverified lines | F-04: Ninja-thread external. F-06: Reddy and Knight 2011, **no ref, paper not located in data/external**. F-34: s85 "impl" line, which the lead audit found not independent. F-40: two s92 lines (lead audit: written rule fails) | acceptable as marked (they do not count). Stale: the F-34 line should become axis `method` or be dropped |
| fake downloads: 3 | IVTFF spec (real copy held), Meister 1902 zip (real copy held), Greshko 2025 PDF (**not obtained**, O-018) | 2 acceptable (tombstone the fakes); Greshko **needs acquisition** |
| same measurement, different values | **none emitted** in this build | n/a |

### 1.6 FINDINGS-GRAPH

- **Findings with no lines: none** (51 findings).
- Thin findings:
  - 1 line only: F-10, F-49, F-50.
  - **Empty `claims: []`: F-42, F-43.** F-42's two lines (db-s95/96/97/106) and two of F-43's lines (db-s109, db-s111) cite Daybreak results **that have no CLAIMS row at all**.
- Lines with no `ref`: F-04 (Daybreak independent run), F-06 (Reddy and Knight), F-11 (Argon s36/s37), F-16 (Davis hands).
- **Hypotheses with no points: H-18 and H-20.** H-20 is the subject of 5 runs (P-68..P-72), 2 of them filed (P-69, P-72). P-72 put a line on F-33, but no point exists for H-20.
- Pending rows not closed, against the clock at 09:33 on 2026-10-19:
  - **P-52 roach r14**: briefed 2026-10-18 16:15, about 17 h ago. roach's r14 fixture was running at 17:16 and again at 20:47. No return has arrived. Over 12 h.
  - **P-62 r16**: briefed 21:05, about 12.5 h ago. The lead told roach to HOLD it at 00:52 (D-073 pivot message), but the row still says `briefed`. It should read `held`.
  - **P-65 r17**: briefed 21:18, about 12.25 h ago. It stays live under D-073. Over 12 h.
  - **P-56 r15**: says rejected or withdrawn, but a result was delivered (section 1.1).
- Run-id namespace: Daybreak's "r14 bc3075" (<team-comms>, 20:46-21:43) shares the name r14 with roach's P-52 r14. That is another id collision.

### 1.7 Registers: flagged claims still cited by findings

| claim | flag | cited by | class |
|---|---|---|---|
| c-417 | **STALE**: results_s74.txt was overwritten; the 49.8% / 1/15 numbers are gone. The current file shows L4 ZL3b at 4/15 | F-31 claims, plus a **verified (counted) split line** | **needs-fix**: mark the line unverified and restate F-31 from c-516. All 3 F-31 lines rest on the one overwritten file |
| c-349 | UNVERIFIED ("results_r1 on the second machine, not copied") | F-01 claims plus a counted impl line | stale flag: `runs/roach-r1r2-raw/results_r1.txt` now exists and shows IT +0.1731, B +0.22. **Re-verify and upgrade** |
| c-350 | UNVERIFIED | F-03 claims plus a counted impl line | same: results_r2 shows ZL B +0.2340, margin +0.0071, IT fails. Re-verify |
| c-535 | RECONCILED (D-064) | F-09 (line already `unverified`) | acceptable |
| c-335, c-352, c-359, c-372, c-410, c-427, c-430, c-432, c-433 | words such as FAILED, PARTIAL or superseded appear only inside VERIFIED amendment notes | various | acceptable |

## 2. What I verified and what I only inferred

Verified by command:
- `findings_graph.py sprawl` (09:25).
- `tools/vkb/check.py`.
- The binding stub command on all 142 stubs (bash loop), with fallback to root.
- `evidence.stub_check` on the 31 failures.
- Hash resolution of the r6-r12 inputs against the V: mirror.
- sha256 of every `data/vkb/*.sqlite*` file.
- r15 `MANIFEST.sha256 -c`.
- VKB SQL for the warning details.
- yaml parses of the graph for lines, claims, points and pending rows.
- The CLAIMS status scan.
- Results-file reference scan.
- Existence checks for every evidence path of c-559..c-590.
- CALL lines of 7 results files.
- File mtimes versus stub mtimes.

Inferred, or not checked:
- The 26 "rerun-after-refreeze" runs. I inferred an overwrite from creation time < stub mtime < last write. I did not read each script diff. It is possible that a dev run wrote the file before the freeze. Even then the file was overwritten.
- The IV acceptance of vx01 A1 (file not found).
- Whether the Reddy and Knight 2011 PDF is held under another name (searched `data/external` by name only).
- Hours since briefing come from <team-comms> file mtimes, not from the message bodies, except P-62 and P-65, which carry timestamps in their names.

## 3. Surprises

- A blind replication that disagrees (r15) has been sitting unfiled for 13 h while its P-row says it was withdrawn.
- The rule "never overwrite a results file" appears broken on about 16 more runs besides s93 and s96. stub_ok=1 hides this because the stub was re-hashed after the run.
- The live knowledge base `data/vkb/vkb.sqlite` is itself pinned by two stubs, so D-071 and VKB rebuilds conflict.
- X-09 is graded `verified` even though our own c-576 measures 22% unanimity per locus.
- F-42 and F-43 carry graded lines with no CLAIMS row and rest on files outside the repo.

## 4. Assumption candidates for the cleanup plan

1. "Every stub-pinned file is inside the repo." **False.** r6-r12 inputs live on `<local-path>`. Verify: rerun the resolver; copy into `runs/roach-rN/../` or teach stub_check about the mirror.
2. "Moving root .py files is safe if they are unpinned." Only true per file. 150 root files are pinned by root stubs, and later stubs (s76-s96) pin the same `s69_prefix_stream_memory.py`. Verify: build the union of pinned paths across all 142 stubs before any move, and re-run this baseline after the move. Expected: 111 OK strict, and the 7 known failures unchanged.
3. "codex_lab is an archive, not evidence." **False.** 15+ claims and 5 graded lines cite it. Verify: grep CLAIMS and the graph for `codex_lab` before any move or retire.
4. "stub_ok means pre-registered." False for the 28 stub-newer runs. Verify: compare results creation time, stub mtime and results last-write time per run.
5. "The VKB can be rebuilt freely." It breaks the s114 and s125 stubs unless the prior DB is kept under the `.orig-<hex>` name. Verify: run stub_check after each rebuild.

## 5. Prioritized fix list

| # | fix | effort | risk |
|---|---|---|---|
| 1 | Take in roach r15: copy the bridge folder to `runs/roach-r15/` (manifest-verified). Add a CLAIMS row with the printed call NO DRIFT (ZL/IT HIT, RF MISS). Add an F-50 impl line with `agrees: false`, so F-50 becomes CONTESTED. Correct the state of P-56 | low | low |
| 2 | Audit the 28 stub-newer-than-results runs: list which overwrote a frozen output. Treat the D-064/D-065 cases the same way (findings whose only lines rest on them go `unverified`). Start with F-31/s74 (c-417 is already STALE) | medium | medium (could demote findings) |
| 3 | F-31: mark the c-417 line unverified and restate it from c-516 or the current s74 numbers. Re-verify c-349 and c-350 against `runs/roach-r1r2-raw/` | low | low |
| 4 | Give F-42 and F-43 CLAIMS rows for db-s95/96/97/106/109/111 (intake audit), or mark those lines unverified | low | low |
| 5 | Make s125 and r6-r12 verify without editing stubs: copy the snapshot to `data/vkb/vkb.orig-4ed349.sqlite`, and mirror the roach corpora to the relative paths the stubs name (both are copies, not moves). Then stop pinning the live VKB in new stubs; pin a dated snapshot instead (decision row) | low | low |
| 6 | Link the 30 sprawl claims as in the table in section 1.2: 5 L entries, 2 N entries (transliteration disagreement with c-576/c-567/c-568, which also re-grades X-09; H-20 evidence with c-587), and 21 `standalone_claims` | low-medium | low |
| 7 | Pending rows: P-62 → `held` (D-073). Chase or close P-52 (r14, 17 h) and P-65 (r17, 12 h) through <team-comms>. Record the r14 id collision with Daybreak's bc3075 r14 in the alias map | low | low |
| 8 | Ask the vx01 owner (Voynich Analyst) to file `results_vx01_a1.txt` ("no segmenter ADEQUATE"). Until then flag X-01 as at-risk for F-11 and F-40. Do not touch the files (live work) | low | low |
| 9 | Mark c-575 STALE. Acquire Greshko 2025 (O-018) and Reddy and Knight 2011 (F-06 line ref). Tombstone the two fake downloads that have real copies | low | low |
| 10 | Tool gaps (an owner edits them; not edited here): evidence.py mapping of s115 to the `s115_a0` stub; recognize `.previous` VKB snapshots and the V: mirror; flag "results last-write > stub mtime" as its own WARN | medium | low |

Appendix: the 111 stubs that pass the strict command (hash-line counts in parentheses):
- n-series: n1 (1), n2 (2), n3 (5), n3b (4), n4 (17), n4b (1), n6_habit7k_glyph (1), n7 (1).
- p4: p4d1 (5), p4u1 (2).
- roach: r3, r4, r5 (1 each).
- s128 v1-v5 (8/18/28/50/63; **root only**).
- s100-s128: s100 (48), s101 (60), s102 (60), s103 (5), s104 (61), s106 (35), s107 (48), s108 (56), s109 (3), s111 (9), s115_a0 (2), s115_a1 (232), s115_a1b (212), s117 (7), s120 (2), s122 (6), s123 (27), s124 (1352), s126 (30), s128_p72 (6).
- s1-s45 (single-line unless noted): s10 (2), s15, s17 (2), s18 (2), s1_v2, s20, s21, s24, s27, s28 (2), s29, s2, s30, s31, s32, s33, both s34 stubs, s35_physical, s36, s37, s38, s39, s41, s42, s43, s44, s45.
- s48-s78 (single-line unless noted): s48, s49 (14), s50 (2), s51_b (5), s51_o051, s52_b (5), s52_p4comp1, both s53 stubs, both s54 stubs, s55 (16), s56, s57, s58, s59 (8), s60, s61 (2), s62 (9), s63, s64 (17), s66, s67 (19), s68 (2), s70, s71, s72, s73 (11), s74, s75 (8), s77, s78 (7).
- s85-s99: s85, s86 (16), s88, s92, s93, s97 (47), s98 (25), s99 (246).
- vx01: vx01_a1_gen (5), vx01_a1_known_answer (31), vx01_a1_metrics (2), vx01_common (2), vx01_seg_mdl (2).
