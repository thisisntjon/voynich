# Phase 8.5 cold-start re-score of the question bank

Stamp: Mon Oct 19 10:22:19 PDT 2026 (`date`). Scorer: fresh agent with no prior context. It worked read-only except for this file. It did not open phase8-1-baseline.md or any other phase8-* file except the bank.

Bank check: `sha256sum workflow/research/phase8-1-bank.md` returned 0b005a3a1772f6853255b87ed67e4ada8839b70986154afd466c007e5b543920. This matches the expected hash.

Counting: an **open** is any access that returned file content (a Read, a grep or query that printed lines or rows, or a command that printed file text). Path-only listings, count-only listings and empty or failed searches are not opens, but they still count as steps. A **step** is one tool call. Content reused from an earlier question counts as 0 new opens.

**Setup (counted separately):** AGENTS.md (preloaded into context), the bank (1 open), and INVENTORY.md as the single index file (1 open). There was also one hash-check step and one path/line-count step, so setup took 4 steps and 2 tool opens plus AGENTS.md. INVENTORY.md gave almost no routing value: it lists folders, not where each kind of fact lives. The AGENTS.md canonical map did the routing.

## Per-question results

| Q | Opens | Steps | Result |
|---|---|---|---|
| 1 | 4 | 5 | partial |
| 2 | 1 | 1 | complete |
| 3 | 1 | 1 | complete |
| 4 | 3 | 3 | complete |
| 5 | 2 | 2 | complete |
| 6 | 3 | 4 | partial |
| 7 | 2 | 2 | complete |
| 8 | 1 | 1 | complete |
| 9 | 3 | 3 | complete |
| 10 | 2 | 2 | complete |
| 11 | 1 | 1 | complete |
| 12 | 1 | 1 | complete |
| 13 | 1 | 1 | complete |
| 14 | 2 | 5 | complete |
| 15 | 1 | 1 | complete |
| 16 | 2 | 3 | complete |
| 17 | 0 | 0 | complete (reuse) |
| 18 | 1 | 1 | complete |
| 19 | 1 | 1 | complete |
| 20 | 1 | 1 | complete |

### Q1. f68r1: section, quire, hand, label count, published facts, findings
- **Answer:** quire I (Beinecke IX), bifolio I-1 with f67, section/illustration A (astronomical; Stolfi subset "cos"), Davis hand 4 (Currier "?"). It has 29 star labels and 37 loci in total, plus 7 lines and 31 tokens in `folios`. Published facts come from Zandbergen (2025) and Stolfi/Reeds: "Sun over Moon" title, three-way foldout, pencilled "a", yellow/blue star colours, RZ language A/Ce. Register rows: L-346, O-012 (closed by s52/s29). No finding names f68r1. The nearest label findings are F-43 (CONTESTED) and F-44 (SINGLE), and both are generic.
- **Source:** `tools/vkb/queries/folio_dossier.py f68r1` (VKB `folios`, `page_facts`); VKB `findings`.
- **Cost:** 4 opens, 5 steps (dossier; an empty grep of the graph for f68; a table list; a schema query; a findings search).
- **Gaps and conflicts:** the dossier has no "findings" section, and the graph has no folio-to-finding link, so "findings that touch it" cannot be answered directly. Published facts differ on hand (LFD 4 vs Currier ?), language (Zandbergen "-" vs Currier "?") and subset (A vs cos). The dossier flags these as DIFFER.

### Q2. F-20 support and grade
- **Answer:** F-20, "There is no internal crib", is TRIANGULATED and standing. Supporting lines:
  - s53 method (c-388), with Argon s53 impl and data (c-377)
  - Daybreak db-s114 external line: repeated labels at the null, 6/15 after correction
  - s128-p72 external line: NO_LINK p 0.72 at power 0.958 (c-590)
  - controls: s115-A0 and s54
- **Source:** VKB `findings` / `finding_lines`, from `workflow/FINDINGS-GRAPH.yaml:418`.
- **Cost:** 1 open, 1 step.
- **Note:** the db-s114 line cites a results file outside this repo (`lab/codex_lab/...`).

