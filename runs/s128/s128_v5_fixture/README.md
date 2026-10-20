# s128 v5 fixture: stub-form check and N2-strata behaviour check (no Voynich data)

Run on the Grok Bot box, 2026-10-19 ~02:38-02:45 PDT, in a scratch root laid out like the project. Copied into it from Skynet:
vparse.py (0e317c9a...91c1), runs/s128/s128_layout_counts_v2.py (fcfd4ac4...0d35), runs/s128/s128_f0n2_real.py (79c9d1bb...a07e31),
runs/s128/s128_herbal_profile.py (c8d0a4e8...2f5f), the Ventura TEI (d17b4b81...b950), and from runs/s128/s128_v4_fixture/ the made-up
inputs synthetic_ivtff_v4.txt (a343e358...73b8, as data/fixture/) and madeup_counts.tsv (a3c656dd...e71, as data/fixture/).
The frozen scripts were run unchanged (same sha256 as in the v4 and v5 stubs). No script was edited or written for v5 apart from the
test harness t5_strata_check.py, which only imports functions from the frozen s128_f0n2_real.py and feeds them made-up page layouts.

Why: the v4 stub lists every entry as '<sha256> *<path>'. Both frozen scripts read only '<sha256><two spaces><path>' lines
(read_stub: `"  " in ln`). The v4 fixture tests used two-space test stubs, so this did not show there.
- stub_star.sha256 (v4 form) and stub_twospace.sha256 (v5 form): same 7 files, same hashes; sha256sum -c accepts both.
- T1: s128_layout_counts_v2.py with the star-form stub -> every entry NOT_IN_STUB, exit 2, nothing written (negative control).
- T2: same with the two-space stub -> HASH_CHECK_OK, exit 0; output out_t2.tsv sha256 600a7f0f...a729 = v4 fixture out_c1.tsv (positive control).
- T3: s128_f0n2_real.py with the star-form stub -> NOT_IN_STUB, exit 2, nothing written.
- T4: s128_f0n2_real.py with the two-space stub on madeup_counts.tsv -> NAME 15/15, RARITY 0/15, CALL_F0N2_REAL PASS, exit 0
  (out_t4.txt; same per-seed numbers as the v4 fixture R1 run).
Consequence: with a star-form stub, step d0 would exit 2 and s128 would stop. The v5 stub is written in two-space form.

t5_strata_check.py / t5_strata_check.log: what the frozen s128_f0n2_real.py strata()/n2() do on made-up layouts, used to write v5's
widening, one-page-stratum, fill-order and overflow wording to match the frozen deciding code:
- A: singles > 25% of the page set -> widened pages join only each other by (Q,H,L), never an existing multi-page stratum.
- B, D: singles <= 25% -> no widening; a single page stays a one-page stratum.
- C, D: a held page's start token is never swapped with another page; a one-page stratum's paragraph-initial tokens are permuted
  only among that page's own paragraph-initial slots.
- E: chapter tokens past the page's last slot are dropped. F: fill order = strata by first page (count-list order inside), held pages last.
Logs: stub_form_tests.log (T1-T4), t5_strata_check.log.
