# Phase 8 investigation: census and duplication

Date: 2026-10-19 09:30 PDT (from `date`). Angle: census-duplication. This is a read-only investigation. This file is the only thing written to the repo.
Working scripts and raw outputs (not part of the repo): `<home>/AppData/Local/Temp/claude/<agent-project>/<session>/scratchpad/p8cd/` (census.py, analyze.py, pins2.py, var.py; files.json, dups.json, pins2.json).

## 1. What I found

### 1.1 Whole tree
- 15,178 files and 10.68 GB, not counting `.venv`, `.uv-cache`, `.uv-python` or `.git`. `du` on the whole tree gives 11 GB.
- Size by top-level entry:

| entry | files | size | what it is |
|---|---|---|---|
| `data/` | ~11.3k | 9.3 GB | inputs, external corpora, VKB, MSI |
| `runs/` | 3,249 | 590 MB | 76 `sNN` dirs, 12 `roach-rNN`, 2 `vx`, 1 `explore` |
| `.uv-cache/` | n/a | 178 MB | package cache (regenerable) |
| `.venv/` | n/a | 35 MB | environment (regenerable) |
| repo root (loose files) | 956 | 55.7 MB | see 1.2 |
| `workflow/` | 86 | 13 MB | plan, map, graph, curation |
| `__pycache__/` (9 dirs) | 211 | 11 MB | bytecode (regenerable) |
| `tools/` | 110 | 3.0 MB | tooling, including `tools/vkb` |
| `.inventory/` | 43 | 1.6 MB | registers and runs |
| `.tmp/` | 52 | 1.2 MB | probes, wheels, a uv lock, phase-2 text |
| `scoreboard/` 31, `research_notes/` 15, `docs/` 14, `incoming/` 11, `tests/` 6, `results/` 2, `reports/` 2, `experiments/` 2, `codex_lab/` 1 | | under 1 MB each | |

- Hotspots inside `data/` (9.3 GB):
  - `data/msi/f1r` holds 3.8 GB: 3.6 GB `raw` (100 MB TIFFs plus `MANIFEST.sha256.tsv`) and 199 MB `processed`. The MSI is not all on D:. f1r sits on C:, and only f17r and f116v (8.0 GB) are in `<local-path>`, with their own `MANIFEST.sha256`.
  - `data/external` holds 3.8 GB:
    - `models` 2.0 GB: grounding-dino-base 892 MB, siglip 779 MB, dinov2-base 331 MB.
    - `library` 744 MB, of which `fulltext` PDFs are 530 MB and `web` is 155 MB.
    - `yale_scans` 522 MB.
    - The rest is under 80 MB per subdir.
  - `data/atlas` 506 MB: crops 355, work 69 (including `superseded_crops_v1` 36), scans 68.
  - `data/anchor_A1` 388 MB.
  - `data/vkb` 321 MB, of which the live DB is 24 MB. The rest is backups:
    - 11 `vkb.sqlite.*.previous` files, 196 MB;
    - 5 `vkb.sqlite.building.*.failed` files, 49 MB;
    - `vkb.orig-6615aa.sqlite`, 20.6 MB;
    - `test_*.sqlite` files, about 36 MB.
  - `data/controls_tabular_ruled` 285 MB.

### 1.2 Root census (956 files)

| class | count | size |
|---|---|---|
| results (`results_*`: 369 .txt and json siblings) | 536 | 5.8 MB |
| scripts (.py, including 5 `.orig-<hash6>.py` repair copies) | 205 | 5.8 MB |
| stubs (`*.prereg.sha256`) | 126 (plus 16 under `runs/`; 142 in all) | 0.5 MB |
| docs (.md) | 37 | 0.4 MB |
| media: `Screenshot 2026-10-18 *.png` | 32 | 41.7 MB |
| data (txt/json) | 8 | 1.4 MB |
| diffs | 6 | small |
| logs | 4 | small |
| config (`pyproject.toml`, `uv.lock`) | 2 | small |

- The 32 screenshots are 75% of root bytes. None of them is referenced anywhere.
- Root temp and variant files:
  - `results_m4_phase1_board.prev.txt` (byte-identical to `results_m4_phase1_board.txt`);
  - `results_p4d1_core_order.run1-crashed.txt`;
  - 5 `*.orig-<hash6>.py` (the D-071 repairs; see 1.4);
  - a stray `analyze.py`;
  - `grokactivity101926.txt` (modified today);
  - `docx_extract.txt`, `explorediscussion.txt`, `register_extract.txt`.
