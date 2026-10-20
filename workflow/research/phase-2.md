# Phase 2 investigation — s20 / s22 / s23 / v2.1 / multiplicity / sharing

Stamped Sat Oct 17 20:41:22 PDT 2026 (`date`). Read-only; no experiment run; `python -I` for the JSON reads.
Files opened: PLAN.md:39-70,96-144; results_s2_u123_controls.txt; results_n6_ab_split.txt; results_s15.txt; results_s18.txt:294-314;
results_s30_phase2_deltas.txt; C-constraints.md; phase-1-instrument.md §2, §6; PREREG-v2.md:27-47,60-75,149-160,215-243; s15_ranges.json;
results_s17_*.json; results_s18_cremma_*.json; n6_ab_split.py:1-73,292-330; scoreboard/run_v2.py:242-252,385; every `*.prereg.sha256`
(`sha256sum -c`); m1_coordinates.py:31-33,136,185,389; C-helpers/pw_m1_column.py:17-24; o1_direct_pixel_and_ink_spacing.py:8-58,287-298;
s30_phase2_u2_u3_deltas.py:28-59,213-219,282-412; TEAM-HANDOFF.md:64-70,266.

**Headline surprise.** A peer session already ran the Phase 2 deltas under prefix **s30** (pre-registered 20:19,
`s30_phase2_u2_u3_deltas.prereg.sha256` matches the script on disk): the Currier A/B position-stratified null
(results_s30:3-14), per-alphabet 41-page widths for 5 alphabets (results_s30:16-26) and an ink-boundary split/merge row
(results_s30:28-32). TEAM-HANDOFF.md:266 still reserves s20–s24 for this session and lists s30/s31 as "completed by
decryption/Argon session"; s32 onward is free. PLAN.md:139's re-scope (20:05) predates s30 (20:19) and does not cite it.

## 1. s20 — what remains after s2 Parts 2A–2B (and s30 Part 1)

Done on disk, pre-registered: whole-text (hand, section, slot) null, 102.7–102.9 % survival on 3 translits
(results_s2:20-23); edge-table transfer A→B, B→A, 166→41, Dante-rank all ≥ +0.09 (results_s2:26-30); **A-only and
B-only stratified null at their own sizes**: A ZL3b +0.1263±0.0017 vs within-line +0.1206 (104.8 %), RF1b 105.4 %,
IT2a 105.4 %; B 103.0–103.1 % (results_s30:4-9); Latin syllable and Dante tables drive coupling on A and B
(results_s30:12-14). So question (b) — does A's coupling survive a position-stratified null at A's size — is
answered YES by s30 Part 1, with a 200-shuffle null and 3 translits. Nothing to re-run.

What remains is (a): A and B scored on the coupling metrics against (i) the s15 widths and (ii) a **real-line** L
range. Neither exists as a filed comparison: n6 scored A/B against m4's pseudo-lined L ranges
(results_n6_ab_split:27,29: A IN L on cross_excess_eva 0.1203 and x_edge_mi_word 0.1265; B OUT at 0.2321/0.2404),
and s15_ranges.json's L ranges are still m4's (cross_excess_eva L 0.0261–0.1459, x_edge_mi_word L 0.0280–0.1497).

Do the s17/s18 .json rows carry per-metric values usable as an L range? **Yes, with a gap.** Each file is
`{row, seed, provenance, ranges_file}` and `row` carries every v2 key (`cross_excess_eva`, `x_edge_mi_word`,
`jsd_first_fg`, `x_moran_I`, `tokens`, `family`, `in_out`, …). Checked: results_s17_italian_dante.json row
cross_excess_eva 0.1615, x_edge_mi_word 0.1672, tokens 25001; results_s18_cremma_prose15.json 0.0239 / 0.0414 /
6890. The gap: `x_edge_mi_word` is `None` on 19 of 21 per-manuscript CREMMA rows (the extras step died with
ZeroDivisionError on 2-page manuscripts, results_s18:309); it exists only on the pooled rows (all, c15, prose15),
SBB_PK_Hdschr25 and UBL758. Real-line native rows (no `_relined8`, no `_marks`): cross_excess_eva spans
−0.0946 (BGO-511, 169 tokens) to 0.2478 (LaurPlut33.31, 1267 tokens); with a ≥5k-token floor the max is Dante
0.1615, then Occitan 0.1084, BIS-193 0.0974, Roland 0.0911; x_edge_mi_word over the 10 rows that have it spans
0.0298 (gib_realline_pooled) to 0.1672 (Dante). Reading, unverified until filed: A (0.1203 / 0.1265) is inside the
≥5k real-line L range on both metrics; B (0.2321 / 0.2404) is above every real-line row. A size floor must be
pre-registered because the sub-2k CREMMA rows inflate both ways.

