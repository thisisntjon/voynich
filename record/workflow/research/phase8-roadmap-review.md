# Phase 8 roadmap: adversarial review
Date: 2026-10-19 09:39 PDT (from `date`). Reviewer: read-only subagent. Inputs: workflow/PLAN.md "### Phase 8" and the (Phase 8) registry rows; phase8-synthesis.md; phase8-findings-integrity.md section 5; phase8-stress-test.md; phase8-source-of-truth.md; AGENTS.md binding rules; the three VKB stub pins (grep of *.prereg.sha256).

## 1. Ordering
- **O1. 8.2 intake before the 8.3 id rule.** 8.2 adds claims and VKB runs rows for db-S124..S141, R14, Grok s128 and roach-12B audits. Two of these are collision cases now: Daybreak "r14 bc3075" vs roach P-52 r14, and Grok s128 vs lead s128 (integrity report; synthesis section 1). Filing them before the prefix rule writes new ambiguous rows, which 8.3 then has to renumber. **Fix:** move "owner run-id prefixes, atomic claim (runs/<id>/), alias rows for r14/s128" and the duplicate-id check in sprawl into 8.1. Leave the canonical map table in 8.3.
- **O2. 8.1 VKB rebuild against stub pins.** The live file data/vkb/vkb.sqlite is pinned by three different hashes (s114 6615aa, s125 4ed349, s128_p72 a830e2). At most one stub can pass at any time, and every rebuild breaks the one that currently passes. The .orig-<hash6> copies keep the bytes, but a stub verifies its named path, so it still fails. D-071 binds scripts, not data, so the rebuild does not violate it. It does violate criterion 3 ("no new verification failures"), because a rebuild is exactly such a failure. **Fix:** before any rebuild, record a decision row (integrity fix #5) saying that new stubs pin a dated snapshot, never the live DB, and that the stub sweep resolves live-VKB pins against the .orig copies. Take the 8.1 stub-sweep baseline *before* the rebuild, not alongside it.
- **O3. Freeze the bank before any fix.** The bank and its baseline are listed alongside the graph fixes. If the X-01/F-31 fixes land first, the baseline is already improved. **Fix:** make "bank frozen by hash plus baseline" step 0 of 8.1.

## 2. Missing work
- **M1.** Integrity fix #2 (audit the 26-28 runs that were re-run in place or have a stub newer than their results) is absent; 8.1 lists only F-31. Criterion 8 nonetheless requires every fix to be done or dispositioned. **Add** it to 8.1, or give it a dated deferral row.
- **M2.** Integrity fix #7 (chase or close P-52 r14 and P-65 r17 through <team-comms>) is absent. **Add** it to 8.2.
- **M3.** O-073 (the s127 manifest is off by one for 204 rows) is in the gap list but in no sub-phase. **Add** it to 8.5 as "fix the manifest as a new file, or tombstone it". Page facts built on it give wrong folio answers.
- **M4.** workflow/comms (27 of 28 files are byte copies of <team-comms>) appears in the synthesis but has no step. **Add** a declared-mirror line in 8.4, and file the one repo-only message to <team-comms>.
- **M5.** Coordination with the Codex cleanup has no checkpoint. **Add** to 8.1: confirm by <team-comms> ack that Codex writes nothing in this tree, and add a registry assumption "the Codex split holds" with a check (an mtime scan of files Codex could touch) at each sub-phase end.
- **M6.** The D-072/D-073 research track writes to CLAIMS, LEARNINGS, the graph and the VKB at the same time as Phase 8 does. Nothing in the roadmap serializes those writes. **Add** a rule: register and graph edits are append-only with id allocation via the 8.1 atomic claim; re-run sprawl and the VKB lag check after each sub-phase, not just once.
- **M7.** Integrity fixes #8 (vx01 owner files results_vx01_a1) and #10 (tool gaps, owner edits) depend on other sessions. The declarations assumption is already invalidated. **Add** a disposition path ("flag at-risk in the graph and stop") so criterion 8 can close without their action.

## 3. Criteria that need a judgment call
- **C2** ("every duplicate home retired or declared derived") has no list. **Reword:** "each of the N homes in phase8-source-of-truth.md's table has a status cell"; fix N now.
- **C4** ("every team artefact outside the repo") is unbounded; <team-comms> alone has 426 matching names. **Reword:** "every item in phase8-team-external.md's numbered list, plus anything newer than a fixed scan date found by the same scan command".
- **C5** says "every acquirable item is pulled", while the stopping rule says to stop after two null batches. The two contradict each other. **Reword:** "every listed gap has acquire / not-acquired-with-reason status; acquisition stops by the rule".
- **C7**: "no answer slower" needs a defined unit (opens plus calls, not seconds) and an answering agent that has not seen the fixes. Otherwise contamination decides the result. **Reword:** the acceptance run is done by a fresh agent (or roach) with the bank's hash checked.
- **C1** "0 unreferenced results": state whether the 536 root results count. If they do, this is the largest task in the phase and no sub-phase owns it.

## 4. Assumptions with no verification point
- A1 ("declaration plus indexing is enough") is marked verified from 6 timed questions only. **Re-verify** it on the 20-question baseline in 8.1.
- No registry row covers: the VKB rebuild is deterministic (needed to compare lag); the Codex split holds; the D-073 track does not collide with Phase 8 ids. **Add** these with check points at the 8.1 and 8.3 exits.

## 5. Breakage risks with no mitigation
- **The VKB builder glob.** evidence.py:1193 reads only ROOT/results_*.txt plus runs/*, so any results file moved by curate drops silently. 8.4 says "zero-risk clutter only" but never names the guard. **Add:** curate moves exclude results_*, *.prereg.sha256 and anything in the 2,454-path pin set; a VKB run count before and after each move must match.
- **findings_graph refs.** Graph ref lines name file paths. **Add** "findings_graph.py render plus sprawl show no new missing refs" to the 8.4 exit check alongside the stub sweep.
- **External_items moving from world.py to a data file** (8.2) changes how the VKB is built. **Add** a before/after row-count diff of external_items. world.py is not in any stub I grepped (root and runs/*/ stubs only; other stub locations unverified).
- **Concurrent writers:** see M6.