- No zips at root. 17 zips sit under `data/` as downloaded source bundles.

### 1.3 Duplication
- Exact duplicates: hashed by size-collision then full SHA-256; no file was over 64 MB inside a collision group, so every hash is a full hash. The result is 610 groups and 108.6 MB redundant. The duplication is almost all under `data/`:

| area | groups | redundant |
|---|---|---|
| `data/external/library` internal (83 groups: same PDF under two VL ids, e.g. VL00751 = VL01003, 10.3 MB) | 83 | 44 MB |
| `data/external/papers/rozanova_*_src` vs `data/external/word-coordinates/lrozanova-*` (the same repro bundle unpacked twice) | 292 | 17 MB |
| `runs/s123/crops` vs `runs/s126/crops` (same page crops) | 15 | 9 MB |
| `data/external/library` vs `data/external/voynich-nu-ivtff` (and `library/primary` vs `library/web` copies of voynich.nu) | 11+ | 9 MB |
| `data/external/cremma` vs `data/external/cremma-medieval-lat-mlc1` | 82 | 5 MB |
| `data/atlas/crops` vs `data/atlas/work/superseded_crops_v1` | 8 | 5.5 MB |
| singles: `yale_scans` vs `facsimile`/`facsimile_full`, Greshko supplement in 2 places, Lull 1515 OCR in 2 controls dirs, `data/ZL3b-n.txt` vs the library copy | | ~10 MB |

- Root-only exact groups (8). These are mostly reproductions that happened to give identical bytes, not junk:
  - `CLAUDE.md` = `GEMINI.md` (both just `@AGENTS.md`);
  - `n4b_habit7k_glyph.py` = `n6_habit7k_glyph.py`, and their stubs are identical too. The n4b stub names `n6_habit7k_glyph.py`.
  - `results_n4b_glyph.txt` = `results_n6.txt`;
  - `results_m4_phase1_board.prev.txt` = `results_m4_phase1_board.txt`;
  - `results_p1.txt` = `results_p1_order.txt`;
  - `results_s1_v2_joint.txt` = `results_s25_v2_joint.txt`;
  - `results_s2_u123_controls.txt` = `results_s26_u123_controls.txt`.
- Near-duplicate result variants at root: 23 by name. 10 carry timestamp suffixes (`results_s114_20261018_195048.txt`, s115, s117, s120, s122 to s126, s128). There are also 2 `amend1` (s87, s89), 2 `_v2_joint`, `.prev`, `run1-crashed`, `results_r2.txt` and `results_s96_frozen1_1055`/`frozen2_1103`.
- Result families are wide. n7 has 136 root files, s18 109, n6 59, s17 21, s20 13. These are per-corpus, per-condition outputs of one run id, not drafts.
- Superseded drafts at root:
  - `PREREG.md`, `PREREG-v2-DRAFT.md`, `PREREG-v2.md` and `PREREG-v2.1.md` (all still referenced 9 to 20 times);
  - `PLAN-X01-B-FALLBACK-v6.md` plus `PLAN-X01-B-FALLBACK-v5-to-v6.diff`;
  - root `PLAN.md` beside `workflow/PLAN.md` (INVENTORY lists both as live);
  - the `vx01_*` disclosure, notes and names series (13 .md, 6 of them with zero inbound references).
- `reports/*.md` (2) appear to be compiled from `research_notes/<same name>/*.md` (unverified: inferred from matching names; I did not diff the content).

### 1.4 Stub-pinned set (D-071)
- There are 142 stubs: 126 at root, 11 in `runs/roach-r3..r13`, and 5 in `runs/s128` (`s128_name_slot_prediction_v1..v5`).
- They name 2,454 resolvable paths:
  - root 149;
  - `data/` 2,148: herbals_alchemical 731, herbals_period 442, external 300, anchor_A1 230, anchor_A1b 207, anchor_A0 167, controls_* 65, translit 3, `data/vkb/vkb.sqlite`;
  - `runs/` 289;
  - `tools/` 25;
  - `scoreboard/` 4.