Smallest run (prefix s20, one script, one output): six run_v2 calls, ~20 s each (results_s15:40-42 timing), then
a reader that pulls the two coupling keys from the s17/s18 rows and the s15 widths:
```
python -m scoreboard.run_v2 --voynich --lang A --ranges s15_ranges.json --out results_s20_voy_A.txt
python -m scoreboard.run_v2 --voynich --lang B --ranges s15_ranges.json --out results_s20_voy_B.txt
python -m scoreboard.run_v2 --meta data/translit/RF1b.meta.json --lang A --n-sample 40000 --ranges s15_ranges.json --out results_s20_RF1b_A.txt   (and B; IT2a A/B)
```
`--lang` reads page field `lang` (run_v2.py:247); all five data/translit sidecars carry it (checked page0 keys).
s15_ranges.json has `x_family: gibberish` so X prints too. The script's own output `results_s20.txt` states, per
metric and per half on 3 translits: value; s15 width (cross hw 0.0304, edge-MI hw 0.0320, results_s18:306); m4 L
in/out; real-line L min/max at the ≥5k floor with members; and the s30 survival line quoted with its hash.
Decision statistic to pre-register: A IN the ≥5k real-line L range on both coupling keys on all three translits
AND B OUT on both → "coupling is a B property, A inside L" becomes a CLAIMS row; otherwise U2's remaining half
is recorded as "size-dependent". No new null is needed. Inputs that exist: s15_ranges.json, results_s17_*.json (10),
results_s18_cremma_*.json (72), results_s30_phase2_deltas.txt, results_n6_voy_{A,B}*.json (cross-check).

## 2. s22 — fixed unit

**o1 has no token stream or sidecar on disk.** `o1_direct_pixel_and_ink_spacing.py` reads
`data/external/word-coordinates/.../direct_pixel/results_unblinded.csv` (:44) and six facsimile JPEGs (:19,57),
measures gap profiles, and writes only `results_o1.txt` (:58,298). No `data/*` output, no `.meta.json`, no `runs/o1`.
s30 Part 2B's "ink-driven" row is **not** o1's segmentation: it re-parses `data/ZL3b-n.txt` under three space
conventions ('.'+',' / '.' only / split before medial gallows and benches) justified by o1's measured gap and lift
sizes (s30 script :213-219). It is a tokenisation-sensitivity row, and it is the only ink-split row obtainable
without a new o1 run that emits per-word boundaries.

Without it s22 can only file what is on disk: results_s2:40-44 (h2_25k EVA 2.126 / glyph+ 2.397 / GC2a 2.540,
types_25k 5417–6349, hapax 0.680–0.702), results_p2.txt:1-4 (same four rows, RF1b-e variant), and
results_s30:17-32. Per-alphabet width: s30 Part 2A already has 200-split 41-page CIs for h2, sd_len, types, hapax,
JSDf and cross_excess on all five sidecars (ZL3b_eva h2 [2.054, 2.152] reproduces s15 exactly; glyph+ [2.305, 2.440];
GC2a [2.456, 2.574]). Those are v1-estimator widths. A full-v2 per-alphabet width (every extra, edge null nrep 20)
needs an s15-style run at 4.5 s/split × 200 = 15 min per alphabet (results_s15:7), 30 min for glyph+ and GC2a.
Recommendation: not needed; h2 and sd_len are the only alphabet-specific bands (PREREG-v2.md:42-47) and s30 covers
them. s22 is therefore a filing step (CLAIMS rows + a U3 verdict line) unless Jon wants the o1 sidecar built, which is
a new deliverable (ink-boundary token stream for 5 folios only, ~5k lifts, results_o1), not a Phase 2 cost.

## 3. s23 — power refile and hash checks

Hash checks run now (`sha256sum -c` over every stub; this is a read, not an experiment):
| Stub | Result | Note |
|---|---|---|
| n4_habit7k.prereg.sha256 | all 17 OK | results_n4.txt prints no hash (PREREG-v2 §9 requires it); stub covers data/ZL3b-n.txt and 3 sidecars |
| n5_signature_discrimination.prereg.sha256 | line 2 FAILED, line 50 OK | amendment 19:24 after crash; current script = amended hash 9b9cd7eb… |
| n6_ab_split.prereg.sha256 | line 2 FAILED, line 29 OK | amendment 19:41; results_n6_ab_split:2 prints e1352ed3… = amended |
| n6_habit7k_glyph / n4b_habit7k_glyph | OK (same hash 52fb51e4…) | two stubs, one script |
| n7, s1, s2, s15, s17, s18, s30, s31, n3b | OK | n7/s2 results print the hash |
| p1_bifolio | **no stub exists** | p1_bifolio_null.py hash 3aba99a6… appears only inside n3b's stub (OK); results_p1_bifolio.txt:1-4 prints no hash |
| scoreboard/PREREG-v2.sha256 | OK (PREREG-v2.md f8c42d76…, run_v2.py 7dfdc9f7…, gibberish_to_meta.py) | |
s23 should record the two amended stubs as "match the amendment, not the original", and the p1_bifolio gap as
"verifiable only through n3b's stub; no first-line hash in the result".

