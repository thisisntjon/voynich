> **Snapshot of 2026-10-19.** The research is paused and this is a handover copy. Status lines, queues, assignments and "next" actions below describe the team at that moment and are historical. Start at the repository's `README.md`.

# Voynich top-10 leads and pursuit program — Plan (living document)

Format: phased-investigation-workflow (`/phased`). Triage depth: **Deep** — high uncertainty, a century of false positives, and the next round is where the expensive compute (GPU key search, multi-session agent time) gets spent; being wrong about the ranking wastes it.
Current stage: D-072 bridges parked (Fontana c-625 HOLD; Egerton s133 PROCESS_INVALID, identity route infeasible; D-084). D-079(f) pivot review: reviewer proposal D-084(d) is with Astra (execution owner). Win definition: D-081(e). Entry point: FINDINGS-MAP section 0. (2026-10-19 12:53)
Last updated: 2026-10-19 12:53 PDT

## Problem

**Problem:** After ~90 filed tests across four sessions today (`.inventory/INDEX.md`), the project has no key, no family verdict, and 41 open questions (`.inventory/registers/OPEN.md`). The strongest signals kept dying within hours (word order → n2, page MI → n3, type budget → k4, column copying → m1). Effort is dispersed: three sessions pick tests by local momentum, and no ranked list says which leads are worth the next round and in what order.
**Why now:** The inventory and red team are fresh (18:53); the next round is the first that would commit GPU time and a joint-producer build. Without a ranking, the likely outcome is another day of locally interesting tests that do not move the Tier-1/2/3 ladder in `PLAN.md §0`.
**Original hypothesis (Jon, verbatim):** "based on our organized learnings, findings, testing what are our top 10 biggest leads and what is the best way to pursue them all and why"

## Goal

A ranked list of the ten leads most likely to produce a Tier-1 (reading), Tier-2 (family killed or favoured by a pre-registered margin) or Tier-3 (new hard constraint) result, each tied to its evidence rows, its refuter, and its cost; and a pursuit program that orders them by dependency and risk, runs the independent ones in parallel across the live sessions, pre-registers each before it runs, and stops a lead the moment its refuter fires. The end state is a round plan that any session can execute from this file and the inventory alone.

## Success criteria (checkable)

Revised 2026-10-17 19:36 after the investigation (SYNTHESIS.md). Removed: "ten leads listed" (old criterion 1) and "at least three leads can reach Tier-2" (old criterion 6): the hypothesis of a ten-item list was killed; the deliverable is a dependency-ordered sequence whose early steps are Tier-3 controls.

1. Every step of the sequence names the LEARNINGS/OPEN/REDTEAM ids it rests on, the single result that would refute or retire it, its best-case Tier, and a cost (low/medium/high).
2. Every step is traceable to result files via CLAIMS ids; no step rests on a STALE, UNSUPPORTED or withdrawn row (the p1 Part D interval, the m1 single-seed P and the c1 hand-2 negative are withdrawn as evidence).
3. The program states, for each step, what it depends on and what can run in parallel across the live sessions; nothing is scheduled before its blocker, and no two board-scale or NMF jobs run at once (E-dependencies cap).
4. Each step has a pre-registration stub (metric, threshold, kill rule, output path, prefix) frozen with a sha256 before it runs; one script, one output path.
5. An adversarial review (separate agent) has signed off on the roadmap or its objections are recorded in the registry.
6. Each of U1, U2, U3 is retired (verified or invalidated with a dated result file) before any Tier-2 entrant is built; a Tier-2 verdict, if reached, is scored once on the frozen v2 (or a dated amendment) on all/A/B with a stated margin.
7. Reporting uses a per-round multiplicity correction; negatives are filed with a power statement.

## Assumption registry

- Assumption: the organized learnings contain roughly ten leads that, pursued in a planned order, can move the manuscript question past "not deciphered" (Tier-2 or better).
  Source: Jon's hypothesis
  Status: invalidated (2026-10-17 19:33, SYNTHESIS.md: four of six angles find three upstream unknowns U1–U3 that no listed lead retires; replaced by a six-step sequence)
  | Affects: Phases 1–4
- Assumption: U1 — the line-edge profile (JSDf 0.176) and m5 anatomy are properties of the text, not generic scribal layout habits.
  Source: inferred; no real-manuscript prose line control exists (every L control is pseudo-lined; real-line numbers on disk are verse 0.034 and print 0.0026)
  Status: verified (2026-10-17 20:37, results_s18.txt: U1 HOLDS by the pre-registered rule; pooled 15th-c. Latin prose excess +0.008 vs Voynich +0.173 at matched size; guard, leave-one-out, _marks sensitivity and re-wrap agree; s17 on v2: max language/gibberish excess 0.091). Caveat carried: verse/formulaic Latin at 114–201 lines reaches +0.10–0.14 (O-047)
  | Affects: Phase 1 (retires it); Phases 2 (v2.1 bands), 3, 4 rest on it
- Assumption: U2 — the +0.18-bit cross-space coupling is word ordering, not line position, and a producer handed Voynich's own edge table has shown something by reaching it. (n6-ab 19:48: the coupling is a Currier-B property; A sits inside the natural-language range on it.)
  Source: inferred; Feaster 2022 shows a positional confound in the Smith–Ponzi anomalies; within-line shuffle null also destroys position
  Status: split (2026-10-17 20:05, results_s2_u123_controls.txt, peer, pre-registered): first half VERIFIED — 102.7–102.9 % of the MI excess survives a (hand, section, slot) stratified null on three transliterations; second half INVALIDATED — an edge table fitted on A, on B, on 166 train pages, or rank-mapped from Dante all generate ≥ +0.15, so a producer handed a table reaching the coupling is mechanical. s20 (20:50, results_s20.txt): the coupling anomaly is a Currier-B property; A sits inside the real-line language range on all three transliterations. U2 fully retired
  | Affects: Phase 2 s20 (retires it); Phase 3 entrants; any "coupling reached" claim
- Assumption: U3 — h2 2.1 (score.py estimator, 25k cap; four filed variants 2.093–2.397), ~7k types and hapax 0.68 are properties of the text rather than of EVA segmentation.
  Source: m7/p2 show h2 2.397 (glyph+) and 2.540 (GC2a); v2 §2 calls the band alphabet-specific
  Status: verified as a table (2026-10-17 20:51, s2 3A, p2, s30 2A–2B, s15): h2 and types are unit-specific (2.10 EVA to 2.51 GC2a; 4.5k–8.4k types under boundary variants) while the edge profile and coupling are unit-stable. No o1 ink stream exists (O-048)
  | Affects: Phase 2 s22 (retires it); v2.1 bands; Phase 3
