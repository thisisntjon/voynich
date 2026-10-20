# Phase 8.1 step 3: audit of runs re-run in place, and CLAIMS intake for F-42/F-43

Written 2026-10-19 09:55 PDT (clock read with `date`). Read-only: nothing else in the tree was edited. Owner: lead audit subagent (session <session>).

Sources read: VKB `runs` query (28 rows, stub_mtime > results_ctime), `workflow/research/phase8-findings-integrity.md` (sections 1.3-1.7, 2, 5), DECISIONS D-059..D-066, D-071, the lead's Argon audit messages in `workflow/comms/` (S70-S75 REVIEW 10:16Z, S73-S75 AUDIT 11:30Z, S85-S92 AUDIT 16:24Z, S93 INTEGRITY, S96 REJECTED), every stub's comment lines, NTFS creation and last-write times of each results file, script and stub, CLAIMS.md, and `workflow/FINDINGS-GRAPH.yaml`. Grade effects were computed with `tools/findings_graph.py::grade()` on an in-memory copy of the graph (the file was not touched).

## Part A. 28 runs whose stub is newer than their results file's creation

### A.1 What the times show

- 26 of 28 results files were written again after the stub was re-stamped (last write > stub mtime > creation). This matches the integrity report's count of 26.
- s87 and s89 were not overwritten: the amended run wrote `results_s87_amend1.txt` and `results_s89_amend1.txt`, and the original file's last write precedes the stub change.
- What would refute "the first output was a real verdict that was later replaced": a first run that crashed or was killed before printing a verdict. This can be checked only where the first output survives or a filing read it.
  - **Checked, first verdict existed:** s74 (c-417 numbers filed by D-059 are gone from the file), s70 and s75 (D-059 read their first summaries), s93 (Daybreak audit, D-064), s96 (D-065), s33 (c-335 notes a 21:23 run, superseded).
  - **Checked, first output was a crash or refusal and is kept:** p4d1, s52, s69, s82, s99. For s83, the stub records a native crash before any fold finished; there is no kept output, but there was nothing to keep.
  - **Not checked (unverified):** s2, s35, s36, s37, s38, s51, s54, s63, s72, s73, s85, s86, s88, s92. For these the first file content is lost.
- Caveat on NTFS creation time: a file deleted and recreated within about 15 s keeps its old creation time (tunnelling). A creation time also marks when a run *started* writing. s72 was "still running" at 03:14 per D-059, although its file was created at 02:55.
- **D-063's premise was wrong for these runs.** The S85-S92 audit message says "every stub predates its results". That is true of the last write only. By creation time, all four results files (s85, s86, s88, s92) predate their stubs.

### A.2 Per-run table

Times are PDT on 2026-10-17 (p4d1 to s51) and 2026-10-18 (s52 onward), in the order: results created → script edited → stub re-stamped → results last written. "lines" lists `F-xx:axis`; `(unv)` means already unverified and `(dis)` means agrees: false.