m1 over 10 seeds: no CLI seed in `m1_coordinates.py` (`SEED = 20261017` :32, `random.Random(SEED)` :389;
output fixed to results_m1_coordinates.txt :31). The template is `C-helpers/pw_m1_column.py:20-24`: per seed
`rng = np.random.default_rng(seed); res = m.collect(pages, rng); _, dci = m.boot(res, rng, n_boot=300)`. s23's
script imports m1 unchanged, loops seeds 0–9 with `n_boot=N_BOOT` (1000, :33) and writes `results_s23.txt` with
the 10 P(column-specific ≤ 0) values, their median, and the share < 0.05. C-constraints:150-152 already saw
0.003–0.093, 7/10 < 0.05, so the refile is expected to read "seed-unstable, no verdict". ~1 min per seed.

"Refiled with a power statement" means each negative is re-stated next to its smallest detectable effect:
- c1 hand 2: p = 0.133 (results_c1:10; 7 blocks, 105 assignments, floor 0.0095). Power 0.8 only at s = 0.60, 0.6 at
  s = 0.50; the manuscript sits at s ≈ 0.60–0.65 (C:28). Statement: "misses its own effect size 20–40 % of the time;
  not a negative". No re-run; c1 uses `default_rng(0)` (c1_quire_null.py:180).
- m6 Lc (24 pairs): r = 0.50 gives power 0.6 — no power at any plausible effect (C:34). Ls (64 pairs): r = 0.15 power
  1.0, r = 0.10 power 0.6 (C:33). ALL p = 0.050 is at r ≈ 0.015, below the r = 0.05 grid (C:30). No re-run.
- a3/d6: p = 0.106 (results_a3:2) / 0.0945 at 40 pages (results_d6:91); d6 SENSITIVITY 55 pages p = 0.0199
  (results_d6:93). Power curve not run (C:42-44, "unverified"): refile as "sample-size negative, power unverified".
Manifest gap list: j4, p2, q1, Q_RESULTS.md, TOP10-LEADS.md, s1/s2/s25/s26, s29, s30, s31, s15–s19 are absent from
.inventory (PLAN.md:49 names the first group); s23 lists them, does not edit the manifest.

## 4. v2.1 amendment — what must change in PREREG-v2.md (243 lines, frozen 19:27)

1. §3 "Known and accepted: Currier A alone fails m_final_enrich (×6.21)" (PREREG-v2.md:67-69) becomes a rule.
   Options: (A) A-derived bands — re-derive the seven v1 bands from Currier A's own 41-page bootstrap (C §2 last
   column: m_final 5.8–6.8, jsd 0.136–0.146, cross 0.131–0.139; a run like s15 restricted to A pages, 15 min);
   (B) drop m_final_enrich for A rows only, keep the other six (n6: A fails exactly that one band on all 3 translits,
   results_n6_ab_split:17). Recommendation: **(B)** with a sentence that an A-only joint pass is 6/6, because (A)
   fits bands to a 11k-token half whose enrichment widths are 14–19× (C:61-62) and would silently loosen every A band.
2. §3/§4 band widths: attach the s15 within-manuscript widths as the stated margin for every in/out call
   (s15_ranges.json `within_manuscript`, hashed b995aba6…); no band value moves (s15 reconciles s2 Part 3B 6/7,
   redup_pct CI differs, results_s15:52-53 — note it).
3. §7 families: X (gibberish) present via n7_gibberish_ranges.json (ac281dfd…); the eight X-jackknife extras stay
   no-weight (s15_ranges.json `no_weight_reasons`, O-046). State that the gibberish family is scored, never favoured
   on those eight.
4. §3 edge bands: U1 HOLDS (results_s18:303) — edge bands keep full weight; add the O-047 caveat (verse/formulaic
   Latin at 114–201 lines reaches +0.10–0.14) and the s19 re-wrap clause result.