- Assumption: the inventory registers are complete and current enough to rank from.
  Source: inventory run 18:53
  Status: holding (p1 overwrite repaired 19:24; n4/n5 rows filed 19:33; j4/p2 (peer) and q1/Q_RESULTS.md/TOP10-LEADS.md (muse wonder (helper agent; self-identified 20:02 via Jon's paste), 19:25) are not yet in the manifest)
  | Affects: Phase 2 s23 bookkeeping (verifies it)
- Assumption: the two-family framing (encoded language vs content-free generation) is adequate for ranking leads.
  Source: PLAN.md §6; contested by REDTEAM #6; B-prior-art adds a period-plausible third shape (homophonic + nulls + names list)
  Status: invalidated as adequate (2026-10-18 02:38): framings beyond the two families were tested and failed (s24, s34, s37, s51, s64); the measured slot memory (s69) points to a third shape, a word-level table procedure, which is neither plain language nor letter encipherment (synthesis §3)
  | Affects: Phase 3 s24 (checks it before the pair is fixed); Phase 5
- Assumption: ZL3b EVA with the frozen bands is an acceptable scoring basis for ranking.
  Source: PREREG v1/v2; REDTEAM #4
  Status: holding with a known defect (bands derived from the target; h2/sd_len alphabet-specific) — v2 frozen 19:27 keeps m4 family ranges; amendment expected after step 3
  | Affects: Phases 1–3 (amended in Phase 2)
- Assumption: the peer sessions' pre-registered n1–n5 and p1 results are sound as filed.
  Source: results_n1–n5.txt, results_p1_bifolio.txt; hashes recorded
  Status: verified by hash (2026-10-17 20:51, results_s23.txt ledger: 122/124 OK, the 2 FAILED are superseded pre-crash originals; p1_bifolio has no stub of its own, hash OK via n3b's); one reversal stands (n6 supersedes n4 on F1 and hand-1 NMI).
  | Affects: Phase 2 s23 (verifies by hash), Phase 3
- Assumption: the filed negatives (c1 hand 2, m1 columns, m6 Lc/Ls, a3/d6) are negatives.
  Source: result files as filed
  Status: invalidated for those five (2026-10-17 19:26, C-constraints power curves); refiled 2026-10-17 20:51 in results_s23.txt (c-322/c-323) and the INDEX D-list
  | Affects: Phase 2 s23; D-list entries that cite them
- Assumption: content-side signals that are "significant" at p<0.05 are evidence.
  Source: project practice
  Status: invalidated (C-constraints: 291 of 582 p-values today are <0.05); Phase 2 ledger 2026-10-17 20:51: family m=7, BH survivors none (c-324); v2.1 adopts BH + power statements
  | Affects: Phase 2 (reporting rule), Phase 3
- Assumption: compute is available for the key search tonight.
  Source: environment
  Status: invalidated for tonight (C: GPU 13.2 of 16.3 GB used by other processes; RAM 3.6 GB free); RTX 5080 remains the only GPU
  | Affects: Phase 4
- Assumption: the historical nomenclator family can reach ~7k types.
  Source: K4 construction
  Status: invalidated (B-prior-art §5, DECODE: 72 % of keys >100 entities, names-dominated; no period code near 7k); K4 is a bound, not a hypothesis
  | Affects: Phase 3 entrant choice

- Assumption: a Tier-1 reading is reachable by computation from this transcription for the leading cipher family.
  Source: phase-4 re-scope (main session 22:25)
  Status: split (2026-10-18 02:38, results_s50.txt, D-057): solver power VERIFIED on planted ciphers at all rungs (L1–L4, 6/6); family-match INVALIDATED within the tested grid (no verbose-homophonic cipher reproduces h2, A14 and Moran together). Not a statement about the manuscript's readability
  | Affects: Phase 4 (closes it); Phase 5 (no key search scheduled)
- Assumption: the picture (slot layer, line-scoped prefix memory, local cores) does not depend on our SlotSegmenter.
  Source: inferred; A21 shows rare-core statistics partly measure the segmenter
  Status: unverified — roach r3 (independent segmenter, three claims) running; boundary-aware re-score proposed for phase 5. Update 2026-10-18 12:07 PDT: AT RISK (graph X-01). r3 filed (c-414: R3b, R3c replicate; R3a sign only); s76 4/5 calls hold under Zattera (c-413); D-063 retracted the s85/s88/s92 X-01 discharges (F-34 C2B_NAIBBE False; F-39 mechanism reverses under Zattera/Seg_Affix2; s92 CALL_1 14/15). Decided by s96 (P-28)
  | Affects: Phase 5 (load-bearing for the table-family test)

- Assumption: A14, that different cores carry no sequential order, is a property of the text.
  Source: s55 f2, P4-D1 (SlotSegmenter cores)
  Status: INVALIDATED (2026-10-18 03:27, results_s80.txt c-419/c-420): at matched inventory size cores order positively (+0.045 at K=100); the full-inventory sign is negative for real languages too. Pre-registered reading: reopen letter-in-core ciphers. Pivot check below. Update 2026-10-18 12:07 PDT: the graph's X-06 (a plug-in MI excess detects core order at the inventory size used) is FLIPPED; F-26 and F-37 rest on it and are CONTESTED after D-063 (s85 C3A/C3B False). Re-test: Argon s96 (P-28), running
  | Affects: P4-D1 letter-in-core exclusion; s50 construction conflict; synthesis §1.4, §2, §3; dots 14, 15, 26

- Assumption: the table-and-grille family is the mechanism behind the prefix memory (synthesis 3).
  Source: s69 call pattern
  Status: WEAKENED (2026-10-18 03:16, results_s71.txt): weakened grille 0/15 LOQO on all three transliterations (c-415). Line-sticky Naibbe, which carries plaintext, matches the prefix-memory pattern (c-416); s81 tests it on LOQO. Update 2026-10-18 12:07 PDT: s81 filed (c-428, F-34): a line-held affix table reproduces the prefix memory on held-out quires, but sticky Naibbe predicts none of them (cores 0/15); the slot-layer table is the working model, the grille is not
  | Affects: phase 5 item 1; synthesis 3; H-05, H-14 in FINDINGS-GRAPH

- Assumption: (Phase 8) Reducing sprawl and duplication, and filling gaps, will make the knowledge base organized and complete enough to triangulate.
  Source: Jon's hypothesis
  Status: refined (2026-10-19 09:36, phase8-synthesis.md: integrity and integration fixes plus declaration/indexing, not file moves; acquisition gated by triangulation value)
  | Affects: Phase 8
- Assumption: (Phase 8) Most root files can be organized without moving them (stub-pinned paths); organization comes from declaration and indexing, not relocation.
  Source: educated guess (126 stubs pin relative paths)
  Status: verified (2026-10-19 09:36, census + stress-test: 142 stubs pin 2,454 paths; no timed question gets faster from moves)
  | Affects: Phase 8
- Assumption: (research track) A results file whose stub verifies was produced by the design frozen before the data (pre-registration holds).
  Source: prior knowledge (stub discipline, D-063..D-065)
  Status: invalidated (2026-10-19 09:57) for 18 runs: phase8-1-rerun-audit.md shows 26 results files were overwritten after the stub was re-stamped. 8 are kept (already ruled), 2 are already rejected, and 18 are post-hoc: s2 s33 s38 s51 s54 s63 s70 s72 s92, plus s35 s36 s37 s73 s74 s75 s85 s86 s88. If their lines stop counting, F-02, F-18, F-27, F-29 and F-36 (load-bearing) fall from TRIANGULATED to SINGLE, F-26 to SINGLE, and F-31 loses every verified line. D-063's premise for s85, s86, s88 and s92 was wrong: their stubs postdate the results' creation.
  | Affects: findings scoreboard (FINDINGS-GRAPH grades); Phase 8.1 step 3; D-073 research track (absorbed 2026-10-19 10:02, D-075)
- Assumption: (Phase 8) A 20-question cold-start bank measures whether the cleanup helped.
  Source: research (phase8-stress-test.md)
  Status: unverified (bank not frozen, baseline not taken)
  | Affects: Phase 8.1 (baseline), 8.5 (acceptance)
- Assumption: (Phase 8) Other sessions will honour declarations about their files.
  Source: research (phase8-stress-test.md)
  Status: invalidated (2026-10-18 Daybreak ignored the not-canonical request); mitigation: index read-only, never depend on their edits
  | Affects: Phase 8.2, 8.4
- Assumption: (Phase 8) Every stub-pinned VKB version survives as vkb.orig-<hash6>.
  Source: research (census) + lead fix
  Status: verified (2026-10-19 09:36, L-360)
  | Affects: Phase 8, every future VKB rebuild

## Baseline ranking under test (peer-reported 19:19; not yet confirmed by Jon in this session) — verdict 19:33: superseded by the SYNTHESIS.md sequence; items 1, 2 (as hypothesis), 9 dropped; 4, 5 demoted to gates; 7 done (n5); 8 promoted to step 1

The decryption session reports Jon approved this top-10 and method at 19:13. The investigation treats it as
the baseline to confirm, reorder or replace, not as settled: 1 joint anomaly as the target (edges + 0.18-bit
coupling + ~7k types / hapax 0.68 / h2 2.1); 2 K4 lossy code + rare codewords + m5 line-end draws (O-040);
3 matched edge-table generator, same budget (O-038); 4 Currier A vs B as separate systems (O-010); 5 hand-1
NMI vs 7k habit generator + bifolio null (O-039/O-041; n4); 6 gibberish as fourth family (O-031; n7); 7
generation signatures on cipher output (O-003; n5); 8 diplomatic Latin line-break control (O-014/O-026); 9
key search on a planted key, only if 2 passes (O-009/O-025); 10 physical/external checks (O-021, O-018,
O-030, O-016). Method: Phase 0 freeze v2 · Phase 1 items 4–7 · Phase 2 paired tournament 2 vs 3 with 8 as
control, fixed in advance, scored once, 3 seeds, 41 held-out pages · Phase 3 item 9, gated.

## Phasing

Vertical slices, riskiest assumption first. Phase 1 is detailed; later phases are coarse by design and will be re-planned by their own investigations.

**Prefix table (supersedes the per-lead list in E-dependencies §3; E's s1, s2, s5, s10, s15 keep their meaning, the rest of E's s-numbers are released; j, n, p, q, t1 are taken).** One script, one output path; claim the prefix in TEAM-HANDOFF.md before writing the script.

| Prefix | Phase | Experiment | E-dependencies name |
|---|---|---|---|
| s15 | 1 | within-manuscript band widths table (l1 200 splits + m7 + p2, full edge-null nrep) | E s15, unchanged |
| s17 | 1 | on-disk real-line pre-test (pooled gibberish, Nibelungenlied, Dante; RN-Top -am odds ratio) | new |
| s18 | 1 | CREMMA sidecars + v2 score | new |
| s19 | 1 | CREMMA re-wrap test (8×20, 9-word) | new |
| s20 | 2 | position-stratified coupling null + A-fitted edge table + Latin syllable table | new (replaces E s13) |
| s21 | 2 | Daybreak's within-line Moran I on real-line gibberish and CREMMA pools (reassigned 20:45; Timm's bound was done by s2 Part 2C, c-309) | new |
| s22 | 2 | fixed-unit h2/types/hapax (glyph+, v101, RF1b, o1 ink splits) | new |
| s23 | 2 | power refile (m1 ×10 seeds, c1 hand 2, m6 Lc/Ls) + hash-verify n4/n5/p1_bifolio + manifest gap check | new (absorbs E s16) |
| s1 | used | peer's `s1_v2_joint_producers.py` (joint producers on v2; 19:38) — taken, not Phase 3 | collision with E s1 |
| s2 | used | peer's `s2_u1_u2_u3_controls.py` (U1/U2/U3 pre-tests; 19:48; copies as s25/s26) — taken | collision with E s2 |
| s27 | 3 | K4 shared-codeword producer, as a bound only | was E s1 |
| s28 | 3 | matched edge-table generator, 7k budget, real-line-derived table | was E s2 |
| s10 | 3 | period-plausible cipher twin: homophonic + nulls + names list + line-end draw (O-024) | E s10, unchanged |
| s24 | 3 | family-framing check (copied-without-understanding, liturgy, conlang) | new (replaces E s11 scope) |
| s5 | 3 | joint producer, only if s2 vs s10 do not tie | E s5, unchanged |
| t1 | 4 | GPU noisy-channel key search, positive control first | E t1, unchanged |
| s30, s31 | peer | s30 Phase 2 U2/U3 deltas (20:19); s31 null-glyph entrant pre-test (20:24) — peer-owned, pre-registered, hashes OK | not in E |

### Phase 1 — Real-line control (retire U1) `[status: done 2026-10-17 20:37]`
Close-out: Produces exist (results_s15.txt + s15_ranges.json; data/controls_realline/ sidecars; results_s17.txt; data/external/cremma/ + 54 CREMMA sidecars + CREMMA_MANIFEST.md; results_s18.txt; results_s19.txt). Verifies: U1 verified; success criteria 2, 4 met for the phase (all four steps hash-frozen before running, results traced to CLAIMS c-312–c-319); criterion 6 first of three retired. Not verified, inherited by Phase 2: O-047 (verse/formulaic matched comparison); prose15 column count; the Latin h2/types rows carry no weight (abbreviations unresolved).
Phase plan: `workflow/phases/phase-1.md` (20:05; s17 is now a v2 re-score of the peer's s2 Part 1 corpora plus a real-line gibberish sidecar; CREMMA fetch is 6.95 MB plain XML at tag v0.1.2; kill rule reworded to pooled prose15 ≥5k tokens).
Intent: decide whether the line-edge profile, m5 anatomy, CHARWIN and Moran I are properties of the text or of scribal layout, using real manuscript lines instead of pseudo-lines.
- **Produces:**
  - `results_s15.txt`: the within-manuscript widths (41-page bootstrap, 200 splits, edge-null nrep 20) for every v2 metric, written to a ranges JSON that `run_v2.py --ranges` can read. C-constraints computed these but wrote no result file; nothing downstream may cite them until this exists.
  - `data/controls_realline/*.meta.json` in the `id` dialect (folio-style ids, one page per manuscript page, real lines and paragraph marks kept): `gib_pooled` (already exists), `mhg_nibelungenlied` (currently .txt only; the m4 loader re-wraps it 8×20, so a sidecar is required), `italian_dante` verse, and later the CREMMA manuscripts. A one-line check that `run_v2.py --meta` preserves line boundaries (token count per line equals the sidecar) is part of the step.
  - `results_s17.txt`: jsd_first, jsd_last, p_init, m_final, cross-coupling, position entropy, CHARWIN, Moran I on the pooled gibberish (per-writer rows reported, unweighted: ~260 tokens each), Nibelungenlied and Dante with real lines; plus RN-Top's line-final -am odds ratio reproduced on ZL3b (native vs re-lined).
  - `tools/cremma_to_meta.py` + `data/controls_realline/cremma_*.meta.json`: CREMMA Medii Aevi transcription XML only (GitHub API metadata 19:38: 242 XML files, 11.8 MB; images excluded), official HTR-United/Zenodo release, into the new folder `data/external/cremma/`, size checked first with a hard stop above 200 MB, logged in `data/external/README.md`; scripts outside that folder; parsers run with `python -I`. Per-manuscript rows flagged `prose15` when the manuscript is 15th-century single-column prose by the datapaper's table; a pooled `prose15` row is the primary decision unit.
  - `results_s18.txt`: the s17 metrics on CREMMA per manuscript and pooled, scored with `run_v2.py --meta … --family L --ranges results_s15.json`.
  - `results_s19.txt`: re-wrap test, the same CREMMA text wrapped 8×20 and 9-word, to measure how much of each metric the line template itself produces.
- **Pre-registration stub (frozen with a sha256 before s18 runs; s15 and s17 run first and may not change it):**
  - Decision statistic: jsd_first on the pooled `prose15` row (≥5k tokens required; if fewer, the pooled all-CREMMA row with a stated caveat). Secondary: jsd_last (alphabet-neutral line-final profile; Voynich 0.078–0.094 across transliterations, p2) and the s15 widths.
  - Outcomes, exhaustive on jsd_first: **below 0.10** → U1 holds: scribal prose lines do not produce Voynich's edge profile; edge bands keep full weight and the m5 target stands. **0.10 to below the s15 lower bound (0.149 provisional)** → U1 partly invalidated: the edge profile is partly layout; edge bands drop to one Tier-3 constraint and may be cited only together with the real-line comparison. **At or above the s15 lower bound, including above the upper bound** → U1 invalidated: edge bands lose weight under v2's in/out rule and "the only metric outside every family" is withdrawn.
  - "Retired" for success criterion 6 means any of the three outcomes recorded in `results_s18.txt` with the s15 ranges file hashed; Phase 3 may start under any outcome, with the edge bands weighted as that outcome says.
  - Re-wrap clause (s19): if wrapping moves jsd_first by more than the s15 width (±0.036 provisional) the real-line effect is reported as the difference, not the raw value.
  - Kill rule: CREMMA cannot be parsed into ≥3 manuscripts with ≥5k tokens each, or no `prose15` manuscript exists; then the pre-test (s17) stands alone and U1 stays unverified, recorded as such.
- **Verifies:** U1; success criteria 2, 4, 6 (first of three); O-014, O-026, O-031, O-043 (in part).
- **Cost:** low (s15, s17: from disk, one bootstrap job) + medium (s18–s19: ~12 MB download, sidecar builder, one board-scale run under the concurrency cap).
- **Depends on:** nothing. Runs in parallel with Phase 2 s20–s23.

### Phase 2 — Coupling, unit and power repair (retire U2, U3) `[status: done 2026-10-17 20:55]`
Close-out: Produces exist (results_s20.txt, results_s21.txt, results_s23.txt, s22 filed as c-325/c-326/L-113, PREREG-v2.1.md + scoreboard/PREREG-v2.1.sha256 verified). Verifies: U2 verified for both halves and the coupling located in Currier B; U3 verified as a table; the five negatives refiled; BH + power rule adopted; n-series hashes verified; success criteria 6 (second and third) and 7 met. Inherited by Phase 3: O-047 (verse matched comparison), O-048 (o1 token stream), the 1/55-floor caveat on hand-1 NMI.
Phase plan: `workflow/phases/phase-2.md`. Investigation found the peer's pre-registered s30 (20:19) already ran the A/B stratified null (both halves survive, 103–105 %) and per-alphabet widths; o1 has no token stream; Phase 2 compute is ~12 min on one CPU: s20 A/B coupling vs s15 widths and real-line ranges, s21 (reassigned) Daybreak's within-line Moran I on real-line gibberish and CREMMA, s22 filing, s23 power/hash/BH ledger with m1 x10 seeds, then PREREG-v2.1 (Currier-A rule: m_final dropped for A rows). Peer's s31 (20:24) is a Phase 3 entrant pre-test, recorded, not the scored-once run.
Re-scope after the Phase 1 investigation: s20 shrinks to a language-stratified v2 re-run (the position-stratified null and the A/B/Dante edge-table transfer are done in results_s2_u123_controls.txt Parts 2A–2B); s21 is done (Part 2C: 53,261 implied plaintext letters for a 1.528 letters/token verbose cipher; 34,857 words for a word cipher) and becomes CLAIMS rows; s22 keeps the o1 ink-split row and per-alphabet widths only. s23 and the v2.1 amendment are unchanged.
Intent: make the remaining anomalies citeable or kill them: ordering vs position for the coupling, alphabet dependence for h2/types/hapax, and the reporting rules.
- **Produces:** `results_s20.txt` position-stratified coupling null (shuffle within line-position strata), an edge table fitted on Currier A and scored on B, and a Latin syllable table; `results_s21.txt` Timm's token bound (38k tokens vs plaintext letters at 1.5–2 per token) applied to F3 and joint producers; `results_s22.txt` h2 (stated definition: 25k-token cap, all lines, the score.py estimator; the other three filed variants reported beside it), types and hapax on fixed unit inventories (glyph+, v101/GC2a, RF1b, and o1's ink-driven splits per D §4) with s15 widths; `results_s23.txt` m1 over 10 seeds to its own path, c1 hand-2 and m6 Lc/Ls refiled with power statements, sha256 verification of results_n4/n5/p1_bifolio against their prereg files, and the manifest gap list; `PREREG-v2.1.md` dated amendment, hashed, only if s15/s18/s20/s22 move a band, and in any case stating the Currier-A rule (A-derived bands, or m_final dropped for A rows, since A fails m_final in 40/40 draws) and BH reporting.
- **Verifies:** U2, U3; the "negatives are negatives", "p<0.05 is evidence" and "n1–n5/p1 sound as filed" assumptions; success criteria 6 (second and third), 7; makes O-024 buildable.
- **Cost:** low each; no GPU; one NMF-class job at a time.
- **Depends on:** nothing for s20–s23; the v2.1 amendment waits on Phase 1 (s15, s18).

### Phase 3 — Entrant pair on the amended board (Tier-2 attempt) `[status: done 2026-10-17 22:21 — tie at this design; results_s35.txt]`
Close-out: Produces exist (results_s27/s28/s10/s35.txt, runs/s27|s28|s10/, four stubs OK). Verifies: success criterion 6 Tier-2 clause NOT met (tie); the two-family framing is adequate as a board but neither mechanism reaches A5. Debt: s10 calibration floor (18k types), s28 lam at the bisection bound, m_final out after the M2 fix; pools include the held-out pages (design-provenance block). Phase 4 computational trigger not met (D-047).
Redesign 21:15: one mechanism per family (s10 letter-level cipher, s28 generator), three pre-committed predictions each (CHARWIN sign, F1, within-line Moran I; Δ with page-bootstrap interval), scored once; verdict = "registered lean" or "tie"; Tier 2 not claimed from this pair. s24 done (NOT SUPPORTED, D-046); s32 done (A1 size clause).
Change 20:05: U2b shows any skewed edge table (even rank-mapped Dante) reaches the coupling, so the Phase 3 stub must name which metrics the handed table determines (coupling, edge MI) and weight the pair only on what it does not fix (types, h2, line-edge vocabulary, CHARWIN, Moran I, F1, NMI-h1). Entrant prefixes move to s27/s28 (s1/s2 taken).
Intent: the first experiment that can favour a family by a registered margin, built only on retired unknowns.
- **Produces:** s10 a period-plausible cipher twin (homophonic alphabet + nulls + small names list + m5 line-end draw; positive control = the Zenodo workbook key on `flow_cipher_layer`); s2 a matched generator with the same real-line-derived edge table and the 7k budget; s1 K4 as a bound only; s24 family-framing check before the pair is fixed; s5 joint producer only if s2 vs s10 do not tie. Each with a prereg stub, scored once on v2.1, all/A/B under the A-rule, 3 seeds, 41 held-out pages, with CHARWIN, Moran I, the F1 held-out residual (+0.046; reopened by results_n6.txt) and hand-1 section NMI (holds against the powered 7k generator, results_n6.txt; cited with the C-constraints 1/55-floor caveat) in the target set, each conditional on the s23 hash check.
- **Verifies:** two-family framing adequacy; success criterion 6 (Tier-2 clause). Ceiling: Tier 2.
- **Depends on:** Phases 1 and 2 complete (U1–U3 retired, v2.1 hashed), and Phase 1 outcome "U1 holds" plus s20 showing the coupling survives the position-stratified null (stop rule, 20:02). Scored once; the effort stops after it regardless of outcome.
- **s24 approval (Jon, 2026-10-17 20:20 PDT, verbatim):** "Jon approves the bounded musical/hybrid notation check at s24 after current Phase 1, using fixed predictions and matched randomized/nonmusical controls with the same ordering search. Confirm its resource cap before execution. Don't interrupt the current job, create another team or expand compute. This approval does not cover other experiments or key searches." Cap stated for confirmation: one CPU process, no GPU, no paid calls, expected under 5 min, hard stop 15 min, existing edge matrices and slot tables only, outputs results_s24.txt, prefix claimed first. Fixed predictions: (1) the edge-transition matrix seriates (band-diagonal under some ordering, above matched controls); (2) coupling resets across line ends more than within lines; (3) removing the putative pitch slot leaves a small syllable inventory with language-like statistics. Controls with the same ordering search: row/column-shuffled matrices, real-line language edge tables (Latin, Nibelungenlied, Dante), generator tables (c2, N2, Timm-Schinner). Runs after Phase 1 closes.

### Phase 4 — Key search and human-input evidence (Tier-1 attempt) `[status: done 2026-10-18 02:38 — Tier 1 not reached; solver power shown on planted ciphers, no matched L4 constructible (s50); internal anchor route closed (D-053); producer route closed (D-056); synthesis: workflow/research/synthesis-2026-10-18.md]`
Re-scoped 22:25 (main session; reason: Phase 3 tied, so the old trigger below never fires, and Jon asked at 22:12 for routes to a reading). New intent: decide whether Tier 1 is reachable at all. Cheapest decisive test first: P4-D1 (core→core statistic on planted ciphers), then P4-D2 (CPU solver ladder L1–L4; this removes the GPU gate), P4-D3 (blind identifiability), P4-U1 (spaces), P4-COMP-1 (recipe/zodiac structure). A parallel human-input track covers same-plant pairs, corrections, Meister and Greshko. Proposed stop rule and details: [research/phase-4.md](research/phase-4.md).
Superseded intent (kept for history): only if Phase 3 favours the cipher twin. t1 GPU noisy-channel search with the positive control first; in parallel the human-input items (physical and archival checks: O-021, O-018, O-030, O-016) that no computation here supplies.
- **Depends on:** Phase 3 verdict; a `torch.cuda.mem_get_info` read at run time showing enough allocatable memory for t1's positive control (nvidia-smi and mem_get_info disagreed at 19:20, C §4; unverified which governs allocation).

### Phase 5 — Table family and segmenter independence (Tier-2 attempt on the measured slot memory) `[status: done 2026-10-18 12:15 — closed into Phase 6; core-layer producer arm continues as s94/6.4]`
Source: workflow/research/synthesis-2026-10-18.md §5.
- **Table-and-grille family on leave-one-quire-out: Argon's s71** (`s71_weakened_grille_and_sticky_naibbe_loqo.py`, claimed 02:3x before this plan; it also covers the sticky-table Naibbe variant). Not duplicated here. voynich-08 files it against the pre-registered rule and D-056 (fifth producer; LOQO is primary).
- **Boundary-aware segmentation of rare cores: Argon's s70** (`s70_canonical_segmentation_and_rare_cores.py`). It also repairs the s65(b) space-fitting design.
- **s76 (voynich-08): independence from our segmenter.** Re-measure the slot-layer picture under a second segmenter of a different design: Zattera's 2022 published slot model, fitted on training only. Measures: s69 M1 and the matched line reset, M7 core-to-frame dependence, A14 core order, s56 R(1). Verdict: segmenter-independent if every sign and interval call matches on all three transliterations. Distinct from Argon's s70, which repairs our own segmenter.
- **s50 follow-ups (language ID, wider L4): Argon's s72.** Not duplicated.
- **Roach r3:** independent code and segmenter for prefix order, core-dependent affixes, and word length within versus across lines. Already running.
- **s78 (voynich-08): pictures against cores, order-free.** Page-pair picture similarity (text masked) against core similarity on herbal pages, controlled for hand, quire and bifolio, with planted positive and shuffled negative controls. Started early as the first meaning-side test, on Jon's order-free directive.
- **s79 (voynich-08): reading-order audit.** Re-scores the constraints with words reversed within lines, lines reversed on each page, pages shuffled, and glyphs reversed within words, then classifies each constraint by the reading order it assumes.
- **Then, only if s76 and r3 hold:** meaning-side tests that need no anchor (synthesis §5.3).
- **State 2026-10-18 12:07 PDT (items above are all filed):** the arm moved by D-060 (cipher families, closed by D-061), D-061 (core-layer genre: s87, s89, s90 filed, F-40), D-062 (line-scoped producer: s91 filed, F-41; Argon s93 ULP93 filed, P-25) and D-063 (lead audit of s85, s86, s88, s92: F-26, F-37, F-39 CONTESTED; X-06 flipped; X-01 at risk). s95 filed (F-21 per-quire test underpowered). Running: s94 (shared lexicon + quire tilt + per-line pool, P-26) and Argon s96 (D-063 amended runs, P-28). Live list: `workflow/FINDINGS-MAP.md` §6.
- **Done when:** s70 and s71 are filed with verdicts, r3 is filed, and the map and synthesis are updated (met; superseded by the D-060/D-061/D-062 arms above). **Depends on:** nothing running. **Produces:** a Tier-2 call on the table family, and a verified-or-invalidated registry entry for segmenter dependence.

### Phase 6 — From 'how' to 'what': controls that could rescue language, then predictions only meaning could make `[status: executing — gate approved by Jon 2026-10-18 12:15 ("Approve as proposed")]`

Basis: deep investigation 2026-10-18 — workflow/research/next-steps-gaps-2026-10-18.md, next-steps-external-prediction-2026-10-18.md,
next-steps-redteam-2026-10-18.md, learnings-audit-2026-10-18.md (top-10 method lessons bind every run below); Daybreak and Sylvie
syntheses (D-064, H-16..H-18). Why: the map describes the production architecture well, but (i) H-01's exclusion rests only on
plainly written alphabetic European controls (red-team risk 1), (ii) H-14 vs H-05 at the top is fragile, and (iii) nothing yet
separates meaningful encoding from disciplined pseudotext — only an external prediction can.

- **6.0 Integrity (cheap, first).** Audit Argon's s96 (D-063 re-runs) before it moves F-26/F-37; reconcile s93 (D-064); fix the
  inventory's curate FAIL (42 dangling paths); run all of 6.1-6.4 under the learnings-audit top-10 rules (printed call filed,
  no overwrite, planted control passes first, LOQO, matched K, impl only for independent code).
- **6.1 Rescue-language controls (H-16, H-17 vs H-01).** Run real texts written the hard way through the full F-40 signature +
  s67 slot battery: heavily abbreviated Latin on real manuscript lines (CREMMA abbreviations kept), an abjad text (unvowelled
  Hebrew/Arabic), a syllabic/verbose re-spelling of Latin/Italian (each syllable a fixed multi-glyph group, line-held spelling
  variants), and a shorthand/notation sample (recipe sigla / Tironian-style). Call: any control reaching the four-part core
  signature AND >= 4/6 slot battery reopens H-01 via H-17; none doing so strengthens F-40 with an external-genre axis.
- **6.2 Separate H-14 from H-05 (E1).** Lag-2 prefix dependence conditional on the intervening prefix: line-held table predicts
  residual dependence, one-step grille predicts none; fitted s81/s71 producers as positive/negative controls. ~2-3 CPU-h.
- **6.3 First external prediction (X1).** A label's less-common core recurs in the physically nearest text lines more than in
  farther lines on the same page; label frame and common cores as negative controls; recency control. MDE rank shift
  ~0.07-0.14 on 85-170 matched labels. A pass is the first object-level referential link (against pseudotext, H-05/H-07).
- **6.4 Content vs mechanism (E2, after s94).** Do core pairs that co-occur on pages in training quires co-occur in the
  held-out quire beyond what the best line producer (s94 or successor) generates?
- **6.5 Independent replication (E3, roach).** Blind re-implementation of F-34 (line-held affix table) to give it `impl`.
- **Later (needs scan measurement first):** X2 recipe star-class prediction from the paragraph's first line (285 paragraphs,
  MDE AUC ~0.61-0.72); star classes measured by two independent automated scan classifiers with agreement reported (no human
  labelling).

Done when: 6.1 decides H-17/H-16 vs H-01 at the stated call; 6.2 moves F-14's weight to H-14 or H-05; 6.3 is filed with its
power stated; each result filed by TRIANGULATION.md and the map re-rendered.

### Phase 7 — Search the encoding space systematically; build cribs from outside the text; replicate by default `[status: approved by Jon 2026-10-18 13:07 ("yes please"); G1 frozen in D-066 (j)]`

Why: our edge over earlier work is scale with discipline (pre-registered generate-and-test, independent teams, multilingual period texts, digitized comparison corpora, GPU). Use it to rule out whole regions of (encoding x language) at once, and to get cribs that do not come from the text.

- **7.1 Encoding-space grid.** Cells = period-documented or spec-derived constructions x candidate languages (Latin, Venetian, Lombard, Tuscan, Bavarian, Alemannic; Czech, Occitan, Hebrew later). Every cell: recovery gate, then the joint profile (core signature, slot battery, length rhythm, h2, lag-2 prefix residue). Survivors must predict held-out quires and beat their shuffled-plaintext twin. G1 = s104 (D-066 (j)). Each grid is frozen before it is built; failed regions are recorded with the property that kills them.
- **7.2 Crib engine.** Expand s103 (once its recovery gate passes) to every openly licensed illustrated herbal and recipe book (s105): plant identities and caption names, zodiac months, star-marker classes (X2, Argon s100). A decipherment candidate from 7.1 must predict these cribs before they are looked at.
- **7.3 Replication by default.** No result moves the scoreboard until an independent implementation (roach) reproduces it or the lead audit passes, recorded in TRIANGULATION.md. roach r6-r8 are the first under this rule.

- **7.4 Physical evidence layer** (D-069, Jon approved): (1) leaf contact/offset/stain map from the Yale scans, reconstructing original page adjacency from physical evidence alone, then re-testing order-dependent findings; this is also the only way to separate subject from writing batch (s111 HOLD); (2) transcription-free glyph segmentation and clustering from the scans, seeded by Rozanova boxes (X-01, O-056, hands by shape); (3) Davis 2024 raw 16-bit multispectral stacks (f1r erased text; layer order on f17r, f116v; O-060). Each is frozen in D-066 with a known-answer gate before it runs.
- **7.5 One knowledge base** (D-070): data/vkb/vkb.sqlite rebuilt by `python tools/vkb/build.py` from the canonical sources; every fact a row with source and audit status; `tools/vkb/check.py` gates coverage and contradictions. Every filed result is followed by a rebuild. Done when the build passes its checker and the first relationship queries run.

Done when: G1 is decided by its frozen rule; the crib corpus has a recovery-gated match result; every load-bearing finding has an independent implementation or an explicit reason it cannot.

### Phase 8 — Knowledge consolidation: one source of truth, no duplication, gaps mapped and filled `[status: executing 8.1 — framed 2026-10-19 09:24, Jon approved via AskUserQuestion: Phase 8 in PLAN.md, triage Deep, scope = organize + gap-map + acquire]`

- **Problem (observed 2026-10-19 09:24):** 953 loose files at the repo root (536 results, 205 scripts, 37 .md; 11 GB total); 30 claims c-559..c-589 linked to no finding; 15 root .md with no declared status (findings_graph sprawl); parallel sessions colliding on ids (D-067/D-073, s127/s128) and duplicating decisions (D-072/D-073); team knowledge spread over <team-comms>, codex_lab, workflow/comms, incoming/, roach bridge.
- **Why now:** D-072/D-073 moved the project to external validation and held-out meaning; triangulation needs every fact findable once, with provenance. Duplicates and unfiled results are where wrong numbers and repeated runs come from (L-340, L-351).
- **Original hypothesis (Jon, verbatim):** "clean up this project and reduce sprawl and duplication as much as possible the goal is to make sure that our source of truth, fact findings, knowledge it organized and as complete as humanly possible (literally) we want everything so we can triangulate and solve the mystery of voynich"
- **Hard constraints:** nothing deleted (moves only, tombstoned, via curate archive/retire); no file named in any prereg stub moves (D-071, stub verification); no results file overwritten; no new synthesis/status files beyond this phase's research notes (D-058); other sessions' live work is not moved.
- **Success criteria (draft, checkable; revise after investigation):**
  1. `findings_graph.py sprawl` reports 0 unlinked claims c-300+, 0 unreferenced results, 0 undeclared root .md.
  2. A one-table canonical map (in AGENTS.md) names exactly one home per fact type (claims, learnings, decisions, open, findings, runs, page facts, external items, comms); every duplicate home is either retired with a pointer/tombstone or declared derived.
  3. A stub sweep after any move shows no new verification failures versus the pre-move sweep.
  4. Every team artefact outside the repo (<team-comms>, codex_lab, roach bridge, Grok/Argon/Muse runs) has a VKB external_items row with intake class; 0 unaudited.
  5. A gap register (OPEN rows) lists each missing source/page/section fact with acquire / cannot-acquire status, and every acquirable item is pulled into data/external and intake-classed.
  6. Run-id and register-id allocation has one rule that prevents collisions, written in AGENTS.md and TEAM-HANDOFF.
  7. Cold-start test: a fresh agent answers 10 fixed questions from AGENTS.md plus at most 3 file opens.
- **Investigation:** done 2026-10-19 09:36: workflow/research/phase8-*.md (6 angles) and phase8-synthesis.md. Verdict: REFINED.
- **Criteria revised 2026-10-19 09:39** after the investigation and the adversarial review (phase8-roadmap-review.md, verdict "ready after fixes"). Each is checked against a fixed list:
  - **C1:** `findings_graph.py sprawl` reports 0 on all three counters. A root results file counts as declared once a claim, graph line or TEAM-HANDOFF row references it.
  - **C2:** the AGENTS.md canonical map names exactly one home for each of the 13 fact kinds in phase8-source-of-truth.md.
  - **C3:** the stub sweep after any change shows no new failures against the 8.1 baseline. Stubs that pin live vkb.sqlite resolve against vkb.orig-<hash6> under the 8.1 decision.
  - **C4:** every body of work in phase8-team-external.md's inventory has an external_items row with an intake class.
  - **C5:** every item on phase8-completeness-gaps.md's acquisition list has a disposition: acquired, deferred under the stopping rule (with a reason), or not acquirable. The stopping rule: acquire only what feeds a pending test or a D-072/D-073 gate, and stop after two batches that change no grade.
  - **C6:** run and register ids follow the owner-prefix rule, and sprawl's duplicate-id check reports 0.
  - **C7:** a fresh agent that never saw the fixes answers the frozen 20-question bank with at most 3 file opens per question, and no answer takes more opens than the baseline.
  - **C8:** every item in phase8-findings-integrity.md's fix list is fixed or has a dated disposition.
- **Roadmap (direction approved by Jon 2026-10-19 09:39; revised after review; 8.1 is detailed, the rest coarse):**
  - **8.1 Baseline, pins, ids, integrity** `[status: done 2026-10-19 10:03 — approved 2026-10-19 09:41]`
    - **Step 0:** freeze the 20-question bank by hash. A fresh agent scores the baseline (file opens and steps per question) before any fix.
    - **Step 1:** take the stub sweep baseline. Write a decision row: stubs that pin the live VKB resolve against vkb.orig-<hash6>; new stubs pin a named snapshot, not live vkb.sqlite. Teach the rebuild to copy any pinned live DB to .orig first.
    - **Step 2:** id rule. Owner run-id prefixes; an atomic claim, where runs/<id>/ is created before use; duplicate-id and duplicate-title checks added to sprawl. The registers get one writer, the lead; other sessions send rows through <team-comms>.
    - **Step 3:** integrity fixes:
      - X-01 discharges corrected at the s76 graph lines (vx01 A1);
      - an audit of the 26-28 re-run-in-place and stub-newer-than-results runs, re-grading what rests on them (F-31 / c-417 first);
      - claims for F-42 and F-43;
      - P-52, P-62 and P-65 states updated, with a chase on roach r14/r17;
      - malformed DECISIONS rows fixed.
    - **Step 4:** VKB refresh. check.py FAILs when the VKB lags the registers or external_items is older than the newest team result. VKB run counts are compared before and after.
    - **Done so far 2026-10-19 09:48:**
      - Bank frozen: workflow/research/phase8-1-bank.md, sha256 0b005a3a...3920.
      - Baseline by a fresh agent (phase8-1-baseline.md): 44 opens over 20 questions, median 2. Hardest questions: Q1 folio dossier (7 opens), Q19 Egerton Ventura (unfiled; 0.743 vs 85% here against 0.686 vs 0.90 in phase8-team-external, to reconcile in 8.2), Q6 unfiled Daybreak work, Q9 pending runs (three homes disagree on r14), Q5 Parisel.
      - Stub sweep baseline: phase8-1-stubsweep.txt, 143 stubs, 110 clean under the strict command, 33 with explained failures.
    - **Phase 8.1 plan (steps 1-4):**
      - **Files touched:** DECISIONS.md (pin decision D-074), AGENTS.md and TEAM-HANDOFF.md (id rule), tools/findings_graph.py (sprawl duplicate-id and duplicate-title checks; not stub-named), tools/vkb/build.py and check.py (orig-copy guard, lag FAILs; not stub-named, checked), FINDINGS-GRAPH.yaml (X-01 discharges, F-31, F-42/F-43 claims, P-52/P-62/P-65), CLAIMS.md (F-42/F-43 rows), DECISIONS.md table repair.
      - **Verification:** stub sweep re-run shows no new failures against the baseline; findings_graph check/render/sprawl run; VKB check PASS with run count not lower than before; the X-01 line renders at-risk on the affected findings.
      - **Done when:** the 8.1 Produces list exists, C3/C6/C8 are checked off with dated lines, and the re-run-in-place audit table is written to workflow/research/phase8-1-rerun-audit.md.
      - **Roadmap deltas from 8.1 investigation:** the baseline is already near C7 (median 2 opens). The value lies in Q1 (dossier, kept in 8.4 but moved up within it), Q6/Q19 (8.2 intake) and Q9 (8.1 pending fixes). No phase removed.
    - **Produces:** the bank and baseline, the sweep baseline, the pin decision, the id rule in AGENTS.md and TEAM-HANDOFF, a fixed graph and a fresh VKB.
    - **Verifies:** the cold-start-bank assumption (baseline), the VKB-originals assumption; C3, C6, C8.
  - **8.2 Team intake** `[status: done 2026-10-19 10:19; codex_lab index carried]`
    - external_items moves out of world.py literals into a data file.
    - Every body of work in phase8-team-external.md gets a row, and its results get claims under 8.1 ids: Daybreak db-S124..S141, roach-12B audits as replication lines, Fontana GPU, Egerton Ventura, R14, Grok s128 calibration, vx01.
    - Read-only VKB indexes of codex_lab, from Codex's index per the split, and of <team-comms>
    - workflow/comms copies of <team-comms> are declared derived mirrors.
    - Check that the Codex split holds: no edits by either side in the other's tree, verified by mtime scan.
    - **Verifies:** C4; the declarations-assumption mitigation.
  - **8.3 Canonical map** `[status: done 2026-10-19 10:15]`
    - One table in AGENTS.md covering the 13 fact kinds.
    - TEAM-HANDOFF's "measurement map" wording resolved.
    - One assumption registry named.
    - **Verifies:** C2.
  - **8.4 Declare and dossier** `[status: done 2026-10-19 10:15; optional moves not done]`
    - All root .md files declared in the graph.
    - A tools/vkb dossier query that gives everything about one folio in one command.
    - page_facts duplicates flagged.
    - O-073 sent to its owner.
    - Last and optional, because it speeds no bank question: tombstoned curate moves of zero-risk clutter (unreferenced screenshots, failed VKB builds). Never results, scripts, stubs or pinned paths. VKB run count and the graph ref check are compared after the moves.
    - **Verifies:** C1, C3.
  - **8.5 Gated acquisition and acceptance** `[status: done 2026-10-19 10:29]`
    - Apply the stopping rule to each item on the acquisition list first, then acquire the items that pass: candidates are 5 transliterations into the VKB, 7 MSI folios to D:, open papers, McCrone OCR, and a VKB sources refresh.
    - A fresh agent re-scores the bank.
    - **Verifies:** C5, C7.

## Phase log

- 2026-10-19 11:44: **D-078: Sylvie's AI-advantages report adopted with lead adjustments.** D-072 is kept.
  - **Order:** Egerton first reads (Sylvie decides), then s132, then a specialized transcription tool if s132 fails (needs Jon), then image retrieval only after a bridge survives.
  - **CE retrieval pilot:** approved as CE-lane work in <local-path>, with agent reviewers only, from two model families (local 5080 or API, cap $25).
  - The lead supplies the case families.

- 2026-10-19 12:53: **D-084: both bridges parked; pivot review.** The replacement verifier REJECTED packet v3 (P43 facing-page label), so s133 is PROCESS_INVALID: preserved, not scored. Astra found the Ventura identity route infeasible. L-376: crop to the box instead of masking pages. Reviewer pivot proposal to Astra: internal referents fixed by the manuscript (zodiac 299 nymph labels, 12 signs x 30), with an order-agnostic, powered test after a published-first check, plus a power audit of the label-referent nulls (c-297 has no power check and assumes a fixed ring start).
- 2026-10-19 12:47: **D-083.** Jon (relayed by Astra) authorized a fresh replacement verifier for s133 packet v3. It replaces the unavailable original IV and supersedes D-081(d) route (i). The authorization came after the read but before any score. The replacement verifier is running under Astra. Fontana is on HOLD (Astra adopted the recommendation). H-20 confirmed untested. The f90r1 observation is added to O-072.
- 2026-10-19 12:41: **D-082.** s133 isolation ACCEPTED (CLEAN with disclosed deviations). Original IV identified (grok bot <session>) but at its weekly usage limit until 10-25, so s133 is likely held about 6 days; Astra escalates. D-079(f) pass branch corrected: no frozen Egerton transfer exists. Astra's transfer design: CHANGES REQUIRED (identity source for all boxes, name-matching rule, evaluability from labels, power-derived threshold, clustered null, frozen feature bank, independent scorer). F-20 title narrowed. O-077 records the audit-tool defects.
- 2026-10-19 12:35: **s132 FAILED (c-625).** Astra scored once: L05 0.9348, L15 0.7755, ROUTE_C1=FAIL. The reviewer verified the stub and hash and reran with the same output. 10 of 14 edits fall on confusable classes the readers had flagged (L-375). Per D-079(f), Fontana stops unless Jon approves the specialised-tool route. Astra routed the IV v3 recheck to the original IV through Grok Bot/Eve (19:34Z). F-40 narrowed to its tested scope (O-075).
- 2026-10-19 12:20: **D-081 reviewer dispositions.** s132 C1a and C1b ACCEPTED for scoring (C1b reconciled with frozen PROTOCOL line 19; the reviewer's PROCESS_INVALID reading is kept on record). s133 BLOCKED ON at scoring: the IV's v3 clearance is missing (Records Correction 1 §5); it unblocks with an IV ACCEPT, or with Jon's pre-score waiver. Astra's novel-discovery target ACCEPTED as the win definition. s133 RESPONSE.csv delivered at 12:16 (sha 77c5e747) and preserved.
- 2026-10-19 12:03: **D-080 ownership split (Jon).** Astra executes and schedules; Opus reviews designs and results and keeps the canonical records. Handover sent through <team-comms>. s132 C1a is done (audit clean after review; SHEET_OK), and C1b is running. s133 dispatch manifest recorded (runs/s133/dispatch_manifest.md); its isolation review is still to be assigned by Astra.
- 2026-10-19 11:55: **Lead mandate (Jon: 'You are lead on this project FYI').** D-079: the lead lifted the Egerton Ventura-pending stop. s133 frozen (stub 58b239ef); packet hint check HINT_CLEAN (agent, as the IV is silent); fresh blind reader running. Grok's s129 recheck is filed on c-621. Grok's seven messages are acknowledged with a matching To label, and Grok is assigned as standing auditor (s131 now, s133 on filing). D-079(f) fixes the next step for each outcome, including both failing (pivot check, then one recommendation to Jon). s132 C1a is running.
- 2026-10-19 11:29: **Jon brief 11:17 (reading pilot, Egerton owner, X-01 published-first) executed.**
  - **Fontana s130:** both reading aids failed the 0.95 gate.
    - R2, enhanced crops: 0.80/0.797 (c-622).
    - R1, picture-sheet inventory: 0.936/0.915 (c-624), a close miss.
    - Stopped per protocol (L-372).
  - **Audit flaw found and fixed:** the earlier reader audits grepped empty task .output files. Redone from the real transcripts with tools/audit_reader_isolation.py (positive control passes); all readers clean (L-371; c-621 corrected).
  - **Egerton:** the first reads of rows 129-390 have no owner (O-074). Grok stopped at 128 on Jon's instruction, pending the Ventura proposal. Addendum 1 gives the choice of reader to Eve, and none has been named. Eve was asked, and Jon was asked whether the hold stands.
  - **X-01:** published-first (L-370) found published split-free cousins for 8 of 9 findings, and external lines were added to F-11/F-13/F-14 (unverified)/F-30/F-34.
    - F-15 restated split-free in s131: RESTATED x3 (c-623). X-01 is discharged for F-15. roach was asked to replicate.
    - Ungated context: Voynich words sit between free assembly and natural vocabulary (L-373).
  - Open items O-074..O-076.

- 2026-10-19 11:11: **s129 Fontana folio-1v known-answer: STEP_A_GATE=FAIL; stopped per protocol.**
  - Agreement was 0.7066 against 0.95 over 5 seeded lines (c-621).
  - Step B, the solve, was not run. The one attempt is used.
  - Isolation was clean for both readers. Recorded deviation: reader B rendered its own packet images with Python.
  - What it means: this protocol failed on this page within its budget, not agents in general. The glyphs are 25-30 px tall, there are 5 confusable pairs, and slash clusters could not be counted (L-369).
  - Both D-072 bridges are now blocked: Egerton on inputs (L-365) and Fontana on reading.
  - Next per D-077 (d): the approved X-01 restatement, starting with the published-first check.
  - Any new Fontana reading route needs Jon.

- 2026-10-19 10:42: **Confirming review (Jon brief; nothing launched). No change to D-077.**
  - A second review of the canonical record (FINDINGS-MAP section 0, D-072..D-077, L-339..L-367, latest CALLs s122-s128) reached the same single next step independently: Fontana folio-1v known-answer on Jon's go. The queue is blocked on inputs and a human go, not on ideas: Egerton first reads (18/21 rows missing, L-365), Fontana glyph reading (D-077 Step A).
  - Confirmed vs reported: accepted board = 19 findings (section 0); 32 disputed (mostly X-01-carried); F-50 now CONTESTED after r15b was filed (L-361); 54 post-hoc lines stopped counting (D-075). Nothing in the newest results is evidence of meaning.
  - Stop/defer confirmed: new picture-label tests (four power/measurement failures: s115-A0, s116, s121, s125), new generators/segmenter variants (D-072), X-01 restatement until Fontana B or its stop, s128 v5.
  - Learning filed: L-368.

- 2026-10-19 10:40: **Evidence review (Jon brief 10:38; nothing launched). Decision D-077.**
  - **Approvals:** Jon approved the Fontana transcription and the X-01 restatement (AskUserQuestion, about 10:36). Both wait for his go.
  - **Changed by the evidence:**
    - **Egerton gate is unscorable for now** (L-365). The first read is missing for 18 of 21 primary rows, and at n<=21 no score clears 0.85 or 0.90 at a 95% lower bound. The IV v3 verdict does not unblock it.
    - The canonical lead ruled the deviation (D-077 c): T1 (at least 19/21) and D-b (blank or absent rows dropped from the denominator), reported with intervals.
    - Image matching calibrates only as the mutual-top-5 graph (L-366).
    - Grok's s128 calibrations are post-hoc (c-614/c-615, L-367).
    - The 41-item intake audit was applied: external items now 13 admissible, 15 scope, 23 data-only, 5 not-admissible, 1 unaudited (IV-RESCORE-X01-A1.md not on disk).
  - **Next single step:** the Fontana folio-1v known-answer. It reuses the detected 19-line cipher block, the 1,151-character manual plaintext, alignment anchor canvas 7 = 1v, and the alphabet figure.
    - Done = two filed CALLs: transcription agreement against the 0.95 gate, and blind decode of lines 11-19.
    - Limit: one attempt, 4 h. Stop on either fail.
  - **Avoid repeating:**
    - picture-label tests on short labels (four failed power or measurement);
    - thresholds frozen without the interval achievable at the real n;
    - waiting on a gate whose inputs do not exist;
    - one-to-one assignment statistics;
    - calibrations run before their stub;
    - treating an audit PASS or a self-audit as replication or acceptance.
  - **Deferred:** X-01 restatement (after Fontana), s128 name-slot v5 (D-072 hold), new Egerton rules.

- 2026-10-19 10:29: **8.5 closed; Phase 8 closed. Lead handoff (D-076).**
  - **C7, bank re-score** by a fresh agent (workflow/research/phase8-5-rescore.md; bank hash verified):
    - opens went from 44 to 33 and the median from 2 to 1;
    - 18 complete, 2 partial (Q1 folio-to-findings, Q6 unfiled Daybreak work), 0 not found.
  - **Stale items it found, and what was done:**
    - AGENTS.md start-here now names D-072/D-075 and FINDINGS-MAP section 0.
    - TEAM-HANDOFF s111 changed from "running" to "filed".
    - The roach queue is now pending rows P-73..P-81, so the stage line agrees with the pending table.
    - The LEARNINGS header id-band rule is marked historical.
    - team_files owner is now inferred from the <team-comms> file name (Q6).
    - folio_dossier now links a folio to findings through its claims (Q1).
    - Not changed: O-069 already says "done" in its state column (scorer misread); Parisel 2025 vs 2026 (bank wording, frozen); quire letters (documented in folios.quire).
  - **C5:** every listed gap has an acquire or not-acquired status with a reason (8.5 triage above).
  - **Jon brief 10:24 ("OPUS 5.5 lead and canonical-record cleanup"):**
    - The single entry point is FINDINGS-MAP **section 0**. It is generated from a lead-edited status_board block plus lists computed from the graph: accepted 19, disputed 32, rejected 15, pending review 33, assigned 10. It also shows lanes and reply routes, and the reviews.
    - The lead identity and reply route are in TEAM-HANDOFF.
    - D-076 records the review dispositions:
      - Grok assessment: accepted.
      - Daybreak steps 1-2: accepted, 17/17 tests.
      - Banners: accepted with a correction.
      - Library P2-P5: verified as reported complete only.
    - D-076 also names the strongest finding (F-04, structural only) and the next decision (stay on the D-072 Egerton gate; the next observable is the IV verdict on blind-read-1 v3).
    - Messages to Grok and Daybreak were sent and validated.
  - **Carried:**
    - codex_lab_index.tsv from Daybreak;
    - O-073 with Grok;
    - roach r17 to r26;
    - 41 unaudited external items;
    - any new Egerton or Fontana experiment waits for Jon's approval.

- 2026-10-19 10:19: **8.2 closed (C4 checked).**
  - The intake agent wrote data/external/intake/external_items_extra.tsv: 57 rows (admissible 9, scope 6, data-only 1, unaudited 41). It also wrote claim_drafts.md: 22 drafts, each verified by opening the named file.
  - The lead filed them as c-599..c-620.
    - Two became F-49 data lines: db-S138, where the Llull table reproduces the echo direction (c-610), and R14, the Barcelona combinatory table with in-row reuse and row reset (c-613; scorer not independently rerun).
    - The other 20 are declared standalone, each with its reason:
      - the f/p bounded negatives are H-17 notes;
      - db-S125 carries an overwrite flag;
      - db-S137 is directional, so it waits for the reading-order audit and an impl run;
      - the calibrations and the roach-12B notes are filed as leg notes.
  - Learnings: L-363 (the Egerton "discrepancy" is one run measured against two thresholds; BELOW_THRESHOLDS) and L-364 (an audit PASS covers only the leg it checked).
  - O-070 updated: **neither D-072 bridge has survived its first stage**. Egerton Ventura v1 held-out is BELOW_THRESHOLDS (c-612). Fontana alignment passes, but glyph recognition fails (c-611).
  - VKB rebuilt: CHECK PASS; external_items 144 rows, all with an intake class; team_files 3,939.
  - C4 checked: every body has a row with a class, and 7 names were spot-checked.
  - The Codex split holds: the only change seen was in Grok lib01's own folder.
  - workflow/comms is declared a derived mirror in the AGENTS.md canonical map.
  - Carried: codex_lab_index.tsv has not been delivered by roach Codex. team_files loads it when it lands.

- 2026-10-19 10:15: **8.3 closed; 8.4 closed; 8.5 acquisition triage done (acceptance waits on 8.2).**
  - **8.3 (C2):** AGENTS.md now has a "Canonical map" table: one hand-edited home per fact kind, plus derived views that are never edited.
    - TEAM-HANDOFF line 1 no longer calls itself the measurement map; it is the run-id and prefix register and run log.
    - Assumption registries are named: X-ids in FINDINGS-GRAPH.yaml are manuscript assumptions; U-ids in PLAN.md are plan assumptions; there is no third.
    - D-073 is marked "[MERGED into D-072; D-072 governs]".
    - The id prefixes kept are the adopted ones (gk-, ar-), not phase8-source-of-truth §5.2's proposal (gb-, ag-).
  - **8.4 (C1, C3):**
    - sprawl reports 0 undeclared root .md files and 0 duplicate ids.
    - New tool tools/vkb/queries/folio_dossier.py gives a one-command folio dossier: structure, scans, loci per transliteration, page_facts with AGREE/DIFFER flags (the duplicate flagging), and register rows naming the folio. It is linked from the AGENTS.md map.
    - O-073 was sent to Grok/Voynich Expert (<team-comms>; validated).
    - The optional tombstoned moves were deliberately skipped: they speed no bank question, and every move risks a referenced path.
  - **8.5 acquisition under the stopping rule** (acquire only what feeds a pending test or a D-072 gate; batches of 2 or fewer; stop after two null batches). The list is phase8-completeness-gaps.md §5.
    - P1 manifest: sent to its owner (O-073).
    - P9 Egerton images: already held by the team (<team-comms> egerton747_caption_crops_fullres_grokbot_20261019.zip, data/egerton_caption_gate); the gate is blocked on reads, not images.
    - Fontana: images held by Daybreak; alignment is a team task, not an acquisition.
    - Not acquired, with reasons (none feeds a pending test or gate under D-072):
      - P2 MSI, about 33 GB: no pending test reads ink layers.
      - P3 papers and P8 history: structural comparators, which are paused by D-072.
      - P4 McCrone OCR: no pending test.
      - P5 five transliterations into loci: CD2a/FG2a/GC2a need alphabet maps, and LSI needs a ;X-locus parser; the per-transliteration segmentations would be invalid for non-EVA alphabets. Reopen when a replication needs transcriber triangulation.
      - P6 Greshko: needs a browser session; FAKE row stays flagged.
      - P7 voynich.nu figures, P10 BnF, P11 ninja: no pending test.
      - P12: not obtainable by an agent.
    - Batch 1 is therefore the zero-download VKB sources refresh.
      - world.py DISK_REFRESH: Layfield & Davis 2026 goes MISSING to HAVE (PDF on disk); Tironian goes MISSING to PARTIAL (CNT image zip).
      - check.py now WARNs when a HAVE row's path is gone.
      - Result: sources MISSING 8 to 6; VKB CHECK PASS.
      - Grades changed: none. This is null batch 1 of 2.
  - **Open in 8.5:** a fresh-agent bank re-score (C7) after 8.2 closes.

- 2026-10-19 10:08: Jon: "you have my standing approval to proceed through this" — standing approval for the Phase 8 gates (8.2-8.5); report at the end, AskUserQuestion only for pivots or anything outside the approved roadmap.
- 2026-10-19 10:03: **8.1 closed.**
  - **C3** (no new stub failures; pinned stubs resolve via vkb.orig): checked.
  - **C6** (id rule written and broadcast; sprawl reports 0 duplicate ids): checked.
  - **C8** (integrity fix list): fixed or dispositioned. Done: r15 filed, X-01 discharges, the post-hoc audit and D-075, F-42/F-43 claims c-593..c-598, pending states, DECISIONS repair. VKB rebuilt and passing.
  - **Surprises:**
    - 18 post-hoc runs (pivot above);
    - another session declared the 30 recent claims before 09:36;
    - F-42 quoted fixture values as effect sizes (corrected).
  - **Debt:**
    - 9 replications are pending on roach;
    - the IV acceptance file for vx01 A1 is missing locally.
### Pivot — 2026-10-19 10:02
Flipped: the assumption that a verifying stub means a design was frozen before its data, for 18 runs (registry entry). Decision (Jon): absorb plus roach blind replication (D-075, L-362). The 54 lines from those runs stop counting; 7 findings drop to SINGLE and F-25 to CORROBORATED. The Phase 8 roadmap is unchanged; replications are added to the research track as validation work.

- 2026-10-19 09:52: 8.1 steps 1-4 done except the re-run audit (agent running).
  - **D-074 pin rule:**
    - build.py protect_pinned() is added;
    - the s114, s125 and s128-p72 stubs verify against vkb.orig-6615aa, 4ed349 and a830e2.
  - **Id rule:**
    - written into AGENTS.md and TEAM-HANDOFF, and broadcast;
    - sprawl now checks for duplicate ids and finds 0.
  - **X-01 discharges:** withdrawn on the 8 lines that rest on segmenters vx01 A1 found inadequate (c-592).
  - **Repairs and states:**
    - DECISIONS table repaired: 9 fixes, no text lost;
    - P-52 and P-62 closed;
    - P-65 (r17) re-chased.
  - **VKB checks:**
    - check.py now FAILs when the VKB lags any register;
    - VKB rebuilt and passes, with 252 runs before and after;
    - stub sweep shows no new failures against the baseline (C3).
  - **Other session:** before 09:36, another session declared c-559..c-589 standalone and the vx01 .md files historical in the graph. sprawl now reports 0 on all counters.
- 2026-10-19 09:41: Phase 8 roadmap approved by Jon (after adversarial review, phase8-roadmap-review.md). Starting 8.1.
- 2026-10-19 09:36: Phase 8 investigation complete (6 angles). Integrity fix applied: roach r15b filed (c-591, L-361), CALL NO DRIFT, F-50 now contested. VKB originals protected (L-360).
- 2026-10-19 09:08: s128-p72 VERIFIED: CALL NO_LINK at power 0.958; F-20 gains an external line (human matches). Internal plant-name anchor closed. Run-id collision with Grok Bot s128 recorded in TEAM-HANDOFF.
- 2026-10-19 01:23: s122 VERIFIED: CALL overall C (c-588, L-356); word combinations are page-local, not table rows; tri T is p/f gallows. Structural co-occurrence line closed under D-073.
- 2026-10-19 00:52: PIVOT D-073 (Jon approved). s124 VERIFIED: weak page grouping below real herbal controls (c-587, L-354).
- 2026-10-19 00:48: PIVOT APPROVED (D-072): structural exploration has reached diminishing returns. The active meaning path is Egerton prospective transfer -> Fontana known-answer recovery -> one held-out semantic-role prediction. s124 may finish unchanged; all other new structural/generator/language/visual variants are parked unless they directly unblock one of those gates.



- 2026-10-19 00:38: s126 VERIFIED stop: NOT_MEASURABLE again (3 of 4 bifolios usable; c-580, L-350). Descriptive only: f79 green / f80 blue on the central sheet, f84r green / f84v blue. Published colour notes being pulled as the next line.
- 2026-10-19 00:32: s123 VERIFIED stop: CALL NOT_MEASURABLE (c-579, L-349); blue water missed by the frozen calibration; the split call is an artefact, not filed.
- 2026-10-19 00:30: s125 VERIFIED stop: CALL NO_CONTROL (c-578, L-348); no Voynich label overlap computed.
- 2026-10-19 00:24: LAUNCHED (Jon approved, D-066 cc): s123 water colour, s124 root groups, s125 label vocabulary (power gate first), Daybreak witness search for illustrated plant-physiology sources. New H-20 (picture programme, Taiz & Taiz 2011 verified to exist: Chronica Horticulturae 51:2).
- 2026-10-19 00:11: VERIFIED: VKB panel_images table added and rebuilt; all 227 pages/panels link to a scan (L-347); VKB CHECK PASS. Found: A1's 27 multi-panel foldout scans never joined to text/quire, so earlier image x text work excluded the foldouts.
- 2026-10-18 23:26: s122 FAILED/BLOCKED: Claude Code killed the fixture at 117/180 jobs because system memory was critically low (other processes). PARTIAL fixture (runs/s122/fixture_20261018_223828.txt, no FIXTURE_GATE line, cannot be named in a stub): near-copy never T on 30/30 (core, word, tri), table T on 28/28; content and pool not started. Unplanned: near-copy books score C in tri on 10/10, so the tri C bar may not be content-specific (note only, no call). Restart (about 75 min, deterministic) awaits Jon.
- 2026-10-19 00:55: SOURCE/STRATEGY UPDATE: D'Imperio directly supports the root-crown/stolon/sap visual precedent and Panofsky's celestial-plants-compounds programme (c-581, H-20), but this remains a subject-matter hypothesis. s125 stopped at NO_CONTROL (c-578); s123/s126 were NOT_MEASURABLE (c-579/c-580); s124 remains briefed. db-S141 accepted only for Penn/Sloane graph-rule calibration (c-586; null q99 3, maximum 5). Egerton crop/caption gates have no returns and still block graph scoring. Fontana cipher+transcription acquired (c-584) but unaligned; generic TrOCR failed one-page preflight (c-585); O-071 is the next gate.
- 2026-10-18 22:11: FAILED/BLOCKED (by frozen stop rules): s116 label-to-object power 0.36 (L-342); s121 duplicate detector precision 0.13 on real herbals (L-343). Conclusion: internal image-to-text meaning tests are unpowered for this book; meaning route = external referent (Daybreak D-066 z) or text structure (s117), O-070.
- 2026-10-18 21:17: VERIFIED: s120 SHEET_BATCH (c-560, L-339, F-51 at-risk): the bifolio sheet is a production batch, p 0.0001 on all three transliterations, survives removing layout features. FAILED at fixture and filed: s113 (G2 refit loses its planted producer, L-336), s118/s119 (L-337/338). A1b: only page type validated across models (L-335). Next: r17 blind replication; s116, s117 running.
- 2026-10-18 21:04: Big-picture review (5 lenses, L-334). DECIDED by Jon: s116 A2 label-to-object, s117 in-line co-occurrence, s118 sheet as unit, roach r16 robustness (r14/r15 withdrawn); Fontana scouted, queued. LAUNCHED: s116 prep, s117, s118, r16 request.
- 2026-10-18 20:45: VERIFIED: s115-A0 (c-559, L-330): real herbal word-picture links r 0.09-0.10, seen only 40 % of the time at Voynich size, so F-33's null says nothing about meaning; image test powered. s115-A1 labels frozen (L-328, same-model kappa). Intake audits A-D filed (L-329). Next: A1b independent labeller (gemma4), A2 design with real-herbal power check.
- 2026-10-18 20:01: DECIDED by Jon: anchor (meaning) track s115, D-066 (t). LAUNCHED: A0 real-manuscript positive control; A1 blind image categories. A2 waits for both.
- 2026-10-18 19:53: VERIFIED: s114 DRIFT_ONLY (stub 4/4, fixture PASS, c-558, L-327, F-50 at-risk): quire drift beyond hand x section in all three transliterations; mechanism constancy not supported. Next: roach blind replication of s114; intake audit of 48 external items (3 agents).
- 2026-10-18 19:44: FAILED/BLOCKED: s112 stopped at fixture (planted-batch 3/12, L-326); no real run. DECIDED by Jon: G2 redesign = envelope + signatures (new run id, fixture first); MSI on D:. LAUNCHED: G2-envelope design+fixture agent; MSI f17r/f116v download to D:.
- 2026-10-18 17:46: Results sorted (no-theater rule). FAILED/BLOCKED: G2 s110 stopped at fixture (L-323); contact map v5 all gates fail, parked (L-324, O-068); MSI only f1r (disk, O-069). PARTIAL: glyph prototype (L-325); VKB features + exploratory scan (quire effects beyond hand/section; Rw1/rhythm show no folio-level association). LAUNCHED: s112 (Jon approved).
- 2026-10-18 17:04: Parallel work plan (Jon: 'plan ahead ... you are only using one agent'). Running in parallel: G2 s110; roach r14; A 7.4.1 contact-map design+prototype (known-answer gate: Layfield & Davis links); B 7.4.2 scan-only glyph segmentation design+prototype (gate: Rozanova boxes / EVA counts on held-out pages); C 7.4.3 MSI acquisition (local, hashed); D VKB enrichment (per-folio features, intake of 48 unaudited external items, parser gaps) then an all-pairs per-folio relationship scan; E integrity O-066/O-067; F s105 unblock prep (O-062). Queued for Jon: O-064 held-out label-column test; 7.4.1/7.4.2 frozen designs after prototypes; O-063 table transcription.
- 2026-10-18 16:12: roach r13 filed (c-542, L-319): replicates s101; F-23/F-30 CONTESTED (D-068 result). Intake of outside work filed: 15 Daybreak results with scope, Argon h19 simulator not admissible (circular), Daybreak corpora copied to data/controls_daybreak/ (L-320).
- 2026-10-18 16:08: sprawl audit (repo, external, gap map) acted on: stale entry points marked, alias map extended, METHODS/TOOLS rows, fake downloads noted; teammates asked to mark non-canonical status files; intake audit of outside work running. Phase 7.4 (D-069) and 7.5 VKB (D-070) added. G2 (s110) launched.
- 2026-10-18 16:08: s111 filed HOLD (c-541, L-318): subject and quire barely cross in the book; the powered subject arm is null (no cross-quire topic vocabulary). G2 (s110) next.
- 2026-10-18 15:58: roach r12 filed (c-456, L-226): F-04 rhythm replicated independently but Kalevala metrical verse has it too; the manuscript behaves like metrically constrained composition. s109 rescoped (Daybreak pre-freeze HOLD missed; L-227: grep <team-comms> for audits before every freeze).
- 2026-10-18 15:57: s109 filed (c-455, L-225, O-064): Argon's ok-/ot- label code is word frequency (not reproduced); recurring adjacent label pairs are mostly single-glyph letter columns, a possible shared key; held-out test parked.
- 2026-10-18 15:48: Big-picture review: the evidence converges on line-by-line composition from a quire-local core stock with a one-step affix habit; the open fork is whether quire locality is subject (content) or writing batch (procedure). Jon approved s111 to decide it, before G2; frozen in D-066 (p).
### Pivot — 2026-10-18 15:43
What flipped: s101 (Argon, lead integrity audit passed; c-454, L-224) shows the LOQO criteria behind load-bearing F-23 and F-30 recover planted true producers on only 0-4/15 folds, so those exclusions are uninformative. Decision (Jon: 'Absorb (Recommended)', D-068): F-23 and F-30 to at-risk; roach r13 replicates; new TRIANGULATION power rule; roadmap unchanged (G2 s110 fixture already enforces planted recovery >= 10/15).

- 2026-10-18 15:11: s108 filed NOT ASSESSABLE (c-453, L-223, O-063): printed-table OCR 39-53% accurate against images. s109 launched.
- 2026-10-18 14:42: Jon approved G2 (s110, combinatory-table procedures, content vs random input, locality fitted directly); frozen in D-066 (o); runs after s108. Argon's Fontana mechanism, Bodleian manifest and agent-built plant concordance not adopted (contradicted or unverified).
- 2026-10-18 14:40: roach r11 filed (c-452, L-222): 11 more natural texts never repeat words in-line; Voynich itself passes only 6/15 blocks (S1). F-40 gains a data line.
- 2026-10-18 14:34: s94 stopped at its fixture after the last allowed revision (L-221): the joint fit cannot recover quire locality; no real data read. Quire locality is now the property every core generator misses (s91, s94, r10); G2 must fit it directly.
- 2026-10-18 14:31: s107 filed (c-451, L-220, F-49): CALL_RESTATE_F40 True via a 957-token Llull combinatory table only; medical tables avoid in-line repetition. F-40 rescoped; H-19 opened. s108 launched next.
- 2026-10-18 14:14: s105 HOLD at stage 1 (c-450, L-219, O-062): corpus from the outside synthesis was wrong (2 of 4 not in the alchemical-herbal family), no plant identities, Gallica refused. Parked; no re-freeze.
- 2026-10-18 14:08: Jon approved s108 (ruled medical tables, after s107) and s109 (label network, after s108); both frozen in D-066 (m), (n). s105 told to hold LJS 419 rectos out of the unrelated control (likely alchemical-herbal family per the Penn catalogue).
- 2026-10-18 14:06: roach r9 filed (c-448, L-217, F-48): page-level affix drift real but ordinary (Latin has it); drifting table fails 0/15. r10 filed (c-449, L-218): no simple core generator fits; all miss quire locality. D-067 amended to 'multi-scale state'. s104 correction: shuffled twins pass the core signature under single segmenters (c-447 note).
- 2026-10-18 13:47: s105 design frozen in D-066 (l-frozen): data gate, natural copy-pair positive control, planted part-chimeras, power bar tied to the positive-control gain. Acquisition and gates launched; Voynich scoring waits for s107.
- 2026-10-18 13:45: Daybreak audits filed: s100 kappas reproduce (scope: shared-detection visual partitions); 321 physical star entries, `<%>` incomplete (L-216, O-061); s106 HOLD reproduces, alternation 93.86%. s104 timing note added to c-447.
- 2026-10-18 13:42: s104 G1 filed (c-447, L-215, F-47): 0/18; closed within G1. Shuffled input fits the line rhythm better than real word order. G2 (procedure side) waits for roach r9/r10.
- 2026-10-18 13:38: s106 (X2) HOLD (c-446, L-214): recipe star fill alternates down the margin (17/277 deviations), so stars are layout, not an external crib. External route continues with s105 after s107.
- 2026-10-18 13:25: PIVOT approved by Jon ('Reframe to drifting state'): working affix model restated from a line-held table to a slowly drifting prefix/suffix state with short-range suffix order (roach r6, s98). H-14 stays live but narrowed; roach r9 tests the drifting table; s104 scores the r6 profile as a survivor prediction. No running work stopped.
- 2026-10-18 13:23: roach r6-r8 filed (c-442..c-444, L-212, L-213). r6 rejects the line-held affix table (0/15; no line reset, regional drift) -> F-34 CONTESTED (pivot-check: H-14's main support). r7: in-line reuse unique vs references, but the per-quire four-part conjunction is not replicated -> F-40 scoped to whole-text. r8: low recurrence is the robust cipher mismatch -> F-39 restated, no longer contested. s104 amended before freeze (D-066 j-amend). s103 guarded as INCONCLUSIVE (runs/s103/LEAD-READING.md).
- 2026-10-18 13:20: s103 filed INCONCLUSIVE (c-441, L-211): herbal matching underpowered with two herbals; s105 crib engine gated on a stronger part-level representation and a larger corpus.
- 2026-10-18 13:07: s98 filed (c-440, L-210, F-46): H-05-like, prefixes close to first-order with a weak residue; the s81 line-held table overshoots lag-2 ~3x. Phase 7 approved by Jon and written; G1 (s104) frozen in D-066 (j) with F-46 added to its spec.
- 2026-10-18 13:04: s102 filed (c-439, L-209, F-45): 0/12 period cipher x recipe-language cells; closed within tested constructions (D-066 (h)). Spec for any surviving encoding: low h2, positive length rhythm and in-line reuse must come from the encoding step.
- 2026-10-18 12:33: 6.1 s97 filed (c-438, L-207): CALL_REOPEN_H17_H16 False; 0/6 hard-way natural texts reach the core signature or slot battery; H-17 weakened (moderate), H-16 weakened (thin). A verbose re-spelling with line-held variants gives in-line reuse but loses order and locality.
- 2026-10-18 12:30: Sylvie reset reconciled (D-066): db-s98 FAILED for current scope; run-id alias map; synthesis corrections; X2 frozen as the next eligible question pending s100 kappa. Acknowledgment <team-comms> sent.
- 2026-10-18 12:25: 6.3 s99 filed (c-437, L-206, F-44): NEGATIVE, rare label cores are not nearer the physically closest body lines (n 57, MDE 0.088). External route moves to text-independent classes (s100 star markers, Argon <session>).
- 2026-10-18 12:19: 6.0: Argon s96 rejected (D-065: overwrite + thresholds set at observed values); F-26/F-37/F-39 stay CONTESTED. Inventory curate grade FAIL 57 -> PASS 100. Argon results quarantined until lead audit.
- 2026-10-18 12:15: deep next-steps investigation done (4 research files + Daybreak/Sylvie syntheses); learnings register consolidated (L-188..L-204, 26 supersession markers, theme index); docs updated; Phase 6 proposed for Jon's gate.
- 2026-10-18 12:10: D-064: Argon's s93 not admissible (frozen run DC0355 finished CALL_3 False, UNIFIED_CANDIDATE False; script edited and result overwritten); all s93 graph lines unverified. Daybreak synthesis cross-checked: F-42 (quire-local tail pool, order-symmetric) and F-43 (label-page retrieval, representation-dependent) added; db-s114 external line on F-20. Deep next-steps investigation running (gaps, external prediction, red-team, learnings audit).
- 2026-10-18 12:07 PDT: documentation pass. s93 (Argon, P-25) is filed in the graph: ULP93 pool + line-sticky affixes reports C1 14-15/15 and de-aliased C2 10-12/15 (results_s93.txt); F-09 TRIANGULATED; X-08 discharged on F-16. D-063 status carried into this plan (registry and phase 5). s94 and Argon s96 running; s96's results file is partial and unfiled.
- 2026-10-18 09:33: s95 filed (c-436, L-187): F-21's per-quire test is underpowered (R_P1 cannot separate copied from composed Latin at quire size); contested line resolved as uninformative, F-21 vs H-10 weakened to weak. D-063 audit of Argon s85-s92 applied earlier (F-26, F-37, F-39 contested). s94 running.
- 2026-10-18 09:15: s91 filed (c-435, L-185, F-41): a fitted per-line core pool reproduces in-line reuse and cross-line avoidance on 45/45 held-out quires with no copying, but the full signature on only 21/45 (too quire-local) and the slot battery on 0-1/15. Open: weak order with near-uniform quire spread. Argon s93 (pool + line-sticky affixes) running.
- 2026-10-18 06:49: s90 filed (c-434, L-184): no human writing tested (natural, list, ritual, tabular, gibberish, constructed) reuses words in-line. The core signature points to a mechanical within-line step. Next: the deferred line-scoped producer with a bias-corrected fit (s91).
- 2026-10-18 06:41: s89 arm A filed (c-433, L-183): 0/10 repetition genres match; all lack in-line reuse; Steganographia closest (3 of 4). 23 real texts in 7 genres now fail in-line reuse.
- 2026-10-18 06:02: s87 amendment filed (c-432, L-182): no reference class reproduces the core layer. Four-part core signature: weak real order, in-line reuse, cross-line avoidance, quire locality. Next s89: line-repetition genres and a weak-transition line-scoped producer on LOQO.
- 2026-10-18 06:00: s87 partly filed (c-431, L-181, F-40): no natural text (4 list, 5 prose, 4 verse) repeats words inside lines; Voynich does (1.2x). The order and generator parts are hit by a page-id defect; amendment re-run authorised to a new file (results_s87_amend1.txt).
- 2026-10-18 05:40: s83 filed (c-430, L-180, F-39): homophone letter/syllable cores under a line table fail 0/15; core order twice too strong, R(1) below 1. Phase-5 cipher arm (D-060) complete. Plain, homophonic and per-line-table ciphers with plaintext letters in the cores all fail held-out quires on the corrected statistics. Map: the slot layer has a working mechanism (line-held table, F-34); the core layer is a word-level stream with weak order and line-bounded reuse (F-12, F-13, F-06).
- 2026-10-18 05:19: s84 filed (c-429, L-179): inconclusive (controls failed 2/6). Order-free, Voynich never beats the null p95 and no language is stable. The stem solver cannot separate stem codes from letter-in-core ciphers. F-36 contested; the s73 lead does not reproduce.
- 2026-10-18 04:30: Argon s73/s74-amendment/s75 audited and linked (c-514..c-519; F-35..F-38; L-178). c-417 STALE (file overwritten). s73's word-stem verdict relabelled: Voynich stems align +35..+82 bits above null (intermediate, a lead for H-06); s84 proposed to re-run it order-free on LOQO.
- 2026-10-18 04:27: s81 filed (c-428, L-177, F-34): the sticky Naibbe cipher predicts 0/15 held-out quires, but its line-held table reproduces the prefix-memory pattern out of sample (13-15/15). The slot layer now has a working mechanism; the core side is the open part. s83 tests homophone cores under that table.
- 2026-10-18 04:00: s82 filed (c-427, L-175): plain cipher families reach the weak core order (25 + 25) but none matches jointly; h2, rhythm and prefix memory fail. Roach r5 filed (c-425, c-426, L-176): core held-out order and within-line repetition independently replicated; 'affixes carry none' withdrawn. s83 (homophone cores + line table) is the direct test of the three missing ingredients.
- 2026-10-18 03:36: s78 filed (c-424, L-174, F-33): inconclusive by rule (C+ 17/20 vs 18); no core-picture link at MDE r ~0.23; frames associate (style). Meaning stays open; a powered version is parked behind the cipher work (D-060).
### Pivot — 2026-10-18 03:28

- **What flipped:** A14 (cores carry no sequential order). s80 shows weak positive order at matched inventory size (+0.045 at K=100). It is below every language and below all 12 planted letter-in-core ciphers at K=100-200, but inside their range at K=50. The full-inventory statistic reads negative even for Dante (c-419, c-420).
- **What falls with it:**
  - P4-D1's exclusion of letter-in-core ciphers (reopened).
  - s50's construction conflict, whose core-order target was the biased statistic (F-25 at risk).
  - s49/s55's 'outside both families on core order' (F-26 at risk).
  - The synthesis 3 inference 'word-level, not letter-level'.
- **Options considered:** absorb; re-plan phase 5 around cipher families; open decipherment now; return to investigation.
- **Decided:** re-plan phase 5 around cipher families (Jon approved, D-060).
- **What changes:** phase 5 items become
  - (a) s82, re-scoring the s50 and P4-D1 families against the corrected profile;
  - (b) s83, homophonic letter- or syllable-in-core ciphers with a per-line affix table, fitted and scored on LOQO;
  - (c) the solver on the manuscript, gated on a construction that matches.
  s78 (pictures) and s81 (sticky table) continue unchanged.

- 2026-10-18 03:27: s80 filed (c-419, c-420, L-172, dot 30): A14 INVALIDATED; pivot check started (execution frozen except running s78/s81). s79 filed (c-421, L-173, dot 31): only page drift needs bound page order. s70 partly filed (c-422, c-423).
- 2026-10-18 03:19: roach r4 filed (c-418, L-170, dot 29). Pre-registered outcome 'controls failed' (negative control biased up to +0.03). Core order near 0 at matched K, far below letter-in-core ciphers (call ii YES). A14 restated in the graph: weak, not 'below shuffle'. P4-D1's exclusion holds on the relative gap. F-12 stays at-risk until s80 resolves the s76 disagreement. No pivot: the dependent conclusion (letter-in-core disfavoured) survives.
- 2026-10-18 03:16: Findings graph and triangulation gate adopted (D-058; workflow/FINDINGS-GRAPH.yaml, FINDINGS-MAP.md, TRIANGULATION.md, tools/findings_graph.py). Sprawl: 0 unlinked recent claims, 0 orphan results, 0 undeclared root docs. Argon s71/s74 filed (c-415-c-417, L-168, D-059); s75 not filed (stub fails), s70 held for fixes. Map's top-weighted live family is now a per-line table cipher (H-14); s81 claimed to test it on LOQO; roach r5 proposed for the impl gaps on F-06/F-13.
- 2026-10-18 02:59: roach r3 filed (c-414, L-167, dot 28): R3b and R3c replicate; R3a sign replicates below the 0.05 bar. s80 size-matched A14 launched. Roach briefed for r4 (blind A14 at matched inventory).
- 2026-10-18 02:58: s76 partly dependent: 4/5 calls hold under Zattera's segmenter; A14 flips positive on all three (c-413, L-166, dot 27). A14 marked AT RISK in map and registry; s80 size-matched A14 test claimed. Pivot-check deferred until s80 decides (not yet a confirmed flip).
- 2026-10-18 02:51: Jon: assume no known reading order (choose-your-own-adventure or backwards). s78 (picture-core similarity, order-free) and s79 (reading-order audit of all constraints) claimed and launched. Steward R3 author-label receipt published.
- 2026-10-18 02:39: Phase 5 gate approved by Jon ("Approve as proposed"). Prefix check found Argon had claimed s70-s75 at 02:31-02:34 covering two of the three items, so voynich-08 runs only s76 and files Argon's s70/s71/s72 (2026-10-18 02:41).
- 2026-10-18 02:38: **Phase 4 closed.** Tier 1 not reached. vs plan: the GPU key search never ran, because the CPU solver ladder answered first. It found solver power is not the limit; no cipher of the leading family can be built to match. Surprises: the anchor route closed on the text side (D-053); four producers failed held-out prediction (D-056 stop); s69 located a line-scoped one-word prefix memory that only table-and-grille mechanisms show. Debt: segmenter dependence (A21), held-out split reuse (D-056), s50 language ID untested. Synthesis: workflow/research/synthesis-2026-10-18.md. Next: phase 5 gate.
- 2026-10-18 02:27: s50 solver ladder: L1-L4 pass 6/6 on planted controls; no matched L4 in the 81-point grid (h2 floor 2.167 vs 2.10; h2/A14 conflict), evidence against the verbose-homophonic family as built (c-411/c-412, L-164, dot 26, D-057 wording). Argon s60/s63 added as A20/A21 (Argon's A23/A24; L-165 caveat on boundary-bleed controls). s50 wording corrected per Sylvie (D-057); her ack seen and confirmed in <team-comms>; roach voynich-91 answered with the r3 brief.
- 2026-10-18 02:19: s69 prefix-stream memory: one-word memory on top of the core, resets at line breaks, not at gallows; only Rugg grille reference shows prefix order (c-410, L-163, dot 25). Amendment 1 after failed run 1 (count TypeError).
- 2026-10-18 02:13: comms: registration <team-comms> (correlation <team-comms>) delivered to the shared <team-comms> folder by Jon's own copy after two classifier denials of this session's write; copy sha256 matches the staged file (746a1d2c…). Two-way reply: none yet. Roach Claude briefed for independent replication r3 (prefix-stream order, core-dependent affixes, within- vs cross-line word length) plus copy-back of r1/r2 raw files.

- 2026-10-18 02:05: s68 Parisel switch is scribe (c-408, L-161, dot 24); s65 A1/A5 robust to drawing gaps, space fitting untested by design (c-409, L-162). Agent left an unused runs/s66/fixture.txt inside Argon's s66 folder (s66_parisel_* draft), noted in TOMBSTONES.
- 2026-10-18 01:59: s67 constrained assembly + cadence, LOQO: 0/15, 1/15, 0/15 folds (c-406/c-407, L-160, dot 23). Core-class affixes confirmed (types, CHARWIN). Prefix-stream order and quire-local vocabulary unreached by any producer. Producer route closed.
- 2026-10-18 01:48: prior art: team published-findings register read; A5 word-length within/cross-line split not found in sources; edge-coupling line-break split is published by Rozanova & Temerev 2026 (Table 4), added to map B2.
- 2026-10-18 01:47: s62 'local edit-chain' by rule but ~2 % (below Latin/Dante; herbal none) supersedes s59's tentative reading (c-404, L-158, dot 20). s64 Naibbe excluded at default settings (c-405, L-159, dot 22).
- 2026-10-18 01:38: s61 joint whole-word producer 0/6, 0/6, 1/6 held-out with types and R(d) matched (c-402/c-403, L-157, map dot 21). D-056 stop rule fires: no more producers on the 41-page split. Standing constraints: rhythm needs a non-lexical state; words are assembled from parts under tight rules.
- 2026-10-18 01:33: literature consumed (workflow/research/literature-2026-10-18.md): Parisel 2026 x2 and Steckley 2024 full; Greshko 2025 main text and Meister 1902 blocked. Changes: A15/dot 9 reworded (drawing gap = weak edge, L-156); s68 Parisel switch within hand, s64 Naibbe in s55 taxonomy, s65 drawing-gap robustness and space-fitting.
- 2026-10-18 01:28: s59 rare-core parents: pre-registered verdict inconclusive (negative control failed on RF1b; N3 null cannot separate Latin from a mutator). Within-page shuffle shows no local edit-1 parent excess (c-400/c-401, L-155, map dot 20, exploratory). s62 confirms on the 166 training pages with N1 as decision null.
- 2026-10-18 01:26: D-056 held-out reuse guard fixed before s61 reports (s61 last producer on the 41-page split; any pass must re-pass leave-one-quire-out). Literature consumption (Parisel 2026, Steckley & Steckley 2024, Greshko 2025, Meister 1902) assigned to an agent.
- 2026-10-18 01:20: s58: counted affix wrapper over local-memory cores holds 1/6 (ZL3b), 2/6 (RF1b/IT2a) held-out; no-copy twin 2/6 (c-398/c-399, L-154, map dot 19). CHARWIN sign is affix-borne; rhythm and line starts need joint, longer-state word choice. Fit set p_copy 0.02 (types +65 %). Next: s61.
- 2026-10-18 01:20: D-055: research Argon's 10 actions triaged (s59 parent chains launched; s60 reserved for Argon; archive/lab items declined). Map dot 8 wording and section C refreshed; O-045 closed by s36.
- 2026-10-18 01:12: s38 CHARWIN scale reconciled. Argon's canonical n5 re-score reproduced exactly (baseline +0.0951; physical streams +0.078..+0.188, all positive). Argon's O-048 'word half open' wording predates s47, which closed it.
- 2026-10-18 01:08: s57: local-memory copy-and-vary model fitted on 166 pages holds 0/6 held-out predictions on ZL3b/RF1b/IT2a (null 1/6; c-396/c-397, L-153, map dot 18). Repetition belongs to the cores, order to the slot layer. Next: s58 two-layer wrapper + local-memory cores on the same held-out predictions.
- 2026-10-18 00:55: register id collision with Argon repaired (D-054: voynich-08 ids renumbered, ranges split, README rule). Argon's s52–s54 integrated as map dot 17 (no comparator structure; composition-type errors; rhythm needs length-state persistence). s50, s57 running.
- 2026-10-18 00:51: s56: no refractory zone; cores are bursty with smooth decay, rare cores most (c-382/c-383); 'cores repel' withdrawn (L-143); local memory favours candidate 1. Next: s57, fit the R(d) decay shape with a pre-registered self-citation model on training pages and predict held-out pages.
- 2026-10-18 00:42: s55: code vs generator not separable without line-edge features (c-393); Voynich outside both classes on core/prefix features (c-394, L-151, map dot 15). Next: s56 core repetition by distance.
- 2026-10-18 00:29: s49 done: binary PASS 21/24, twins FAIL 6/10, Voynich between word-code and generator, unassigned (c-390–c-392, L-150, map dot 14). Next: s55 code-vs-generator discriminant without line-edge features.
- 2026-10-18 00:25: s54: no label-text link to known herbal partners (c-389, L-149); image/label anchor route closed (D-053). s49 finishing, s50 running.
- 2026-10-18 00:18: s53: image matching has real signal (MRR P 0.0005) but fails the top-5 rule (3/13); no predictions frozen (c-388, L-148). Next: s54 pre-registered label-text test on the 13 known pairs.
- 2026-10-18 00:05: Argon s51 Parts 2–3 filed: alphabet bake-off leaves the anomalies unchanged (c-373); Currier A/B confounded with Davis hands (c-374, L-138, map dot 12).
- 2026-10-18 00:05: s52: Currier B is not verse-like (no caesura, no ending echo; c-372, L-137). s49, s50, s53 running.
- 2026-10-18 00:00: s48 (GPU same-plant image matching) FAILED its known-pair control (c-371, L-147). Next: one part-level retry (s53), then close the image-anchor route if it fails.
- 2026-10-17 23:54: s51 (mine): B coupling not separable from Priapea at matched size, A3 downgraded to a verse-like genre fingerprint (c-387, L-145). Argon's s51 Part 1: no independent superimposed stream; frame and core coupled within words (c-370, L-146). O-051, O-052 closed. Prefix collision recorded.
- 2026-10-17 23:43: s47 done: ink gaps agree with certain spaces (κ 0.87), commas intermediate, gallows pen-lifts not gaps; O-048 closed both halves (c-384–c-386, L-144, A19). s48/s49/s50 running.
- 2026-10-17 23:37: Jon set the standing goal (D-049: no human tasks, lead decides). Decisions D-050 (fan-out files stay), D-051 (register ownership), D-052 (Phase 4 gate taken: s48 GPU same-plant image matching, s49 identifiability, s50 solver ladder). s47 running.
- 2026-10-17 23:34: organisation pass (Jon: contain sprawl, keep docs current). README rewritten as the front door with reading order and house rules; 12 superseded root docs carry a pointer line (nothing moved or deleted); INDEX current state rewritten; FINDINGS-REPORT addendum 8; strategy revised after s36 (board exhausted under a shared wrapper, L-130). Filed Argon's s36/s37/s38 (c-361–c-365, L-130/L-131) and the ten-theories bundle as exploratory (L-132, D-048). Next: s47 word-boundary κ test.
- 2026-10-17 23:15: s45 (GPU) done, PARTIAL (127/150 clean pages): ink line breaks reproduce the line-initial profile (P1 HOLDS, c-359); ink word gaps fail P2/P3 on the bands, consistent with segmentation noise (c-360, L-129); O-048 line half closed. Dry-run file kept as runs/s45/results_s45.dryrun-unregistered.txt.
- 2026-10-17 22:58: s43 filed (c-357, L-128): neither 'one layer is nulls' cipher reproduces the manuscript. Leads batch s39–s44 complete. s45 GPU: a dry-run scoring on 18 pages wrote results_s45.txt at 22:55 BEFORE the stub (22:56); instructed the agent to rename it as unregistered and score only the full segmentation under the frozen stub. Not filed.
- 2026-10-17 22:44: filed s39 (F1 lives in the cores), s40 (prefix stream ordered, matches neither Latin nor generators), s41 (no single suffix class carries B; coupling runs from core-final glyphs, A too), s42 (tie), and the main session's P4-D1 (cores order lexically, not alphabetically; MIXED) and P4-U1 (commas are both squeezed spaces and junctures). c-351–c-356, L-126/L-127, CONSTRAINTS-MAP dot 10. s43 and s45 still running.
- 2026-10-17 22:35: independent replication on the second machine (stopped for compute before its REPORT.md; report written here as workflow/research/replication-roach.md). R1 (A1) replicated; R2 (A3 margin) not: short Latin verse reaches Voynich B, confirmed in our own s18 per-ms files excluded by s20's 5k floor. A3 corrected; c-349/c-350, L-125, O-052. Source result files remain on the second machine.
- 2026-10-17 22:29: Jon: "lets put the gpu to good use". GPU job s45 launched: ink-derived line and word boundaries from the public Yale scans (O-048), RTX 5080 16 GB confirmed (torch cu128, CUDA available). Caps: scans into data/external/yale_scans/ (fresh dir, text/JPEG only, stop above 6 GB, logged in data/external/README.md), tooling in a scratchpad venv with system site-packages (project env untouched), segmentation is a pipeline step, the scoring step is pre-registered (s45 stub) before the ink stream is scored; outputs runs/s45/ sidecars + results_s45.txt. Nothing uploaded anywhere.
- 2026-10-17 22:43 (main session, Phase 4): P4-D1 MIXED (results_p4d1_core_order.txt). Letter- and chunk-in-core ciphers with free affixes are CLEAR of A14 in 12/12 cells (+0.06 to +0.15 vs Voynich ≤ −0.024). Word-in-core codes reach it (Dante −0.018). So the core stream behaves lexically, not alphabetically. P4-U1 BOTH (results_p4u1_space_regimes.txt): commas are a mixture of squeezed spaces (line-end rise p 0.0005) and junctures (joined form R 1.66). IT2a has no commas. P4-D2's L4 target needs a re-scope (plaintext in the affix stream or whole word, or a word code) before it is built, and goes back to Jon. Details: research/phase-4.md §Results.
- 2026-10-17 22:23: s34 done (TEST INVALID on the independence half: selector missed its planted control; valid negative on the residual half: no glyph-class partition leaves a language-like residual, 0/1022 vs 345/1022 planted; c-346/c-347, L-123, O-051). s44 done: A +0.135, B +0.218 at 773 lines, both far above all Latin prose; A overlaps one short verse hand only (c-348, L-124; A1 updated). s39–s43 running concurrently.
- 2026-10-17 22:21: Phase 3 closed: tie at this design (results_s35.txt; c-342–c-345; D-047; L-122). Cipher reaches CHARWIN, generator reaches F1, neither reaches Moran. Phase 4 trigger not met; the main session's Phase 4 investigation proceeds at Jon's request as read-only research.
- 2026-10-17 22:17: Jon: "we have free compute both cpu and gpu". The ≤3-process / one-at-a-time cap is lifted for the approved steps: s39–s44 run concurrently where independent, s34 starts now instead of after the ledger. GPU stays unused until a GPU step is approved (Phase 4 t1 is still pending its gate).
- 2026-10-17 22:14: Jon: "Lets investigate all" (the five layer-split leads of 22:13 plus the red-team A-only draw). Approved as pre-registered, one-CPU, no-GPU, no-new-data steps, run one at a time after s34 (prefixes s39–s44; Argon holds s36–s38): s39 F1/CHARWIN by layer (prefix/core/suffix streams); s40 prefix stream as a text (entropy, Zipf, 166→41 held-out predictability vs habit/null); s41 Currier-B coupling by suffix class; s42 line-above recency decomposed into same-core/changed-affix vs same-affix/changed-core (Timm–Schinner test); s43 null-glyph twins with cores-as-nulls and affixes-as-nulls on the v2.1 board (scored once); s44 Currier-A-only matched-size line-initial draw vs the Latin per-manuscript rows. Each writes only its script, stub and results_<prefix>.txt.
- 2026-10-17 22:11: findings report written at workflow/FINDINGS-REPORT.md (Jon's request); manifest rows added; INDEX points to it.
- 2026-10-17 22:09: main-session red team (four items) weighed: ledger gains a design-provenance block (pools/R_la include held-out pages; round labelled "mechanisms fixed after pilots, scored once") and a rule-provenance column; s33 re-run labelled s33-b in CLAIMS. Needs Jon: (a) A-only matched-size U1 draw ("B outside, A inside" restatement) is a new experiment; (b) optional dual v2/v2.1 scoring of Phase 3 as a reader-only step.
- 2026-10-17 22:08: Sylvie's review applied (L-121): A13/A14/A15/A5 reworded to the defensible statements, prior-art section B2 added; public baseline "What the world knows" saved at workflow/research/public-baseline.md (Sylvie's text, links unverified by this session). Direction confirmed by Jon and Sylvie: use the affix finding to make a prediction on untouched material before seeing it.
- 2026-10-17 21:54: Argon (decryption session) delivered s33 (re-run, chain repaired), s34_morphology and s35_physical results; all three stubs verify. Filed c-335–c-341; CONSTRAINTS-MAP A13–A15 (two-layer word: affix layer carries rhythm, coupling and section vocabulary; cores shared and orderless; drawing gaps are not line edges; labels reachable by a class-conditioned generator). O-004/O-005/O-027/O-043(mechanism)/O-049/O-050 closed by Argon in OPEN.md. Prefix collisions on s34/s35 recorded (TOMBSTONES); no overwrite; cite by filename. Entrant implication: Phase 3 mechanisms are judged against A13/A14 as well; s34_superimposed_streams still queued.
- 2026-10-17 21:34: prefix collision on s33 (peer line-scale interlock, unclaimed, post-run script rewrite: O-050, L-118 unverified-chain); Phase 3 ledger renamed s35. Peer content, if its chain is repaired, says A5 is manuscript-wide (A and B) and affix-borne.
- 2026-10-17 21:33: s34 pre-registered (stub 4c27fd61…, re-frozen after a pre-run amendment: the original types ≤3000 bound was stricter than every language control at 25k tokens, so P1 bounds are now the language-row ranges and the selector is S = I_self − I_cross; original hash kept as a SUPERSEDED comment line). Not run; queued after s33.
- 2026-10-17 21:19: Jon approved s34, the superimposed-streams (glyph-class partition) check, pre-registered now and queued to run after the Phase 3 pair (s33). Scope: one CPU, <5 min expected, 15 min hard stop; positive control (CREMMA Latin + planted pitch glyph) must be recovered before the Voynich result counts; negative controls gibberish + generators; writes s34 script, stub, results_s34.txt only. Jon's framing: "the music and the words may be superimposed on top of each other".
- 2026-10-17 21:16: Jon approved the Phase 3 predictions-first plan ("Approve and execute"). Prefix s33 claimed for the ledger.
- 2026-10-17 21:13: s24 (approved musical/hybrid check) done in 7.3 s under cap: NOT SUPPORTED, all three predictions fail on all three transliterations (results_s24.txt; c-332–c-334; D-046). Inventory refresh done 21:12 (333 manifest rows, INDEX rewritten, gate-2103: one G3 coverage FAIL from ~328 root fan-out result files, owner decision pending). Next: Phase 3 redesign plan for the gate.
- 2026-10-17 21:09: s32 (O-047) done, results_s32.txt: A1 holds against pooled Latin verse (492 lines) and all verse/epic corpora at 200–773 lines; two single short Latin verse/formulaic hands (114–201 lines) are inside the same-size Voynich draw interval. O-047 closed with a size clause on A1 (CONSTRAINTS-MAP A1, c-330/c-331, L-116). s24 running under its cap.
- 2026-10-17 21:05: Jon chose "Redesign: predictions first" at the Phase 3 gate. s32 = O-047 matched-line verse comparison; s24 = approved musical/hybrid check under its cap; both launched. Phase 3 plan to be rewritten as one mechanism per family with pre-committed predictions on the three separators, scored once on the 41 held-out pages.
- 2026-10-17 21:05: Phase 3 investigation (workflow/research/phase-3.md): the planned entrant pair (cipher twin vs matched generator, same pools/table/lexicon) ties on 7 of 10 judged quantities by construction; separators are CHARWIN, F1 and Moran I only; both entrants are kill-candidates under v2 §7; a Tier-2 "favoured" verdict is not available from the pair, at best a registered two-metric lean. ~80 min compute. Goes to the gate as a finding, not a plan. workflow/CONSTRAINTS-MAP.md written (12 established constraints, connections, open items). Inventory refresh running (manifest gaps, INDEX rewrite, gate).
- 2026-10-17 21:00: Sylvie (via Jon): keep the within-line word-length constraint as a feature Phase 3 candidates must explain alongside the others; no restart, no mechanism tuned to that number; a candidate counts when it accounts for the pattern and predicts on untouched material. Adopted. Methodological note adopted for the Phase 3 stub: differences between datasets are judged by effect size with a page-bootstrap interval, not by comparing per-dataset p-values; passed to the Phase 3 investigation.
- 2026-10-17 20:55: Phase 2 closed in 11 minutes of compute. s20: coupling is a Currier-B property, A inside the real-line language range. s21: Daybreak's within-line Moran I reproduced exactly; real-line gibberish not above its own null; Voynich alone beats its shuffle null. s23: 122/124 stub targets OK (2 superseded pre-crash originals), m1 seed-unstable (7/10), three negatives underpowered, BH survivors none. PREREG-v2.1 frozen 20:55 (sha256 87e09ce3…). Surprise: my 20:42 gibberish caveat on Daybreak was wrong at the within-line level and is withdrawn (L-115). Debt: no o1 token stream (O-048).
- 2026-10-17 20:45: Phase 2 investigation done and plan written. U2 retired for both Currier halves by the peer's s30; Phase 2 reduces to s20 comparison, s21 Moran cross-check (Daybreak's statistic on real-line gibberish; filed c-320/L-111), s22 filing, s23 ledger, v2.1 amendment. Six decisions taken (phase-2.md). Peer's s31 entrant pre-test recorded, not counted.
- 2026-10-17 20:37: Phase 1 closed. Verdict U1 HOLDS (results_s18.txt): scribal prose lines do not produce the Voynich line-initial profile; edge bands keep full weight. Surprises: rhymed verse exceeds Voynich on the line-final side (c-314); real-line human gibberish shares Voynich's positive Moran I and CHARWIN sign (c-315); verse/formulaic Latin at ~100–200 lines reaches +0.10–0.14 (O-047). Debt: run_v2 extras/bake-off fail on 2-page manuscripts (ZeroDivisionError, KeyError markov3), reported as NA. Stop rule (20:02): does not fire; cheap Phase 2 steps proceed, then one entrant pair scored once.
- 2026-10-17 20:22: Jon appointed this session Voynich lead and asked for registration with Sylvie via the <team-comms>/<team-comms> steward (<team-comms> comms files). Steward requests read (routing handoff, authority delta, decipherment priority). The registration/ack file write to <team-comms> was blocked by the harness permission classifier; the ack is staged at workflow/comms/ for Jon to copy or to grant the write. s24 musical/hybrid check approved by Jon with a cap, after Phase 1.
- 2026-10-17 20:13: Astra's independent audit (support-phase1-audit.md) folded into the s18 stub before freezing: pooling guard with per-manuscript calibrated excesses and leave-one-out; punctuation as boundary; abbreviation-mark sensitivity family; matched-size Voynich reference; block-initial labelled as a column proxy. CREMMA agent redirected mid-build. Daybreak is independently re-running n5's CHARWIN/Moran I (O-043).
- 2026-10-17 20:05: Phase 1 investigation done (phase-1-instrument.md, phase-1-cremma.md). Found a peer's pre-registered s2_u1_u2_u3_controls.py already ran the on-disk U1 pre-test (outcome A), the position-stratified coupling null (genuine ordering), the edge-table transfer (mechanical, even from Dante), Timm's bound, the alphabet table and seven band widths. Registry updated; Phase 2 re-scoped; Phase 3 stub change required; prefixes s1/s2 taken, entrants to s27/s28. Pooled gibberish sidecar is 8×20 wrapped, so a real-line sidecar is a new deliverable.
- 2026-10-17 20:02: Jon: proceed, under the stop rule stated by the coordinator and accepted: run Phase 1 and the cheap Phase 2 steps; if real scribal lines land inside the Voynich edge band, stop and write up; if they sit well below and the coupling survives the position-stratified null, run the entrant pair once and stop after it regardless of outcome. Phase 4 runs only on human-input evidence.
- 2026-10-17 19:57: n7 filed: G favoured with the gibberish family present (all/A/B); X-vs-L size-dependent; edge MI and Moran I outside every family for all/B. s15 released: X per-writer ranges too wide to bind, X jackknife extras must not set bands (O-046). Phase 1 investigation started (two agents: instrument, CREMMA).
- 2026-10-17 19:52: n6 filed (two experiments under one prefix). A/B: SAME on full-size ranges, SPLIT matched-size; A inside L on the coupling metrics. Glyph-model 7k generator: F1 reopened, hand-1 NMI holds, reversing n4. Registry and Phase 3 target set updated; sequence unchanged. s15 held until n7's X ranges land (eight metrics regain weight).

- 2026-10-17 19:34: investigation gate approved; hypothesis killed as stated; six-step sequence adopted and cut into the four phases above.
- 2026-10-17 19:41: adversarial review (10 objections, sign-off "no") folded in: Phase 1 stub made exhaustive on jsd_first with an alphabet-neutral line-final statistic; prefix supersession table added (E s1/s2/s5/s10/s15 kept, s17–s24 new); s15 band-widths file added as a Phase 1 deliverable; size floor in tokens; pooled gibberish only; n-series hash check and NMI-h1 exclusion written in; Currier-A rule required in v2.1; sidecar dialect and line-preservation check stated; GPU dependency phrased as a measurement; h2 definition and o1 ink splits named.

## Research

- workflow/research/SYNTHESIS.md — investigation synthesis (done)
- workflow/research/A-lead-harvest.md — every candidate lead scored (done)
- workflow/research/B-prior-art.md — field's open questions, closed leads, missing controls (done)
- workflow/research/C-constraints.md — power curves, floors, multiplicity, execution limits (done)
- workflow/research/D-stress-test.md — attack on the ten-leads hypothesis (done)
- workflow/research/E-dependencies.md — dependency graph, wave plan, pre-registration stubs (done)
- workflow/research/prereg-v2-freeze.md — v2 freeze note (done)
- workflow/research/phase-1-instrument.md — run_v2 sidecar/ranges facts, s15 reuse, real-line corpora, n7 artefacts (done)
- workflow/research/phase-1-cremma.md — CREMMA layout, manuscript table, fetch plan, RN-Top method (done)
- workflow/phases/phase-1.md — Phase 1 plan and stub (done)
- workflow/research/phase-2.md — Phase 2 investigation (done)
- workflow/phases/phase-2.md — Phase 2 plan (done)
- workflow/research/phase-3.md — Phase 3 investigation (done; pair cannot separate as designed)
- workflow/CONSTRAINTS-MAP.md — established constraints and their connections (living page)
