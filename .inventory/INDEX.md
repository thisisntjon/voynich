# Voynich manuscript research — inventory index

**Last inventory:** 2026-10-17 21:09 PDT (refresh of the 18:53 build; p1 repoint 19:27) · **Gate:** FAIL on G3 coverage only (333 rows, 0 shape fails; 328 root sidecar outputs unaccounted, see `runs/2026-10-17/gate-2103.txt`) · **Claim coverage:** 73 % of numbers in 22 root docs · **Claims:** 332 rows, 283 VERIFIED (8 literature), 25 STALE, 23 UNSUPPORTED (10 literature-only), 1 unscored
*L0 map. Keep under ~150 lines. Depth lives in `registers/`. Numbers live in result files, never here.*

## What this is
A one-day (2026-10-17), multi-session computational attack on the Voynich manuscript (Beinecke MS 408)
using the Zandbergen–Landini EVA transliteration, natural-language, real-line and synthetic controls, and
a frozen board (v1 seven bands; v2 family discrimination; v2.1 amended margins). Goal per `../PLAN.md §0`:
a fixed key or code that reads ten unseen pages. Result: **not deciphered**; the day narrowed what the
text can be, killed several of its own best leads, and left three constraints that survive their controls.

## Current state (2026-10-17 23:33)
- **Front door:** `../README.md` (reading order). Plain-language results: `../workflow/FINDINGS-REPORT.md`. Constraints
  and how they connect: `../workflow/CONSTRAINTS-MAP.md`. Next steps: `../workflow/research/strategy-2026-10-17.md`.
  Workflow of record: `../workflow/PLAN.md`. Measurement map and prefix claims: `../TEAM-HANDOFF.md`.
- **Phases:** 1 closed 20:37 (U1 holds), 2 closed 20:55, 3 closed 22:21 as a **tie** (`../results_s35.txt`, D-047). Phase 4
  (routes to a reading, main session) is written in `../workflow/research/phase-4.md`; its gate is Jon's.
- **Line constraint (A1)** confirmed three ways: transcription (s18/s44: A +0.135, B +0.218 vs Latin prose +0.008),
  independent replication on a second machine (c-349), and ink line breaks from the Yale scans (s45, c-359).
- **Two-layer word:** the within-line rhythm lives in the prefix/suffix layer (s33, s39); the held-out word-order residual
  lives in the cores (s39), which order like words, not letters (P4-D1). Two-layer producers with either copied or
  Latin-stem cores both reach F1, the rhythm and the character-model sign on most cells (s36, Argon): **the board can no
  longer tell generator from message under a shared wrapper** (L-130).
- **Corrected:** the Currier-B coupling is reached by short Latin verse manuscripts (replication + own s18 rows; A3, L-125).
- **Killed at tested designs:** edge-pitch music (s24), glyph-class superimposition residual (s34), liturgy,
  copied-without-understanding and conlang framings (s37), plain ciphers with one layer as nulls (s43).
- **Open:** word boundaries from ink (O-048 word half: s38 boxes vs s45 pixels disagree), O-051, O-052.
- **Exploratory, not citable:** `../incoming/ten-theories/` (no stubs, held-out leakage; D-048).

## The five things that matter
1. **`../workflow/CONSTRAINTS-MAP.md`**: the established constraints A1–A15 and the dots between them.
2. **`../results_s18.txt` + `../results_s44.txt` + `../results_s45.txt`**: the line is a unit of the text, in A and B, in the ink.
3. **`../results_s39.txt` + `../results_s33_line_scales_interlock.txt`**: rhythm in the affixes, content-like order in the cores.
4. **`../results_s36_two_layer_operator_core.txt`**: the two-layer producers that exhaust the board's discriminating power.
5. **`../workflow/research/phase-4.md`**: the cheapest decisive tests for whether a reading is reachable at all.

## Where to look
| I need… | Open |
|---|---|
| every asset, value-ranked (A 54 · B 210 · C 53 · D 16) | `INVENTORY.md` (rows v-215+ not yet rendered there; use the manifest) |
| a machine list / to diff (333 rows) | `MANIFEST.jsonl` |
| a number and its source file (332 ids, `c-001`…) | `registers/CLAIMS.md` (+ `runs/2026-10-17/claims-notes.md` for the definitional variants of h2, coupling, edges) |
| what we tried and what failed (117 rows, failures first) | `registers/LEARNINGS.md` |
| a metric definition, its implementation and test (86 rows) | `registers/METHODS.md` |
| how to run something, which Python, what it writes (114 rows) | `registers/TOOLS.md` |
| why we chose or killed something (45 rows) | `registers/DECISIONS.md` |
| open questions with closer and cost (49 rows) | `registers/OPEN.md` |
| the adversarial pass (23 attacks, ranked five, unknowns) | `registers/REDTEAM.md` |
| where an old file went, prefix collisions, what was deleted and why | `registers/TOMBSTONES.md` |
| the file-level census the curate run made (overlaps this tree) | `../INVENTORY.md`, `../workflow/curation/` |