| run | owner | timeline | ruling already made | claims | graph lines | disposition |
|---|---|---|---|---|---|---|
| p4d1 | lead | stub 22:29:12 → created 22:29:22 → crash; script + AMENDMENT 1 22:31:16 → rewritten 22:41:48 | c-355 VERIFIED with amendment; crash partial kept as `results_p4d1_core_order.run1-crashed.txt` | c-355 | none | **keep** |
| s2 | lead | 19:49:02 → 19:50:12 → 19:50:24 → 19:51:33 | none; the stub has no comment at all | c-306..c-310 | none | **post-hoc** (no grade effect) |
| s33 | Argon | 21:26:59 → 21:36:55 → 21:38:57 → 21:39:49 | c-335 notes the 21:23 run as "superseded"; VKB quarantined (D-065) | c-335, c-336 | F-11:impl, F-11:data | **post-hoc** |
| s35 | Argon | 21:27:35 → 21:36:37 → 21:37:35 → 21:39:01 | quarantined (D-065); c-339 says "stub before run", which is true only of the rerun | c-339..c-341 | F-18:physical, F-18:impl | **rerun (new id)** |
| s36 | Argon | 22:45:55 → 23:14:16 → 23:14:16 → 23:23:06 | quarantined (D-065) | c-361, c-362, c-366, c-367 | F-29:impl, F-29:split, F-29:data | **rerun (new id)** |
| s37 | Argon | 22:17:29 → 22:24:57 → 22:25:07 → 22:26:20 | quarantined (D-065) | c-363, c-364, c-367 | F-27:impl | **rerun (new id)** |
| s38 | Argon | 22:31:45 → 22:36:59 → 22:37:09 → 22:38:18 | quarantined (D-065) | c-365, c-368, c-369 | none | **post-hoc** (no grade effect) |
| s51 | Argon | 23:49:51 → 23:51:14 → 23:51:32 → 23:55:28 | two SUPERSEDED pre-crash lines in the stub; the second fix (c2i on shuffle) changes the null; crash output not kept; quarantined (D-065) | c-370, c-373, c-374 | F-08:impl, F-15:impl, F-16:impl, F-27:data | **post-hoc** (lowest risk; can become keep if the lead audit accepts the crash record) |
| s52 | lead | stub 23:59:20 → created 00:01:10 (run 1 FAILED) → script + AMENDMENT 1 00:01:27 → 00:04:04 | c-372 VERIFIED with amendment; run 1 kept at `runs/s52/run1_FAILED_results.txt` | c-372 | none | **keep** |
| s54 | lead | 00:03:10 → 00:07:11 → 00:07:24 → 00:08:29 | stub SUPERSEDED line: run 1 completed with a Part 3B input bug; run 1 output not kept | c-379..c-381 | none | **post-hoc** (no grade effect) |
| s63 | Argon | 01:40:40 → 01:49:01 → 02:02:00 → 02:03:18 | quarantined (D-065); c-502 and c-503 already STALE | c-502, c-503, c-508, c-509 | F-22:impl | **post-hoc** |
| s69 | lead | created 02:08:29 → run 1 FAILED 02:12:20 → AMENDMENT 1 02:13:08 → 02:17:37. The script mtime of 12:17 is the D-071 text rewrite, and `.orig-785e5c` verifies | c-410 VERIFIED with amendment; run 1 kept as `runs/s69/run1_FAILED_*`; D-071 | c-410 | F-14:data, F-14:split | **keep** |
| s70 | Argon | 02:55:44 → 03:37:34 → 03:37:34 → 03:43:13 | D-059 held the first output (intervals exclude their own points); the rerun was requested, but in place; quarantined (D-065) | c-422, c-423, c-512, c-513 | F-13:impl, F-18:physical, F-22:seg | **post-hoc** |
| s72 | Argon | 02:55:06 → 03:33:41 → 03:33:58 → 04:32:31 (D-059: "still running" at 03:14) | quarantined (D-059, D-065) | c-520, c-521 | F-25:impl | **post-hoc** |
| s73 | Argon | 03:21:56 → 04:17:03 → 04:17:03 → 04:18:15 | D-059 at 03:14: "s73 has no stub", so the first run had no stub at all; quarantined (D-065) | c-514, c-515 | F-35:impl, F-35:method, F-35:data, F-36:impl | **rerun (new id)** |
| s74 | Argon | 02:48:28 → 03:29:46 → 03:29:55 → 03:31:26 | c-417 filed on the first output (D-059), then marked STALE; lead message 11:30Z: "never overwrite"; quarantined (D-065) | c-417 (STALE), c-516 | F-31:split/c-417, F-31:impl, F-31:data/c-516 | **rerun (new id)** |
| s75 | Argon | 02:51:31 (run 03:01) → 03:07, then 03:17:08 → 03:17:18 → 03:18:45 | D-059: not filed, "re-freeze and re-run"; lead 11:30Z: "the s75 re-freeze is valid"; D-065 (later) requires a new id | c-517..c-519 | F-32:impl, F-37:impl, F-38:impl | **rerun (new id)** |
| s82 | lead | stub 03:41:15 → created 03:41:31 → crash 03:47:44 → script 03:48:06 → stub 03:48:24 → 03:58:30 | FAILED/AMENDMENT lines (json default only); crash log and `runs/s82/results_run1-crashed.txt` kept; D-060, D-061 | c-427 | F-25:method, F-25:data | **keep** |
| s83 | lead | script 04:20:03 → stub 04:20:16 → created 04:20:50 → native crash → stub 04:26:45 (hash lines unchanged) → 05:38:41 | FAILED/AMENDMENT lines: same frozen files re-run; D-060, D-061 | c-430 | F-39:split, F-39:data, F-39:method | **keep** |
| s85 | Argon | 05:07:50 → 05:21:04 → 05:21:21 → 05:32:15 | D-063 contested its verdicts; the premise was wrong (see A.1); quarantined (D-065) | c-522..c-524 | F-05:impl, F-24:impl(unv), F-24:seg, F-26:method(dis), F-26:data, F-30:seg, F-34:seg(dis), F-34:impl(unv), F-37:method(dis), F-37:data, F-38:split, F-38:seg, F-38:data | **rerun (new id)** |
| s86 | Argon | 05:16:16 → 05:26:19 → 05:26:34 → 05:38:55 | D-063, D-065, D-066 | c-525..c-527 | F-02:data, F-02:split, F-02:physical, F-21:data/seg/physical(unv), F-21:split(dis), F-33:impl, F-33:seg, F-39:impl | **rerun (new id)** |
| s87 | lead | stub 05:58:34 → created = last write 05:59:32 → script 06:00:33 → stub 06:00:52 → `results_s87_amend1.txt` 06:01:19 | not overwritten; AMENDMENT 1 authorised by the lead; D-061, D-066 | c-431, c-432 | F-40:method, F-40:data | **keep** |
| s88 | Argon | 06:34:37 → 07:32:56 → 07:33:06 → 07:40:46 | D-063, D-064, D-065, D-066 | c-528..c-530 | F-05:split, F-23:split/seg/physical, F-36:order, F-36:data, F-39:seg, F-39:seg(dis), F-39:order | **rerun (new id)** |
| s89 | lead | stub 06:38:33 → created 06:38:47, last write 06:39:12 → script 06:40:01 → stub 06:40:18 → `results_s89_amend1.txt` 06:40:37 | not overwritten; D-062; P-21 uses amend1 | none (exact-name scan) | none | **keep** |
| s92 | Argon | 08:06:31 → 08:29:17 → 08:29:45 → 08:33:01 | D-063 (written rule fails), D-065 | c-531..c-533 | F-40:seg(unv), F-40:order, F-40:physical(unv), F-40:physical(dis) | **post-hoc** |
| s93 | Argon | 09:01:58 → 10:02:42 → 10:02:52 → 10:17:21 | **rejected, D-064**; `results_s93_frozen1.txt` exists | c-534..c-536 (RECONCILED) | F-09 x3 (unv), F-16:physical(unv), F-41:method(unv) | **already rejected; no action** |
| s96 | Argon | 10:55:57 → 12:03:02 → 12:03:27 → 12:15:19 | **rejected, D-065**; frozen1/frozen2 files exist | c-537..c-540 | none | **already rejected; no action** |
| s99 | lead | rev0 stub 12:22:36 refused (CR byte) → created 12:22:43 → rev1 stub 12:23:07 → 12:24:34 | no scoring ran under rev0 (refusal kept at `runs/s99/results_s99_refused_rev0.txt`); D-066 | c-437 | F-44:physical, F-44:seg(unv) | **keep** |

