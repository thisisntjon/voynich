# External Voynich sprawl audit (read-only)

Stamp: 2026-10-18 15:56 PDT (from `date`). Nothing outside the scratchpad was created, moved or edited.
Canonical repo state used: workflow/FINDINGS-MAP.md (generated 15:48), PLAN.md phase log through 15:48 (s111 frozen; D-068 F-23/F-30 at-risk; s108 NOT ASSESSABLE; s105 HOLD; s103 INCONCLUSIVE; F-48 drifting table rejected).
Reflection check method: grep of .inventory/registers/{CLAIMS,LEARNINGS,DECISIONS,OPEN}.md, workflow/FINDINGS-GRAPH.yaml, TEAM-HANDOFF.md, PLAN.md, runs/, data/external for run ids, filenames and key strings. A "no" means no hit for those strings; a differently-worded mention could exist (unverified beyond the strings listed).

## 1. Location summary

| Location | Holds | Reflected in repo | Contradicts repo |
|---|---|---|---|
| <team-comms> (809 Voynich/Daybreak/Argon-named files, excl. .partial) | <team-comms> comms; Daybreak status/top-10 syntheses (31 VOYNICH-TOP10 versions); roach r5-r12 packages + zips; db-S123 run; r12 ablations; S107 Llull follow-ups; R14 (Pal. lat. 984 / BC Ms 3075) work orders; S109 pre-freeze HOLD; skynet/codex audits of s82-s88 | partly (r5-r11, s101, s100/s106 audits, db-s114 ghost issue as O-059) | yes, in places (see 3) |
| lab (root) | Oct-17 early battery a1-g1, own PLAN/TEAM-HANDOFF/FINDINGS | yes: all 39 results_*.txt byte-identical in repo | no (stale, superseded) |
| ...\yonichmanuscript\codex_lab | Daybreak lab: 221 experiment files (db-s88..db-s123), 117 reviews, acquisition corpora, incoming roach r5,r9-r12 copies, 4 status files | partly: db-s88..99, 101, 104-106, 109, 111, 114, 115, 118, 120 cited; rest no | status files: yes (stronger than repo on S101) |
| <home>/.gemini/antigravity/brain/<session>-... (Argon) | VOYNICH_MASTER_FINDINGS_INDEX.md, voynich_deep_web_and_cross_manuscript_triangulation.md, concrete_truths, cryptanalysis_report; scratch labs h19_fontana_lull, o062_herbal, padua_astro_balneo, physical_forensics | partly (s108/s109 designs drew on it; PLAN 14:42 says Fontana mechanism, Bodleian manifest, plant concordance "not adopted") | yes (s105 "100% unblocked") |
| ...\brain\<session>-... (Argon) | multi_agent_deep_investigation_synthesis.md (cross-section label network, 20-quire collation, tabular corpora) | partly (s108 texts, s109 question) | mild |
| ...\brain\<session>-... | voynich_10_theories_investigation.md | yes (incoming/ten-theories, L-132 EXPLORATORY) | no |
| <local-path> | r1r2-raw, r3-r12, ten-theories; no r13 yet | r1-r11 yes (runs/roach-r*); r12 NO | r12 result vs F-04 framing (see 3) |
| <local-path> | only incoming\ten-theories (mirror) | yes | no |
| memory dir (7 files) | goal, roster, comms, CPU, triangulation, order-agnostic | n/a (guidance) | no |
| <local-path>, other *codex* dirs | unrelated projects (no Voynich in <local-path>) | n/a | n/a |
| Desktop/D: depth-4 *voynich*.md (Oct) outside the above | none found | n/a | n/a |

## 2. Unfiled results, data sets and findings (not in canonical repo)

