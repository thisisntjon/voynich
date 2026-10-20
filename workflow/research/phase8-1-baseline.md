# Phase 8.1 cold-start baseline (answers to phase8-1-bank.md)

Date: 2026-10-19 09:46 PDT (from `date`). Started 09:41:46 PDT.
Scorer: a fresh agent with no prior project knowledge, read-only except for this file. No web access. I did not open any `workflow/research/phase8-*.md` file other than the bank.

Counting rules used:
- **Open**: an access that returned file content. This includes a Read, a grep or query that printed matching lines or rows, and a command that printed file text.
- **Not an open**: path-only or count-only listings (ls, `grep -l`, Grep count mode) and searches that returned nothing. These still count as steps.
- **Step**: one tool call. One Bash call that chains several greps counts as one step and one open.
- Content reused from an earlier question's access counts 0 new opens. The reuse is noted.
- **Setup**, outside the per-question counts: AGENTS.md was preloaded in context (0 steps). Read the bank (1 step, 1 open). `wc -l` and `date` on the key files (1 step, line counts only). Read INVENTORY.md (1 step, 1 open). Setup totals: 3 steps, 2 opens.

Main entry points found: AGENTS.md, then `tools/vkb/README.md`. The VKB is `data/vkb/vkb.sqlite`, queried with `python tools/vkb/query.py`. It answered Q1, Q6, Q12, Q16 and Q18 fastest. `workflow/FINDINGS-GRAPH.yaml` (F-, H-, X-, P- ids) and the registers in `.inventory/registers/` answered most of the rest.

---

## Q1. f68r1: section, quire, hand, label count, published facts, findings that touch it

**Answer.**
- **Quire, sheet and section.** Quire I (Zandbergen q09), bifolio I-1 (conjugate f67), foldout panel 1. Section A (astronomical); the wide facts table says Z/A.
- **Hand and language.** Davis hand 4. Currier language "-"; RZ language A (page) / Ce (folio, bifolio).
- **Text and labels.** 7 paragraph lines and 31 tokens. There are 29 star labels: VKB `n_label_loci` 29 and published count 29. The older inventory's 34 is label tokens, not loci. There are 37 loci in all: 4 standard lines, 3 floating-paragraph lines, 1 circular item and 29 star labels.
- **Published facts.**
  - Sun face with small rays at the top, moon face at the bottom, 29 labelled stars between them (Zandbergen 2025).
  - Pencilled "a" in the upper left by a later owner (Zandbergen, writing page).
  - Stolfi title "Sun over Moon". Colours: yellow on most stars, blue on some (Reeds).
  - f68 is a three-way foldout, and its folio number is on f68v2.
  - Bax/Stolfi star-label cribs exist.
  - No one-to-one Yale canvas (s45 rule).
- **Findings that touch it.**
  - **F-28** (no antidotary, alphabetical or zodiac order). Via **O-012**, the star and zodiac labels (f68r1–r3) were tested as ordered lists: null (s52_p4comp1, c-376).
  - **L-346**: the explorediscussion.txt reading "oky" for f68r1 is not in ZL3b and is not admissible.
  - No `finding_lines` or `claims` row names f68r1 directly.

**Canonical source.** VKB `folios` row f68r1, whose src is `data/ZL3b-n.txt:3052` and `data/folio_evidence_inventory.tsv:124`. VKB `page_facts`: `data/external/page-facts/astro-physical/facts.tsv:88-94` and `data/external/page-facts/catalogues/facts.tsv:2053-2067`. `.inventory/registers/OPEN.md:18` (O-012) and `workflow/FINDINGS-GRAPH.yaml:577` (F-28).

**Accesses, in order:**
1. Grep count "f68r1" over the repo. Paths and counts only; not an open.
2. Grep f68r1 in `docs/FOLIO-EVIDENCE-INVENTORY.md`, `data/folio_evidence_inventory.tsv`, `data/s127_picture/sources/folio_facts_wide.tsv`, `.inventory/registers/OPEN.md` and `LEARNINGS.md`, plus the tsv headers. **open**
3. ls `tools`; grep f68r in `FINDINGS-GRAPH.yaml` and `FINDINGS-MAP.md`. **open**
4. Read `tools/vkb/README.md`. **open**
5. VKB query: `folios` where folio='f68r1', plus the table list. **open**
6. VKB query: `page_facts` where folio like 'f68r%'. **open**
7. VKB query: `finding_lines` and `claims` text containing f68, plus grep for zodiac in the graph. **open**
8. Graph lines 570–580 (F-28 header). **open**

