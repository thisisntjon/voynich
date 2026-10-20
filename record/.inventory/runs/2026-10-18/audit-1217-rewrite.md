# Audit: the 12:17 rewrite of five shared scripts

Written 2026-10-18 16:32 PDT (clock read with `date`). This was a read-only investigation. This file is the only write it made. Scratch reconstructions are in `<home>/AppData/Local/Temp/claude/<agent-project>/<session>/scratchpad/recon/`, outside the repo.

## 1. Files touched 12:10 to 12:25 (repo root, tools/, scoreboard/)

Nothing in tools/ or scoreboard/ was touched in this window.

| group | file | Created | Written |
|---|---|---|---|
| A. rewritten by `sed -i` (new CreationTime) | s23_power_hash_ledger.py, s35_phase3_ledger.py, s47_ink_space_agreement.py, s65_drawing_gap_robustness.py, s69_prefix_stream_memory.py | 12:17:46 | 12:17:46 |
| A'. compiled right after the rewrite | `__pycache__/` .pyc files for the same five. The header src_mtime is 12:17:46 and the sizes match the current files, so these are the new versions. | 12:17:46 | 12:17:46 |
| B. inventory pointer appended | CLAUDE.md, GEMINI.md | 10-17 20:11 | 12:17:55 |
| C. curate re-run | INVENTORY.md | 10-17 | 12:18:42 |
| D. unrelated runs | results_s96.txt (12:15:19, written before the rewrite); s99_label_nearby_lines.py, its .prereg.sha256 and results_s99.txt (12:21 to 12:24) | | |

The same actor also edited these files outside the scanned folders: `.inventory/registers/CLAIMS.md` line 427 (row c-323, a path text fix), `workflow/research/phase-1-cremma.md` line 67, and `workflow/curation/rules.json` (added `acknowledged_dangling`).

## 2. Originals and hashes

I found no physical copy of the old versions anywhere I looked:
- <local-path>
- the <team-comms> zip packages
- lab
- <home>/.gemini
- <local-path>
- <home>/.codex
- `*.previous` files
- the .pyc files, which were rebuilt from the new source

\\roach was not reachable.

The originals can be rebuilt exactly. I reversed the `sed` substitutions recorded in the transcript, and each rebuilt file matches its stub hash byte for byte:

| file | original (stub) | current |
|---|---|---|
| s23 | 41da7be0ffb78c07... | 9db8c9dd37f2dce7... |
| s35 | 714af357b825594f... | 94b2e1f447cc50a2... |
| s47 | 1ce14f231f9f6137... | 4d8cee813aa8cd64... |
| s65 | 2b182cb96a82d0d4... | c795a4a501b1c0a6... |
| s69 | 785e5cf3096f8a7d... | 11e722d4a0391d34... |

The older s69 hashes e83c4671dbdd and 4ced8e1c6630 belong to s69's failed run 1 from 02:12. That version was replaced by 785e5c before the 12:17 rewrite.

## 3. What the edits changed

None of the five files contains a CR or a BOM, before or after, so line endings and encoding are not the cause. The only changes are the strings below:

| file | lines | change | class |
|---|---|---|---|
| s47 | 42 (docstring) | `tools/segment_scans.glyphs` → `tools/segment_scans.py glyphs` | cosmetic, no change in behaviour |
| s65 | 13 (docstring) | `tools/ivtff_to_meta.clean` → `tools/ivtff_to_meta.py clean()` | cosmetic |
| s69 | 21 (docstring), 229 (comment) | same as s65 | cosmetic |
| s23 | 248, inside an `emit()` string | `(research/phase-2.md` → `(workflow/research/phase-2.md` | cosmetic, but it changes one printed line of the results text; no numbers change |
| s35 | 194 and 196, provenance labels printed by `emit` | `research/phase-3.md` → `workflow/research/phase-3.md` | same as s23: two printed lines change |

None of these modules reads its own `__doc__` or source. No logic, constant or threshold changed.

## 4. Who made the change and why

The edit was made by Claude Code subagent `<tool-call>`, task "Inventory dangling-path repair". The `sed -i` command ran at 19:17:45Z (12:17 PDT), followed by `python -m py_compile`.

Chain of agents: main session `<session>` (voynich-08) → `<tool-call>` ("6.0 audit s96 and fix inventory") → `<tool-call>`.

Its brief said "correct the mention in the doc that contains it with a minimal edit". It treated .py docstrings and emit strings as docs, to clear curate's 42 dangling path mentions. The curate grade went from FAIL 57 to PASS 100. It never checked whether the files were pinned by prereg stubs.

`curate.py` itself writes no scripts. It writes INVENTORY.md, workflow/TIMELINE.md, workflow/curation/* and, with `mark --apply`, banners on .md files only.

Argon's `.gemini` brain only references s47 in its own scratch scripts. Argon session <session> did log activity in the window, but its entries start at 19:19:25Z, after the edit, and they name these scripts only in text it read, never in a write. I found no edits by Argon or Daybreak in this window. Transcript timestamps are in UTC, and only session <session> had activity at 19:15 to 19:19Z.

## 5. Impact

Runs that used the old code, with matching hashes:
- s23, s35, s47, s65, s69
- s71, s76, s79 to s85, s87 to s93, s95 and s96

All their results files are dated before 12:17.

Runs that used the new code, with stubs pinning 11e722:
- s101 imports s69 directly.
- s97, s98, s99, s102, s104, s107 and s108 import it transitively, through s71, s76, s81, s87, s91 and s97. s47 also reaches some of them through s77.

The code is behaviourally identical, so no filed number can change.

The real damage is verification. `sha256sum -c` now FAILS on the stubs of:
- s23, s35, s47, s65 and s69
- s76 to s91, s95 and s96

Any audit or roach replication of those runs will fail its hash check.

Claims that rest on these runs carry provenance risk only, not value risk:
- direct runs: c-323, c-342, c-410, c-416, c-427, c-428, c-454, c-511, c-513, c-519, c-523, c-527, c-533
- runs that hash s69: c-414, c-433, c-438, c-440, c-510, c-515, c-518, c-522, c-524 to c-526, c-528 to c-532, c-534 to c-540, c-545
- runs on the new code: c-437, c-439, c-453, c-544, c-546, c-547

## 6. Remedy (nothing deleted, nothing overwritten)

1. Restore each original under a new name, for example `s69_prefix_stream_memory.orig-785e5c.py`, from the reconstruction. Confirm each hash before filing.
2. Add a `#` comment line to every stub with a failing check. It should say "12:17 sed -i by agent-<session>, docstring/emit-only; original preserved as <name>, hash verified". Comment lines do not change the stub hash.
3. Add a DECISIONS or LEARNINGS row: scripts pinned by stubs are not docs, so curate dangling-path fixes must use `acknowledged_dangling` and never edit .py files.
4. Optional check: re-run s69 from both versions under a new run id, for example s69-hashcheck, and diff the outputs.