### Q3. Naibbe-type cipher tested?
- **Answer:** Yes, several times.
  - H-04, the per-word Naibbe table cipher, is "excluded at default settings".
  - s64 (c-405): Greshko's Naibbe, rebuilt from his tables, has an orderless prefix stream, and Voynich sits 4.5-4.7 z from it.
  - s71 (c-416): line-sticky Naibbe reproduces the s69 call pattern.
  - s81 (c-428): sticky Naibbe predicts 0/15 held-out quires (F-34).
  - Earlier: c4/f3 (c-105, c-177) and the s85 segmenter check (c-523).
  - Verdict: Naibbe as built is excluded; only the line-held table idea survives in narrowed form (H-14).
- **Source:** `workflow/FINDINGS-GRAPH.yaml:23,500-507,684-704`; CLAIMS c-405, c-416, c-428.
- **Cost:** 1 open, 1 step.
- **Stale flag:** the F-34 s85 seg line carries a POST-HOC note (D-075) and has stopped counting.

### Q4. H-14 status and evidence
- **Answer:** "narrowed (D-067)". A fixed line-held table is contested by roach r6 and s98, a drifting table failed 0/15 (r9, L-217), and what remains is a multi-scale state.
  - For: F-14 (moderate, c-416); F-34 (moderate, the only mechanism whose memory holds out of sample); F-30 (weak).
  - Against: F-34 (strong, 0/15), F-39, F-45, F-46 (lag-2 overshoot about 3x), F-47, F-48 (drifting table also fails), F-30 (weak).
  - D-067 records the reframe.
- **Source:** `workflow/FINDINGS-GRAPH.yaml:32` (reused from Q3) plus the edges at 323, 627-628, 704-705, 807, 971, 997, 1021, 1046; DECISIONS D-067.
- **Cost:** 3 opens, 3 steps.
- **Gap:** VKB `finding_links` returns 0 rows for target H-14. The finding-to-hypothesis edges exist only in the YAML, so the derived view is incomplete for hypotheses.

### Q5. Parisel result
- **Answer:**
  - The paper: `data/external/papers/parisel_2026_arxiv_2604.19762.txt` (and .pdf). c-222 records "neither class reproduces all four signatures simultaneously".
  - The project's own test: s68 (`results_s68.txt`, c-408, L-161). Parisel's per-folio cho/che switch is not two-state within any Davis hand; the switch is the scribe (hand 1 about 0.67, hands 2/3 about 0.10-0.17). This is filed under F-16 (Currier A/B is a scribe split).
- **Source:** CLAIMS c-222, c-408; LEARNINGS L-161; `FINDINGS-GRAPH.yaml:348-362`.
- **Cost:** 2 opens, 2 steps.
- **Conflict:** the bank says "Parisel 2025", but the repo file is a 2026 arXiv paper (2604.19762). The VKB `external_items` query failed on a wrong column name, which is not an open.

### Q6. Daybreak output since 2026-10-18 not filed here
- **Answer (partial):** VKB `external_items` lists 47+ Daybreak items. Their intake classes are admissible 14, data-only 18, not-admissible 15, scope 21 and unaudited 9, and every one has an empty `filed_as`. The newest results are:
  - db-s124: launched-only, no results file
  - db-s125: NO_DETECTED_MARGIN_SIGN_LINE_RELATION, flagged ctime before stub
  - db-s126: descriptive only
  - db-s127: CALL_CONTEXT_EQUIVALENT
  - db-s128, db-s129, db-s130: bounded negatives, with drafts in `data/external/intake/claim_drafts.md`
  - db-s123: HOLD at the data gate

  Most of these live in `lab/codex_lab/experiments/` or `<team-comms>`.
- **Source:** VKB `external_items` (from `data/external/intake/*.tsv`).
- **Cost:** 3 opens, 4 steps.
- **Why partial:**
  - VKB `team_files.owner` is empty for all 3939 rows, so a by-owner, by-date query returns nothing.
  - `external_items` has no date column and `filed_as` is blank everywhere, so "since 2026-10-18" and "not yet filed" cannot be computed. The second part can only be inferred from the intake class.

