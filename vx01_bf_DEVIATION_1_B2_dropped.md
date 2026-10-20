# vx01 Part B deviation 1: B2 dropped from PLAN-X01-B-FALLBACK-v1
Date 2026-10-18 PDT. Decision: Eve (lead), on IV-REVIEW-X01-B-FALLBACK-v0.md item 4 (d2ab5f40b22beeb3f28feb7c2916753d8210c328b52d6d3c3c5ebd223ddc1df7). Recorded by the Voynich Analyst. New file; nothing frozen or run.
- What v5.1 says: 5b runs B0, B1 and B2 under the fallback (v5.1:155, :160). B2 = "thin tests resting on X-01": F-44 Zattera arm (pool events until MDE <= 0.10) and F-50 constancy (MDE <= 0.4 SD) (v5.1:161).
- What changes: B2 is NOT run under PLAN-X01-B-FALLBACK-v1. No `vx01_b2_*` script is written or frozen.
- Why: both arms are segmented, so neither can run on whole-word units as 5b requires (5b:156):
  - F-44's arm is a Zattera-segmented test, and Zattera failed all 9 A1 cells (IV-RESCORE-X01-A1.md);
  - F-50 is built on SQLite DB features and is A3 N/A (v5.2 0c).
  - B-FALLBACK-v0 gave B2 seeds and a script name, but no units, pass line, null or falsifier.
- Effect: F-44 and F-50 keep their current status; no claim either way comes from this plan. The B2 seeds of v5.1 3a (dev 20264101-103, gate 20264201-203) stay in frozen `vx01_common.py` and are never used. Their hashes in GATE_SEED_SHA256 still block their use as dev seeds.
- Reopen: only under a new plan id that defines B2 on whole words, with its own fixed lines, null and falsifier.
UNVERIFIED until IV signs.