### Roach
- r12 (word-length rhythm, blind): <local-path> (identical copy <team-comms>, zip <team-comms>, codex_lab\incoming\roach_r12_20261018). Repo P-41 still `state: briefed`; no runs/roach-r12. VERDICT "Voynich-specific positive in-line rhythm NOT HOLDS": Voynich ZL 12/15, IT 11/15 blocks positive, XLINE 0/15 (replicates rhythm and line reset), but KALEVALA_VERSE 15/15 (Roget PARA 15/15). Bears on F-04 and on H-01 counter-evidence.
- r13: not delivered (brief sent 22:44Z).
### Daybreak (codex_lab\experiments\results_*)
- db-s100 NO_LARGE_TAIL_PICTURE_LINK_DETECTED
- db-s102 NO_REPLICATED_GEOMETRY_LINK (only a research-note mention)
- db-s103 s93 recurrence overshoot: DIAGONAL_CAUSE
- db-s107 NO_EARLY_HEAD_FRAME_REGISTER_LINK
- db-s108 f57v Latin consonant key: NO_RING_KEY_SIGNAL
- db-s110 label anchor: REPRESENTATION_DEPENDENT_LABEL_SIGNAL
- db-s112 NO_OBJECT_LEVEL_LABEL_VISUAL_LINK
- db-s113 NO_EXTERNAL_CONTAINER_LABEL_FORM_LINK
- db-s116 NO_TWO_PART_ANTIDOTARY_ARCHITECTURE
- db-s117 order-free Antidotarium graph: UNDERPOWERED
- db-s119 medical recipe family retrieval: UNDERPOWERED
- db-s121 NO_IDENTIFIED_RECIPE_SOURCE_OR_FAMILY
- db-s122 NO_TRANSFERABLE_EXTERNAL_LABEL_FORM
- db-s123 Llull held-out continuation: HOLD at data gate (14 rows / 26 tokens < 30/100) — <team-comms>,txt,json,py,sha256}; codex_lab\experiments\db_s123_*
### Daybreak post-result analyses of lead/roach runs (<team-comms> and codex_lab\reviews)
- R12 identity ablations: VOYNICH-R12-EXACT-WORD-ABLATION*, VOYNICH-R12-S0-S1-S2-ABLATION* (removing identical pairs keeps 84-96% of cadence excess)
- R11-R12 quire coupling (cadence vs exact recurrence r=.601, vs boundary contrast r=.707; S1 core contrast -.109): <team-comms>, codex_lab\reviews\r11_r12_quire_coupling_2026-10-18.md
- S107 Llull rhythm/stability and physical-unit correction: VOYNICH-S107-LLULL-RHYTHM*.{py,txt,json}, VOYNICH-S107-LLULL-JOINT-LEAD-2026-10-18.md, s107_lull_cadence_physical_unit_correction_2026-10-18.md
- Lead S109 pre-freeze audit: VOYNICH-LEAD-S109-PREFREEZE-AUDIT-2026-10-18.md (+ .json), <team-comms>: HOLD_BEFORE_FREEZE, six missing requirements (no alias-removal locus table, no hand/section stratification, L and R pooled, page-wide adjacency, ...). Not in repo registers; repo now has runs\s109\fixture_0..2.txt.
- R14 physical combinatory-table controls: Vatican Pal. lat. 984 (p0012/p0013 ruled 4-char rows; p0015 triangle), Barcelona BC Ms 3075 f114r-f119r (1457), UCM BH MSS 106 negative preflight. Reviews: codex_lab\reviews\{pal_lat_984,bc_ms_3075}_table_visual_triage_2026-10-18.md, ucm_bh_mss_106_layout_preflight_2026-10-18.md, lullian_combinatory_reference_sources_2026-10-18.md; data codex_lab\acquisition\bc_ms_3075_r14\ (1.9 MB, receipt + manifest). Zero repo hits for Pal. lat / Barcelona / 3075.
- Roach r13 proposal (continuous reference contrast): <team-comms> (differs from repo P-50 r13 = s101 replication).
### Daybreak data sets (codex_lab\acquisition)
- s114_stolfi_full_label_catalogue.csv, s113_stolfi_label_attributes.csv, s112_object_label_registration.csv (label/object catalogues)
- s115_antidotarium_nicolai_latin_recipes.csv, s119_scribonius_latin_recipes.csv, s119_liber_de_coquina_latin_recipes.csv, s119_corema_*_culinary_recipes.csv, corema_collection\ (9.5 MB), corema_m2_alemannic\, external\ (22 MB). No CoReMa / label-catalogue hits in repo.
### Argon data sets (<home>/.gemini/antigravity/brain/<session>/scratch/)
- o062_herbal\alchemical_herbal_98_concordance.tsv (1-98 plant concordance), canon_misc_408/500 parsed manifests + shared_species.tsv, beasley_2024_thesis.{pdf,txt}, iiif_manifests\, witness_iiif_status.json
- physical_forensics\exp3_e3_leaf_collation_all.tsv, exp3_e3_bifolio_lobo_affinity.tsv (collation/conjoint-leaf), exp1_e5_hesitation_summary.tsv (15,666 ink gaps), exp2_e1_spatial_proximity.tsv (43 Rozanova pages)
- h19_fontana_lull\ (Fontana NAL 635 pegboard simulator; results_h19_fontana_lull.txt: FONTANA_NAL635_LULL_CHAMBERS SHOWS_F40_CORE=True, FULL_C1=True — unregistered, Argon quarantined D-065)
- padua_astro_balneo\ (Alfonso Lapidario 290 degree stones, Astrolabium 1494/1502, De balneis compression, star_deviations_catalog.tsv)
- In <session> synthesis: cross-section label scan (ok-/ot- 30/101 vs 87/755), Q1-Q20 collation + 7 missing-leaf gaps + Davis 5-scribe map, tabular corpora URLs (archive.org OCR for Saladino, Savonarola, Astrolabium editions). Repo: s109 uses the label question; no collation table, no concordance, no Fontana/h19 hits.