### Q7. X-01
- **Answer:** **at-risk**. Latest evidence is vx01 A1 (c-592, Eve / Voynich Analyst): on planted books, no segmenter (Slot, Zattera, Seg_Affix2, Canonical) is adequate (Slot 0/15 in all 9 cells). So the Zattera/Seg_Affix2 lines no longer discharge X-01 (2026-10-19). It is still discharged only by the whole-word lines and roach r5. The VKB `assumptions` table agrees.
- **Source:** `workflow/FINDINGS-GRAPH.yaml:42`; CLAIMS c-592.
- **Cost:** 2 opens, 2 steps.

### Q8. roach's blind replication of s114
- **Answer:** roach r15/r15b used its own code, frozen 2026-10-18 20:44. Test A: ZL p 0.0009 HIT, IT p 0.0006 HIT, RF p 0.0545 MISS, so **CALL NO DRIFT**. Test B: p 0.45/0.35 at an MDE of about 1.0 SD. Filed as c-591 and pending row P-56 (state filed). The result makes F-50 contested.
- **Source:** CLAIMS c-591; `FINDINGS-GRAPH.yaml:1361` (P-56); `runs/roach-r15/results_r15b.txt`.
- **Cost:** 1 open, 1 step.
- **Conflicts:** P-56 names the run "r15" while c-591 says "r15b". "s114" is ambiguous with Daybreak db-s114 (the label test under F-20), though the alias map resolves it.

### Q9. Pending runs and owners
- **Answer:**
  - The VKB `pending` table has exactly one live row: **P-65 r17, roach, briefed**, a blind replication of s120 (conjugate leaves more alike).
  - PLAN.md `Current stage:` adds a roach replication queue r17-r27 (D-075: F-36 first via s73/s88, then s85, s86, s36, s35, s37, s74, s75). Only r17 has a pending row.
  - Phase 8.5 (this re-score) is the lead's executing stage.
- **Source:** VKB `pending` (from the FINDINGS-GRAPH P-rows); `workflow/PLAN.md:4`; DECISIONS D-075.
- **Cost:** 3 opens, 3 steps.
- **Stale:** `TEAM-HANDOFF.md:392` still says s111 is "running (do not touch)", but P-51 s111 is `filed`. `TEAM-HANDOFF.md:233` lists s94/s96 as running, though line 232 marks that as superseded.

### Q10. Next authorized action and governing decision
- **Answer:** **D-072** (2026-10-19 00:48; D-073 is merged into it) governs. Its active order is:
  1. Egerton crop/caption gates, then prospective graph transfer.
  2. Fontana known-answer recovery.
  3. Only after a bridge survives, one image-only role-to-text prediction.

  O-070 (updated 10:18) says both bridges failed their first stage: Egerton Ventura is BELOW_THRESHOLDS (c-612) and Fontana glyph recognition failed. The only authorized compute is therefore validation: **D-075** sends roach to blindly replicate 9 post-hoc runs (F-36 first). PLAN.md's stage line agrees.
- **Source:** DECISIONS D-072, D-073, D-075; OPEN O-070 (seen in Q19); PLAN.md:4 (seen in Q9).
- **Cost:** 2 opens, 2 steps, plus reuse.
- **Conflict:** AGENTS.md "Start here" says D-066 is "the single standing next-question entry". But D-066 is 41 KB, its last amendment (ee) is s128, and the pivot D-072/D-075 now decides the next action. A newcomer following AGENTS.md reads the wrong row first.

### Q11. Where a new learning goes and how its id is allocated
- **Answer:** in `.inventory/registers/LEARNINGS.md` (canonical home, per the AGENTS.md map). Per the AGENTS.md Phase 8.1 id rule, only the lead session writes L-rows. Other sessions send rows through <team-comms> (`<team-comms>`), and the lead files them, which avoids collisions. The current maximum is L-364.
- **Source:** AGENTS.md (setup reuse); LEARNINGS.md header and tail.
- **Cost:** 1 open, 1 step.
- **Conflict:** the LEARNINGS.md header still gives the older band rule ("Lead band L-153..L-299, Argon band L-300+ (D-054)"). Recent lead rows (L-363, L-364) are in the "Argon band", so the header is stale against the Phase 8.1 rule.