### A.3 Count per disposition

| disposition | n | runs |
|---|---|---|
| keep (amendment documented, first output was a crash or refusal or is kept, accepted at filing) | 8 | p4d1, s52, s69, s82, s83, s87, s89, s99 |
| already rejected (D-064/D-065), no further action | 2 | s93, s96 |
| re-grade lines "post-hoc" (stop counting); no rerun needed for any standing finding's grade | 9 | s2, s33, s38, s51, s54, s63, s70, s72, s92 |
| post-hoc **and** needs a rerun under a new id to restore a standing finding | 9 | s35, s36, s37, s73, s74, s75, s85, s86, s88 |

- Rerun criterion: once all post-hoc lines stop counting, a `standing` finding falls to SINGLE or loses every verified line.
- Any rerun is new structural compute. D-073 stopped that, so each rerun needs a lead decision. Until a decision is made, the post-hoc downgrade applies.
- A rerun must use a new id, thresholds frozen before seeing the original outcome, and preferably blind (roach), per D-065.

### A.4 Grade effect if every post-hoc line (18 runs) stops counting

Computed with `findings_graph.grade()` on a copy of the graph. ◆ means load-bearing.

- **To SINGLE or no verified line:**
  - F-02: TRIANGULATED → SINGLE (method)
  - F-18: TRIANGULATED → SINGLE (method)
  - F-27: TRIANGULATED → SINGLE (method)
  - F-29: TRIANGULATED → SINGLE (method)
  - F-31: TRIANGULATED → no verified line
  - F-35: TRIANGULATED → no verified line
  - ◆F-36: TRIANGULATED → SINGLE (split)
  - F-38: TRIANGULATED → no verified line
  - F-26: CONTESTED → SINGLE (method)
  - F-37: CONTESTED → no verified line
