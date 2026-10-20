# Phase 8 investigation: team knowledge outside the repo (angle: team-external)

Stamp: 2026-10-19 09:32 PDT (from `date`; work began 09:25). Read-only. This file is the only write.
Method: directory listings, file heads and summary sections only, grep of the repo registers, and VKB queries. No bulk reads.
"Registers" means `.inventory/registers/{CLAIMS,LEARNINGS,DECISIONS,OPEN}.md`. "Graph" means `workflow/FINDINGS-GRAPH.yaml`. "ext row" means a VKB `external_items` row.

## 1. What I found

### 1.0 VKB external_items as it stands
- `SELECT intake_class, COUNT(*) FROM external_items GROUP BY 1`: 87 rows (admissible 8, data-only 32, not-admissible 30, scope 17).
- Every row comes from the 2026-10-18 audits (`.inventory/runs/2026-10-18/audit-external-A/B/C`, `audit-intake`, `audit-sprawl_external`). The newest Daybreak run with a row is db-S123.
- **No ext row exists for** Grok Bot (s128 calibration, lib01, Egerton Ventura rule, blind-read packets), the Independent Verifier (IV-*), Eve / Voynich Analyst (vx01, `<home>/voynich-backups`), roach-12B, Muse, roach r13 to r15, Fontana GPU, the Egerton crop/caption/QC work, `<local-path>`, or `data/external/library`. Check: a `LIKE` query on msi, backups, library, grok, fontana_v1, egerton and consumption returned 0 rows.
- The VKB `runs` table holds db-s88 to db-s123 (35 rows). **db-S124 to db-S141 (18 runs) are absent.**

### 1.1 Locations: which exist (searched with `find /c /d -maxdepth 3` and `find <home> -maxdepth 4` for `*voynich*` and `*yonich*`)

