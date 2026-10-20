# vx01_bf CODE DECISIONS 1 — open code choices in vx01_bf_rk.py and vx01_b0_fitter_recovery.py (UNVERIFIED)

Plan: PLAN-X01-B-FALLBACK, cited only by sha256 4ed0314a7c8aef4d925dee4fbab3ef8eca3a005352062563e3708a0273e63f3e
(its title still reads v4). Base plan v5.1 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393.
Status: both scripts WRITTEN ONLY, for IV code review. Nothing was run (not --dev, --build-params or the probe).
Nothing was frozen and no stub was written. Only checks done: ast.parse, py_compile (into /tmp on the box, outside the
project) and pyflakes (no findings), on the box, not on Skynet.
Rule for every item: where v5 leaves a choice open, the plainest option was taken. IV rules on each one.

## A. Seeds and books
- D-01 Family field of derive_seed = the producer id used in the scripts (s57, s58, s61, CA, CA0, s81_fit, s81_75,
  LP91, r13A, r13B, WTG_global, WTG_scribe). Fold field of a whole planted book = "book"; an MEI book uses fold =
  its fold quire (FOLDS[i]); fits and copies use fold = the scored quire q.
- D-02 Book controls: power, nuisance, wrongfam (planted with family W), mei; MEI-map books "meimap|<cand>|<r>";
  r13B MEI table "meitable|<cand>" (own rng, family r13B, fold "book"). <cand> = "<key>=<value>" (e.g. "R=64").
- D-03 / D-04 Fit and copy seed controls carry the book control as a prefix: "<ctl>|fit|<q>|<eval>" and
  "<ctl>|copy|<r>" (ctl = power, nuisance, mei, wrongfam-<W>). Without the prefix, the power, nuisance and
  wrong-family refits of P in one cell would reuse the same copy seeds. v5 §4 writes `fit|<fold>|<eval index>` while
  §6 writes `fit|<eval>` (a small inconsistency in the plan); the fold is in the fold field anyway.
  <eval> = order of FIRST evaluation of a parameter key in the fit's cache (keys rounded to 6 dp, as the original
  fitters' caches). Oracle copies: "oracle-power|copy|<r>", exactly as §7.
- D-05 SD = numpy std with ddof = 0 (for d_k and the copy SD sd_k,q of the MEI map).
- D-06 s57/s58/s61/CA/CA0 `text()` takes line counts only (s101:691), so their copies match pages and lines but
  NOT words per line. The plan's band says "pages, lines, words per line"; for these producers that cannot hold.