### Q12. Published plant identifications for f2r
- **Answer:** all of them are Centaurea / cyanus:
  - Ethel Voynich notebook: "Cyanus?"
  - Petersen: "cyanus silvestris (O'Neill), Centauria (Holm)", via Zandbergen
  - Bax 2014: genus Centaurea
  - Velinska 2013, as reported by Bax: Centaurea [unverified]
  - Dana Scott, via J. Bunn: Centaurea cyanus [unverified]
  - Sherwood & Sherwood 2008: Centaurea diffusa, with C. biebersteinii as alternative
  - Petersen plant number 2
- **Source:** VKB `page_facts` (from `data/external/page-facts/<pull>/facts.tsv`).
- **Cost:** 1 open, 1 step.

### Q13. F-51 (sheet as production batch)
- **Answer:** F-51 is **CORROBORATED, status at-risk**. The two leaves of a bifolio are more alike than neighbours. Evidence:
  - s120 on three transliterations with cell-matched strata (c-560), plus a layout-free sensitivity check
  - the Table 5 conjoint audit (dropping f115r: T -0.15, p 0.0001 x3)
  - planted-sheet fixture 20/20, no-sheet 0/20
  - external direction-only agreement from Layfield & Davis 2026 (marked unverified)

  It is **not independently replicated** yet: roach r17 (P-65) is briefed but has not delivered.
- **Source:** VKB `findings`/`finding_lines` for F-51 (from FINDINGS-GRAPH); P-65 (reused from Q9).
- **Cost:** 1 open, 1 step.

### Q14. VKB version frozen by s125, and how to verify its stub today
- **Answer:** the stub `s125_label_topic_gate.prereg.sha256`, at the repo root and not in `runs/s125/`, was frozen 2026-10-19 00:29:16. It pins `data/vkb/vkb.sqlite` at sha256 `4ed3497cfd73f0acf5b4bd2c222ebc40f91de961e316996fabed79895a2aaff5`.
  - The live vkb.sqlite has since been rebuilt. Per **D-074**, the vkb line verifies against `data/vkb/vkb.orig-4ed349.sqlite`, and I hashed it: it matches 4ed3497c...aff5.
  - `tools/vkb/evidence.py` accepts the `.orig-<hash6>` copy.
  - Verify the other lines with `grep -v "^#" STUB | tr -d '\r' | sha256sum -c -`.
- **Source:** DECISIONS D-074 (reused from Q10); the stub file; sha256sum of the pinned copy.
- **Cost:** 2 opens, 5 steps.
- **Friction:** stubs are not in `runs/<id>/`. I guessed a stub name once (no such file), and an `ls` of runs/s125 vs the root was confusing. A naive `sha256sum -c` on the stub will FAIL the vkb line today unless the reader knows D-074.

### Q15. Power of the s128-p72 plant-name test
- **Answer:**
  - A planted-link power gate: power 0.958 at k=5 planted links, against the 0.8 bar.
  - A real positive control: Egerton 747 headings to their own chapters, NAME_LINK 200/200 (MRR 0.636 vs Voynich null q99 0.128).
  - Shuffled Voynich 0/10 and fixture strong 10/10 / absent 10/10.
  - Result: NO_LINK, p 0.72.
- **Source:** CLAIMS c-590 (`results_s128_20261019T090659.txt`); F-20 line (reused from Q2).
- **Cost:** 1 open, 1 step.
- **Conflict:** the run id s128 collides with Grok Bot's s128 herbal-profile calibration (c-614 notes it).

### Q16. Multispectral (MSI) images held
- **Answer:**
  - f1r: 38 bands, 3.81 GB, in `data/msi/` (Lazarus Project / RIT, local use only).
  - f116v (47 files) and f17r (38 files): in `<local-path>` with `MANIFEST.sha256` (external_items: 86 files, 8.0 GB, unaudited).