- Other kinds of entries:
  - 292 entries do not resolve. All come from roach stubs (r11 135, r12 137, and r6 to r13 a few each). They use roach-side relative paths such as `../r11/r11.py` and `../dl_ZL/...`, so they pin files that live on roach, not here.
  - 2 entries point to D: (`<team-comms>` and `<team-comms>`, from the s128 v3 stub). Those two <team-comms> files are pinned too.
  - 25 lines in the vx01 stubs pin by hash only (`script_sha256=`, `plan_sha256=` and so on). 16 of these resolve to root files: `vx01_a1_gen.py`, `vx01_a1_known_answer.py`, `vx01_a1_metrics.py`, `vx01_common.py`, `vx01_seg_mdl.py`, `vx01_gate_seeds.json` and `vx01_a1_known_answer_dev_runs.log`. The 9 that do not resolve are plan and dev-log hashes; their targets are not at root, or were since edited.
- Hash check of every pinned path: 3,579 lines match and 24 do not, across 9 files. All 9 are explained:
  - **Amendment chains** (an earlier line not marked `# superseded:`, while the last line matches): `n5_signature_discrimination.py`, `n6_ab_split.py`, `s40_prefix_stream_as_text.py`.
  - **The D-071 "12:17 rewrite"**: `s23_power_hash_ledger.py`, `s35_phase3_ledger.py`, `s47_ink_space_agreement.py`, `s65_drawing_gap_robustness.py` and `s69_prefix_stream_memory.py` were all rewritten at 2026-10-18 12:17. The repair copies `*.orig-<hash6>.py` exist, and each one hashes to its stub (checked). `s69` is also re-pinned at its new hash `11e722…` by s101 onward, so both versions are load-bearing.
  - **`data/vkb/vkb.sqlite`** no longer matches s114 (`6615aa…`) or s125 (`4ed3497…`). Those exact DB states survive only as `data/vkb/vkb.orig-6615aa.sqlite` and `data/vkb/vkb.sqlite.20261019-004344.previous`; both match by hash (checked). **These two "backup" copies are evidence, not junk.**
- Root movability:
  - **Hard-pinned (do not move): 285.**
    - 126 stubs;
    - 149 files named by path or hash, of which 142 are scripts, 4 results, 1 doc and 1 data;
    - 5 `.orig-*` repair copies (`tools/vkb/evidence.py` looks them up beside the stub);
    - 5 root modules imported by pinned scripts but named in no stub: `a5_verbose.py`, `a6_solver.py`, `b3_slot_claims.py`, `ctl_common.py`, `ctl_nomenclator.py`. Moving these breaks the pinned code.
  - **Free by D-071: 671.** 532 results, 53 .py, 36 .md, 32 screenshots, 6 diffs, 4 txt/json, 3 logs, `pyproject.toml` and `uv.lock`. Within the 671:
    - 164 are named as string literals inside pinned scripts' source. They are mostly output paths (`results_n6*.txt` and similar), plus inputs such as `n7_gibberish_ranges.json`, `PLAN.md` and `TEAM-HANDOFF.md`. Moving them changes where a re-run writes or reads (soft pin).
    - 311 are cited by name in docs, registers, tools or root sources. Generated inventories are excluded from that count.
    - **360 are referenced nowhere**: 310 results, 32 screenshots, 9 .md (the vx01 series and `PLAN-X01-B-FALLBACK-v6.md`), 6 diffs, 1 log, `grokactivity101926.txt` and `s127_facsimile_manifest.py`.
  - Of the 536 root results, 215 are cited by name in non-generated docs: 136 in `TEAM-HANDOFF.md` and 94 in `workflow/FINDINGS-GRAPH.yaml`. The uncited ones are mostly the n6, n7 and s18 per-corpus fan-out.

### 1.5 Curate census
- I **did not run** `curate.py run`. The code shows it writes `INVENTORY.md`, `workflow/TIMELINE.md` and `workflow/curation/*`, which is outside `.inventory/runs` (curate.py lines 1190, 1313 and 1384). Even `check` rewrites `workflow/curation/scan.json`.
- The existing scorecard is `workflow/curation/SCORECARD.md` from 2026-10-18:
  - Verdict PASS, grade 100/100, 5,480 rows.
  - Labels: KEEP-LIVE 2,380, KEEP-PINNED 1,166, KEEP-REFERENCED 1,009, ARCHIVE-CANDIDATE 872, KEEP-STATE 29, SUPERSEDED 17, REFUSED 7.
  - 31 unresolved referrers on superseded rows; 0 bags; drift clean as of then.
  - It refused 9,465 of 14,938 files (63%, 397 MB) as out of scope.