Opens 7. Steps 8. Confidence: **likely**. The findings list may be incomplete because there is no folio-to-finding link table.

## Q2. Results supporting F-20 and its current grade

**Answer.** F-20, "There is no internal crib". Grade **TRIANGULATED**, status **standing**.
- **Evidence lines:**
  - method: s48/s53 image embeddings and part-level matching (`results_s53.txt`, c-388).
  - impl: Argon s53 text-side labels (`results_s53_p4a1_p4e1_anchors_and_errors.txt`, c-377).
  - data: 3 transliterations plus word and stem variants (same file, c-377).
  - external: Daybreak db-s114 (Stolfi label catalogue, 6/15 after the ghost-row correction, p 0.745), `codex_lab/experiments/results_s114_repeated_label_object_consistency.txt`.
  - external: s128-p72 human matches, NO_LINK p 0.72 at power 0.958 (`results_s128_20261019T090659.txt`, c-590).
- **Controls:** s115-A0 real-herbal retrieval (power 0.995, `results_s115_a0_20261018T203952.txt`) and the planted label-text link (`results_s54.txt`).
- **Claims:** c-371, c-377, c-388, c-389.
- **Decision:** D-053.

**Canonical source.** `workflow/FINDINGS-GRAPH.yaml:418` (F-20), with the grade at `workflow/FINDINGS-MAP.md:60`.

**Accesses:**
1. awk the F-20 block in the graph, plus grep F-20 in the map. **open**

Opens 1. Steps 1. Confidence: **certain**.

## Q3. Has a Naibbe-type cipher been tested, and with what verdict?

**Answer.** Yes, several times.
- **H-04 (per-word random-table Naibbe):** "excluded at default settings". F-14 and F-24 are strong against it.
- **F-30, plain Naibbe:** Greshko's Naibbe rebuilt from his own tables gives no prefix order. In s81, 0/15 LOQO folds match.
- **F-34, sticky Naibbe:** line-sticky Naibbe matches the s69 call pattern on 13–15/15 held-out quires, but every variant predicts 0/15 quires (s81, s85). F-34 is **CONTESTED, at-risk**: the s85 Zattera arm fails, and roach r6 and s98 contest it.
- **Early work:** the plain-Naibbe controls in `results_c4.txt`, `results_f3.txt` and `results_g0.txt` all fail the board (c-105, c-112, c-177).

**Canonical source.** `workflow/FINDINGS-GRAPH.yaml:23` (H-04), `:500-507` (F-30, `results_s81.txt`) and `:684-704` (F-34, `results_s85.txt`). Claims c-105, c-112 and c-177 are in `.inventory/registers/CLAIMS.md`.

**Accesses:**
1. Grep -i naibbe in the graph, the map, all registers and TEAM-HANDOFF. **open**

Opens 1. Steps 1. Confidence: **likely**. The tests are clear, but "the verdict" is split across H-04, F-30 and F-34.

## Q4. Current status of H-14, and the evidence

**Answer.** H-14 is the table cipher whose affix table is held for a line (the sticky Naibbe family).
- **Status:** "narrowed (D-067)". A fixed line-held table is contested by roach r6 and s98. A drifting table failed 0/15 (roach r9, L-217, c-448, F-48). What remains is a "multi-scale state": fast within-line order, slow page drift and quire-local vocabulary.
- **Score:** 2.0 / 5.3.
- **For:** F-14 (m), F-30 (w), F-34 (m\*).
- **Against:** F-30 (w), F-34 (s\*), F-39 (m\*), F-45 (m), F-46 (m\*), F-47 (m), F-48 (m\*).

**Canonical source.** `workflow/FINDINGS-GRAPH.yaml:32` (H-14), `workflow/FINDINGS-MAP.md:27`, and `.inventory/registers/DECISIONS.md:73` (D-067 and its amendment).

**Accesses:**
- (Reused from Q3: the graph and map H-14 lines.)
1. Grep the DECISIONS rows D-066, D-067 and D-07x. **open**

Opens 1 (plus 1 reused). Steps 1. Confidence: **certain**.

## Q5. Which file holds the Parisel 2025 result, and what did the project conclude?