- **Source:** OPEN O-069; VKB `external_items`; directory listings.
- **Cost:** 2 opens, 3 steps.
- **Conflict:** O-069 says "f17r and f116v blocked by free space on C:", but `external_items` and the disk show both stacks on D:. O-069 is stale.

### Q17. Decision governing whether a new structural run may start
- **Answer:** **D-072** governs (D-073 is merged into it): new structural compute is stopped, and any new run in the parked classes needs Jon's explicit approval. D-075 allows validation replications. D-071 adds that hashed scripts are frozen, so a change needs a new run id.
- **Source:** DECISIONS D-072/D-073/D-075 (reused from Q10).
- **Cost:** 0 opens, 0 steps.
- **Conflict:** the same as Q10: AGENTS.md points to D-066.

### Q18. Davis scribe for quire 13
- **Answer:** **Hand 2**, for all 20 pages of quire M (13th quire: f75r-f84v, the biological/balneological quire).
- **Source:** VKB `folios.hand_davis`.
- **Cost:** 1 open, 1 step.
- **Friction:** VKB stores quires as letters (M, I), so a query for "13" alone returns nothing. I guessed the letter mapping, and it was not documented in what I read.

### Q19. Egerton Ventura held-out identity rule vs threshold
- **Answer:** rule v1 (Grok Bot), held-out n=35 captions: first_word **0.686 vs a frozen 0.90**, normalised **0.743 vs a frozen 0.85**, so CALL **BELOW_THRESHOLDS**. The development set was also below. The D-072 Egerton gate is not passed.
- **Source:** CLAIMS c-612; LEARNINGS L-363 (which reconciles two reports that only looked contradictory); OPEN O-070.
- **Cost:** 1 open, 1 step.

### Q20. Pharma-herbal pairs eye-checked "same", and their crops
- **Answer:** 7 pairs:

  | Pair | Pharma folio | Herbal folio |
  |---|---|---|
  | P02 | f102r1 | f37v |
  | P03 | f102r2 | f47v |
  | P04 | f102r2 | f32v |
  | P05 | f102r2 | f18v |
  | P06 | f102r2 | f23r |
  | P10 | f89v2 | f48r |
  | P26 | f99r | f96v |

  Crops are in `data/external/page-facts/eyecheck/crops/`, with per-pair paths in the `crop_paths` column.
- **Source:** `data/external/page-facts/eyecheck/pairs.tsv`. I found the path in the D-066 (ee) text reused from Q9.
- **Cost:** 1 open, 1 step.

## Summary

- **Total opens:** 33 across 20 questions (setup adds 2 tool opens plus AGENTS.md).
- **Total steps:** 39 (setup adds 4).
- **Median opens per question:** 1.
- **Results:** 18 complete, 2 partial (Q1, Q6), 0 not found.

## Hardest three

1. **Q6 (Daybreak unfiled output).** The derived views cannot answer it. VKB `team_files.owner` is blank for all 3939 rows, `external_items` has no date and `filed_as` is empty for every row, and the results live outside the repo (codex_lab, <team-comms>). "Since 2026-10-18" and "not yet filed" had to be inferred.
2. **Q1 (f68r1 dossier).** The dossier answers structure and published facts at once, but no index links findings to folios. Finding the related findings meant schema discovery (two wrong-column errors overall) and title text searches, which still gave only generic label findings.
3. **Q14 (s125 VKB pin).** The stub sits at the repo root, not in `runs/s125/`. The live DB no longer matches the stub, and verifying it requires knowing D-074 and the `vkb.orig-<hash6>` convention. It took 5 steps, the most of any question.

Q9 and Q10 came close. They needed three homes (VKB `pending`, PLAN.md stage line, DECISIONS D-072/D-075), and two docs were stale: TEAM-HANDOFF:392 still says s111 is running, and AGENTS.md points to D-066 rather than D-072/D-075.