- `workflow/curation/dups.json` lists 424 exact groups and 27 MB redundant within its scope.
- Archive candidates by rule: stale-unreferenced 441 and duplicate-twin 431, almost all under `data/` (829) and `runs/` (42). Only 1 is at root.
- Curate's root "KEEP-PINNED 657" uses rule `pinned-hash`, meaning the file's hash is quoted somewhere, for example in CLAIMS.md. That is not the D-071 stub pin; see Surprises.

## 2. Verified vs inferred

**Verified** (scratch scripts named in the header):
- File count and sizes: `os.walk`, plus `du --apparent-size` per entry.
- Duplicate groups: full SHA-256 within size-collision groups.
- Stub parse and resolution: both root-relative and stub-dir-relative paths were tried.
- Hash check of all pinned paths: 3,579/24.
- The 5 `.orig` repair hashes: `sha256sum`.
- The VKB backup to stub-hash matches: `sha256sum data/vkb/*`.
- The import closure of pinned scripts: AST imports plus `"x.py"` string literals.
- Citation counts: substring search of root names in non-generated .md, .yaml and .py.
- The curate write targets: grep of curate.py.
- D-071 text: DECISIONS.md line 77.
- The D: MSI layout: `ls` and `du`.

**Inferred or unverified:**
- That `reports/*.md` derive from `research_notes/`.
- That the 2 GB `data/external/models` duplicates the HF cache. `~/.cache/huggingface/hub` has `models--facebook--dinov2-base` and `models--IDEA-Research--grounding-dino-base`; I did not hash-compare them, and siglip is not in that listing.
- That the MSI raw TIFFs are re-downloadable from Beinecke.
- That non-matching `.previous` VKB copies are pinned by no `runs` row in the VKB. I did not query the VKB `runs` table.
- The import closure misses dynamic imports such as `importlib` with computed names, and `subprocess` calls on names built at runtime.
- A citation by substring can over-count, for example `results_s1.txt` inside `results_s1_v2…`. So "360 unreferenced" is a lower bound on the safe-to-move set only if over-counting dominates. Treat it as approximate.

## 3. Surprises
1. **VKB backups are evidence.** `vkb.orig-6615aa.sqlite` and `vkb.sqlite.20261019-004344.previous` are the only on-disk copies matching the s114 and s125 stub hashes. Because the live `vkb.sqlite` has moved on, s114 and s125 can no longer be verified against it. A "delete .previous copies" cleanup would destroy pre-registration evidence.
2. **"Pinned" means two things.** D-071 pins about 285 root files; curate's `pinned-hash` labels 657. A plan that uses curate labels as the D-071 set is wrong in both directions. It would freeze results that can safely move, and it misses that curate does not see the import-closure modules or the `.orig` copies as pins.
3. **Most stub pins are not at the root.** 2,148 pins are under `data/` and 289 under `runs/`, so reorganizing `data/` is far more constrained than reorganizing the root.
4. **Roach stubs pin 292 paths that do not exist here** (roach-side layout), and s128 v3 pins two files on `<team-comms>`. Those <team-comms> files are now under D-071 too.
5. **MSI is split across drives.** f1r (3.8 GB) is in the repo on C:, while f17r and f116v (8 GB) are on D:. Decision text in PLAN.md 2026-10-18 19:44 says "MSI on D:".
6. **Amendment chains are not marked.** 3 stubs carry an earlier hash line without `# superseded:`, contrary to the AGENTS.md convention, and `sha256sum -c` on them reports a failure.
7. **Several byte-identical results come from different run ids** (s1 = s25, s2 = s26, n4b = n6, p1 = p1_order). These are reproductions worth recording as such, not just dedupe targets.
8. Screenshots alone are 41.7 MB, 75% of root bytes, and nothing references them.

## 4. Assumption candidates (what the cleanup plan would rest on)

