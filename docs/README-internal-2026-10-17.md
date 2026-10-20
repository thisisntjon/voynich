# Voynich manuscript investigation

**Status (2026-10-17 23:33 PDT): not deciphered.** No key, reading or language has been found, and nothing here predicts a
word on pages we have not looked at. What the work has produced is a set of tested constraints that any explanation must
meet, a list of explanations that were tested and failed, and a strategy for the next steps.

## Start here (read in this order)

> Superseded 2026-10-18 16:01 PDT: the start-here list is now AGENTS.md "Start here" (workflow/PLAN.md `Current stage:`, workflow/FINDINGS-MAP.md section 1, DECISIONS D-066, LEARNINGS, TEAM-HANDOFF). Status: FINDINGS-MAP section 1 / D-068. The table below is the 2026-10-17 order; rows 1-3 and 5 are historical narrative, not current status.

| # | File | What it tells you |
|---|---|---|
| 1 | `workflow/FINDINGS-REPORT.md` | Plain-language account of everything established, what failed, and the addenda since |
| 2 | `workflow/CONSTRAINTS-MAP.md` | One page: each established constraint with its number and source, and how they connect |
| 3 | `workflow/research/strategy-2026-10-17.md` | What we do next and why, in priority order |
| 4 | `workflow/PLAN.md` | The workflow of record: phases, gates, prefix table, phase log (newest first) |
| 5 | `.inventory/INDEX.md` | Map of the registers: every number (CLAIMS), finding and failure (LEARNINGS), decision, open question |
| 6 | `TEAM-HANDOFF.md` | Where each measurement lives, prefix claims, how to run things |

Public-evidence baseline (no project results): `workflow/research/public-baseline.md`.

## House rules (all sessions)

- **Pre-register.** Hash the script into `<name>.prereg.sha256` before it runs; the result file prints the hash and
  `stub_match`. A result without a pre-run stub, or with held-out leakage, is exploratory: it is filed but never cited
  (D-048). Example: `incoming/ten-theories/`.
- **Results files win.** If a doc and a `results_*.txt` disagree, the result file is right.
- **Claim a prefix** in `TEAM-HANDOFF.md` before writing `s<NN>_*` files. Prefixes are no longer unique; cite by filename.
- **One home per thing.** Numbers live in `.inventory/registers/CLAIMS.md`; constraints in `workflow/CONSTRAINTS-MAP.md`;
  state in `workflow/PLAN.md`. Do not start new status, plan or summary files at the root.
- **Id ranges (D-054).** voynich-08 files c-396–c-499, L-153–L-299, O-053–O-099; every other session files c-500+, L-300+,
  O-100+. Check the last id in the register before appending.
- **Nothing is deleted.** Superseded docs carry a pointer line at the top; moves go through `.inventory/registers/TOMBSTONES.md`.

## Historical documents (superseded, kept for the record)

`PLAN.md` (root, 15:25 campaign plan), `TOP10-LEADS.md`, `OPPORTUNITY-NEXT.md`, `REGISTER-DIFF.md`, `PREREG-v2-DRAFT.md`
(superseded by `PREREG-v2.md` and `PREREG-v2.1.md`), `STEAL-VERIFY.md`, `J_RESULTS.md`, `K_RESULTS.md`, `Q_RESULTS.md`,
`R_RESULTS.md`, `SCOUT-EXTERNAL.md`, `BREWER-LEWIS-CHECK.md`, `REDTEAM-CHECKLIST.md`, `docs/rounds/`. Their findings are
harvested into the registers.

## Layout

- **Scripts** sit at the root with a letter prefix per round (`a1_…` to `m7_…`, `ctl_…`). They import each other by flat filename, so don't move them.
- **Results**: each script writes `results_<prefix>.txt`. If a results file and a doc disagree, the results file wins.
- **Data**:
  - `data/ZL3b-n.txt` is the reference transliteration, read through `vparse.py`.
  - `data/controls/` holds natural-language controls.
  - `data/controls_synthetic/` holds generator and cipher controls.
  - `data/external/` holds other transcriptions, word boxes, cribs and published corpora; its fetch log is `data/external/README.md`.
  - `data/facsimile/` holds six page images.
- **Scoreboard**: `scoreboard/` is the benchmark scorer (`score.py` is frozen v1), with reproduction tests in `tests/`.

How to run anything is in `TEAM-HANDOFF.md` under "Run".