**Answer.**
- **The paper:** Parisel 2025, "Directionality of the Voynich Script", arXiv:2509.10573 (catalogue id VL00346).
- **The file:** it is held only as a PDF, `data/external/wave5-parisel-2025/parisel_arxiv_2509.10573.pdf`. There is no .txt extraction.
- **Conclusion:** the project filed none from it. The catalogue-to-findings row has no `project_ids`. The research note says "Abstracts not retrieved". No F-, L- or c- row cites 2509.10573.
- **Related work, not this paper:**
  - The project's reading-direction work is s92 (c-532, F-40): uniform reading-order reversals pass in 36/36 cells.
  - The Parisel papers that were tested are the 2026 ones: 2604.19762 (c-222) and the per-folio cho/che switch (s68, c-408, L-161: not two-state within a hand).

**Canonical source.** `data/external/library/inventory/held_documents.tsv:243`, `data/external/library/catalogue_to_findings.tsv:77` and `data/external/README.md:251`.

**Accesses:**
1. Grep -i parisel over .md, .yaml and .txt files (excluding phase8 files and the web library). **open**
2. ls `data/external/papers`; `grep -l` for 2509.10573. Paths only; not an open.
3. Grep 2509.10573 and parisel in `catalogue_to_findings.tsv`, `held_documents.tsv`, `data/external/README.md` and `computational_recent.md`. **open**
4. ls `wave5-parisel-2025`; grep VL00346 and "directional" in the graph and registers. **open**

Opens 3. Steps 4. Confidence: **likely** for the file. **Unsure** that "no conclusion" is right: a conclusion could sit in a file I did not search.

## Q6. Daybreak output since 2026-10-18 not yet filed in this repo

**Answer.** These are derived by my own cross-check; there is no canonical "unfiled" list.
- **Method:**
  - Daybreak writes to `lab/codex_lab/experiments/`; 60 results files there are dated 2026-10-18 or later.
  - I matched them by filename against the VKB `external_items` table, the graph, the registers and TEAM-HANDOFF, then by run id (`db-sNN`).
- **Unfiled by both filename and run id:**
  - db-s115 amend1 (s52 q20 page filter)
  - db-s125 (f49v margin key line relation)
  - db-s126 (f49v cycle rarity)
  - db-s129 (fp selector)
  - db-s130 (fp skeleton prediction)
  - db-s131 (fp local state)
  - db-s134 (O-062 herbal positive control, with run1)
  - db-s135 (O-062 Voynich application)
  - db-s139 (global witness assignment, with run1)
  - db-s140 (full gallery witness recovery, with run1)
- **Named by id only, not by file:** db-s90, s91, s93, s94, s95, s99, s104, s105, s106, s120, s127, s128 and s141. These are partly filed.
- **Listed but unclassified:** `external_items` lists 52 Daybreak or <team-comms> items with an empty `filed_as`, for example db-s100, s102, s107, s112, s113, s116, s117, s121 and s122. Each has an intake class, but none is filed to a finding.
- **Not checked:** <team-comms> messages.

**Canonical source.** VKB `external_items` (intake_class and filed_as) and the TEAM-HANDOFF.md run-id alias map (lines 366–394).

**Accesses:**
1. Grep -i daybreak in TEAM-HANDOFF.md. **open**
2. VKB query: `external_items` intake counts, and Daybreak rows with empty `filed_as`. **open**
3. find Daybreak results newer than 2026-10-18, cross-checked against `external_items` and grep of the graph, registers and TEAM-HANDOFF; prints the unfiled names. **open**
4. Count `db-sNN` mentions in the graph, registers, TEAM-HANDOFF and PLAN. **open**

Opens 4. Steps 4. Confidence: **unsure**. No single canonical answer exists, and my filename and id heuristic may mis-classify some items.

## Q7. Is X-01 (SlotSegmenter units) verified, at-risk or flipped, and what is the latest evidence?

**Answer.** **At-risk.**
- **Basis given in the graph:** "s76: 4/5 slot calls hold under Zattera, A14 flips; A21 rare cores are boundary shifts".
- **Latest evidence:**
  - The s85 lead audit (2026-10-18): the line-sticky result holds under SlotSegmenter and Seg_Affix2 but fails under Zattera, so "X-01 stays at-risk". The C2B_NAIBBE line is at `results_s85.txt:310`, and the run gave no X-01 discharge.
  - Argon s96 (P-28) tried to discharge X-01 and was rejected (D-065).
  - Roach r5 discharged X-01 for F-06 only. s76 discharged it for F-11, F-12, F-13 and F-14 (struck through in the map).
