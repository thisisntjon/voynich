# Phase 8 synthesis: knowledge consolidation
Date: 2026-10-19 09:36 PDT (from `date`). Inputs: phase8-census-duplication.md, phase8-source-of-truth.md, phase8-findings-integrity.md, phase8-team-external.md, phase8-completeness-gaps.md, phase8-stress-test.md.

## Verdict on Jon's hypothesis: REFINED
"Clean up sprawl and duplication; make knowledge organized and complete" holds as a goal. The method changes:
- **Moving files is the wrong lever.**
  - 142 stubs pin 2,454-2,627 paths, 161-285 of them at the repo root.
  - The VKB builder silently drops moved results.
  - Four other sessions write in parallel.
  - The 2026-10-18 curate pass scored 100/100 while onboarding load rose 2.5x.
  - None of the 6 timed researcher questions would get faster from moves (stress-test).
- **The real problems are integrity and integration, not clutter:**
  - unfiled results;
  - stale derived views;
  - contradictory copies;
  - team work invisible to the repo;
  - id collisions.
- **"Complete, literally" needs a stopping rule.** Acquire what feeds a pending test or a D-072/D-073 gate. Stop after two acquisition batches that change no grade.

## Cross-angle picture
1. **Integrity defects that change answers. Fix first.**
   - roach r15b was delivered complete and never filed. **Fixed in this phase:** c-591, L-361, and F-50 now CONTESTED.
   - X-01 is shown discharged on 9 findings in FINDINGS-MAP while the evidence says at-risk (vx01 A1: no segmenter adequate). The fix belongs in the graph's s76 `discharges` lines, not in the hand-edited FINDINGS-MAP_X01-FIX copy.
   - 26 runs were re-run in place after freeze (Argon s70-s92, D-064/D-065 pattern). F-31 rests entirely on c-417, which is STALE.
   - F-42 and F-43 cite Daybreak runs that have no CLAIMS row (`claims: []`).
   - The VKB lags the registers: 3 claims, 5 learnings, 1 open item behind. external_items is a day stale.
   - TEAM-HANDOFF still says s124 is unfiled. One VKB row merges two different s128 runs.
   - Three VKB versions are pinned by stubs. The s125 version survived only as a rotating backup. **Fixed in this phase:** vkb.orig-6615aa/4ed349/a830e2 (L-360).
2. **Unintegrated team work.** It exists, but the repo has no claim and no external_items row for it:
   - Daybreak db-S124..S141; audit-D graded S128-S135, but none of them is filed;
   - roach-12B's 7 independent-audit PASS reports;
   - the Fontana GPU campaign (alignment passes, glyph recognition fails);
   - Egerton Ventura held-out (BELOW_THRESHOLDS 0.686 vs 0.90);
   - R14 Barcelona (primary_pass);
   - Grok's s128 herbal calibration;
   - vx01_a1 (no segmenter adequate);
   - the 15 root .md files of the vx01 series, all undeclared.
3. **Source-of-truth ambiguity.**
   - Most fact kinds have 2+ homes. 10 of 19 spot-checked facts disagree across homes.
   - AGENTS.md calls TEAM-HANDOFF the measurement map, while README and TRIANGULATION say CLAIMS.
   - Assumptions live in two registries: PLAN U-items and graph X-ids.
   - external_items rows are Python literals in world.py, which breaks the D-070 "derived" rule.
   - workflow/comms holds 27 of 28 files that are byte copies of <team-comms>
4. **Id collisions.**
   - Shared run ids: s100-s111, s127, s128.
   - The same decision is recorded twice (D-072/D-073).
   - The D-054 id bands are abandoned.
   - Seven DECISIONS rows are malformed, and one blank line splits the table.
5. **Clutter.** Real, but low value to fix:
   - 32 unreferenced screenshots (75% of root bytes);
   - 610 byte-identical duplicate groups (109 MB, mostly data/external);
   - 11 .previous and 5 .failed VKB builds;
   - MSI f1r (3.8 GB) still on C:.
   - 671 root files are movable, but no question gets faster from moving them.
6. **Gaps that matter for triangulation.**
   - MSI for 7 more folios (about 33 GB, public).
   - 5 transliterations held but not loaded (GC, FSG, Currier, VT, LSI).
   - Open papers not held: Reddy & Knight, Amancio, 13 VOY2022 papers, Bax 2014.
   - McCrone is an image-only scan; the Taiz file is 0 bytes.
   - Section S has no labels and thin page facts; section B has no colour facts.
   - The s127 facsimile manifest is off by one (O-073).
   - VKB sources is stale.
7. **Duplicate cleanup effort.** Codex is running the same cleanup in yonichmanuscript. Jon chose a split by repo (09:35), and the split was sent via <team-comms>.

## Conflicts between angles
- **Stub pin counts:** census 2,454 vs stress-test 2,627. They count different things (unique paths vs path mentions). The plan uses the census set: unique, resolved paths.
- **Unlinked claims:** integrity says 5 to existing findings, 2 new findings, 21 standalone. Stress-test says about 21 are literature or data facts. These agree.
- **The D-067/D-073 collision:** source-of-truth could not find it. The lead created it and renumbered it to D-073 at 00:53, so it is resolved.

## Assumption candidates (seed the registry)
- A1: Declaration plus indexing gives most of the benefit without moves. Verified by the stress-test timings. Holding.
- A2: The 20-question cold-start bank measures improvement. Unverified until the bank is frozen and the baseline is taken.
- A3: Other sessions will honour declarations about their files. Invalidated on 2026-10-18 (Daybreak ignored the not-canonical request). Mitigation: index their files read-only, and never depend on them editing.
- A4: Every stub-pinned VKB version is preserved as a vkb.orig-<hash6> copy. Verified 2026-10-19 09:40.
