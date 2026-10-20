# Cold-start acceptance test — 2026-10-17 18:55 PDT

Rule: answer using only INDEX.md plus at most two register opens. Each answer names where it was found.

| # | Question a resuming agent must answer | Answer | Found in |
|---|---|---|---|
| 1 | What is the current source of truth for the scoreboard, and can I edit it? | `PREREG.md` + `scoreboard/score.py`, frozen; hashes in `scoreboard/PREREG.sha256`. Do not edit; freeze v2 beside it (O-007). | INDEX "Five things" #2; OPEN O-007 |
| 2 | We want to use held-out word order as evidence the text has content. Has that been tried, and what happened? | Yes (F1/F3/K). Killed by n2: a 4 % word-pair habit generator reproduces the manuscript's residual on all three transliterations. Caveat: that generator has ~1,750 types; rerun at 7k is O-039. | INDEX "Do NOT resume"; LEARNINGS L-027; OPEN O-039 |
| 3 | Which number in the live documents is unverified or wrong? | 25 STALE and 22 UNSUPPORTED rows; e.g. the 10.728 retirement bar (c-079, flat-UNK artefact), the 15–25k type budget (c-200, refuted by k4), "all rotation-null p=0.000" (c-066). | INDEX "Read these before trusting"; CLAIMS §E / claims-notes.md |
| 4 | What should the next producer target, and what must it not do? | m5's four draws (paragraph-initial gallows lexicon, y/d/t/s line-start reweighting, m/g line-end set, d-drift) plus edge coupling at ≤7k types; no third glyph rule, no nudging c2's two rates. | INDEX "Five things" #3 and "Do NOT resume"; DECISIONS D-032/D-020; OPEN O-008 |
| 5 | Which claims does the red team say we treat as known but never measured? | Real scribal line-edge habits; whether coupling is Voynich's or the handed table's; power of the negatives; whether h2 ≈ 2.1 is text or alphabet; where word boundaries are; bifolio null. | INDEX #5 → REDTEAM §3 |

Result: 5/5 answered within the budget. Holes found and fixed during the test: none in the registers; `results_p1.txt`
(bifolio null, another session, 18:47) is not yet in MANIFEST.jsonl — add when filed (O-004).