- **Next test:** roach **r16** (P-62, briefed), alphabet and segmenter sensitivity of about 10 load-bearing statistics (D-066 w).
- **Still resting on it:** about 21 findings, including F-39 through F-51 (map row X-01).

**Canonical source.** `workflow/FINDINGS-GRAPH.yaml:42` (X-01), `workflow/FINDINGS-MAP.md:99` and `:661`, and graph `:1310` (P-28) and `:1344` (P-62).

**Accesses:**
1. Grep X-01 in the map, and the X-01 line in the graph's assumptions block. **open**
2. Grep the X-01 row in the map, plus X-01 in LEARNINGS and DECISIONS. **open**
3. Grep P-28 and P-62 in the graph. **open**

Opens 3. Steps 3. Confidence: **certain** for the status; **likely** that this is the latest evidence.

## Q8. What did roach's blind replication of s114 find, and how is it filed?

**Answer.** Roach **r15b**, own code, frozen 2026-10-18 20:44:03 on roach.
- **Test A:** quire eta² on hand × section residuals, 10,000 within-cell permutations. The frozen rule calls DRIFT only if p < 0.01 on ZL3b and p < 0.05 on both RF1b and IT2a. Results: ZL p 0.0009 (hit), IT p 0.0006 (hit), RF p 0.0545 (miss). The call is **NO DRIFT**.
- **Test B:** R_within(1) and cadence give p 0.45 / 0.35, with an MDE of about 1.0 SD.
- **How it is filed:**
  - Claim **c-591**: "VERIFIED 2026-10-19 09:36". The manifest checks OK. The stub cannot be verified here because the roach-side inputs are not mirrored.
  - **F-50**, as an impl line with agrees: false. F-50 is now CONTESTED (status at-risk).
  - Pending **P-56**, state filed.
  - Learning **L-361**: the run was delivered before its withdrawal and found unfiled by the Phase 8 audit.

**Canonical source.** `runs/roach-r15/results_r15b.txt`, `.inventory/registers/CLAIMS.md:653` (c-591) and `workflow/FINDINGS-GRAPH.yaml` (F-50 block; P-56 at :1338).

**Accesses:**
1. ls `runs` (roach dirs); grep s114 together with roach, replic or r1x in the graph, TEAM-HANDOFF, LEARNINGS and DECISIONS. **open**
2. ls `runs/roach-r15`; grep c-591 in CLAIMS; awk the F-50 block in the graph. **open**

Opens 2. Steps 2. Confidence: **certain**.

## Q9. Which runs are pending right now, and who owns each?

**Answer.** These are the graph `pending` rows that are not filed or rejected:
- **P-52:** roach r14 (owner roach voynich-91), state briefed. It is an identifiable table-and-grille fitter. However, the PLAN log for 2026-10-18 21:04 says "r14/r15 withdrawn", so r14 is likely not live; the graph and PLAN disagree.
- **P-62:** roach **r16** (owner roach), briefed. Alphabet and segmenter sensitivity, deciding X-01, F-40 and F-08.
- **P-65:** roach **r17** (owner roach), briefed. Blind replication of s120 (F-51).

Other active work (PLAN `Current stage:` line, 2026-10-19 09:41):
- Phase 8.1 investigating (lead).
- The D-072/D-073 tracks in parallel: the Egerton crop and caption gates (Daybreak), and Fontana known-answer recovery (O-071, gate pending).
- TEAM-HANDOFF claims: Grok Bot s128 (frozen v1–v5 preregs, held under D-072) and lib01 (library infrastructure).

**Canonical source.** `workflow/FINDINGS-GRAPH.yaml:1334`, `:1344` and `:1347` (the pending block), and `workflow/PLAN.md:4` (stage line) with the Phase log at `:323` onward.

**Accesses:**
1. Grep pending P-rows in the graph, excluding filed and rejected. **open**
2. Grep the PLAN "Current stage", plus in-flight, running or claimed lines in TEAM-HANDOFF. **open**
3. PLAN header, section list and file tail. **open**
4. PLAN lines 323–345 (Phase log). **open**

Opens 4. Steps 4. Confidence: **likely**. Live status is spread over the graph, PLAN and TEAM-HANDOFF, and r14 is ambiguous.

## Q10. Next authorized action under the current strategy, and which decision row says so

