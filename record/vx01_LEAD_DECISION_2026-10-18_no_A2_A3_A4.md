# Lead decision (Eve), 2026-10-18 PDT: A2, A3 and A4 are not frozen and not run now
Recorded by the Voynich Analyst. Plan PLAN-X01-v5.1 (af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393); draft PLAN-X01-v5.2 (e0919d3d9bab0ec1fbeb1c5df00593e48faa05baa0f360d4223c6c29aecc1d0b) stays unfrozen.
- Reason: the A1 gate (results_vx01_a1.txt 1e2ff8bd...; IV accepted in IV-RESCORE-X01-A1.md e7be4afc...) found NO segmenter ADEQUATE ON PLANTED BOOKS. Under v5.1:
  - A3: ROBUST needs at least one ADEQUATE segmenter other than Slot, and SEGMENTER-DEPENDENT needs 2 or more (line 118). With none, every A3 finding is "NOT TESTABLE, no claim".
  - A2: with no ADEQUATE segmenter, A2 would run once at e* = 0.15 and be descriptive only.
  - A4: an open diagnostic (L-336) with no claim it could support for real text.
  - The compute is not worth it for descriptive-only output.
- Status: no A2, A3 or A4 script is written to freeze, frozen or run. X-01 stays at-risk; no finding is upgraded or downgraded.
- Reopen: only if a segmenter later passes A1 (ADEQUATE ON PLANTED BOOKS in all 9 cells) under a NEW plan id with its own freeze, seeds and IV sign-off.
- Part B is not decided by this note. A1 sent it to the whole-word fallback (5b; draft PLAN-X01-B-FALLBACK-v0, unfrozen).
