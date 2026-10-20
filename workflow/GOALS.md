# Goals — voynich (living document)

Format: goal-setting discipline (`/goals`). Project-scoped goals that ladder UP to the
portfolio (`~/.claude/planning/goals/GOALS.md`).
Last updated: 2026-10-19

<!-- Quality bar for EVERY goal: Outcome (not activity) · Achievable · Verifiable (yes/no
     DoD) · Owned · Horizoned. Every goal here must name the portfolio Quarter/North Star it
     advances — a project goal that ladders up to nothing belongs in the portfolio file or
     nowhere. -->

## Ladders up to

- ↑ NS2 — this repo is the canonical investigation (`workflow/comms/<team-comms>`). A closeout here is what NS2 asks for. It does not exist yet.
- ↑ portfolio Q3 — one door and a knowledge base that matches the claims register. Done 2026-10-19.

---

## Quarter — 2026-Q4

### PQ1 — The sprawl gate is clean and the knowledge base matches the claims register
- **Outcome:** A third party in this repo gets a clean sprawl report and a knowledge base whose claim count equals the claims register.
- **DoD:** All three are true. (1) `python tools/findings_graph.py sprawl` prints 0 unlinked c-300+ claims, 0 unreferenced `results_*.txt`, and 0 undeclared root markdown. (2) `python tools/vkb/check.py` prints `VKB CHECK: PASS`. (3) `SELECT COUNT(*) FROM claims` equals the number of `CLAIMS.md` rows matching `^\| `c-`.
- **Owner:** Jon
- **Horizon:** 2026-Q4 · target 2026-11-16
- **Status:** done 2026-10-19 09:35. (1) 0, 0 of 365, 0. (2) PASS, 0 fail, 10 warn. (3) 547 and 547.
- **Ladder:** ↑ portfolio Q3 (and through it to NS2) · ↓ PN1, PN2
- **Same goal as:** portfolio Q3

---

## Now — this week / sprint

### PN1 — The sprawl gate reports no orphans
- **Outcome:** Every recent claim, result file, and root markdown is declared in the findings graph.
- **DoD:** `python tools/findings_graph.py sprawl` prints 0 unlinked c-300+ claims, 0 unreferenced `results_*.txt`, and 0 undeclared root markdown.
- **Owner:** Jon
- **Horizon:** Now · by 2026-11-02
- **Status:** done 2026-10-19 09:32. Output: 0 claims, 0 of 365 results, 0 root markdown.
- **Ladder:** ↑ PQ1

### PN2 — The knowledge base contains every claims-register row
- **Outcome:** The derived database matches the claims register and still passes its checker.
- **DoD:** `python tools/vkb/check.py` prints `VKB CHECK: PASS`, and `SELECT COUNT(*) FROM claims` equals the number of `CLAIMS.md` rows matching `^\| `c-`.
- **Owner:** Jon
- **Horizon:** Now · by 2026-11-02
- **Status:** done 2026-10-19 09:35. Rebuild PASS. Counts 547 and 547.
- **Ladder:** ↑ PQ1

---

## Archive
