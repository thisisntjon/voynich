# vx01_bf NAMES 1 — v6 script names mapped to the code-3 files (UNVERIFIED)

Plan: PLAN-X01-B-FALLBACK, cited only by sha256 dfc2e0886700a240c39bccf845a126577751682845456e5864058483b8de1a5f (v6).
Ruling: Eve, 2026-10-19: no v7. Where v6 names a `_c2` script, the file that runs is the `_c3` file below.
Hashes re-checked read-only on Skynet (root and voynich-backups) and on the box before this file was written.

## Script roles
| v6 role (v6 §9 #) | v6 name | File that runs | sha256 |
|---|---|---|---|
| 6b, nuisance spread r_k | `vx01_bf_rk_c2.py` | `vx01_bf_rk_c3.py` | 048733479c539a79f1e9446c2fec50724216ed43b5227c7c1f62a210c77fc59d |
| 7, B0 fitter recovery | `vx01_b0_fitter_recovery_c2.py` | `vx01_b0_fitter_recovery_c3.py` | 55893c3052183b577180a6d5e863486a4e7a4e7d69b7561e9b6024ad11671b2c |

## v6 lines that name a _c2 file
| v6 line | Names (_c2) | Read as (_c3) |
|---|---|---|
| 49 | `vx01_bf_rk_c2.py` | `vx01_bf_rk_c3.py` |
| 53 | `vx01_bf_rk_c2.py` | `vx01_bf_rk_c3.py` |
| 57 | `vx01_b0_fitter_recovery_c2.py` | `vx01_b0_fitter_recovery_c3.py` |
| 82 | `vx01_bf_rk_c2.py` | `vx01_bf_rk_c3.py` |
| 83 | `vx01_b0_fitter_recovery_c2.py` | `vx01_b0_fitter_recovery_c3.py` |
| 113 | `vx01_b0_fitter_recovery_c2.py` | `vx01_b0_fitter_recovery_c3.py` |
| 147 | `vx01_bf_rk_c2.py`; `vx01_b0_fitter_recovery_c2.py` | `vx01_bf_rk_c3.py`; `vx01_b0_fitter_recovery_c3.py` |
| 347 | `vx01_bf_rk_c2.py` | `vx01_bf_rk_c3.py` |
| 348 | `vx01_b0_fitter_recovery_c2.py` | `vx01_b0_fitter_recovery_c3.py` |
| 356 | `vx01_b0_fitter_recovery_c2.py` | `vx01_b0_fitter_recovery_c3.py` |
| 455 (§17 changes row) | `vx01_bf_rk_c2.py`, `vx01_b0_fitter_recovery_c2.py` | history: the code-2 files the v6 rename named; the files that run are the _c3 files above |

## Follow-on names (from the _c3 script names)
| Item | rk | B0 fitter |
|---|---|---|
| Stub | `vx01_bf_rk_c3.prereg.sha256` | `vx01_b0_fitter_recovery_c3.prereg.sha256` |
| Dev log | `vx01_bf_rk_c3_dev_runs.log` | `vx01_b0_fitter_recovery_c3_dev_runs.log` |
| Gate log | `vx01_bf_rk_c3_gate_runs.log` | `vx01_b0_fitter_recovery_c3_gate_runs.log` |
| Pin-check log | `vx01_bf_rk_c3_pin_checks.log` | `vx01_b0_fitter_recovery_c3_pin_checks.log` |
The B0 fitter reads the rk script, stub and gate log by these _c3 names (RK_SCRIPT, RK_STUB, RK_GATE_LOG).

## Unchanged names
- Output file and run-folder names are unchanged: `vx01_bf_rk_table.json`, `results_vx01_bf_rk.txt`,
  `vx01_bf_plant_params.json`, `vx01_b0_mei_map.json`, `vx01_b0_oracle_results.json`, `results_vx01_b0.txt`,
  `runs/vx01_bf_rk/`, `runs/vx01_b0/`.
- "vx01_bf_rk output hash" at v6:348 names the output table `vx01_bf_rk_table.json` (made by `vx01_bf_rk_c3.py`).

## Code decisions (hashed by both c3 stubs)
| File | sha256 |
|---|---|
| `vx01_bf_CODE_DECISIONS_1.md` | fa94d24858fddcd7f723a9960a5d1a978dd65f412a0c21bc7832808b5b5a42a5 |
| `vx01_bf_CODE_DECISIONS_2.md` | b65b20cb9e9a1970b355ff61a1988fe7e154ddc8960f473c1123456f2584b3db |

NAMES_1 holds the c3 hashes, so the c3 code can't hold NAMES_1's hash (that would be circular); the stubs and gate logs cite v6 + NAMES_1 by sha256 in the run record.