| Location | Owner | What | Size and latest file | ext row |
|---|---|---|---|---|
| `<team-comms>` | <team-comms> comms (all agents) | 3,950 entries in total; about 680 Voynich-related by name. Prefix counts: VOYNICH-DAYBREAK 73, Grok Bot 30, Sylvie/steward 63, lead b379 35, roach-voynich91 37, IV 20 (8 `IV-*.md` plus 12 requests), VOYNICH-ARGON 11, ROACH-12B 7. Also 21 subfolders (roach r5 to r13 packages, `db_s135_result_20261018`, `daybreak_evidence_state_20261018`, and others) | latest 2026-10-19 09:21 (Daybreak known-answer checkpoint) | one umbrella row, data-only, "partly" filed |
| `lab/codex_lab` | Daybreak (Codex) | 337 files in `experiments/` (60 `results_*`, db-s100 to db-s141), `reviews/`, `acquisition/`, `preregistrations/`, MEANING-RECOVERY-STRATEGY and EXECUTION-PLAN (dated 2026-10-19), OPERATIONAL-USE-REGISTER.tsv | 5,695 files; latest 2026-10-19 00:36 | 36 rows, none newer than db-S123 |
| `lab` (root and siblings) | Daybreak / "Codex root session" | `fontana_v1/` (659 files, 02:29), `egerton_caption_v1/` (682 files, 01:42), `egerton_qc_v1/` (95 files), `kraken_deps`, `kraken_site`. **`workflow/PLAN.md` was modified at 09:24 today, "Current stage: cleanup framing → awaiting gate", with Jon's same hypothesis.** It also holds the root files VOYNICH_VISUAL_TO_SEMANTIC_TRIANGULATION and KNOWN_ANSWER_VISUAL_SEMANTIC_CONTROL_CHECKPOINT (09:11 to 09:21) | latest 09:24 (live) | early-battery rows only |
| `<local-path>` (= `<local-path>`) | roach voynich-91 / 91b | r1r2-raw, r3 to r13, **r15** (r15b), `corpora/` (mirrors of ZL, IT, RF, CREMMA and DANTE), ten-theories; also non-Voynich September messages | r15 clock end 2026-10-18 20:44 PDT | 2 rows (r1 to r12) |
| `<home>/voynich-backups` | Eve / Voynich Analyst (Grok Bot) | 3,895 files, 493 MB: PLAN-X01 v0 to v5.2, PLAN-X01-B-FALLBACK v0 to v6, VX01-CALL-MAP, ADVANTAGES v1/v2, `FINDINGS-MAP_X01-FIX-2026-10-19.md/.diff`, vx01_bf code c1 to c3, `vx01_work/`, a robocopy snapshot `2026-10-18_2214` | latest 2026-10-19 02:38 | none |
| `<local-path>` | lead (Phase 7.4 MSI) | 86 files, 8.0 GB (f116v, f17r) | 2026-10-18 19:49 | none (named in DECISIONS/OPEN) |
| `<local-path>` | mirror plus `<private-project>` | 2,505 files, 128 MB | 2026-10-19 01:07 | mirror row only |
| `<home>/AppData/Local/Temp/voynich-mine` | unknown (early lit mining) | 35 files, 33 MB: D'Imperio, Davis and carbon-dating texts | 2026-10-18 01:41 | none |
| `<local-path> voynich-analyst-sv3-render-20261019}` | <private-project> / Voynich Analyst | CE briefs; a re-render of FINDINGS-MAP v4 (07:37 today) | 07:37 | none (CE is out of scope; see the global CLAUDE.md) |
| `~/.grok/memory-v2/workspaces/{<session>, <session>}` and `~/.grok/sessions/*` | Grok Bot sessions | agent memory sqlite | 09:23 (live) | none (guidance class) |
| Grok Bot box `/workspace/team/voynich/` and `/workspace/voynich-library/` | Grok Bot | blind-read packets v1 and v2 originals, library harvest | **not reachable from Skynet**; cited in <team-comms> CHANGELOG files | none |
| repo `incoming/` | Argon (<session>) | `ten-theories/` only (2026-10-17) | 1 entry | yes (L-132) |
| repo `codex_lab/reviews/` | Daybreak | 1 file (`s60_s63_evidence_audit_2026-10-18.md`) | 10-18 02:40 | not checked |
| repo `workflow/comms/` | lead b379 | 28 staged outbound messages (latest TO-DAYBREAK-GROKBOT-EGERTON-READER-OFFER, 16:09Z) | live | n/a (lead's own) |
| repo `data/external/daybreak-intake-20261019/` | lead intake of Daybreak | 7 files: Fontana acquisition, TrOCR preflight, db-S141 intake audit, wave-5 review | 10-19 | basis of c-584, c-585, c-586 |
| repo `data/external/library/` (lib01) | Grok Bot | catalogue_v2 with 2,979 rows, 506 OA PDFs, 560 texts, primary_sources, GAPS.md | 10-19 02:55 | none; **0 mentions in INVENTORY.md** |
| Not found | | `runs/s127` (only `data/s127_picture/` exists); `IV-RESCORE-X01-A1.md` (cited by sha e7be4afc in two vx01 files; not under Desktop, voynich-backups, <team-comms> or <local-path>) | | |

### 1.2 Bodies of work

For each body: owner; what it is; latest date; repo claim, learning or finding; ext row and intake class; results the lead never filed.

1. **Daybreak db-S124 to db-S141** (codex_lab). The audit was done but the results are mostly unfiled.
   - db-S124 to db-S138 were audited in `.inventory/runs/2026-10-18/audit-external-D.md` (20:31). That audit grades db-S128, S129, S130, S131, S132 and S133 as "admissible (bounded negative)", db-S134 as admissible calibration (POSITIVE_CONTROL_PASS), db-S135 as UNDERPOWERED, and db-S137 and db-S138 as scope.
   - Registers and graph mention db-s124, s125, s126, s129, s130, s131, s132, s133, s134, s135, s139 and s140 **zero times** (grep, case-insensitive). db-S127 and db-S128 appear once or twice, in learnings and decisions only. Only db-S141 is filed (c-586, O-070).
   - db-S139 (`GLOBAL_WITNESS_ASSIGNMENT_NOT_CALIBRATED`) and db-S140 (`FULL_GALLERY_WITNESS_RECOVERY_NOT_CALIBRATED`) have results dated 2026-10-19 and no audit and no claim.
   - None of these runs has an ext row or a VKB runs row.
2. **db-S141 (c-586).** Filed narrowly: Penn/Sloane calibration only. The limiting correction `reviews/db_s141_ljs419_family_contamination_correction_2026-10-19.md` is reflected in O-070. **Integrated.** It still has no ext row.
3. **Egerton 747 gates** (Daybreak, Grok Bot, IV; 2026-10-19 00:55 to 02:00).
   - The material: manual crop checkpoint (11 tranches, 217 pages, 390 boxes), Codex-Daybreak crop QC response (`egerton_qc_v1`), Kraken caption OCR acquisition (`egerton_caption_v1`), and roach-12B "R14 AND EGERTON V4 INDEPENDENT AUDIT PASS" (04:36Z).
   - Grok Bot's **Ventura identity rule v1 held-out result:** `n=35 first_word=0.686 normalised=0.743 -> CALL: BELOW_THRESHOLDS` (frozen 90%/85%).
   - Crop-pair f28v/f34v, labelled "NOT BLIND".
   - Caption-gate deviation note v2 with IV sign decisions, and blind-read-1 packets v1 to v3 (v3 awaiting IV recheck).
   - In the repo: CLAIMS has 8 Egerton mentions, graph 1, OPEN 2. `data/external/ventura_egerton747` holds the TEI. **The Ventura held-out BELOW_THRESHOLDS call and the crop QC are not filed.** No ext row. Status: live; the lead offered readers at 16:09Z.
4. **Fontana** (Daybreak). The acquisition is filed (c-584, c-585). **The GPU campaign result** (`yonichmanuscript/fontana_v1/FONTANA_GPU_CAMPAIGN_RESULT_2026-10-19.md`, self-audited, not independently audited) **is not filed.** It contains:
   - alignment PASS with 16/16 anchors;
   - Schulte HTR FAIL at 0.4292;
   - V1 glyph cut FAIL;
   - V2 synthetic CTC PASS at 0.9961;
   - real transfer FAIL (33/40 blank);
   - the key solve correctly not run.

   Grep finds no `0.4292` and no "Schulte" result in the registers. No ext row.
5. **R14 Barcelona BC Ms 3075** (Daybreak; roach-12B audit). `reviews/r14_bc3075_real_result_2026-10-19.md` reports `primary_pass = true`, a positive historical-mechanism control, with byte-identical repeat. Roach-12B's audit is "PASS" per <team-comms>. No "BC Ms 3075" or "Barcelona" claim or graph line was found. It is unfiled (unverified only in that it might sit under another name).
6. **Roach-12B independent audits** (auditor `<session>`). Seven <team-comms> messages (02:21Z to 08:13Z on 2026-10-19) record PASS for db-S137, db-S138, D069-G0, D069-G1a, wave3/wave4, wave5 plus db-S139, and R14 plus Egerton v4. There is also one NEEDS-CORRECTION, on CE consumption. **"12B" appears 0 times** in registers, graph, PLAN and TEAM-HANDOFF. Daybreak accepted them (`reviews/argon_roach_return_intake_2026-10-19.md`). The lead has not.
7. **Daybreak label-audit packages:** LJS 419 primary-label intake (lunaria → `lxnbrkb`, a vowel-shift cipher label on a herbal), BnF lat. 17848, Canon Misc. 408 / Beasley-98 concordance. These were sent out for independent audit. LJS 419 as a family is in the registers; the `lxnbrkb` reading appears 0 times. No ext row.
8. **Grok Bot s128 herbal-profile calibration** (`runs/s128/`, 01:25 to 02:53, claimed in TEAM-HANDOFF:399/403). Two known-answer results exist with no claim or learning:
   - **Egerton:** page-unique-in-line-1 S=0.254 vs null q99 0.101 (p 0.005), power 1.0 at 110 pages. **Macer:** S=0.221, but power 0.04 to 0.32. **Gart:** n=9, not significant.
   - **f0n2 calibration:** name N2 15/15 and rarity 0/15 or 1/15.

   The registers cite only s128-**p72** (c-590, the lead's run, which collided on the id). The v5 name-slot prereg is frozen, held under D-072, and awaiting blind re-grade. No ext row.
9. **Grok Bot lib01 library** (`data/external/library/`; it is inside the repo). Not in INVENTORY.md (0 hits). `unchecked_claims.tsv` and `catalogue_to_findings.tsv` are candidate inputs to the claim register and are not wired in. No ext row.
10. **Eve / Voynich Analyst vx01** (repo root: 40 vx01_* files, 4 `.prereg.sha256` stubs; plans in `voynich-backups`).
    - `results_vx01_a1.txt` (23:13): **no segmenter, Slot included, is ADEQUATE ON PLANTED BOOKS.** Every published segmenter scores 0/15 in all 9 cells. vx01_seg_mdl passes G1 and NULL but fails G2.
    - Lead decision note (Eve): A2, A3 and A4 are not run.
    - The graph keeps X-01 "at-risk", with basis s76 only. **vx01_a1 is cited 0 times** in registers and graph.
    - The proposed map fix `voynich-backups\FINDINGS-MAP_X01-FIX-2026-10-19.md` (marked "UNVERIFIED hand fix") is not applied, and should not be: the map is generated.
    - The IV acceptance it cites (`IV-RESCORE-X01-A1.md`) was not found.
    - The B-fallback plan v6 and bf code c3 are unfrozen. No ext row.
11. **Voynich Expert s127** (`data/s127_picture/`). A draft prereg (not frozen) and a 5-image pilot (qwen vs Grok rater: raw 0.58, NA-folded 0.88, rater B not blind). Claimed in TEAM-HANDOFF, parked by D-073. **Integrated as a draft**; nothing to file beyond a pipeline-check learning, if any.
12. **Roach r15b** (bridge `r15/`). `CALL Test A: NO DRIFT` (ZL p .0009, IT p .0006, RF p .0545). The lead's R15 request went out 02:54Z, roach delivered at 03:47Z (20:47 PDT), and PLAN 21:04 records "r14/r15 withdrawn". The graph's P-56 is `rejected` with "withdrawn". **The delivered result is not mirrored in `runs/`**: `runs/roach-r*` stops at r13.
13. **Muse ("muse wonder")**: m0 to m7, q1, Q_RESULTS.md and TOP10-LEADS.md, at the repo root, 2026-10-17. Claims cite each of results_m0 to m7 and q1 between 1 and 13 times, and learnings cite them too. The graph cites only m5. No Muse files are in <team-comms> (0 name hits). **Integrated as claims**, mostly not graph-linked. No ext row; criterion 4 in PLAN lists Muse.
14. **Argon <session> deliveries in <team-comms>** (R14 diplomatic transcription return, DBS136-LJS419-R14QC-AND-PILLARS bundle, three-channel package). Audited in audit-external-D/E and quarantined (D-065, L-329). **Integrated as rejected.** The ext rows cover the `.gemini` brain directories only.
15. **Sylvie / steward** (63 <team-comms> files; the latest asks Grok for a "manuscript-native checkpoint" at 14:26Z). These are guidance, recorded via D-066. Not a results body.

## 2. Verified vs inferred
- **Verified** (command named in §1): the external_items counts and coverage gaps (VKB queries); the VKB runs coverage stopping at db-s123; zero register or graph mentions for db-s124 to s126, db-s129 to s135, db-s139, db-s140, "12B", vx01_a1 and lxnbrkb (grep); the printed calls quoted (head or grep of each results file); the file counts and latest mtimes (`find`/`ls`); the IV-RESCORE file missing from four roots (`find`); the yonichmanuscript PLAN.md "cleanup framing" stage line (`sed -n 1,30p`).
- **Inferred, unverified:**
  - Some unfiled items may be filed under different words. I grepped by id, number and proper name only.
  - The roach-12B PASS verdicts are taken from <team-comms> filenames and Daybreak's intake note. I did not open the audit bodies.
  - The ownership of `voynich-mine` and of the yonichmanuscript root session is guessed from filenames and headers.
  - The r15b withdrawal timing comes from the timestamp order only.
  - Whether the Grok box holds more unfiled results is unknown, because it is not reachable.

## 3. Surprises
1. **A second cleanup initiative is live in `yonichmanuscript/workflow/PLAN.md`** (09:24 today). It has the same Jon hypothesis, its own success criteria, and it calls this repo "the live upstream project". Two consolidations will collide unless one defers.
2. Audit-external-D graded about 10 Daybreak runs as admissible bounded negatives 13 hours ago, and none became a claim. The intake pipeline stops at "audit written".
3. Roach-12B is a whole independent-replication channel (7 PASS reports) that the repo has never named.
4. vx01 A1 is a strong, IV-reviewed (per its author) negative on every segmenter, yet X-01's graph basis still cites only s76. Its IV acceptance file could not be found on Skynet.
5. Grok's library sits inside the repo but is invisible to INVENTORY.md, and the inventory scan predates it.

## 4. Assumption candidates (each with how to verify)
- A1: "<team-comms> is message traffic only; no unique results live only there." **False today:** VOYNICH-R11/R12/S107/DB-S123 `.py/.txt/.json` and the Egerton Ventura result live only there. Verify: `ls /d/<team-comms> | grep -E '\.(txt|json|py|csv|zip)$'` and diff against the repo.
- A2: "external_items covers every external body." **False:** see the §1.0 query. Verify by re-running that query after intake.
- A3: "The yonichmanuscript tree is an archive." **False:** it is live (09:24). Verify with `find ... -newermt` before any move.
- A4: "Daybreak results are filed once audited." **False** for db-S124 to S140. Verify: for each `results_db_s*` in codex_lab, grep the id in CLAIMS and the graph.
- A5: "Roach deliveries are mirrored to `runs/roach-rNN`." **False** for r15. Verify: `ls <local-path>` vs `ls runs | grep roach`.
- A6: "Grok's box holds nothing unique." Unverifiable from here. Verify: ask Grok via <team-comms> for a manifest with hashes (Sylvie already asked at 14:26Z).

## 5. Recommendations
1. **Coordinate with the yonichmanuscript cleanup before any move** (low effort, high risk if skipped). Send one <team-comms> message to Daybreak / the Codex root session saying the repo's Phase 8 is the consolidation, and ask that theirs become a read-only inventory feeding it, with no moves in the repo.
2. **Bulk-load ext rows from this census** (medium effort, low risk). Add one row per body in §1.2 with owner, latest date, intake class and filed_as, via the VKB build source rather than hand SQL. Suggested classes:
   - admissible: the audit-D "bounded negative" runs, db-S134, the R14 BC3075 result, the roach-12B passes, and vx01_a1 (pending IV file);
   - data-only: Fontana acquisition and GPU campaign, Egerton crops and captions, lib01, voynich-msi, the r15b corpora;
   - scope: s128 calibration, db-S137, db-S138, db-S139, db-S140;
   - not-admissible: status and start files, Argon bundles, the ADVANTAGES docs.
3. **File the audited-but-unfiled results as claims** (medium effort, low risk; highest value). In order:
   1. db-S128 to S133 negatives, S134 calibration, S135 underpowered (rules already written in audit-external-D);
   2. vx01_a1, which must also be linked to X-01's basis in the graph, then re-render (do not apply Eve's hand-edited map);
   3. the Fontana GPU campaign (recognition is the blocker);
   4. the Egerton Ventura BELOW_THRESHOLDS call;
   5. the R14 BC3075 primary_pass;
   6. Grok s128 Egerton and Macer calibration (S and power), which is a direct calibration input for any name-slot test under D-073.
4. **Import roach-12B audits as replication evidence** (low effort, medium risk). Open the 7 audit bodies and record each as a `by:` line on the matching claim. Do not move the scoreboard until the lead audit is done (TRIANGULATION.md).
5. **Mirror r15b into `runs/roach-r15/`** as copy-in with its MANIFEST, and file it as "delivered after withdrawal; descriptive" (low effort, low risk).
6. **Close the vx01 IV gap** (low effort). Ask Eve or Grok via <team-comms> for `IV-RESCORE-X01-A1.md`, sha e7be4afc. Until it arrives, file vx01_a1 as UNVERIFIED (its own header says so).
7. **Add `data/external/library/` and `<home>/voynich-backups` to the curate scan scope**, then regenerate INVENTORY (low effort, low risk). The vx01_* root files are stub-named (D-071) and must not move.
8. **One intake rule** for AGENTS.md (low effort): a result is "integrated" only when it has a claim, an ext row and a VKB runs row. The intake audit step closes by writing those, not by writing an audit file.
9. **Out of scope, record only:** the `.grok` memory, <private-project>, `<local-path>` (<private-project>; owned by <private-project>) and `Temp\voynich-mine`. Classify these as scope or not-admissible, and move nothing.
