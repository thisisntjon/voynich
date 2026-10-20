# vx01 A1 disclosure 2: the first version of vx01_a1_known_answer.py is not kept (2026-10-18, PDT)
Plan: PLAN-X01-v5.1 sha256 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393. New file; nothing existing edited.

- First version: SHA256 81e16516428fc28b0a3a0f478da9ba5c76ff6f68d8eedb1e6e663b76b46d2a26. It ran ONCE, in DEV mode (dev seeds 20261111..20261115), 2026-10-18 22:53 PDT (05:53:30Z): metrics hand tests, generator counts, ORACLE ceiling (30/30 dev books pass), and a smoke run of the 8 segmenters on one dev book (time only, no score). Its two lines are in `vx01_a1_known_answer_dev_runs.log` (lines 1-2, script_sha256 81e16516...). Its output: `runs\vx01_a1_dev\dev_report_20261019T055330Z.txt` SHA256 35f0985007ae34535f557367e717404025d2ac036801af741611f66516463807.
- It was overwritten in place (box and Skynet) before the freeze by the version now frozen (SHA256 5c408207c9668f203e3f716caa1d4db1412ea1943fc4c6707aac0eaa00b39d9e). The old bytes are not kept anywhere. It was never run on gate seeds and never with --gate.
- What changed (from my edit script; no rule, threshold, seed, metric or row changed):
  1. The gate scoring and report code in `run_gate` was moved into a new function `score_all(ctx, mode, out_dir, resp, limit=None)`; `run_gate` now calls it with mode "gate", `runs/vx01_a1/` and `results_vx01_a1.txt`. The no-overwrite check moved into `score_all`.
  2. New DEV-only mode `--dev-path-test` (`run_path_test`): runs `score_all` on dev books, 1 per (set, family), into `runs/vx01_a1_dev/path_test_<stamp>/`. (This is the run that wrote dev scores; see disclosure 1.)
  3. Docstring: one paragraph describing `--dev-path-test`; `main()` dispatches to it.
- Not a revision under plan rule 4 (pre-freeze edit; IV ruling (a) in IV-CHECK-X01-A1-STUBS.md).
