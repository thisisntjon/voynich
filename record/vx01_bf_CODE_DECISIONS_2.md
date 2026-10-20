# vx01_bf CODE DECISIONS 2 — additions and one erratum to CODE_DECISIONS_1 (UNVERIFIED)

Plan: PLAN-X01-B-FALLBACK, cited only by sha256 dfc2e0886700a240c39bccf845a126577751682845456e5864058483b8de1a5f (v6).
CODE_DECISIONS_1: sha256 fa94d24858fddcd7f723a9960a5d1a978dd65f412a0c21bc7832808b5b5a42a5 (unchanged; not edited).
Authority: IV-REVIEW-X01-B0F-CODE-2, sha256 cfcffb531034f563880f8814a058d8ae86253b788efd641fc3171f228a6036d4
(points b, c, e and check 2). Applies to code-3: vx01_bf_rk_c3.py and vx01_b0_fitter_recovery_c3.py.
Both code-3 stubs hash this file and CODE_DECISIONS_1, so these rulings freeze with the code.

## D-32 (new): s91 cache key, raw values vs 6 dp rounding
- s91:406 keys its fit cache on the raw parameter values (`tuple(prm[k] for k in KEYS)`). The fitter's Evaluator
  keys every producer's cache on values rounded to 6 dp.
- No effect for LP91: every value its schedule can reach is a GRID value (STARTS, s91:168-170, are on the grid, and
  SWEEP only sets GRID values, s91:163-167). All have at most 2 decimals, so round(v, 6) == v and no two values merge.
  IV checked this by script (IV-REVIEW-X01-B0F-CODE-2 point b).

## D-09 erratum
- CODE_DECISIONS_1 line 27 (D-09) cites the s61 stage-A0 "types part" read as s61:319. The right line is s61:318
  (`lv = evaluate(prm)[1][2]`); s61:319 is the compare. The ruling of D-09 is unchanged. Code-3 fixes the same cite
  in the s61 schedule docstring.
- Same kind, in code only: the LP91 docstring's "FIT_SEEDS average of s91:408" becomes s91:409-410 (s91:408 is
  `prod.set_params`).

## D-33 (new): shared-block measure rule
- The shared block is measured "through the END line": the bytes from the start of the line
  `# ===== BEGIN SHARED BLOCK ...` through the end of the line `# ===== END SHARED BLOCK =====`, without that line's
  final newline. This is IV's code-1 measure (29,929 bytes on code-2). The Analyst's earlier measure (BEGIN marker to
  the start of the END marker, 29,899 bytes on code-2) is no longer used.
- Both scripts compute it with the same function (shared_block_bytes, inside the block), the block carries a comment
  naming the rule, and each stub records shared_block_sha256 and shared_block_bytes by this rule.

## Code-3 implementation choices (for IV's check; no new rule)
- Point a (spawn-free --pin-check): the --pin-check branch is moved above the hook block and the heavy imports.
  Calling platform.uname() first was not taken: on Windows that call is itself the `cmd.exe /c ver` spawn
  (IV-REVIEW-X01-B0F-CODE-2 point a), so it would not make the check spawn-free. env_measure needs no heavy import.
- Point d (user site): runs use `python -s` (or PYTHONNOUSERSITE=1). `--gate` refuses before GATE-START if
  sys.flags.no_user_site is 0 or any loaded module file is under the user site-packages (site.getusersitepackages()
  and the literal <home>/AppData/Roaming/Python/Python311/site-packages). Dev runs are not refused, but each
  trace records both facts, and the freeze check (and --write-stub) refuses if any trace of the script hash shows
  either one. Every pin-check log line also records no_user_site and the user-site module list.