| # | assumption | how to verify |
|---|---|---|
| A1 | The D-071 immovable set at root is the 126 stubs + 149 named + 5 `.orig` + 5 import-closure files (285) | Re-run pins2.py after other sessions stop; add a dynamic-import grep (`importlib`, `runpy`, `subprocess`, `exec(open`) over pinned scripts |
| A2 | Moving a results file breaks nothing as long as references are rewritten or tombstoned | For each move, grep the name across `workflow/`, `.inventory/`, `TEAM-HANDOFF.md`, `tools/`, pinned script source and the VKB (`runs`, `claims` tables); count must be 0 or covered by a tombstone |
| A3 | VKB `.previous` and `.failed` copies other than the two stub-matched ones are not evidence | Hash each and compare against every stub line and the VKB `runs` table's recorded DB hash (if any); grep LEARNINGS/DECISIONS for the timestamps |
| A4 | `data/external/models` is re-obtainable | Hash-compare against `~/.cache/huggingface/hub` snapshots; record model revision ids |
| A5 | MSI raw TIFFs are re-obtainable and the manifest is complete | `MANIFEST.sha256.tsv` row count equals the file count (44 in f1r); source URL recorded |
| A6 | Duplicate copies under `data/external` are not referenced by path in any stub | Intersect each dup group with the pinned set; move only the unpinned twin |
| A7 | The curate `pinned-hash` label means "hash is quoted", not frozen | Read `curate.py` rule `pinned-hash` and spot-check 10 rows' evidence (3 checked: CLAIMS.md hash quotes) |
| A8 | No other session is writing the files to be moved | mtime within the last 6 h: currently only `TEAM-HANDOFF.md`, `grokactivity101926.txt`, `results_s128_20261019T090659.txt` and `s128_p72_label_partner.prereg.sha256`; re-check right before any move |

## 5. Recommendations

| # | recommendation | effort | risk |
|---|---|---|---|
| R1 | Leave all 285 hard-pinned root files (stubs, named scripts, `.orig-*`, import-closure modules) exactly where they are | low | low |
| R2 | Bag (curate archive) the 32 root screenshots (41.7 MB) and `grokactivity101926.txt` after confirming the owner; nothing references them | low | low |
| R3 | Move unreferenced, unpinned root results (about 310) into per-family subfolders, e.g. `results/n7/`, `results/s18/`, `results/n6/`, with tombstones. Do this only after A2 passes per file, and start with the fan-out families (n6, n7, s18, s17, s20), which hold about 340 files | medium | medium (soft pins: 164 names appear in pinned code as output paths, so a re-run recreates them at root) |
| R4 | Do **not** archive `data/vkb/vkb.orig-6615aa.sqlite` or `vkb.sqlite.20261019-004344.previous`. Label them as stub evidence (s114, s125). Bag the 5 `.failed` builds (49 MB) and any `.previous` that fails A3 | low | low once A3 is done |
| R5 | Collapse `data/external` twins (rozanova bundle ×2, cremma ×2, voynich.nu ×3, library VL-id twins). Keep the copy that is stub-pinned or referenced, and bag the other with a tombstone. Saves about 75 MB | medium | low-medium (check A6) |
| R6 | Put the MSI in one place: either move `data/msi/f1r` (3.8 GB) to `<local-path>` beside f17r and f116v, as decided, or record why it stays. No stub pins MSI (checked: 0) | low | low |
| R7 | Mark the amendment chains: the earlier lines in n5, n6_ab_split and s40 stubs should become `# superseded:`. Editing a stub is itself a D-071-adjacent act, so file a decision first; do not edit scripts | low | medium (governance) |
| R8 | Group the vx01 sidecar docs (13 .md, 6 diffs, 4 logs) under one `runs/vx01/` subfolder with tombstones. Keep `vx01_a1_known_answer_dev_runs.log` and `vx01_gate_seeds.json` at root, because both are hash-pinned | low | low |
| R9 | Treat superseded drafts (`PREREG-v2-DRAFT.md`, `PREREG-v2.md`, `PLAN-X01-B-FALLBACK-v6.md` + diff, root `PLAN.md` vs `workflow/PLAN.md`) as archive candidates. They need a supersession pointer, because the PREREG versions still have 9 to 20 inbound references | medium | medium |
| R10 | Regenerable bulk (`__pycache__` 11 MB, `.uv-cache` 178 MB, `data/atlas/work/superseded_crops_v1` 36 MB, `.tmp/` 1.2 MB) can be excluded from the census or bagged. These are not sprawl that matters for truth | low | low |
| R11 | Record the identical-result pairs (s1/s25, s2/s26, n4b/n6, p1/p1_order, m4 .prev) as reproductions in the findings graph rather than deduping them | low | low |