## 6. Cleanup theatre (changes no researcher answer)
- 8.4 "tombstoned curate moves of zero-risk clutter": no bank question gets faster (stress-test). **Cut**, or make it conditional on a bank question it speeds up. Moving MSI f1r off C: is a disk task, not knowledge work.
- 8.4 "generated LEARNINGS index" and "page_facts duplicates flagged": keep only if they map to a bank question.
- 8.3 "malformed DECISIONS rows repaired": keep (it is cheap, and the blank row hides rows from parsers). "One assumption registry named" is wording; merge it into the canonical map.
- 8.5 lists fixed acquisitions (5 transliterations, 7 MSI folios at about 33 GB, papers) before applying the gate. **Reword** it as candidates ranked by which pending test or D-072/D-073 gate each one feeds; acquire in batches of up to 2 items.

## Verdict: ready after fixes

Top 5 fixes, ranked:
1. Freeze the bank and take the baseline as 8.1 step 0, scored later by a fresh agent (O3, C7).
2. Before any rebuild: a decision row on live-VKB pinning and a stub sweep that resolves pins against the .orig copies (O2).
3. Move the run-id prefix, atomic claim and duplicate-id check into 8.1, ahead of 8.2 intake (O1, M6).
4. Bound C2, C4, C5 and C1 to enumerated lists; resolve the conflict between C5 and the stopping rule.
5. Add the 26-28 re-run-in-place audit, the r14/r17 chase, O-073, and a Codex-split check; cut the clutter moves unless a bank question needs them.