## 3. Contradictions / drift vs repo
- S101 strength: <team-comms> VOYNICH-TOP10-EVIDENCE-2026-10-18.md and VOYNICH-EVIDENCE-INDEX say "the associated broad producer exclusions are withdrawn" and "Terminal S101 strengthens the tie"; repo (D-068) holds F-23/F-30 at-risk pending r13 replication. Overstates.
- Argon VOYNICH_MASTER_FINDINGS_INDEX.md §8 and deep_web §2: s105 "Now 100% Unblocked" with the 98-plant concordance; repo: s105 HOLD (O-062), concordance not adopted (PLAN 14:42).
- Argon index row 5 presents a Fontana NAL 635 pegboard model as H-19/G2b; repo: not adopted.
- r12: Daybreak top-10 says "rhythm is not Voynich-specific"; repo F-04 standing with no r12 line (unfiled, not a contradiction of repo text but of its completeness).
- S109: Daybreak HOLD_BEFORE_FREEZE vs repo s109 running (fixtures exist). Daybreak audited a pre-stub state.
- db-s114: FINDINGS-GRAPH line 425 still cites 20/31; Daybreak correction (VOYNICH-DB-S114-GHOST-ROW-CORRECTION-2026-10-18.md) confirms O-059 (15 independent pairs). Repo has O-059 open but graph line unchanged.
- Timestamps: Daybreak files are stamped later than the clock (VOYNICH-CURRENT-STATE "Cutoff 16:35 PDT", S109 audit "16:05 PDT"; file mtimes 15:45-15:48; clock 15:56). Treat their stated times as unreliable.

## 4. Teammate status files a new agent could read as canonical
- <team-comms>
- <team-comms>, <team-comms>, <team-comms> (says "Canonical interpretation"; its read-first list puts codex_lab before the repo)
- <team-comms>, VOYNICH-EVIDENCE-INDEX-2026-10-18.md
- <team-comms> (109 KB) and ~30 other VOYNICH-TOP10-*/voynich-top10-* versions; VOYNICH-TOP10-PLAIN-ENGLISH-2026-10-18.md
- lab/codex_lab/{AGENT-START.md, CURRENT_STATE_2026-10-18.md, EVIDENCE-INDEX.md, BIG-PICTURE-EVIDENCE-SYNTHESIS-2026-10-18.md}
- lab/{TEAM-HANDOFF.md, PLAN.md, FINDINGS.md, LEADS-AND-FINDINGS.md} (Oct-17 stale; TEAM-HANDOFF says "Read in this order (canonical)")
- <home>/.gemini/antigravity/brain/<session>/VOYNICH_MASTER_FINDINGS_INDEX.md ("single retrieval hub", "Current Established Truth")
- ...\<session>-...\voynich_concrete_truths_and_relationships.md, voynich_cryptanalysis_report.md (self-marked superseded)