**Answer.** **D-072** (2026-10-19 00:48), the pivot to externally validated meaning recovery. Its active order:
1. Finish the frozen Egerton crop and caption review gates, then run the already-planned prospective graph transfer without reselection.
2. Make Fontana usable as a known-answer cipher and plaintext control.
3. Only after an external bridge survives, freeze one image-only semantic-role-to-text prediction.

D-073 duplicates D-072 and states that "D-072's order governs". D-066 stays the standing run log. PLAN's current stage is Phase 8.1, with D-072 and D-073 research running in parallel (Egerton gates, Fontana).

**Canonical source.** `.inventory/registers/DECISIONS.md:79` (D-072), with `:80` (D-073).

**Accesses:**
- (Reused: the DECISIONS grep from Q4 and the PLAN stage line from Q9.)

Opens 0 (2 reused). Steps 0. Confidence: **likely**.

## Q11. Where does a new learning go, and how is its id allocated without collisions?

**Answer.**
- **Where:** one row in `.inventory/registers/LEARNINGS.md`, with columns id, belief, result, evidence, change and date, and an entry in the theme index at the top. TRIANGULATION.md gives each kind of item one home: numbers go to CLAIMS.md and findings to FINDINGS-GRAPH.yaml.
- **Id allocation:** **D-054** (2026-10-18 00:55) split the ranges. The lead session voynich-08 uses c-396–c-499, L-153–L-299 and O-053–O-099. Other sessions (Argon) use c-500+, L-300+ and O-100+. L-203 states the rule: "Claim an id band or prefix before writing; external labs are namespaced" (Daybreak runs are `db-sNN`).
- **Caveat:** recent lead rows (L-347 to L-361) sit in the L-300+ band. I found no newer allocation rule, so the band split appears to be no longer followed (unverified).

**Canonical source.** `.inventory/registers/DECISIONS.md:60` (D-054), `.inventory/registers/LEARNINGS.md:246` (L-203) and `workflow/TRIANGULATION.md` (the "Where things live" table).

**Accesses:**
1. LEARNINGS lines 1–20, plus grep allocate, next id, collide or reserve in LEARNINGS, TRIANGULATION and the registers README. **open**
2. LEARNINGS line 246 (L-203), grep "id band" in the registers, TEAM-HANDOFF and TRIANGULATION, and the LEARNINGS tail. **open**
3. Grep D-054 and D-064 in DECISIONS; TRIANGULATION lines 1–12. **open**

Opens 3. Steps 3. Confidence: **likely**.

## Q12. Published plant identifications for f2r, and their proposers

**Answer.** The genus is Centaurea; the usual identification is cornflower.

| Proposer | Identification |
|---|---|
| Bax 2014 | genus Centaurea |
| Velinska 2013, as reported by Bax | genus Centaurea (unverified) |
| Dana Scott, tabulated by J. Bunn | Cornflower / *Centaurea cyanus* (unverified) |
| Ethel L. Voynich notebook | "Cyanus?" |
| Sherwood & Sherwood 2008 | Diffuse knapweed (*Centaurea diffusa*); alternative: spotted knapweed (*C. biebersteinii*) |
| Th. Petersen's 1930s hand transcription | "Cyanus silvestris (O'Neill), Centauria (Holm)", that is, O'Neill and Holm |
| Petersen, via Stolfi | "cyanus segetum, cornflower (caeruleus)", Petersen plant number 2 |
| Stolfi | *Centaurea cyanus*, with doubts: the colour is red, not blue, and the leaves are wrong |
| Zandbergen 2025 | "ELV: cyanus(?); ThP: cyanus silvestris (O'Neill), Centauria (Holm)" |

**Canonical source.** VKB `page_facts` for f2r: `data/external/page-facts/plants/facts.tsv:13-19` and `data/external/page-facts/catalogues/facts.tsv:86`, `:5359` and `:5386-5390`.

**Accesses:**
1. VKB query: `page_facts` where folio='f2r'. **open**

Opens 1. Steps 1. Confidence: **certain**.

## Q13. Evidence that the sheet is a production batch (F-51), and has it been independently replicated?

**Answer.** F-51 is **CORROBORATED**, status **at-risk** (it rests on X-01).
- **Main result:** s120 found that conjugate pages (the two leaves of one sheet) are closer in 43 folio word-form features than same-quire pages at the same bound distance in the same hand × section cell. p 0.0001 on ZL3b, RF1b and IT2a, over 35 sheets (`results_s120_20261018_211618.txt`, c-560).
- **Robustness:**
  - It survives removing layout features (`runs/s120/sens_20261018_211725.txt`).
  - The Table 5 conjoints audit gives the same result, including when f115r is dropped (`.inventory/runs/2026-10-18/audit-table5.md`).