- **To CORROBORATED:**
  - F-05 (data, method)
  - F-08 (method, seg)
  - F-16 (method, split)
  - F-22 (physical, split)
  - ◆F-25 (data, method)
  - F-32 (data, order)
  - F-33 (data, physical)
- **Unchanged grade:**
  - ◆F-11, ◆F-13, ◆F-15, F-24, ◆F-39 and F-40 stay TRIANGULATED or CORROBORATED.
  - ◆F-23, ◆F-30 and ◆F-34 stay CONTESTED.
  - F-21 stays SINGLE.
- For a finding with no verified line, the tool prints "SINGLE" with an empty axis set. The render should show it as ungraded.

### A.5 F-31 exactly

- F-31 has three lines, all with `ref: results_s74.txt`:
  - split/c-417
  - impl (Argon s74)
  - data/c-516
- Its current grade is TRIANGULATED on {data, impl, split}.
- **If the c-417 line alone stops counting: F-31 becomes CORROBORATED** (data, impl; 2 axes).
- If the s74 rerun is treated as post-hoc, as proposed: all three lines rest on the overwritten file and none counts. F-31 has **no verified line**; the tool prints SINGLE with an empty axis set. That stays so until an s74 rerun under a new id is filed.
- The H-05 scoreboard does not move either way. F-31's point on H-05 is `weak`, and weak points weigh 0.
- Note: c-516 (the surviving numbers) still has L4 failing the ≥8/15 LOQO rule (4/15, 3/15, 1/15). F-31's statement "0-2/15" quotes the lost c-417 numbers and is stale.

## Part B. F-42 and F-43: drafted CLAIMS rows

### B.1 What was found

- F-42 cites db-s95, db-s96, db-s97 and db-s106 (refs: the s96 and s97 files). F-43 cites db-s109 and db-s111 (refs: those files) plus c-455 and c-548, which already exist.
- All six results files are in `lab/codex_lab/experiments/`.
- Identical copies are in `<team-comms>` (same sha256). None is in the repo.
- Each stub verifies with the binding command:
  - s95: 7/7 OK
  - s96: 8/8 OK
  - s97: 7/7 OK
  - s106: 7/7 OK
  - s109: 5/5 OK
  - s111: 5/5 OK
- Each stub's mtime precedes the results file's creation. Creation equals last write, so none of these files was overwritten.
- **Correction needed in F-42's statement:**
  - "+0.039" and "+0.059" are the **fixture** values (`fixture_pass=True past_vs_freq=+0.039141 past_vs_cross=+0.058511`, line 4 of the s96 file).
  - On the manuscript, the s96 deltas are +0.0032 to +0.0050 (past_vs_freq) and +0.0036 to +0.0038 (past_vs_cross).
  - The statement should quote those deltas or cite the claim ids.
