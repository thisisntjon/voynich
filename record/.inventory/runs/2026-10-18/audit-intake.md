# Intake audit: Voynich knowledge outside the canonical repo

Stamp: 2026-10-18 16:08 PDT (from `date`). Read-only outside the scratchpad. Helper scripts: `scratchpad\work\verify.py`, `scratchpad\work\resolve.py`.

How it was checked:
- Stubs: every hash line of each `*.sha256` was re-hashed with Python sha256. Relative paths were resolved as `codex_lab\...` -> `lab/codex_lab/...`, and `voynich\` / `VOY_ROOT\` / `upstream\` -> the repo root.
- Times: file creation time (Python `st_ctime` on Windows = PowerShell CreationTime) and mtime.
- Repo code: imports grepped.
- What would refute a reading: a stub that failed, a results file created before its stub, or a printed call that contradicts the verdict. Each was checked per run below.
- `impl`: no Daybreak run counts as `impl`. Daybreak is not blind, and TRIANGULATION says `impl` is code written independently, i.e. roach. Lines go in as `method`, `data` or `external`.

Next free claim id: the highest id in CLAIMS.md at 16:07 was `c-540`, so the drafts use `c-541`... Renumber when filing.

## 1. Daybreak verdicts never filed (db-)

| run | stub verify | stub frozen | results created | printed call (file:line) | thresholds in stub before results | repo code imported | class |
|---|---|---|---|---|---|---|---|
| db-s100 | 9/9 OK | 09:23:41 | 09:25:24 | `results_s100_tail_picture_semantic_link.txt:30 VERDICT=NO_LARGE_TAIL_PICTURE_LINK_DETECTED` (:26 power_pass=True, :27 C1 False, :28 C2 False, :29 C3 True) | yes, prereg lines 38-52 | s78, scoreboard.metrics_new | ADMISSIBLE-WITH-SCOPE |
| db-s102 | 130/130 OK | 09:40:53 | 09:42:26 | `results_s102_tail_objective_geometry.txt:44 VERDICT=NO_REPLICATED_GEOMETRY_LINK` (:42 controls_pass=True, :43 six calls False) | yes, 54-68 | s78, metrics_new | ADMISSIBLE-WITH-SCOPE |
| db-s103 | 3/3 OK (s74 = repo root file, unchanged) | 10:09:16 | 10:09:32 | `results_s103_s93_recurrence_overshoot_diagnosis.txt:21 VERDICT: DIAGONAL_CAUSE` (R42 3.045, R42_no_diag 1.231, F 3.26) | yes, 44-57 | s74 | ADMISSIBLE-WITH-SCOPE (method note) |
| db-s107 | 7/7 OK | 10:25:36 | 10:25:43 | `results_s107_head_frame_to_tail_register.txt:21 VERDICT=NO_EARLY_HEAD_FRAME_REGISTER_LINK` (:19-20 all False; :4 fixture_pass=True) | yes, 44-58 | db-s104 module, metrics_new | ADMISSIBLE-WITH-SCOPE |
| db-s108 | final 8/8 OK; run1 manifest fails on the .py only (serialization fix, amendment1 10:35:48) | 10:35:56 | 10:36:29 | `results_s108_f57v_latin_consonant_key.txt:38 VERDICT=NO_RING_KEY_SIGNAL` (:5, :21 q99 folds 0/15 for both models; bar 12/15) | yes, 53-67 | none (own code; reads repo GC2a) | ADMISSIBLE-WITH-SCOPE |
| db-s110 | 8/8 OK | 10:45:57 | 10:46:21 | `results_s110_label_anchor_robustness.txt:13 VERDICT=REPRESENTATION_DEPENDENT_LABEL_SIGNAL` (:10 C1 False, :11 C2 False, :12 C3 True) | yes, 25-38 | s70, s76, vparse, metrics_new | ADMISSIBLE |
| db-s112 | 8/8 OK (re-frozen 11:04:29) | first freeze 11:03:32, amend 11:04:10 | first output 11:03:41; main file rewritten 11:04:37 | `results_s112_object_level_label_visual_link.txt:13 VERDICT=NO_OBJECT_LEVEL_LABEL_VISUAL_LINK`; first output kept as `results_s112_pre_amend1_invalid.txt:13`, same verdict, all calls False in both | yes, 47-55 | vparse, metrics_new | ADMISSIBLE-WITH-SCOPE |
| db-s113 | 7/7 OK | 11:11:50 | 11:12:51 | `results_s113_external_container_label.txt:8 VERDICT=NO_EXTERNAL_CONTAINER_LABEL_FORM_LINK` (:7 C1 False, AUC 0.407, p 0.70) | yes, 42-56 | none (sklearn) | ADMISSIBLE-WITH-SCOPE (uninformative exclusion) |
| db-s116 | 5/5 OK | 11:31:33 | 11:31:44 | `results_s116_antidotarium_two_part_architecture.txt:11 VERDICT=NO_TWO_PART_ANTIDOTARY_ARCHITECTURE`, but `:6 PASS=False` (planted winning_k 3 is not the registered k) | yes, prereg (preregistrations/s116) lines 88-92: "If it fails, the manuscript test is underpowered" | s52, s70 via VOY_ROOT | NOT ADMISSIBLE as a negative: the verdict contradicts its own rule (D-063). File as UNDERPOWERED. |
| db-s117 | 5/5 OK | 11:35:46 | 11:35:57 (rewritten 11:37:29; the JSON is byte-identical to the copy hashed at 11:36:49) | `results_s117_order_free_antidotarium_graph_mapping.txt:10 VERDICT=UNDERPOWERED` (:8 planted_pass=False, mapping 0.15 < 0.50) | yes | via VOY_ROOT | NOT ADMISSIBLE beyond UNDERPOWERED: see note A |
| db-s119 | 9/9 design + 18/18 execution OK | 12:01:32 (script edited 12:00:32, before freeze) | 12:09:10 | `results_s119_medical_recipe_family_retrieval.txt:41 VERDICT=UNDERPOWERED` (:38 SCRIB_POWER False, :39 POWER_PASS False) | yes, 83-93 | via VOY_ROOT | ADMISSIBLE as UNDERPOWERED (no claim) |
| db-s121 | 14/14 + 3/3 OK | 12:25:06 | 12:25:56 | `results_s121_frozen_role_graph_q20_application.txt:25 VERDICT=NO_IDENTIFIED_RECIPE_SOURCE_OR_FAMILY` (every source/family pass=False; every delta negative) | yes, 34-63 | via VOY_ROOT | ADMISSIBLE-WITH-SCOPE |
| db-s122 | 7/7 OK | 12:40:18 | 12:42:15 | `results_s122_expanded_external_label_form.txt:10 VERDICT=NO_TRANSFERABLE_EXTERNAL_LABEL_FORM` (:8-9 C1, C2 False) | yes, 47-61 | none (sklearn) | ADMISSIBLE-WITH-SCOPE (not an exclusion; weak trend) |

Scopes and notes:
- **db-s100.** Powered only for a large link. At planted strength s=0.10, 0/20 replicates are detected; at 0.20, 12/20; at 0.30-0.40, 20/20 (lines 21-24). So it excludes r of about 0.14 or more, not small links. Bears on F-33 (agrees).
- **db-s102.** Planted gains 0.43-0.62, so only large geometry links are excluded. IT2a foreground p 0.00998 is a single cell, not replicated. Bears on F-33 (agrees).
- **db-s103.** Diagnoses Daybreak's own db-s93 automaton: its recurrence overshoot comes from diagonal self-bigrams (Rw1 3.05 falls to 1.23 when they are removed). It describes the generator, not the manuscript. Use it as a design note for F-41-type producers; no grade change.
- **db-s107.** Early head/frame profile does not predict the later tail register. Against the cross-quire comparator the 95% CIs lie below zero on all 3 transliterations (lines 7-17). Bears on F-42 (consistent: the register pool is not carried by frames). Absence finding with a passing fixture (single fixture, not folds).
- **db-s108.** Excludes the literal Latin/Italian consonant-order reading of the f57v 4x17 ring on GC2a paragraphs. Bears on F-20 (agrees).
- **db-s110.**
  - Canon+Comp MRR is 0.553 against q99 0.537 (p 0.007). C2 fails only because top-1 equals its q99 (0.375 = 0.375).
  - RawWord and Zattera are null, and the leave-one-group-out check passes.
  - This is the representation dependence named in F-43's title. Add it as a `seg` line on F-43 (agrees).
- **db-s112.**
  - Rule break: the results file was overwritten. Mitigation: the first output was preserved, and the amendment (correcting an implementation deviation from the stub) does not change any call.
  - File both outputs.
  - The fixture is planted image clusters, so it is powered only for a strong label-to-object visual link. Bears on F-33 and H-06 (agrees).
- **db-s113 and db-s122.**
  - The positive control is a literal tag string (`zzcontainerzz`, `cc...cc`), not a realistic planted effect. Under D-068 the negative counts as UNINFORMATIVE (`unverified: true`).
  - db-s122 (n 160, 25 containers, 8 pages): Edge2 mean page AUC is 0.656 against q95 0.650 (p 0.040), and Trim1 has 7/8 pages above 0.5 (p 0.063). That is a weak positive trend, not an exclusion.
  - Bears on H-06 and F-33. Neutral. A powered rerun would be cheap.
- **Note A, db-s117 (post-hoc rescue).**
  - The printed manuscript numbers (line 6: Canon+Comp r 0.108, 10/10, p 0.0005; line 7: trim1 0.078, p 0.0005) meet manuscript rules 2-5.
  - Amendment 1 (preregistrations/s117_amend1, 11:36:42) repaired the failed fixture after those numbers were printed. It states that the original numbers "may be interpreted" if the new fixture passes, and it did (`results_s117_amend1_positive_fixture_noise.txt:11 PLANTED_PASS=True`).
  - This is the D-064/D-065 pattern. File only the printed UNDERPOWERED.
  - The resemblance is also non-specific: db-s118 (already on F-28) gives GENERIC; in db-s119 (line 26) Caesar prose is positive (r 0.032, p 0.019); in db-s121 Caesar is positive too (r 0.080, p 0.030).
- **db-s121.** Its power comes from db-s120, where the C1 role graph identifies 4/4 external sources on external-only data (`results_s120...:10-15`). That power was never tested through a Voynich-like encoding, so the D-068 standard is only partly met. Bears on F-28 (agrees: no source or family identified).
- **Id collision.** codex_lab also holds `s123_period_upper_german_recipe_control.prereg.md` (13:01, no results). Alias `db-s123` to the Llull run only.

## 2. db-s123 Llull held-out continuation

- **Stub:** 3/3 OK. The OCR it hashes is the repo file `data/controls_tabular/raw_lull_1515/ARes54311_djvu.txt` (sha aa0bb346...). The <team-comms> copy of the prereg is byte-identical to the codex_lab copy (7566c0f6...).
- **Times:** prereg 14:55:08 and sha 14:55:25, both before results 14:55:30.
- **Printed call:** `results_db_s123_lull_heldout_continuation.txt:4 VERDICT: HOLD` (:3: 14 rows / 26 tokens; the gate needs at least 30 rows and 100 tokens). The gate and calls were in the stub.
- **Class:** ADMISSIBLE as HOLD. There is no scientific claim.
- **My check:** I scanned all 49,604 OCR lines with an approximation of the s107 row detector. Eligible rows exist only in lines 18000-18999 (about 257 rows in total; 37 in 18500-18999). The 1515 print has no other table region, so the HOLD is terminal for this witness. An independent witness (R14) is required.
- **Bearing:** the s107 exception in F-40 and F-49 (neutral).

## 3. R14 combinatory-table manuscripts

What is on disk:
- **BC Ms 3075.** `codex_lab\acquisition\bc_ms_3075_r14\source\`: 7 openings f114r-f120r at 1600x1046 JPG (1.9 MB), with SOURCE_MANIFEST.csv and ACQUISITION_RECEIPT.json. Rights statement: CNE (copyright not evaluated).
- **Previews.** codex_lab\tmp has 96 BC preview and contact-sheet images (1000 px and 300 px), plus Pal. lat. 984 contact sheets.
- **Pal. lat. 984 and UCM BH MSS 106.** Only the IIIF manifests (codex_lab\work_orders; 0.99 MB and 0.84 MB) and canvas maps. No full-resolution table images are on disk.
- **Prereg and scorer.** R14 prereg v1 verifies (1/1, 15:25:17). Amendment 1 sets the primary axis to the horizontal physical row. The freeze manifest verifies 9/9 (15:33:35). Scorer `experiments\r14_physical_rows\r14_score_physical_rows.py`, with synthetic positive and negative fixtures only.
- **No real cell transcription exists for any of the three manuscripts.** Nothing on disk is usable for a full-size Lullian test yet.

Usability:
- I viewed BC f116r. At 1600 px it is legible: each page has 4 ruled columns and 2 table zones of about 20 rows, with one 4-letter cell per column per row (letters b-k, t).
- Estimate from one opening (unverified count): about 160 cells per page, about 1,900 cells and about 480 four-cell rows over f114r-f119r. That is well above the R14 gate of 150 rows and 750 cells.
- Caveat for G2 = s110 (D-066 (o)):
  - Horizontal rows hold only 4 cells, far shorter than Voynich lines.
  - Adjacent cells usually differ in one letter and only sometimes repeat. My reading of f116r row 2 is approximately "b?gb bhtb bhtb bitb" (unverified).
  - So in-line reuse must be measured on these rows, not assumed from the 1515 print's repeated cells.
- Pal. lat. 984: only p0012, p0013 and p0015 are tables. UCM 106: no comparable cell-row corpus (layout preflight only).
- **Class:** DATA-ONLY (images and manifests). The triage reviews are visual preflights with no claim.

## 4. R12 identity ablations and R11-R12 quire coupling

- **Status:** exploratory and post-result. No stub. Code reads repo ZL3b and r11 definitions (`codex_lab\audits\explore_r12_*`, `explore_r11_r12_quire_coupling.py`; the rev0 outputs are preserved). Not `impl`.
- **Exact-word ablation** (`<team-comms>`):
  - :6-9: removing 285/30,826 identical pairs leaves cadence excess 0.0865 of 0.0922 (93.8%), p 0.001.
  - Per quire, 84.8-98.3% is retained.
- **S0/S1/S2 ablation** (`VOYNICH-R12-S0-S1-S2-ABLATION.txt:6-11`): S0 retains 93.8%, S1 (1,163 pairs removed) 95.9%, S2 (2,122 removed) 84.4%; all p 0.001.
- **Quire coupling** (`VOYNICH-R11-R12-QUIRE-COUPLING.txt`; review table): cadence vs recurrence at S0 r +0.601 (Spearman +0.443); cadence vs boundary D at S0 +0.707; S1 boundary -0.109.
- **Class:** ADMISSIBLE-WITH-SCOPE as descriptive lines only (no threshold before the run, so `unverified: true`).
- **Bearing:** F-04 (rhythm is not produced by adjacent identical units) and F-13 (agrees; separates the two processes). The coupling uses 15 units with no multiplicity control.

## 5. Daybreak corpora (codex_lab\acquisition)

| file | size | content | licence | in repo data/? |
|---|---|---|---|---|
| s114_stolfi_full_label_catalogue.csv | 18 KB | 239 labels (from stolfi_labels_1998_raw.html, 136 KB) | not stated (Stolfi web page) | no (repo has only Stolfi crib pages) |
| s113_stolfi_label_attributes.csv | 14 KB | 84 labels with container/botanical attributes | not stated | no |
| s112_object_label_registration.csv | 14 KB | 97 label-object crop registrations | Daybreak-made | no |
| s115_antidotarium_nicolai_latin_recipes.csv | 233 KB | 141 recipes, 18,757 tokens (DBNL TEI) | DBNL `<availability>` empty; 1917 edition (unverified PD) | no |
| s119_scribonius_latin_recipes.csv | 229 KB | 271 recipes, 25,157 tokens (Jocks 2020 Glasgow PhD vol. 2) | thesis: personal non-commercial research only, no reproduction without permission | no; **do not copy** |
| s119_liber_de_coquina_latin_recipes.csv | 94 KB | 173 recipes, 9,073 tokens (Gloning, Giessen) | not stated | no |
| s119_corema_culinary_recipes.csv (+ er1 18 KB) | 80 KB | 235 recipes, 12,499 tokens (a1, b2, er1, w4) | CC BY 4.0 (text, per TEI) | no |
| corema_collection\pools | 9.4 MB | 59 TEI manuscripts; southern-German pools 110k / 151k / 262k tokens on physical lines | CC BY 4.0 (text) | no |
| corema_m2_alemannic | 652 KB | Cgm 384 Alemannic recipes | CC BY 4.0 (per CoReMa) | no |
| external\ | 22 MB | raw sources (PDF/XML/HTML) | mixed, as above | no |
| s120_latin_caesar_control.txt | 170 KB | identical to repo `data/controls/latin_caesar.txt` (cmp) | n/a | yes |

These are DATA-ONLY. Worth copying: the CoReMa pools and CSVs (CC BY), the Antidotarium CSV (DBNL licence to be confirmed), and the Stolfi label CSVs (cite as derived; licence unknown). Do not copy Scribonius.

## 6. Argon (quarantined, D-065)

- **h19 Fontana/Llull simulator** (`results_h19_fontana_lull.txt`; the `FONTANA_NAL635_LULL_CHAMBERS` summary is at :100).
  - **Not registered:** no stub, no sha.
  - **Edited after the run:** the script was modified 15:20:27, after the results were created at 15:16:44, and the JSON/TSV were rewritten at 15:21:48.
  - **Input size:** the driver is 1,680 cells from the repo's synthetic `lull_ars_brevis_table.meta.json`, built into 280 rows of 6 cells. Output is 22,500 generated tokens. "PartA_Authentic" is a misnomer.
  - **Source of the in-line reuse: the generator, not Llull.**
    - `FontanaPegboard` (test_h19_models.py:223-434) is the lead's s91 line-pool producer re-skinned.
    - Each line samples, with replacement, from a pool drawn from Gamma quire lexicons, with a cross-line penalty (pen 0.82) and a core bigram mix (lam 0.68). That penalty plus pool is what gives Rw1 > 1 and Rc1 < 1.
    - The core frequencies, bigrams, prefix/suffix transition tables and junction tables are all fit on ZL3b itself (lines 241-310).
    - The driver only adds +0.12 to one Gumbel key and multiplies one prefix weight by 1.08.
    - The shuffled-driver control also gives SHOWS_F40_CORE and FULL_C1 True (:91).
    - Scoring is on the data it was fit to, with no held-out quires.
  - **Class:** NOT ADMISSIBLE (unregistered, edited after the run, circular).
  - **Other output:** `LULL_MULTIPLICATIO_22500` gets Rw1 26 by tiling 1,680 cells 15 times.
- **Plant concordance** (`alchemical_herbal_98_concordance.tsv`, 98 rows).
  - **Class:** DATA-ONLY, provenance partly unverifiable.
  - The c408/c500 columns come from the Bodleian manifests (c408 fills 98 rows, c500 32).
  - The botanical identifications, diagnostic types and other-witness folios (Aldini 211, Firenze 106, Fermo 18, Lat 17848) are hand-typed tuples in `build_o062_package.py:76ff` with no per-row source.
  - The LJS 419 matches rest on the repo's unverified captions_s103.json.
- **Manifest checks** (curl -L, 16:05):

  | manifest | HTTP | what it is |
  |---|---|---|
  | Bodleian `28e2b6a5-b9a9-4e05-9be2-c1974d0ebd18.json` | 200 | MS. Canon. Misc. 500, 93 canvases, "c. 1500 (?)" |
  | Bodleian `db2fade4-61ee-4a11-a894-19361c551eed.json` | 200 | MS. Canon. Misc. 408, 166 canvases, "15th century, end" |
  | Bodleian image sample | 200 | |
  | Vatican Chig. F.VII.158 | 200 | |
  | Vatican Pal. lat. 1078 | 200 | |
  | Vatican Pal. lat. 984 | 200 | |
  | BSB bsb00094611 | 200 | |
  | Wellcome b19616405 | 200 | |
  | Gallica btv1b10539337k | 403 | |

  No licence field appears in the Bodleian manifests.
- **Beasley 2024** (beasley_2024_thesis.txt:124, 172, 210) places Canon. Misc. 408 in Segre's stemma (siglum C) and lists LJS 419.
- **Physical forensics.** Classes: the collation tables are DATA-ONLY (already in repo); the ink-gap result is NOT ADMISSIBLE.
  - The collation/bifolio tables (104 and 53 rows) derive from the repo's `folio_evidence_inventory.tsv` plus tail-vocabulary cosines. Nothing new to copy.
  - The 15,666 ink gaps are the repo's s47 output re-tabulated (120 tests).
  - The report's claim that "transition surprisal slows the scribe" is unregistered and quarantined. Bears on F-19 and F-14 at most, as a lead for a registered test.

## 7. Draft CLAIMS rows (format of c-437..c-456; renumber at filing)

| `c-541` | db-s100 (Daybreak) "tail-core occurrence/echo vs masked herbal-picture similarity, 119 pages, 3 transliterations: ZL3b tail_occurrence r +0.053 p 0.30 (NOBIF +0.046 p 0.35), echo r -0.004 p 0.79; all 12 cells p >= 0.10; power: planted s=0.10 0/20, 0.20 12/20, 0.30-0.40 20/20 -> C1 False, C2 False, C3 True, VERDICT NO_LARGE_TAIL_PICTURE_LINK_DETECTED" | CALLS, VERDICT | `lab/codex_lab/experiments/results_s100_tail_picture_semantic_link.txt` | lines 5-30 | 2026-10-18 | VERIFIED (stub 9/9 OK; stub 09:23:41, results created 09:25:24) | imports s78/metrics_new: not impl; excludes only r >~0.14; F-33 line (method, agrees) |
| `c-542` | db-s102 "held-out-quire tail cores vs 6 objective herbal geometry measures: planted gains 0.43-0.62 (p 0.002, all 3); real: 0/6 outcomes replicated (gains -0.20..+0.05; only IT2a foreground p 0.010) -> VERDICT NO_REPLICATED_GEOMETRY_LINK" | calls, VERDICT | `.../codex_lab/experiments/results_s102_tail_objective_geometry.txt` | lines 11-44 | 2026-10-18 | VERIFIED (stub 130/130 OK; 09:40:53 < 09:42:26) | large effects only; F-33 line (physical, agrees) |
| `c-543` | db-s103 "db-s93 automaton recurrence overshoot: median Rw1 2.49 at lam 0 rising to 3.05 at lam 0.42; removing diagonal bigrams 1.23; excess fraction removed 3.26 -> VERDICT DIAGONAL_CAUSE" | VERDICT | `.../results_s103_s93_recurrence_overshoot_diagnosis.txt` | lines 6-21 | 2026-10-18 | VERIFIED (stub 3/3 OK; 10:09:16 < 10:09:32) | generator diagnosis, not a manuscript property; F-41 design note |
| `c-544` | db-s107 "early head/frame profile vs later tail register (ZL3b/RF1b/IT2a, 111/111/110 pages): combined gain vs freq -0.0021/-0.0031/-0.0035, vs cross-quire -0.0050/-0.0037/-0.0086 (CI below 0); fixture passed -> all calls False, VERDICT NO_EARLY_HEAD_FRAME_REGISTER_LINK" | CALLS, VERDICT | `.../results_s107_head_frame_to_tail_register.txt` | lines 4-21 | 2026-10-18 | VERIFIED (stub 7/7 OK; 10:25:36 < 10:25:43) | F-42 line (method, agrees) |
| `c-545` | db-s108 "f57v 4x17 ring as Latin/Italian consonant key, 15 quire folds, GC2a paragraphs: candidate above random-key q99 on 0/15 folds for both models (bar 12/15), median gain +0.27/+0.28; fixture passed -> VERDICT NO_RING_KEY_SIGNAL" | VERDICT | `.../results_s108_f57v_latin_consonant_key.txt` | lines 3-38 | 2026-10-18 | VERIFIED (final stub 8/8 OK; 10:35:56 < 10:36:29; run1 crashed at JSON write, fix-only amendment) | F-20 line (method, agrees) |
| `c-546` | db-s110 "S109 label anchor under other representations: RawWord MRR 0.379 (q99 0.558, p 0.80); Canon+Comp MRR 0.553 > q99 0.537 (p 0.007), top-1 0.375 = q99; Zattera 0.567 (p 0.24); leave-one-group-out passes -> C1 False, C2 False, C3 True, VERDICT REPRESENTATION_DEPENDENT_LABEL_SIGNAL" | CALLS, VERDICT | `.../results_s110_label_anchor_robustness.txt` | lines 3-13 | 2026-10-18 | VERIFIED (stub 8/8 OK; 10:45:57 < 10:46:21) | F-43 line (seg, agrees) |
| `c-547` | db-s112 "label text vs object crop similarity, 97 registered items, 12 pages: SlotCoreAll mean z +0.158 (p 0.29), nonjar +0.297 (p 0.13), RawTrim1 p 0.85; first (pre-amendment) run same calls -> C1-C3 False, VERDICT NO_OBJECT_LEVEL_LABEL_VISUAL_LINK" | CALLS, VERDICT | `.../results_s112_object_level_label_visual_link.txt` + `results_s112_pre_amend1_invalid.txt` | lines 4-13 | 2026-10-18 | VERIFIED with note (stub 8/8 OK; results file overwritten 11:04:37 after amendment; first output preserved; verdict unchanged) | F-33 / H-06 line (physical, agrees), strong-link power only |
| `c-548` | db-s113 + db-s122 "label form vs Stolfi container/botanical class, leave-one-page-out: s113 n 40 (8 containers, 5 pages) AUC 0.407 p 0.70; s122 n 160 (25, 8 pages) Full 0.616 p 0.108, Edge2 0.656 p 0.040, Trim1 0.648 p 0.063 -> VERDICTs NO_EXTERNAL_CONTAINER_LABEL_FORM_LINK, NO_TRANSFERABLE_EXTERNAL_LABEL_FORM" | CALLS, VERDICT | `.../results_s113_external_container_label.txt`, `.../results_s122_expanded_external_label_form.txt` | s113 lines 4-8; s122 lines 5-10 | 2026-10-18 | VERIFIED (stubs 7/7, 7/7; 11:11:50 < 11:12:51; 12:40:18 < 12:42:15) | tag-string fixtures only: UNINFORMATIVE under D-068; H-06, unverified: true |
| `c-549` | db-s116 "Antidotarium two-part consecutive-entry architecture on 285 Q20 paragraphs: planted control PASS=False (winning k 3 is not the registered k; p 0.009); Canon+Comp direction p 0.61, raw p 0.59, trim1 p 0.73; printed VERDICT NO_TWO_PART_ANTIDOTARY_ARCHITECTURE" | planted line, VERDICT | `.../results_s116_antidotarium_two_part_architecture.txt` | lines 6-11 | 2026-10-18 | STALE verdict: stub (preregistrations/s116, Positive control) says a failed control makes the test underpowered; file as UNDERPOWERED (D-063) | no F-28 line |
| `c-550` | db-s117 "order-free Antidotarium graph: planted r 0.18 but mapping accuracy 0.15 < 0.50 -> planted_pass False, VERDICT UNDERPOWERED; Canon+Comp r 0.108 (10/10, p 0.0005) printed before Amendment 1 repaired the fixture (PLANTED_PASS True)" | VERDICT | `.../results_s117_order_free_antidotarium_graph_mapping.txt`, `results_s117_amend1_positive_fixture_noise.txt` | lines 5-10; amend1 line 11 | 2026-10-18 | VERIFIED as UNDERPOWERED; amendment written after manuscript numbers were printed: post-hoc rescue, not admissible as a positive (D-064/D-065) | generic per db-s118/s119/s121 |
| `c-551` | db-s119 "medical-recipe family retrieval: ANT power True, Scribonius power False -> POWER_PASS False, VERDICT UNDERPOWERED; Canon+Comp Caesar prose r +0.032 p 0.019 (non-specific)" | VERDICT | `.../results_s119_medical_recipe_family_retrieval.txt` | lines 21-41 | 2026-10-18 | VERIFIED (stubs 9/9 + 18/18; exec freeze 12:01:32 < 12:09:10) | no claim |
| `c-552` | db-s121 "frozen C1 role-graph applied to Q20 (Canon+Comp, trim1): ANT_MED rank 1 r 0.126 but advantage -0.0001 (sign-flip 0.51), every source and family pass False, all deltas negative; Caesar prose r 0.080 p 0.030 -> VERDICT NO_IDENTIFIED_RECIPE_SOURCE_OR_FAMILY" | VERDICT | `.../results_s121_frozen_role_graph_q20_application.txt` | lines 5-25 | 2026-10-18 | VERIFIED (stubs 14/14 + 3/3; 12:25:06 < 12:25:56) | power from db-s120 external-only identifiability (4/4); F-28 line (external, agrees) |
| `c-553` | db-s123 "Llull 1515 held-out OCR lines [18600,19000): 14 eligible rows, 26 tokens < gate 30/100 -> VERDICT HOLD" | VERDICT | `.../results_db_s123_lull_heldout_continuation.txt` | lines 3-4 | 2026-10-18 | VERIFIED (stub 3/3 OK with repo OCR; 14:55:25 < 14:55:30) | terminal for this witness (no other table region in OCR) |
| `c-554` | Daybreak R12 ablation (exploratory) "removing adjacent identical units keeps r12 cadence excess: S0 285/30,826 pairs, 93.8%; S1 1,163, 95.9%; S2 2,122, 84.4%; all p 0.001" | text table | `<team-comms>` | lines 5-11 | 2026-10-18 | VERIFIED numbers, no prereg (descriptive) | F-04 descriptive line, unverified: true |
| `c-555` | Daybreak R11-R12 quire coupling (exploratory) "15 ZL3b quires: cadence vs recurrence S0 r +0.601 (rho +0.443), vs boundary D +0.707; S1 +0.522 / -0.109; S2 +0.296 / +0.243" | text | `<team-comms>` | lines 4-12 | 2026-10-18 | VERIFIED numbers (read at 16:09), post hoc, no gate | descriptive only |
