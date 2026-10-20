# D — Stress test of the "top 10 leads" hypothesis

Stamp: 2026-10-17 19:20 PDT (read from `date`). Scope: `.`, read-only except this file.
Files read: `.inventory/INDEX.md`, `.inventory/registers/{REDTEAM,LEARNINGS,OPEN,DECISIONS}.md`, `PLAN.md` §0 and §6, `TEAM-HANDOFF.md` (19:01 stamp), `TOP10-LEADS.md` (19:03), `OPPORTUNITY-NEXT.md` (head), `results_{n2,n3,n3b,k4,p1,p2,j4,m7_board_translit}.txt`, `results_m4_phase1_board.txt` §2–§5, docstrings of `p1_bifolio_null.py`, `p1_order_sensitivity.py`, `p2_robustness.py`, `j4_context_only.py`, `k4_lossy_nomenclator.py`, grep of `PREREG-v2-DRAFT.md`.

**Hypothesis under attack** (Jon, verbatim): "based on our organized learnings, findings, testing what are our top 10 biggest leads and what is the best way to pursue them all and why" — read as: the organised learnings contain ~10 leads which, pursued in a planned order, move the manuscript question past "not deciphered" to Tier-2 (a family killed or favoured by a pre-registered margin, `PLAN.md` §0) or Tier-1 (a reading).

**The single question**: what would have to be true for this to be wrong, and is it?

It is wrong if any of these holds: (a) no lead can produce a Tier-2 verdict because the scoreboard cannot separate families with the controls that exist; (b) the leads are not ten independent bets but a few unknowns with downstream work; (c) Tier-1 is unreachable by statistics at all; (d) "pursue them all" is a worse procedure than a sequence. Each is tested below against the files. Three of the ten leads have already been run since 19:03; their outcomes are used as evidence.

---

## 1. Every lead on the table tops out at Tier-3

**Claim**: with the controls that exist today, no lead can return a Tier-2 verdict, so the ceiling of the whole list is "a new constraint".

**Why Tier-2 needs separable families.** `PLAN.md` §0 Tier 2 = "one of the three open families killed, or one favoured by a pre-registered margin on a joint scoreboard". That requires (i) a scoreboard whose bands were not derived from the target, (ii) at least one control per family that is not fitted on the target, and (iii) bands that the target's own halves pass. None of the three holds:

