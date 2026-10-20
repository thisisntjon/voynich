# Audit O-066: four stubs that fail the binding check (n5, n6_ab_split, s40, s69)

Written 2026-10-18 17:13 PDT (clock read with `date`). This was a read-only investigation, and this file is its only write in the repo. I used the method of `audit-1217-rewrite.md`. The scratch reconstructions are in `<home>/AppData/Local/Temp/claude/<agent-project>/<session>/scratchpad/o066/` (`n5_orig.py`, `n6_orig.py`, `s40_orig.py`, `edits.json`, `rebuild_s40.py`), outside the repo.

## 0. Verdict

**No script was edited after its run.** Each of the four stubs carries a pre-crash frozen line and an appended amendment line for the same path. The amendment line is not commented out. `grep -v "^#" STUB | sha256sum -c -` checks every uncommented line, so the superseded line always FAILS. These four are the only stubs in the repo root with a duplicated path (I checked all `*.prereg.sha256`). Other amended stubs prefix the old line with `# superseded:`, for example `p4d1_core_order.prereg.sha256`. Each current script hashes to its stub's **last** line, and that version wrote the results. The finding is not new: `c-321` (the s23 hash ledger, 10-17) already filed "2 FAILED (the pre-crash originals in n5 and n6_ab_split, each superseded by an OK amendment line)".

What would refute this: a current hash that differs from the last line, a results file older than the script, or a rebuilt original that does not match the first line. I checked all three, and none of them occurs.

## 1. Timestamps (NTFS, PDT)

| file | Created | Written | note |
|---|---|---|---|
| n5_signature_discrimination.py | 10-17 19:24:18 | 19:24:18 | stub 19:19:24 / 19:24:19; results_n5.txt 19:29:18; header `run=2026-10-17T19:24:21` |
| n6_ab_split.py | 10-17 19:41:16 | 19:41:16 | stub 19:39:56 / 19:41:17; results_n6_ab_split.txt/.json 19:48:40; header records script sha e1352e…, `stub: MATCH` |
| s40_prefix_stream_as_text.py | 10-17 22:29:16 | 22:29:16 | stub 22:27:26 / 22:29:23; results_s40.txt 22:29:36 / 22:29:40 |
| s69_prefix_stream_memory.py | 10-18 12:17:46 | 12:17:46 | the 12:17 sed rewrite (D-071); `.orig-785e5c.py` 16:34:34; stub 02:08:23 / 02:13:08; results_s69.txt 02:08:29 / 02:17:37 |

The Created time of each of n5, n6 and s40 is its amendment time: the Write/Edit tools replace the file. No write to the three scripts happened after its results were written.

## 2. Originals, actors, hashes

| file | actor (transcript) | stub line 1 (frozen) | rebuilt original | stub amendment = current |
|---|---|---|---|---|
| n5 | Claude session `<session>` (cwd Desktop\Python, project dir `<agent-project>`): Write 02:19:03Z, Edit `<tool-call>` 02:19:10Z, `sed -i '/^import random$/d'` 02:19:16Z, stub 02:19:23Z; run 1 crashed; Edit `<tool-call>` 02:24:16Z; amendment 02:24:18Z | fc0f161a31de | **fc0f161a31de… exact** | 9b9cd7ebb0e7 (current file byte-identical to the rebuild + amendment edit) |
| n6_ab_split | Claude session `<session>` (same project dir): Write 02:39:14Z, python `str.replace` x3 `<tool-call>` 02:39:32Z, stub 02:39:56Z; run 1 crashed 02:40; Edit `<tool-call>` 02:41:13Z | 1afe689286e8 | **1afe689286e8… exact** | e1352ed3fc37 (byte-identical) |
| s40 | Claude subagent `<tool-call>` of main session `<session>`: Write `<tool-call>` 05:27:17Z, stub 05:27:21Z; run crashed; Edit `<tool-call>` 05:29:15Z | f2ea72fb245e | **f2ea72fb245e… exact** (the Write content alone) | 78e005177a72 (byte-identical) |

These are not post-run edits by Argon, Daybreak or roach. The n5 and n6 transcripts are not in the voynich project dir, which is why a search of that dir finds only reads. The Codex sessions mention n5 and n6 only after 02:52Z, and only as reads.

## 3. Diff class