- **Controls:** planted sheet 20/20, no-sheet 0/20, drift-only p 0.035 (`runs/s120/fixture_20261018_211553.txt`).
- **External agreement:** Layfield & Davis 2026 agree in direction only. Their unverified line is: conjoint vs facing p 0.000, conjoint vs same-leaf p 0.168, no hand or section control.
- **Replication:** **not yet independently replicated.** Roach **r17** (P-65, a blind replication of s120) is only briefed.

**Canonical source.** `workflow/FINDINGS-GRAPH.yaml` (F-51 block), `results_s120_20261018_211618.txt` and graph `:1347` (P-65).

**Accesses:**
1. awk the F-51 block in the graph. **open**
- (Reused: the map row for F-51 from Q7 and P-65 from Q9.)

Opens 1. Steps 1. Confidence: **certain**.

## Q14. Which VKB version did s125 freeze, and how do you verify its stub today?

**Answer.**
- **Version:** the stub `s125_label_topic_gate.prereg.sha256` (repo root, frozen Mon Oct 19 00:29:16 PDT 2026) hashes `data/vkb/vkb.sqlite` as `4ed3497cfd73f0acf5b4bd2c222ebc40f91de961e316996fabed79895a2aaff5`. That is the VKB build of 2026-10-19 00:10.
- **Why the plain check fails:** the live `vkb.sqlite` has been rebuilt since. Running `grep -v "^#" s125_label_topic_gate.prereg.sha256 | tr -d '\r' | sha256sum -c -` gives 6/7 OK, with `data/vkb/vkb.sqlite: FAILED`.
- **How to verify:** check that line against the preserved copy `data/vkb/vkb.orig-4ed349.sqlite`. I computed its sha256 as `4ed3497c…aaff5`, which matches. The lead made the copy from the rotating backup `vkb.sqlite.20261019-004344.previous` at 09:32 (L-360).
- **Convention:** this is the `<stem>.orig-<hash6>` convention that `tools/vkb/evidence.py` accepts (D-071).

**Canonical source.** `s125_label_topic_gate.prereg.sha256` and `.inventory/registers/LEARNINGS.md:317` (L-360), with D-071 at `DECISIONS.md:77`.

**Accesses:**
1. Grep the L-360 row in LEARNINGS; ls `runs/s125` and the root `*s125*`. **open**
2. cat the stub at the wrong path (no content), plus sha256sum of `vkb.orig-4ed349.sqlite`. **open** (hash output)
3. ls; cat the root stub; run the sha256sum -c verify. **open**

Opens 3. Steps 3. Confidence: **certain**.

## Q15. What showed that the s128-p72 plant-name test had enough power?

**Answer.**
- **Power gate:** a planted power gate on ZL3b with decoy partners, 400 reps, gave **power(k=5 planted links) = 0.958**.
- **Real-language control:** Egerton 747 headings scored against their own chapters, 200 subsamples with pool 128 and n=18. The share of runs with p < 0.01 was 1.000, and the median ed1 MRR was 0.636, against a Voynich null q99 of 0.128 (NAME_LINK 200/200).
- **Fixture:** strong 10/10, absent 10/10.
- **Shuffle check:** shuffled Voynich gave 0/10.
- **Freeze timing:** the stub was frozen at 09:06:51, before the results were written at 09:07:23 (6/6 OK).
- **Call:** NO_LINK, ZL3b p 0.72.

**Canonical source.** `results_s128_20261019T090659.txt:15` (control), `:18` (POWER GATE) and `:67` (CALL), with c-590 at `.inventory/registers/CLAIMS.md:652`.

**Accesses:**
1. Grep c-590 in CLAIMS, L-359 in LEARNINGS, and power, CALL or Egerton in the results file. **open**

Opens 1. Steps 1. Confidence: **certain**.

## Q16. Which multispectral (MSI) images does the project hold, and where?

**Answer.** The MSI source is Lazarus Project / RIT 2014, released by Davis in 2024, covering 10 folios. The project holds **3** of them:
- **f1r:** 38 bands, 3.81 GB, in `data/msi/f1r`, with `data/msi/README.md` and `SOURCE_LISTING.tsv`.
- **f17r:** 38 bands, at `<local-path>`.
- **f116v:** 46 bands plus a PSC TIFF, at `<local-path>`. The D: folder holds 85 files, 8.5 GB, with `MANIFEST.sha256`.