## Do NOT resume (full D-list with reasons in `INVENTORY.md`)
- Letter solvers into Latin/Italian/German with Voynich spaces kept (`a6*`): at the null with a 100 % positive control.
- Topic NMF / within-hand NMI as a discriminator (`b5`): hand 2 is underpowered at its own effect size (s23, c-323), hand 1 sits at the 1/55 floor; hand-1 NMI holds against the powered 7k generator (n6, c-302) but cannot be ranked under correction.
- f57v as a cipher period (`d6`, `e3`): 17 tokens, 18 glyphs, a physical ring; not a key.
- Homophone-class recovery (`f4`, `j1–j3`): no power at Voynich-like type inflation (`i1`).
- Column copying by word index (`b1` T2): replaced by coordinates (`m1`); residual +0.48 pp, seed-unstable (7 of 10 seeds below 0.05, s23 c-322): not a negative, not a positive; no verdict at this design.
- Codebooks as built (`ctl_nomen*`): h2 3.2–3.7 vs 2.1; only a skewed templated code could survive, which is a cipher.
- Nudging c2's two line rules, or a third glyph rule: m5 says the target is four vocabulary draws, not glyph rules.
- Citing F1/F3/K held-out word order as evidence for meaning at small lexicons: n2; at 7k types the question is reopened by n6 (O-045), not settled.
- The three "generation signatures" (char-win, position lock, Moran I) as family discriminators: n5 (D-044). Moran I returns only as the within-line constraint above (s21), which is a different statistic.
- m6 Lc/Ls, a3, d6 as "fails": underpowered or power-unverified (s23, c-323, L-112); they are not negatives.

## Read these before trusting any number
- Four h2 values are all "correct": 2.126 (25k sample, a1/score.py) · 2.109 (all tokens) · 2.093 (lines 2+, b4) · 2.397 (glyph+). State sample and alphabet with the number (`claims-notes.md` §variants); s30 adds 2.51 for GC2a (c-325).
- The h2 and sd_len bands are EVA-specific; the other five v1 bands are transcription-robust (`m7`). v2.1 margins are ZL3b-only (s15).
- redup is estimated three ways: a1/score.py uses /(N-1) over the 25k sample; s2 and b4 use /N over lines 2+ or all tokens (`registers/METHODS.md` notes). Compare only like with like.
- p-values: 582 were computed today, 291 below 0.05 (C-constraints). Under BH at q=0.05 with the Phase 2 family m=7, no survivor (`../results_s23.txt`, c-324); c1 hand 1 and n3 are floor-bound at 1/55 and unranked. Quote a p-value with its family.
- The s23 hash ledger (c-321) lists two FAILED stub lines: the pre-crash originals in `n5_signature_discrimination.prereg.sha256` and `n6_ab_split.prereg.sha256`, each superseded by an OK amendment line in the same file. Match the result file's printed hash to the amendment, not the first line.
- `results_d2.txt` is UTF-16; its 10.728 unigram bar is an artefact (`m3`); b4 generator rows are not cross-process reproducible (hash-seed).
- `results_p1.txt` holds order-sensitivity output, not the bifolio null (TOMBSTONES 19:12); `results_n4b_glyph.txt` carries an N6 header; `results_s25/s26` duplicate `results_s1/s2`.
- 25 doc sentences disagreed with their own result files today (`docs/AUDIT-2026-10-17.md`, CLAIMS §E). The result file wins; `../AGENTS.md` says the same.

## Maintenance contract
- A number goes into a doc only with its result-file name; new numbers get a CLAIMS row in the same change (n3b, s29, s31 numbers quoted in the map still lack rows).
- New rounds append to `registers/LEARNINGS.md` / `DECISIONS.md` / `OPEN.md`; no new summary markdown at the root.
- Moves go through the map owner with a stub and a TOMBSTONES row; deletions only on the user's word naming the path. Prefix collisions get a TOMBSTONES row too.
- Re-run: `python -I ~/.claude/skills/inventory/scripts/census.py --root . --out .inventory/runs/<DATE>/census-<HHMM> --exclude .venv --exclude .uv-cache --exclude .uv-python --exclude __pycache__ --exclude data/external --exclude data/controls_raw --exclude data/controls --exclude data/controls_synthetic --exclude data/translit`, then `validate.py` and `claim_coverage.py` as recorded in `runs/2026-10-17/gate-2103.txt`.
- Known gate limit: per-corpus sidecar outputs at the root (`results_n6_<tag>`, `results_n7_<tag>`, `results_s17/s18/s20_<tag>`, ~330 files) are one asset each but the G3 coverage gate matches directory prefixes only, so they count as unaccounted until either enumerated or moved under `runs/`.

## Gate record
See `runs/2026-10-17/gate.txt` (18:53 build, PASS) and `runs/2026-10-17/gate-2103.txt` (21:09 refresh: validate.py and claim_coverage.py output, census in `census-2103/`), plus `runs/2026-10-17/cold-start.md` (five-question acceptance test).