- **F-42's second line** cites only the s97 file, although its `by` text also names db-s106. db-s106 has its own file (below).
- Proposed ids c-593..c-598 follow the current maximum (c-592). They are provisional: renumber if another session files first.

### B.2 Drafted rows (layout of the last row, c-592; not written to CLAIMS.md)

All six are VERIFIED: I opened each file and saw these numbers on the lines given. Paths are abbreviated in the same way as c-548; the full prefix is `lab/codex_lab/experiments/`.

```
| `c-593` | db-s95 (Daybreak, imports our loaders/metrics) tail-core repeat propensity, 15 folds per transliteration: cross_vs_freq -0.0006 [-0.0022,+0.0009] / -0.0008 [-0.0020,+0.0004] / +0.0004 [-0.0015,+0.0023]; local_vs_freq +0.0055 [+0.0030,+0.0080] / +0.0045 [+0.0024,+0.0065] / +0.0069 [+0.0044,+0.0095]; local_vs_cross +0.0062 / +0.0053 / +0.0065 (all CIs > 0) on ZL3b/RF1b/IT2a -> C1_STABLE False, C2_LOCAL True, C3_LOCAL_OVER_CROSS True, VERDICT QUIRE_LOCAL_PROPENSITY | quire-local propensity, not stable cross-quire | `.../results_s95_tail_core_repeat_transfer.txt` (sha256 fcbfe34c…; copy in <team-comms>) | lines 6-25 | 2026-10-18 | VERIFIED 2026-10-19 09:55: file opened, numbers seen; stub 7/7 OK; stub 08:48:40 < results 08:48:51 (created = last write) | F-42 (split line statement) |
| `c-594` | db-s96 forward vs backward quire tail prediction: past_vs_freq +0.0038 [+0.0014,+0.0061] / +0.0032 [+0.0012,+0.0051] / +0.0050 [+0.0026,+0.0073]; past_vs_cross +0.0038 / +0.0036 / +0.0037 (CIs > 0); future_vs_freq +0.0045 / +0.0039 / +0.0054; past_vs_future -0.0003 [-0.0033,+0.0028] / -0.0004 [-0.0032,+0.0022] / -0.0001 [-0.0029,+0.0029] on ZL3b/RF1b/IT2a -> C1_FORWARD True, C2_FORWARD_OVER_CROSS True, C3_FUTURE True, C4_FORWARD_DIRECTIONAL False, VERDICT FORWARD_SUFFICIENT_SYMMETRIC_CLUSTER (the +0.039/+0.059 on line 4 are fixture values) | order-symmetric quire tail pool | `.../results_s96_forward_quire_tail_prediction.txt` (sha256 de9f4a66…; copy in <team-comms>) | lines 4-29 | 2026-10-18 | VERIFIED 2026-10-19 09:55: file opened, numbers seen; stub 8/8 OK; stub 08:51:55 < results 08:52:07 (created = last write) | F-42 split line |
| `c-595` | db-s97 codicological scale of tail recurrence, 15 folds: quire_vs_cross +0.0046 [+0.0019,+0.0072] / +0.0046 [+0.0024,+0.0069] / +0.0070 [+0.0040,+0.0100]; sheet_vs_quire +0.0026 [+0.0010,+0.0045] / +0.0012 [-0.0003,+0.0029] / +0.0014 [-0.0002,+0.0030]; leaf_vs_sheet -0.0010 / -0.0006 / -0.0006 on ZL3b/RF1b/IT2a -> C1_QUIRE True, C2_SHEET False, C3_LEAF False, VERDICT QUIRE_REGISTER_POOL | quire/register scale, not sheet or leaf | `.../results_s97_tail_core_codicological_scale.txt` (sha256 05e6e9d0…; copy in <team-comms>) | lines 6-21 | 2026-10-18 | VERIFIED 2026-10-19 09:55: file opened, numbers seen; stub 7/7 OK; stub 09:01:14 < results 09:01:23 (created = last write) | F-42 method line |
| `c-596` | db-s106 cross-fitted forward-tail prediction (bootstrap 2000): past_vs_freq +0.0038 / +0.0027 / +0.0023 (CIs > 0); past_vs_cross +0.0034 [+0.0010,+0.0059] / +0.0032 [+0.0010,+0.0054] / +0.0006 [-0.0022,+0.0032]; past_vs_future -0.0002 / -0.0002 / +0.0001 (CIs span 0) on ZL3b/RF1b/IT2a -> CALLS_TWO_OF_THREE past_vs_freq/past_vs_cross/future_vs_freq True, past_vs_future False; CALLS_ALL_THREE past_vs_cross False (IT2a); VERDICT FORWARD_SUFFICIENT_SYMMETRIC_CLUSTER | db-s96 holds under cross-fitting; past-over-cross fails on IT2a | `.../results_s106_crossfit_forward_tail_prediction.txt` (sha256 5051d594…; copy in <team-comms>) | lines 6-24 | 2026-10-18 | VERIFIED 2026-10-19 09:55: file opened, numbers seen; stub 7/7 OK; stub 10:19:48 < results 10:19:54 (created = last write) | F-42 method line (named in `by`, file not yet in `ref`) |
| `c-597` | db-s109 quire-controlled label-to-body page retrieval (fixture MRR 1.000 > q99 0.5625): quire groups 4, pages 22, events 173, MRR 0.630 [0.476,0.857] vs null q99 0.588, p 0.0020, top-1 0.455 vs q99 0.409 (p 0.0060); register groups 3: MRR 0.533 vs q99 0.493 (p 0.0025) -> C1_QUIRE_PAGE_LINK True, C2_REGISTER_PAGE_LINK True, VERDICT LABEL_PAGE_BODY_ANCHOR_CANDIDATE | candidate label-page link (one core representation) | `.../results_s109_label_page_body_retrieval.txt` (sha256 d90059e9…; copy in <team-comms>) | lines 3-8 | 2026-10-18 | VERIFIED 2026-10-19 09:55: file opened, numbers seen; stub 5/5 OK; stub 10:43:52 < results 10:44:03 (created = last write) | F-43 method line |
| `c-598` | db-s111 segmenter-free label anatomy: RawWord MRR 0.379 (q99 0.559, p 0.78); RawTrim1 0.521 (q99 0.551, p 0.025); GlyphTrim1 0.513 (q99 0.562, p 0.056); RawEdge2 0.374 (q99 0.524, p 0.60); paired inner-edge delta +0.121 vs q99 +0.148 (p 0.031) -> C1_FIXED_INTERIOR False, C2_EDGE_INSUFFICIENT True, C3_INTERIOR_BEATS_EDGE False, VERDICT NO_SEGMENTER_FREE_LABEL_LINK | label link not segmenter-free | `.../results_s111_segmenter_free_label_anatomy.txt` (sha256 cebb9416…; copy in <team-comms>) | lines 3-11 | 2026-10-18 | VERIFIED 2026-10-19 09:55: file opened, numbers seen; stub 5/5 OK; stub 10:51:30 < results 10:52:28 (created = last write) | F-43 seg line (agrees: false) |
```

Filing notes, for whoever writes them:
- Add `claims: [c-593, c-594, c-595, c-596]` to F-42 and `claims: [c-455, c-548, c-597, c-598]` to F-43. Add a `claim:` key to each line.
- Point F-42's method line at the s106 file as well, or split it into two lines.
- Fix the F-42 statement's fixture numbers (B.1).
- The evidence lives outside the repo. Copying it to `runs/db-sNN/` (copies, not moves) would remove that dependency.

## What I could not determine

- For 14 runs (s2, s35-s38, s51, s54, s63, s72, s73, s85, s86, s88, s92), whether the first results file held a verdict, a crash or a dev run: the content is gone. The post-hoc disposition does not depend on the answer, because a stub frozen after a real-data file exists is not a pre-registration.
- Whether a lead audit after D-065 lifted the quarantine. No decision row through D-074 mentions one. The VKB still marks these runs `quarantined`.
- For s89, no CLAIMS row cites `results_s89.txt` by exact name; its claims, if any, cite the amend1 file. I did not trace them.