The other seven released folios (8r, 26r, 47r, 70v1, 71r, 93r, 102v1) are not held. The source status is PARTIAL. There is no formal licence; credit the Lazarus Project and RIT, local use only. First look (O-069): erased f1r marginal alphabets are most visible in UV fluorescence.

VKB inconsistency: the `folios.msi` column flags only one folio, so f17r and f116v are not flagged.

**Canonical source.** VKB `sources` row `image-multispectral-imaging-lazarus-project-rit-2014-…`, whose src is `.inventory/runs/2026-10-18/audit-completeness_gap.md:45,140`, and `.inventory/registers/OPEN.md:75` (O-069).

**Accesses:**
1. VKB query: `sources` like multispectral or MSI, plus `sum(folios.msi)`. **open**
2. VKB `gap_note` and src; ls `data/msi` and `<local-path>`; grep O-069 in OPEN.md. **open**

Opens 2. Steps 2. Confidence: **certain**.

## Q17. Which decision governs whether a new structural run may start?

**Answer.** **D-073** (2026-10-19 00:52, approved by Jon): "Stop new structural compute: generators, global similarity scores, segmentation variants, speculative language searches … Any new run in these classes needs Jon's explicit approval."
- **D-072** sets the governing order and parks new producer families, sweeps, segmenter variants and descriptive expansions unless one of its three gates needs them.
- s122 was allowed to finish, and s124 was allowed to finish unchanged.

**Canonical source.** `.inventory/registers/DECISIONS.md:80` (D-073), with `:79` (D-072).

**Accesses:**
- (Reused: the DECISIONS grep from Q4.)

Opens 0 (1 reused). Steps 0. Confidence: **likely**. D-072 or D-073 could each be called "the" governing row, and D-073 defers to D-072's order.

## Q18. Which scribe (Davis 2020) wrote the pages of quire 13?

**Answer.**
- **Quire 13:** quire **M** in the A–T letter sequence, where M is the 13th letter. It holds f75–f84 (biological), with f74 missing.
- **Scribe:** all 20 pages are **Davis hand 2**.
- **Hand source:** the VKB `hand_davis` column comes from the ZL3b `$H` page headers. The VKB README calls this column "hand_davis".

**Canonical source.** VKB `folios.hand_davis`, whose src is `data/ZL3b-n.txt`, the `$H` page variables.

**Accesses:**
1. VKB query: `folios` grouped by quire and hand_davis, plus the `quires` table. **open**

Opens 1. Steps 1. Confidence: **certain**. I did not open the Davis 2020 paper itself.

## Q19. What did the Egerton Ventura held-out identity rule score against its threshold?

**Answer.**
- **Score:** n=35; first-word 0.686, normalised 0.743.
- **Thresholds:** frozen at 90% (first word) and 85% (normalised). The call is **BELOW_THRESHOLDS**.
- **Run details:**
  - Run by Grok Bot about 01:40 PDT on 2026-10-19, once, captions only.
  - The rule `.py` and `.prereg` were unchanged.
  - All 15 INCIPIT-RULE rows were scored as captioned, 3 ambiguous rows and 1 absent row were excluded, and row 4 was dropped by the tokenizer.
- **Misses:** 9 rows. The rule has visible defects: it does not handle macrons, final -z or -ō.
- **Filing:** not filed in CLAIMS, LEARNINGS or the graph. The note says "no gate passed; lead rules".

**Canonical source.** `data/egerton_ventura_rule/egerton_ventura_identity_rule_v1_heldout_result.txt:10-11`, with the note `data/egerton_ventura_rule/<team-comms>`.

**Accesses:**
1. Grep -i ventura in CLAIMS, LEARNINGS, OPEN, the graph and TEAM-HANDOFF (only the s128 claim line). **open**
2. ls `runs/s128`; `grep -l` "identity rule" in the repo and the Daybreak lab. Paths only; not an open.
3. Grep held-out in the s128 results and Egerton in the Daybreak results. No output; not an open.
4. `grep -l` ventura over the repo and codex_lab. Paths only; not an open.
5. ls `data/egerton_ventura_rule`; cat the RESULT note. **open**
6. Grep the CALL line in the result txt; grep its filing in the registers and graph (none). **open**