| file | change | class |
|---|---|---|
| n5 | `try/except` around `score(cut(pages))` in the main loop. It swallows errors only for `key == "X"` (the CONTEXT rows, "no range"), and E/G/L errors still raise. One row is affected: `lull_ars_brevis_table NOT SCORED` (results_n5.txt line 76). `score()` itself is unchanged. | behavioural only in the crash path. The original produced no verdict. CONTEXT rows enter no range or rule, so no filed number could differ |
| n6_ab_split | `fam_members`: `if d.get(f):` → `if isinstance(d.get(f), dict):`. It skips the `bake_winner` list entries that crashed run 1 before scoring. Dict entries contribute the same members. | crash fix; membership from real ranges unchanged; no number could differ |
| s40 | one `emit` f-string with nested same-type quotes (SyntaxError on Python 3.11) split into `gen_core`/`lat_core` helpers. The printed text is the same. | cosmetic. The original could not compile, so it never ran |

## 4. s69

The e83c line was always meant to be superseded. The stub says so itself: "# FAILED run 1 (02:12:20) … AMENDMENT 1 OK (02:13:08): … later line for the script supersedes the frozen hash above". `runs/s69/freeze.txt` and the s69 code also record the amendment (the comment at line 303 and the AMENDMENT notice `emit` at lines 699–700 of `.orig-785e5c.py`). `runs/s69/run.log` records script 785e5c with `stub_match=True`. D-063 and D-065 do not mention s69. The current s69 file fails both lines because of the 12:17 rewrite, which D-071 already repaired with `.orig-785e5c.py`. One correction to `audit-1217-rewrite.md` §2: `4ced8e1c6630` is the sha of the **stub file** at freeze (freeze.txt), not a script hash.

## 5. Claims

| run | claims | value risk |
|---|---|---|
| n5 | c-293, c-294, c-295; c-365 calls `n5.score()` (unchanged by the amendment); c-321 cites the stub | none |
| n6_ab_split | c-299, c-300; c-321 | none (c-301 is n6_habit7k_glyph, not this run) |
| s40 | c-352 | none |
| s69 | c-410 direct; c-416, c-427, c-428, c-454, c-519, c-523 (see audit-1217 §5) | none; provenance already handled by D-071 |

## 6. Remedy (nothing deleted, nothing overwritten)

1. **No re-run is needed.** Each results file came from the hash on its stub's last line.
2. Fix the check, not the files. In `tools/vkb/evidence.py` `stub_check` and in the AGENTS.md binding text, the **last uncommented line per path is binding**. An earlier line for the same path is superseded, and it passes only if a `# FAILED`/`# AMENDMENT` comment sits between the two lines. Do not edit the stubs: `runs/s69/run.log` pins the s69 stub sha (9d7706…), and stubs are append-only.
3. Optional, for symmetry with D-071: restore the pre-crash originals so the superseded lines can be audited. These are the steps, using the scratch inputs above:
   - `s40_prefix_stream_as_text.orig-f2ea72.py` is the `content` of Write `<tool-call>` in `…\<agent-project>\<session>-…\subagents\<tool-call>.jsonl`, written with UTF-8 and `newline=''`.
   - `n5_signature_discrimination.orig-fc0f16.py` comes from session `…\<agent-project>\<session>.jsonl`. Take the Write `<tool-call>` content, apply Edit `<tool-call>` (old→new, unique), then delete the line `import random` (regex `(?m)^import random\n`).
   - `n6_ab_split.orig-1afe68.py` comes from session `…\<agent-project>\<session>.jsonl`. Take the Write `<tool-call>` content and apply the three `str.replace` calls of `<tool-call>`, in order: the two `"--name", f"{t}_…"` → `"--name", t` replacements, then `family=f)` → `family=f, name=n)`.
   - Before filing, check each output: `sha256sum` must equal the stub's first line. Applying the amendment edit must then reproduce the current file byte for byte, which I verified for all three.
   - Add a `#` comment to each stub naming the `.orig` file. Comment lines do not change what the check verifies, but they do change the stub file's own sha. So for s69, record the pinned sha in that comment, or skip the s69 comment.
4. Add a LEARNINGS row: an amended stub must comment out the superseded line (`# superseded:`), or the checker must apply the last-line rule.