- (i) The v1 bands are "derived from filed gaps" around Voynich's own values (`registers/REDTEAM.md` #4; `PREREG.md` per D-004). v2, which would set bands from within-manuscript variability, is not frozen (`OPEN.md` O-007; `DECISIONS.md` D-016: "the v1 bands remain the joint bar").
- (ii) Every G control except `rugg_grille` is seeded, fitted or poured from Voynich (REDTEAM #6, §3 bullet 3); every L control is wrapped into 8/9-token pseudo-lines with no real line edges (REDTEAM #7); the C controls use a 20-letter random alphabet (REDTEAM #22). The m4 board's own note says the G edge range "excludes timm_schinner (poured into the Voynich line shape)" (`results_m4_phase1_board.txt` §2 header) — i.e. the board already knows its G family is contaminated and patches one row.
- (iii) Currier A alone fails the v1 board: `m_final_enrich` 6.21 against a floor of 8 (`results_m4_phase1_board.txt` §2 row `m_final_enrich`, VA column; REDTEAM #6). A band the target's own half fails cannot favour or kill a family by margin.

**What the board actually separates.** `results_m4_phase1_board.txt` §4: 14 of 23 metrics carry no weight because L, C and G ranges overlap. Of the 9 weighted metrics, the only ones outside *all* families on the whole text are `jsd_first_fg`, `cross_excess_eva`, `x_edge_mi_word`, `x_moran_I` (§3 `[voynich_all]`) — three of the four are line-edge or word-boundary quantities. So "family separation" today is carried almost entirely by edge statistics, and those are exactly the statistics for which (a) no L control has real lines and (b) every producer is handed the same Voynich-fitted M5 layer and edge table (REDTEAM #15: "the line-edge bands are now unable to discriminate families: every entrant either gets the Voynich layer or fails").

**Which controls would have to exist for a Tier-2 verdict**, and whether any lead builds them:

| Needed control / instrument | Named where | Built by any Top-10 lead? |
|---|---|---|
| One real 15th-c. scribal transcription with original line breaks, scored on `jsd_first_fg` / p / m / m5 anatomy | REDTEAM #7, §2 finding 3, §3 bullet 1; OPEN O-014, O-026 | **No.** Not on the list. (Lead 8's Cappelli/quid-pro-quo corpora are abbreviation lists, not lined manuscript text.) |
| An edge table R fitted on something other than Voynich (Latin syllable edges, or Currier A → scored on B) | REDTEAM #1, #18, §3 bullet 2 | **No.** Lead 1's joint producer carries Voynich's own R like F3/G1/H1/K1–K4/N1/N2 before it. |
| A G control not fitted on Voynich (Rugg over a Latin table; T–S seeded with Latin) | REDTEAM #6, §2 finding 5 | **No.** |
| Bands from within-manuscript variability, entrants bootstrapped on page splits | REDTEAM #4, §2 finding 4; O-007 | **No.** Lead 1 says "scored on frozen board", i.e. v1. |
| A fixed-unit h2 so producer and target are on one alphabet | REDTEAM #19; O-022 | **Partly.** Lead 10 (now `results_p2.txt`) reports ranges per transliteration; it does not put producers on the same unit. |
| Per-family N/A-aware out counts | REDTEAM #20 | **No.** |

Verdict on (1): **supported.** The ceiling of the list as written is Tier-3. Lead 1 claims "joint-passes (generation Tier-2)" (`TOP10-LEADS.md` item 1), but a generator passing v1 is a sufficiency demonstration on a board built from the target, not a pre-registered margin over a cipher-side producer with the same budget (D-015 #6 requires the matched run alongside). On the current board a joint pass by a Voynich-fitted generator would be Tier-3 at most, and REDTEAM #5 already shows the "circular" G1 list reaches most of the way there by copying Voynich's vocabulary.

Refuter I checked: is there a lead that explicitly builds a non-Voynich-fitted control? Leads 3 and 8 fetch period material for the *C* family. Neither produces lined text or an edge table. Checked; none.

---

## 2. "Ten leads" is the wrong shape: three load-bearing unknowns and everything else downstream

**Claim**: the organised learnings contain two or three unknowns that decide what every statistic means; the ten leads are mostly downstream of them and cannot be interpreted until they are resolved.

The REDTEAM's own "things the project does NOT know" list (§3) has eleven bullets. Collapsing by dependency gives three that every other item inherits from:

### U1 — What real scribes do at line edges
Source: REDTEAM #7, #15, §3 bullet 1; L-068/L-069/L-070; OPEN O-014, O-026. No number for line-initial/final glyph preference in any real 15th-century manuscript exists in the folder; "anomaly outside every family" means "outside every pseudo-line". The edge statistics are the only ones outside all families (`results_m4_phase1_board.txt` §3), the universal producer failure (L-068), and the one place the two-family framing is still being argued.
Downstream of U1: Lead 1 (its pass/fail on `jsd_first_fg`, p, m is uninterpretable without knowing whether a real scribe gives 0.02 or 0.12); Lead 4 (hapax within the edge budget); Lead 9 (label register vs name list depends on what a scribe's habit register looks like); every "G favoured" or "L out" sentence in `PLAN.md` §6 point 8.

### U2 — Whether the edge coupling is the text's or the handed table's
Source: REDTEAM #1, #18, §3 bullet 2; L-072 ("a generator that stores P(first|last) can meet it"); L-085 (F3 "is a mechanism that can carry the table, nothing more"). F3/G1/H1/K1–K4/N1/N2 all carry Voynich's own R; no producer has been given a non-Voynich R and scored on held-out Voynich.
Downstream of U2: Lead 1 (the joint producer will carry R again, so its `cross_excess` pass is a restatement); Lead 3 and the whole K4 family story (the "+0.215..+0.693 crossMI inside the type band" of `results_k4.txt` is bought with R); O-009 GPU key search (its channel model is the F3 flow choice, i.e. R); PLAN §6 point 2.

### U3 — What unit the text is in (alphabet and segmentation dependence of h2, types, hapax)
Source: REDTEAM #19, §3 bullets 7–8; L-042 (h2 2.126 EVA → 2.397 glyph+ → 2.540 v101, `results_m7_board_translit.txt`); L-048/`results_o1.txt` (boxes disagree with ink on 42/43 zero-gap sites); `corpora.py` drops 212 '?' tokens. h2 is the band that kills every generator (G1 seed 1.6, c2 1.8, N2 1.79; REDTEAM #19), and types/hapax — the "most consistent quantitative miss" that Lead 4 is built on — are a function of where the spaces are.
Downstream of U3: Lead 4 (type/hapax budget), Lead 6 (resegmentation is the *attempt* at U3, so it is the one lead that is upstream, not downstream), Lead 10 (done; restates m7), Lead 1's h2 pass, the M19 type-budget metric in `PREREG-v2-DRAFT.md` line 51 (which still says "every producer tested so far needs 15–25k types" — stale by `results_k4.txt`, D-025).

### The one question that is not downstream: is there any content-side signal left?
Hand-1 within-hand section NMI survives by 0.013 / 0.005 on two of three transliterations (`results_n3.txt`); the held-out power test cannot see its own positive control (`results_n3b.txt` Q1 → C on all three, HT_sec median p 0.818/0.692/0.709). Leads 2 and 7 sit here. Lead 7 is now answered: `results_j4.txt` m=3 ARI 0.029 / 0.044 against the 0.15 gate — dead. Lead 2 is a genuine prerequisite (no power, no verdict), but a power-repaired test still only tells you whether *vocabulary clusters by section*; `results_k1.txt` (L-023) and `results_c2.txt` (L-015) show both a section-keyed cipher and a section-seeded generator produce that. It constrains granularity, not family (REDTEAM #13).

Dependency sketch (arrow = "cannot be read until"):

```
U1 real-line scribal control ──► lead 1, lead 4, lead 9, PLAN §6 pt 8 "anomaly"
U2 non-Voynich edge table   ──► lead 1, lead 3, K4 story, O-009 key search
U3 unit/segmentation        ──► lead 4, lead 10 (done), lead 1 (h2), M19
lead 6 (ink resegmentation) ──► U3   (upstream, not downstream)
lead 2 (power repair)       ──► "is hand-1 NMI real" ──► nothing family-level (REDTEAM #13)
lead 5 (order sensitivity)  ──► done (results_p1.txt 19:12), bound-order stats inside quire-permutation range for heaps, outside for adjacency ratio; protective, not discriminating
lead 7 (J4)                 ──► done, dead (results_j4.txt)
lead 10 (p2)                ──► done, duplicates results_m7_board_translit.txt
leads 3, 8 (period attestation) ──► C-family prior only; no board consequence until U2
```

Verdict on (2): **supported.** Ten is the wrong shape. Three unknowns (U1, U2, U3) are load-bearing; of the ten, one is upstream of U3 (lead 6), two are prerequisites for a non-family question (lead 2; lead 7 now dead), three are done or duplicative within 11 minutes of the list being written (5, 7, 10), and the rest cannot be interpreted until U1–U3 are resolved. The list was compiled "from LEADS-AND-FINDINGS, C/E/F/G/K/N/O rounds, J-series, REGISTER-DIFF, BREWER-LEWIS-CHECK, SCOUT-EXTERNAL" (`TOP10-LEADS.md` line 3) — `registers/REDTEAM.md` is not among its sources, which is why its three most consequential items (REDTEAM §2 findings 3, 4, 5) are absent from it.

Refuter I checked: does any lead attack U1 or U2 directly? Lead 1's "edge" component is the G1 edge filter, i.e. Voynich's R. Lead 8 fetches Cappelli abbreviation lists, which are not lined text. Checked; none.

---

## 3. The proof bar is unreachable by any statistical lead

**Claim**: `PLAN.md` §0's Tier-1 ("a fixed key plus a named language or code system that reads ten consecutive pages, applies across Currier A/B, all five hands and all sections, matches labels… fails on shuffled Voynich… predicts held-out folios… survives an adversarial agent that only sees the written key") cannot be produced by any lead on the list or any lead of their kind.

Evidence:
- Every statistical result in the folder is a *family* result; the only path from family to key is O-009 (GPU noisy-channel search under the F3 model), gated on the joint producer passing (D-015 #6, TEAM-HANDOFF Tier 3). That search needs a plaintext language model; `results_a6b_*.txt` (L-002) shows the one solver family that was run lands within ~0.1 bit of its own pseudo-Voynich null for Latin/Italian/German, and F4/I1/J1–J4 (L-020–L-022, `results_j4.txt`) show class recovery has no power at Voynich-like type counts. O-009 is a bet that a better solver beats a null the project has not been able to beat, after a producer passes a board the project cannot yet make family-separating.
- The proof bar demands labels match illustrations without retuning. `results_a3.txt`/`results_d6.txt` (L-032) put label-in-own-page at p≈0.1 on 40 pages; `results_m6_labels.txt` (L-033) says labels are a habit register — and REDTEAM #9 says that result cannot distinguish register from name list. There is no agent-executable path to a label crib: the cribs on disk (`data/external/cribs/`) are explicitly "n/a until a key" (O-029) because the plan forbids the crib → key direction.
- The literature row L-091 (UNTRACED locally) is the project's own prior: no fixed-key claim has ever passed a blind test. The bar was set *because* statistics alone has never produced a reading.

What Tier-1 would actually require is evidence of a different kind: a crib (a label or passage with a known referent), a bilingual, or a provenance document naming the cipher or author. `TOP10-LEADS.md` lines 76–77 explicitly exclude "library/paywall access, forum registration, expert elicitation, facsimile handling" as human work. So the Top-10 is, by its own constraint, a list of Tier-3 work.

**What the project would do differently if it accepted that:**
1. Say it in `PLAN.md` §0: agent-executable statistics can reach Tier-2 only after the board is made family-separating (U1–U3), and cannot reach Tier-1. Stop writing "Tier-2 if it passes" against producer runs on v1.
2. Reframe the campaign's deliverable as the tightest published-quality *constraint set with real controls* (Tier-3 done properly), which is what the day actually produced (L-067 to L-090).
3. Split the queue into "agent" and "human" columns and keep the human column short and specific: Greshko 2025 fetch (O-018), Meister 1902 / Tranchedino sizes (O-016/O-017), one diplomatic Latin transcription with line breaks (O-014/O-026), Voynich Ninja registration (O-033). Three of those four are the inputs to U1 and to the C-family priors that leads 3/8 are trying to approximate from open scraps.
4. Treat O-009 (GPU key search) as what it is: the only Tier-1 attempt, gated on a Tier-2 result the current board cannot deliver. Do not schedule it.

Verdict on (3): **supported.** Tier-1 is outside the reach of every lead on the list and of the list's own constraints.

---

## 4. "All ten in parallel" is worse than a sequence

**Claim**: the folder's record today shows that parallel pursuit destroys evidence and burns leads without moving the family question.

Evidence from the last 17 minutes (TOP10 compiled 19:03; all times from `ls --time-style`):
- **A result file was overwritten.** `TEAM-HANDOFF.md` line 31 cites `results_p1.txt` (`p1_bifolio_null.py`, 18:46) as the bifolio null for the last content-side signal: Hand 1 NMI 0.275 null 0.048 p=0.000; Hand 2 0.333 null 0.131 p=0.012; Part D section-S +1.02 pp [+0.48, +1.78]. `.inventory/INDEX.md` line 21 says "A bifolio null is filed (`../results_p1.txt`); read it before citing any page/topic signal." At 19:12 `p1_order_sensitivity.py` (Top-10 lead #5; its `OUT = Path(__file__).parent / "results_p1.txt"`) wrote the same path. `results_p1.txt` on disk now holds five lines of Heaps/Jaccard order bounds. **The numbers that hold up "hand-1 NMI survives the bifolio null" now exist only as prose in TEAM-HANDOFF and have no result file**, which under D-018 ("the result file wins") means they are uncitable. The same failure mode is already in the register as L-062 (two ctl scripts, one result file) and L-061 (map stale within the hour).
- **The prefix rule was broken.** TEAM-HANDOFF line 203 (19:01): "`a` through `r` … are taken. Next experiments should use `s1` onward." Lead 5 used `p1`; lead 7 used `j4`; lead 10 used `p2`. Two sessions, one namespace, no VCS (REDTEAM #23; O-036).
- **Three leads consumed in 11 minutes; one dead, one duplicative, one destructive.** `results_j4.txt` (lead 7): gate 0.15, best m=3 ARI 0.044 — dead. `results_p2.txt` (lead 10): per-transliteration ranges that `results_m7_board_translit.txt` already reported at 16:46, with a different RF1b prep (`RF1b-e`, 31,142 tokens, JSDf 0.1586, excess +0.1518) that will now sit beside m7's RF1b (0.1809, +0.1729) and generate the next "25 doc/result contradictions" audit item. Lead 5 is the overwrite above.
- **Leads die within hours anyway.** Today's register shows the pattern: F1 word order promoted 16:08, killed 18:29 (D-032); page MI "last content-specific signal" at 18:31 (L-087), withdrawn 18:52 (D-043); the type-budget argument stated in K_RESULTS, reversed by `results_k4.txt` the same session (D-025). Running ten at once means most of the ten are scored against premises that will have changed before they finish, and the result files cannot be re-read against the premise they were run under because the premise is not stamped in them (REDTEAM #23's ledger proposal).
- **The leads are dependent** (§2 above), so parallel running produces results whose interpretation depends on results that have not arrived: a lead-1 joint producer scored before U1/U2 are settled will have to be rerun on v2 with a non-Voynich R, which is the pattern that already happened to G1 → H1 → K1 → j (D-015).

**The sequence that the dependency graph implies** (one owner per step, one result file each, prefix from `s1`):
1. **U1**: one real-line scribal control scored on `jsd_first_fg`/p/m/m5 (O-026). If a real scribe gives JSDf ≥ 0.10, the edge bands measure scribal habit and §6 point 8 is rewritten; if ≤ 0.05, Voynich's 0.176 stands as the anomaly. Either way the board changes.
2. **U2**: F3/G1 rerun with R fitted on Currier A and scored on B, and with a Latin syllable-edge table (REDTEAM #1, #18). One result file says whether +0.18 is the text's property.
3. **U3**: rescore v1 with h2 on one fixed unit for producers and target (O-022), and E1 with ink-driven splits from o1 (lead 6).
4. Freeze v2 with bands from within-manuscript variability, N/A-aware out counts, and the U1/U2 controls in each family (O-007).
5. Only then lead 1 (joint producer) *and* the matched cipher-side producer with the same budget, on v2, pre-registered margin. That is the first run that can return a Tier-2 verdict.
Lead 2 (power repair) can run in parallel with 1–3 because it is on a different axis and does not write to the board.

Verdict on (4): **supported, with a concrete casualty** (the bifolio-null result file).

---

## 5. What the project would see within one round

**If the hypothesis were right** (ten leads, planned order, Tier-2 reachable), one round would show, checkably:
- A pre-registered joint producer and a matched cipher-side producer, scored once each on a frozen v2 whose hash is recorded before either run, with one family passing and the other failing by the registered margin, on ZL3b *and* RF1b *and* IT2a, with Currier A and B passing the same bands.
- A real-line scribal control with `jsd_first_fg` well under 0.10, so that "outside every family" survives a control that has lines.
- A non-Voynich edge table giving cross_excess ≥ +0.09 on held-out Voynich pages.
- Lead 2's power repair with the positive control (`HT_sec`) at p < 0.05 before the manuscript is scored, and hand-1 NMI still holding against a 7k-type generator (O-039/O-041).
- No result file overwritten; every new run on an `s*` prefix; a ledger line per run.

**If the hypothesis were wrong**, one round would show:
- Leads completing in minutes with verdicts that do not touch the family question (`results_j4.txt`: dead; `results_p2.txt`: restates m7) — already observed.
- A joint producer scored on v1 carrying Voynich's R and the M5 layer, passing the edge bands by construction and missing h2/hapax, i.e. one more G1/H1/K1 row (REDTEAM #15).
- The real-line scribal control, once run, landing at JSDf 0.05–0.15, collapsing the edge bands as family discriminators and leaving the board with no weighted metric outside all families.
- Result files overwritten or prefixes colliding (`results_p1.txt` 19:12) — already observed.
- The "last content signal" moving again (page MI 18:31 → withdrawn 18:52; hand-1 NMI now without its bifolio-null file).

Three of the five "wrong" markers are already on disk; none of the "right" markers is.

---

## Verdict

**KILLED** as stated. The organised learnings do not contain ten leads that, in any order, reach Tier-2 on the instruments that exist; they contain three load-bearing unknowns (U1 real-line scribal habits; U2 whether the coupling is the text's or the handed table's; U3 the unit/segmentation dependence of h2, types and hapax) plus one non-family question (is hand-1 section NMI real content, which needs power repair and a 7k-type generator before it can be read, and which — per REDTEAM #13 — constrains granularity, not family). Tier-1 is unreachable by every lead on the list and by the list's own "agent-executable only" constraint.

**Replacement**: a sequence, not a list. (1) U1 real-line control → (2) U2 non-Voynich R → (3) U3 fixed-unit h2 + ink-driven segmentation → (4) freeze v2 with controls not fitted on the target and bands from within-manuscript variability → (5) the joint producer and its matched cipher-side twin, pre-registered, on v2. Lead 2 (power repair) runs alongside as the only content-side item. Everything else on `TOP10-LEADS.md` is either done (5, 7, 10), downstream (1, 3, 4, 9), or a C-family prior with no board consequence until U2 (3, 8). Tier-1 is a human-input question (crib, bilingual, provenance; O-014/16/17/18/33) and should be filed as such in `PLAN.md` §0 rather than pursued through O-009.

Immediate housekeeping the verdict forces: re-run `p1_bifolio_null.py` to a new path (it is the only file behind "hand-1 NMI survives the bifolio null"); stop `p1`/`j4`/`p2` prefix reuse; add a TOMBSTONES row for the overwritten `results_p1.txt`.

---

## Assumption candidates

| # | Assumption | Status | Basis |
|---|---|---|---|
| A1 | The v1 bands cannot deliver a pre-registered family margin because they are derived from the target and Currier A fails them | **verified** | `results_m4_phase1_board.txt` §2 `m_final_enrich` VA 6.21 (floor 8); REDTEAM #4, #6; D-016 |
| A2 | The only metrics outside all families are edge/boundary metrics | **verified** | `results_m4_phase1_board.txt` §3 `[voynich_all]` "outside ALL families: jsd_first_fg, cross_excess_eva, x_edge_mi_word, x_moran_I" |
| A3 | No L control has real line breaks; no real-scribe edge number exists in the folder | **verified** by the registers (REDTEAM #7, §3 bullet 1; O-026); the trithemius "line breaks kept" control's scoring error in m4 §5 not re-opened here, so "none scored" is **inferred** from REDTEAM #7 |
| A4 | Every producer that reaches +0.18 coupling was handed Voynich's own P(first\|last) table | **inferred** from REDTEAM #1, §3 bullet 2 and L-085; `f3_flow_choice.py:10` not reopened by me |
| A5 | h2 is the band that kills every generator and is alphabet-specific | **verified** (`results_m7_board_translit.txt`: 2.126 / 2.397 / 2.540; `results_n2.txt` HT h2 1.73–1.82; REDTEAM #19) |
| A6 | `results_p1.txt` (bifolio null, 18:46) was overwritten at 19:12 by `p1_order_sensitivity.py` | **verified** (`ls` 19:12, 611 bytes; file contents are order-bounds; both scripts set `OUT` to `results_p1.txt`; TEAM-HANDOFF line 31 and INDEX line 21 cite the bifolio content) |
| A7 | Lead 7 (J4) failed its gate | **verified** (`results_j4.txt` m=3 ARI 0.029 / 0.044 < 0.15) |
| A8 | Lead 10 (p2) duplicates m7 | **verified** on ZL3b/IT2a/GC2a rows (identical to m7 at printed precision); RF1b row differs because p2 used `RF1b-e` (31,142 tokens) — a new contradiction source, **inferred** |
| A9 | The TOP10 was compiled without REDTEAM as a source | **verified** from `TOP10-LEADS.md` line 3 source list |
| A10 | Tier-1 is unreachable by agent-only statistics | **inferred** from L-002, L-021/L-022, `results_j4.txt`, L-091 (UNTRACED), O-029 and the TOP10's own exclusion of human work; no file states it |
| A11 | Hand-1 section NMI is the last content-side signal and is now without a bifolio-null result file | **verified** (D-043, `results_n3.txt`, A6) |
| A12 | `PREREG-v2-DRAFT.md` M19 is stale by K4 | **verified** (line 51 "every producer tested so far needs 15–25k types" vs `results_k4.txt` types 5,076–5,613; D-025) |