Opens 3. Steps 6. Confidence: **certain**.

## Q20. Which pharma-herbal pairs were eye-checked as "same", and where are their crops?

**Answer.** **7 pairs** were judged "same". Overall the eye verdicts are: same 7, plausible 22, doubtful 9, different 1, across 39 distinct pairs.

| Pair | Pharma folio (fragment) | Herbal folio |
|---|---|---|
| P02 | f102r1 (#203) | f37v |
| P03 | f102r2 (#205) | f47v |
| P04 | f102r2 (#206) | f32v |
| P05 | f102r2 (#212), label "koldarod" | f18v |
| P06 | f102r2 (#213), label "odalydary" | f23r |
| P10 | f89v2 (#61), label unclear | f48r |
| P26 | f99r (#94), label "tolsasy" | f96v |

- **Crops:** `data/external/page-facts/eyecheck/crops/`, 78 files, for example `P02_pharma_f102r1_203.jpg`. Each file's source scan box is in the `crop_paths` column.
- **Status:** this was one agent's eye-check (lead agent, 2026-10-19) and is not replicated.
- **Use:** these pairs feed s128-p72, whose primary pairs are those with verdict same or plausible and label likely.

**Canonical source.** `data/external/page-facts/eyecheck/pairs.tsv` (column `eye_verdict`), with `data/external/page-facts/eyecheck/README.md`.

**Accesses:**
1. ls `runs/s128/p72`. Paths only; not an open.
2. Inspect the keys of the p72 pairs JSON; grep crop, eye or pairs in `tools/s128_p72_label_partner.py`. **open**
3. ls the eyecheck folder; header of `pairs.tsv`; awk the rows with verdict same. **open**
4. Count verdicts; ls the crops count; head of the eyecheck README. **open**

Opens 3. Steps 4. Confidence: **certain**.

---

## Summary table

| Q# | opens | steps | confidence |
|---|---|---|---|
| 1 | 7 | 8 | likely |
| 2 | 1 | 1 | certain |
| 3 | 1 | 1 | likely |
| 4 | 1 | 1 | certain |
| 5 | 3 | 4 | likely (file) / unsure (conclusion) |
| 6 | 4 | 4 | unsure |
| 7 | 3 | 3 | certain (status) / likely (latest) |
| 8 | 2 | 2 | certain |
| 9 | 4 | 4 | likely |
| 10 | 0 | 0 | likely |
| 11 | 3 | 3 | likely |
| 12 | 1 | 1 | certain |
| 13 | 1 | 1 | certain |
| 14 | 3 | 3 | certain |
| 15 | 1 | 1 | certain |
| 16 | 2 | 2 | certain |
| 17 | 0 | 0 | likely |
| 18 | 1 | 1 | certain |
| 19 | 3 | 6 | certain |
| 20 | 3 | 4 | certain |

**Totals**
- Per-question accesses: 44 opens and 50 steps. Questions 10 and 17 used only content reused from earlier questions.
- Setup: 2 opens and 3 steps.
- Grand total: 46 opens and 53 steps. This excludes the clock read, the write of this file and the hand-off.

**Median opens per question:** 2. Sorted: 0, 0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 7.

**Confidence counts:** certain 11 (counting Q7 as certain), likely 7, unsure 1 (Q6), split 1 (Q5).

**Questions with no answer found:** none fully. Two have weak answers:
- **Q6:** there is no canonical list of unfiled Daybreak output, so my answer is a derived filename and id cross-check.
- **Q5:** I found no project conclusion from Parisel 2025; the absence itself is unverified beyond the files I searched.

**Hardest questions, by opens and steps:**
1. Q1: 7 opens and 8 steps. There is no folio-to-finding link table.
2. Q19: 6 steps. The result sits outside the registers, in `data/egerton_ventura_rule/`.
3. Q6: no canonical source.
4. Q9: pending status is split across the graph, PLAN and TEAM-HANDOFF.
5. Q5: the paper is easy to confuse with Parisel 2026, and the file is held as a PDF only.

**Gaps noticed while answering:**
- VKB `folios.msi` flags 1 folio, but 3 are held.
- Graph P-52 (r14 briefed) conflicts with the PLAN log saying r14 and r15 were withdrawn.
- The D-054 L-id bands are not followed by recent lead rows.
- The Egerton Ventura result is unfiled.
- Ten Daybreak runs from 2026-10-18 have no filing.