5. §9 commands: ranges file becomes `s15_ranges.json`; results must print the ranges-file hash as well as the script hash.
6. New §11 reporting rule: per-round BH (see §5 below) and a power statement with every negative.
7. §6 A/B: add the s20 outcome (A inside real-line L on coupling) as a stated exception, not a verdict.
Hashes to re-freeze in `scoreboard/PREREG-v2.sha256` (new file `PREREG-v2.1.sha256`, old kept): PREREG-v2.1.md,
scoreboard/run_v2.py (unchanged 7dfdc9f7…), s15_ranges.json, n7_gibberish_ranges.json, results_m4_phase1_board.json
(bb861770…, still the L/C/G source). The amendment waits on nothing: s15 and s18 are filed.

## 5. Multiplicity rule for Phase 2 reporting (C-constraints §3)

Per round, one family = every p-value a Phase 2 result file prints. Expected entrants: s23's 10 m1 seeds (report
the median as one p, the 10 as sensitivity), c1 hand 2 (1), m6 Lc and Ls (2), a3/d6 (1, plus d6's 55-page
sensitivity as a second), m ≈ 6 formal p-values; s20 and s22 print no p-values (in/out and survival percentages).
Procedure: BH at q = 0.05 over the family, computed in the s23 script, written as a fixed "P-VALUE LEDGER" block at
the end of results_s23.txt: test, file:line, raw p, rank, BH cutoff (k/m·0.05), pass/fail, floor (exact-enumeration
floors such as c1's 0.0095 are marked "floor-bound", not ranked, C:153-155).
Any later Phase 2 or Phase 3 file that prints a p-value appends a row to the same ledger block in its own result
file and re-states m; the ledger is not a shared file. With m = 6 the BH cutoff for the smallest p is 0.0083;
none of the five refiled negatives can pass, which is the point: they are filed as power statements, not p-values.

## 6. Concurrency / sharing hazards

- Prefix: s20–s24 reserved by this session (TEAM-HANDOFF.md:266) but the peer's s30/s31 already cover the s20/s22
  deltas; claim s20/s22/s23 in TEAM-HANDOFF before writing, cite s30 by hash, never re-run its parts.
- `scoreboard/scoreboard.json`: written by score.py main (truncates), scoreboard/run.py (RMW), g0 (append); run_v2,
  n6, s18, s30 do not touch it (phase-1-instrument §6; run_v2.py:23). Phase 2 scripts must not call score.py main.
- `data/controls_synthetic/*.meta.json` is globbed by m4:167, n5:204, n7:332 and n6:305; any Phase 2 sidecar dropped
  there joins the next rerun's families. Use runs/s20/ or data/controls_realline/.
- `run_v2 --out X.txt` also writes X.json (run_v2.py:385); results_s20*.json names must not collide with a ranges file.
- Other sessions write: results_n7_* / n7_gibberish_ranges.json (any n7 rerun), results_m4_phase1_board.json (m4
  rerun, 703 s, no resume), results_s1/s2/s25/s26/s29/s30/s31 (Argon session), TEAM-HANDOFF.md. Daybreak is
  re-running n5 CHARWIN/Moran I (PLAN.md:162) — n5's stub hash will change again if that lands as an amendment.
- `m1_coordinates.py` writes results_m1_coordinates.txt (:31): s23 imports it, never invokes main. Nothing in Phase 2 is NMF-class.

## Decisions needed before the Phase 2 plan

1. Accept s30 (peer, pre-registered, hash OK) as the filed position-stratified A/B null, so s20 is the six-call
   comparison in §1 and not a new null?
2. Size floor for the real-line L range in s20: ≥5k tokens (drops 18 of 21 CREMMA manuscripts, keeps 10 rows) or
   pooled rows only (all, c15, prose15 plus the four s17 verse/epic texts)?
3. s22: file from disk (s2 3A, p2, s30 2A–2B) or commission an o1 ink-boundary token stream first (new deliverable)?
4. Currier-A rule: option (B) drop m_final for A rows (recommended) or (A) A-derived bands (15-min run)?
5. BH family definition: Phase 2 result files only (m ≈ 6) or all p-values printed since the v2 freeze?
6. p1_bifolio: accept n3b's stub entry as its hash record, or require a retro stub (which cannot be "before the run")?

## Cost table

| Step | Work | Minutes | Slot |
|---|---|---|---|
| s20 | stub + 6 run_v2 calls + reader | 2 compute, ~20 writing | single CPU, run_v2 |
| s22 | filing only (CLAIMS rows, U3 line); optional full-v2 widths glyph+ and GC2a | 0 (+30 optional) compute, ~15 writing | none (single CPU, 4.5 s/split) |
| s23 | 10 m1 seeds (import m1) + ledger + hash table | ~10 compute, ~20 writing | single CPU |
| v2.1 | PREREG-v2.1.md + PREREG-v2.1.sha256 | 0 compute, ~30 writing | none |
| v2.1 option A | A-derived bands run | 15 | single CPU |
