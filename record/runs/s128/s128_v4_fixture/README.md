# s128 v4 fixture tests (no Voynich data)

Run on the Grok Bot box, 2026-10-19 ~02:00-02:20 PDT, in a scratch root laid out like the project:
`vparse.py` (sha256 0e317c9a...91c1), `runs/s128/s128_layout_counts_v2.py`, `runs/s128/s128_f0n2_real.py`, `runs/s128/s128_herbal_profile.py`,
the Ventura TEI at its project path, and the inputs below under `data/fixture/`. The scripts are byte-identical to the ones in runs/s128/ (same sha256 as in the v4 stub).
Inputs (hand-written or made up, invented strings, not from any transliteration):
- synthetic_ivtff_v4.txt, synthetic_ivtff_v4_nomarks.txt: IVTFF-shaped test files.
- madeup_counts.tsv: made-up count list, 112 pages, 4-10 tokens x 5-12 lines, 28 (Q,B,H,L) strata, 2 pages with H '?'.
- madeup_counts_toolong.tsv: 8 pages of 12 x 90 tokens (longer than nearly every Egerton chapter).
Test stubs: stub_ok.sha256 (true hashes) and forced mismatches stub_bad_data, stub_bad_self, stub_missing_data, stub_bad_counts, stub_bad_f0n2self.
C4 altered vparse.py temporarily (appended a comment line) and restored it.
Logs: counts_tests.log (C1-C6), f0n2_tests.log (R1-R4). Outputs: out_c1.tsv, out_c6.tsv, out_r1.txt, out_r4.txt.
Results: C1 exit 0; C2-C5 exit 2, nothing written; C6 exit 3; R1 PASS (NAME 15/15, RARITY 0/15); R2, R3 exit 2, nothing written; R4 FAIL (all seeds failed: NAME 0/15, RARITY 15/15).
