# vx01 A1 disclosure 3: report-only small-inventory books are DROPPED (deviation from PLAN-X01-v5.1 line 100)
Plan: PLAN-X01-v5.1 sha256 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393. New file; nothing existing edited. Recorded 2026-10-18 PDT, before the A1 gate run.

- PLAN-X01-v5.1 line 100 says: "Report-only secondary books at a small, Zattera-sized inventory (25 prefixes, 163 cores, `results_s76.txt:49`) are scored but do not gate."
- The frozen `vx01_a1_known_answer.py` (5c408207...) does NOT build or score them: the plan gave them no seeds in 3a and no suffix count. Eve decided (2026-10-18): DROPPED from this run, not a fork. They never gated, so no A1 label depends on them.
- The A1 gate result therefore covers 8 rows x 135 gate books (3 sets x {G1, G2, NULL} x 15) only. This note goes with the A1 result; v5.2 records the same drop.
