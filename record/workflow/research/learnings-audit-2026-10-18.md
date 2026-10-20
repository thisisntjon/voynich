# Learnings audit, 2026-10-18

Written 2026-10-18 12:14 PDT (clock read with `date`). Scope: `.inventory/registers/LEARNINGS.md` only. The register is still the one home for learnings. This file records how it was audited. No row was deleted and no row's text was edited. Corrections were made only by appending new rows and adding bracketed markers to date cells. A backup taken before the edit is in the session scratchpad. FINDINGS-GRAPH.yaml and the other docs were not touched.

## 1. Census: learnings found outside the register

The following were searched for 'learning', 'lesson', 'what we learned', 'post-mortem', 'pitfall' and `L-nnn`:
- the root `*.md` files, `workflow/`, `workflow/research/` and `workflow/comms/`, plus `.inventory/registers/DECISIONS.md` (D-040..D-064) and `workflow/TRIANGULATION.md`;
- script docstrings in the root and in `tools/`;
- `runs/roach-r1r2-raw/REPORT.md` and `runs/roach-r{3,4,5}/README.md`;
- Daybreak's lab `lab/codex_lab`, read-only and treated as data.

Finding a lesson "not captured" means a grep of the register for its key terms and numbers came back empty. A row that says the same thing in other words could have slipped past that check.

Uncaptured lessons found, now filed as rows L-188..L-204:

| New row | Source | Theme |
|---|---|---|
| L-188 | D-064: s93 edited after freeze, results overwritten | process/gate |
| L-189 | codex_lab pair-null addendum: the ~90 % (P,S)-shuffle retention is mechanical | method |
| L-190 | same, plus independent audit: the core collapse depends on the segmenter (fixed segmenter keeps 48.8-54.1 %) | segmentation |
| L-191 | roach r3: core-dependent affixes are stronger in Latin and Italian | NL controls |
| L-192 | roach r5: raw Witten-Bell gains are negative on IID streams | method |
| L-193 | roach r1/r2: line bootstrap inflates plug-in MI (`explore_r2.txt` absent, so unverified at source) | method |
| L-194 | codex_lab: the s83 positive-control fixture failed (1/4 folds) | ciphers |
| L-195 | D-062: the s89 Arm B self-recovery failed (4/15) | generators |
| L-196 | phase-4-units: the lift-split swing is a split artefact (random-cut numbers have no results file, so unverified) | segmentation |
| L-197 | phase-4-decipherability: a trigram objective prefers a wrong key (scratchpad check, no results file) | ciphers |
| L-198 | codex_lab: the s72 solver freezes a greedy parse | ciphers/segmentation |
| L-199 | codex_lab: the s101 vision labels are invalid (AUC .12-.59) | physical |
| L-200 | codex_lab: the s52 page predicate bug (Q20 has 285 pages, not 295) | process |
| L-201 | C-constraints: h2 small-sample bias, four filed h2 values, `inf` counted as out | method |
| L-202 | C-constraints, D-042: shared RNGs, sidecar dialects, UTF-16 output | process |
| L-203 | D-054, D-064: id collisions, id bands, db-sNN | process |
| L-204 | C-constraints: entrants carrying the manuscript's own tables match by capacity | method |

The search found no lesson-bearing docstrings in the scripts. `docs/` and `workflow/comms/` added nothing new. `results_s96.txt` (P-28, the D-063 amended reruns) was still being written at 12:06 and is not filed. Its two printed calls (`CALL_1A`, `CALL_1B` True) need filing once the run completes.

## 2. Integrity of LEARNINGS.md