- D-07 WTG layout: meta lines and ALL meta pages (s101:718-722); other producers: S67.load_pages lines (s101:685-686).
- D-08 WTG_scribe: each page uses its own hand (s101:721-722). (s71:953 used the held-out quire's dominant hand.)
- D-09 s61 stage A0 used only the types part of the s57 loss (s61:319). L has no types part, so A0 uses the full L.
- D-10 line_sticky75 (s81_75): nothing fitted; L is still computed once at p = 0.75 for hardness.
- D-11 "WTG" in the v5.1:145 pairings = WTG_global.
- D-12 LP91 fit: ONE copy per candidate (§4: "1 simulated copy"), not the FIT_SEEDS average of s91:408.
- D-13 LP91's sticky-cipher seed = the same derived seed as the text copy (s101:740 used one seed for both).

## B. Scoring
- D-14 Band edges inclusive: lo <= v <= hi.
- D-15 Nuisance: if r_k,q is undefined (a statistic undefined on one transliteration), statistic k is undefined
  for that fold. sign: first byte of SHA256("master|T|P|sign|k|q") even -> +1.
- D-16 MEI map: m_k,q = mean of the DEFINED values of the 4 books; quire q is left out of the median when the band
  is undefined, sd_k,q = 0, or no book value is defined. If no quire is left, side_k is undefined (the pair is not
  reached).
- D-17 Both wrong-family pairings of P are computed in every cell up front; the pairing is chosen after all 9 cells
  (first one that is hard in all 9). The hardness fit of W uses W's schedule on P's POWER book training quires.
- D-18 MEI books: the refit of P runs on the whole MEI book (its loss targets need Qtr of that book); only fold i is
  scored.

## C. Run control, trace, freeze
- D-19 The freeze trace = the union of the traces of every dev mode run with THIS script hash (runs/vx01_b0/*/
  trace_*.json); --freeze-check writes a report, --write-stub needs it. vx01_bf_rk: the trace is its --dev run.
- D-20 Coverage required for freeze: build-params; calibrate-mei for every MEI producer x 3 T; oracle for every
  producer x 3 T; dev for every oracle-passing producer x 3 T x 4 controls. The timing run is ZL3b only (§9), so the
  other two transliterations need extra --dev --T runs for the trace (§8a says EVERY mode, EVERY producer, all 3 T).
  This is the clash noted before: IV to rule whether those extra --dev runs are wanted.
- D-21 Every heavy dev mode needs --cap-seconds; a timer thread writes CAP-STOP to the dev log and calls
  os._exit(5). The gate checks its cap only between producers (§9 condition ii). A gate cap stop writes
  GATE-COMPLETE with note "CAP-STOP before <P>"; the rest are "not run, no call".
- D-22 E = Σ over oracle-passing producers of (latest FULL ZL3b dev cell seconds on 20261103 x 9); cap = 2E. A
  probe (one unit) is logged as DEV-TIMING with full_cell=false and is never used by the formula; Eve's probe
  extrapolation (ruling c) is a separate, reported step outside the script.
- D-23 Free RAM >= 4 GB (GlobalMemoryStatusEx); OMP/MKL/OPENBLAS threads = 1; BelowNormal via vx01_common.
- D-24 The six statistics are written twice, byte-identical, in both scripts (BEGIN/END SHARED BLOCK), because a new
  shared module would be a file not in the load list (no freeze).
- D-25 vx01_common's stub check uses plan_sha256 = v5.1's hash, so each stub also carries bf_plan_sha256 (= v5's);
  the scripts refuse --gate if it differs. A prior GATE-VOID of the same script hash refuses a rerun.
- D-26 Pin check (IV add-on): every check writes ENV-PIN-CHECK with t (UTC), t_pt (PT, from
  datetime.astimezone(), no spawn), exe sha256, sys.version sha256, -VV sha256 (= sha256 of "Python " +
  sys.version), sitecustomize sha256, package-list sha256 (compact JSON of the 21 pinned versions) and the
  pywin32_bootstrap file hash. Checks run at start (refuse on mismatch, in dev modes too: pinned 3.11.9 only) and at
  end (recorded). Manual --pin-check writes to <script>_pin_checks.log. v5 says clock time comes only from
  vx01_common.utc_now(); PT is an added field next to it.
- D-27 Writes outside the declared outputs: gate -> VOID; trace -> listed as a freeze problem. Outputs have fixed
  names and are never overwritten (open "x").
- D-28 --dev refuses unless the oracle result file exists; calibrate/oracle/dev refuse unless the rk stub and table
  exist; load_rk also needs the table hash in a GATE-COMPLETE record of the rk gate log.
- D-29 rk modes: --dev (the trace; it computes real r_k before the freeze, which v5 (a) makes unavoidable) and --gate
  (the one frozen run that writes the table).
- D-30 Params: LP91 median over the sorted glob runs/s91/folds/<T>_*.json, as §5/s101; refuses unless it equals the
  15 load-listed files. Page-id disagreement is written in the params file and logged as PAGE-ID-DISAGREE.
- D-31 The record-mode hook BLOCKS a spawn (raises) as well as recording it, so a dev run never spawns.

## D. Not implementable exactly as written in v5 (for IV)
1. Band "words per line" for s57/s58/s61/CA/CA0 (D-06).
2. s61 stage A0 "types part" of the loss (D-09).
3. §4 vs §6 fit seed control text (D-03/D-04).
4. §8a "every mode for all 3 T" vs §9 timing "ZL3b only" (D-20).
5. "Clock time only from utc_now()" vs the IV add-on's PT time (D-26: added, not replaced).
6. LP91 FIT_SEEDS averaging vs "1 copy" (D-12; the plan text was followed).
7. The exact fit() end lines go in the stub (§4); they are in each schedule's docstring and copied into the stub.
   Their accuracy against the frozen sources needs IV's check (if any schedule is not exact, that producer is
   UNINFORMATIVE, §4).