- **Ids.** There are no duplicate ids. `L-028a` is a deliberate sub-row. The lead band runs L-001..L-187 with no gaps, and the Argon band runs L-300..L-316 with no gaps. L-188..L-299 were unused when this audit started (checked by grep across `*.md`, `*.yaml` and `*.txt`). Rows sit out of numeric order in a few places (L-152 after L-100, L-130..L-132 after L-136, L-143 after L-158, and the Argon rows interleaved). That is file order, not an error.
- **Malformed rows.** Eight rows contain an unescaped `|` inside a code span or formula, which splits the cell when the table is rendered: L-119, L-133, L-142, L-154, L-301, L-302, L-306, L-309. The text was left as is, because it was not mine to edit. The fix is to escape each pipe as `\|`. L-072, L-080 and L-204 use the escaped form and render correctly.
- **Evidence paths.** Every backticked evidence path exists. Two globs (`results_a6b_*.txt` in L-002, `runs/s38/*.meta.json` in L-136) resolve to files.
- **Superseded or contradicted rows.** Each was marked in its date cell with `[..., 2026-10-18]`:
  - **A14 flipped by s80 (L-172):** L-123, L-126, L-135, L-142, L-143, L-151, L-164, L-166, L-170.
  - **The 'affixes carry none' half withdrawn by roach r5 (L-176):** L-126.
  - **D-063 corrections of Argon's s85/s86/s88/s92 filings (claims c-522..c-533):** L-312, L-313 (F-21 is also weakened by L-187), L-314 (its `impl` label is wrong under D-064), L-315.
  - **D-064, s93 not admissible:** L-316 → L-188.
  - **Other chains:** L-027 → L-102 (F1 reopened at manuscript scale); L-087 → L-096; L-098 → L-102; L-130 → L-154; L-168 → L-177/L-180; L-178 → L-179; L-308 (its H-06 lead) → L-179.
  - **Rows corrected by new external evidence:** L-118 and L-133 → L-189 and L-190; L-167 → L-191; L-137 and L-139 → L-200.
  - **Rows not marked because they already self-mark:** L-031 (by L-027), L-165 (by L-304), L-085 (non-discriminating), L-121, L-303, L-304.
- **Contradiction still open.** Codex_lab's terminal audit says s93 is CALL_3 False, while L-316 reports TRIANGULATED. The marker on L-316 records this. The graph and lead decide the reconciliation (D-064).
- **Navigation index.** An index was added above the table. It has 15 themes, and every L-id appears under at least one of them.

## 3. Top 10 method lessons the next experiments must obey

1. **File the printed call, not the prose.** A pre-registered call printed False cannot discharge anything. A threshold that was not written before the run gives a descriptive result only (D-063, L-186).
2. **Freeze first and never overwrite.** A stub match is not enough: the source hash must predate the first result. A changed script means a new result file and a new id (L-188, L-097, L-103).
3. **`impl` means independent code.** Our code run on another transliteration counts as `data`. A run that imports our loaders or producers is method or split, whoever ran it (L-186, L-203, TRIANGULATION step 3).
4. **Compare order statistics at matched inventory.** A plug-in MI excess over thousands of sparse types has a biased sign. Use matched-K, and calibrate against language and planted ciphers at the same K (L-166, L-170, L-172).
5. **Decide shuffle-excess claims on the permutation p.** Subsample intervals miss realisation noise (L-171). Line bootstraps inflate MI (L-193). Raw back-off gains are negative on IID data (L-192). Run an IID fixture first.
6. **A planted positive control must pass before the manuscript run.** If the fixture fails, the manuscript result is uninformative and is filed as such. Solver power and construction are reported separately (L-021, L-194, L-195, L-198, D-057).
7. **Treat segmentation and reading order as assumptions to discharge.** Use at least two independently designed segmenters and random-cut controls (L-166, L-190, L-196). Prefer order-free designs, and audit directional claims (L-173).
8. **A property is distinctive only after the reference texts lack it.** Check natural-language, real-line, genre and gibberish references before calling anything Voynich-specific (L-109, L-181, L-183, L-184, L-191).
9. **Evidence comes from held-out quires.** Leave-one-quire-out, and state how many producers have already been tried on a split. A producer that carries the manuscript's own tables or lexicons matches by capacity and proves nothing about mechanism (D-056, L-018, L-130, L-204).
10. **Know what a null can move.** A constrained shuffle that leaves most tokens fixed reports high retention by construction, so report the mutable fraction alongside it (L-189). Undefined metrics count as missing, not as failures. Compare h2 only at a stated token count and with the same unit definition (L-201).
