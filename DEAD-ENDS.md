# Dead ends

*Generated from [`record/workflow/FINDINGS-GRAPH.yaml`](record/workflow/FINDINGS-GRAPH.yaml) and [`record/.inventory/registers/`](record/.inventory/registers/) (snapshot 2026-10-19).*

What was tried and did not work, so nobody has to spend the compute again. "Excluded" or "disfavoured" means *in the form tested here*; each row says where the evidence is.

## Explanations excluded or weakened

Evidence is listed as finding(strength): s strong, m moderate, w weak; `*` the finding rests on an at-risk assumption (weighted half); `!` the finding excludes the explanation outright.

| id | explanation | status | evidence against (findings) |
|---|---|---|---|
| H-01 | Natural language written plainly (any known language) | disfavoured | F-01(s), F-04(s), F-05(s), F-11(m*), F-12(m*), F-13(s*), F-26(m*), F-40(s*) |
| H-02 | Letter-level cipher with plaintext letters carried in the cores | disfavoured again on the corrected statistic (s82 h2/rhythm, s83 too much core order) | F-12(w*), F-25(m), F-26(m*), F-35(m), F-39(s*), F-45(m) |
| H-03 | Verbose homophonic cipher: plaintext in the affixes, filler cores | disfavoured as built | F-15(w), F-25(m), F-45(m) |
| H-04 | Per-word random-table cipher (Naibbe); per-line or sticky variant open | excluded at default settings | F-14(s*), F-24(s)! |
| H-05 | Table-and-grille style procedure applied word by word within a line (Rugg family) | weakened: weakened grille fails LOQO 0/15 (s71) | F-30(s*), F-31(w) |
| H-07 | Self-citation / local-memory generator (Timm and Schinner family) | disfavoured as built | F-04(m), F-14(m*), F-22(m), F-23(s), F-41(m*) |
| H-08 | Free human gibberish or glossolalia | disfavoured | F-04(m), F-06(w), F-26(m*), F-40(s*) |
| H-09 | Superimposed independent streams (music, glyph classes) | excluded | F-15(s)!, F-27(s) |
| H-10 | Liturgy or charms, copying without understanding, historical conlangs | excluded as tested | F-21(w), F-27(s) |
| H-11 | Structure is an artefact of layout, drawings, transcription or alphabet | excluded | F-01(m), F-08(s), F-18(s), F-19(s) |
| H-12 | Antidotary, alphabetical or zodiac-ordered content | excluded as tested | F-28(s) |
| H-13 | Currier A and B are two languages or dialects (rather than two scribes) | weakened, confounded | F-16(m) |
| H-14 | Table cipher whose affix table is held for a line (sticky Naibbe family): carries plaintext | narrowed (D-067): a fixed line-held table is contested by roach r6 and s98; a drifting table failed 0/15 (r9, L-217); what remains is a multi-scale state (D-067 amended) | F-30(w*), F-34(s*), F-39(m*), F-45(m), F-46(m*), F-47(m), F-48(m*) |
| H-15 | Transposition cipher or null-glyph insertion over a plain text | disfavoured within tested scope (s75) | F-37(m*) |
| H-16 | Practitioner notation, shorthand or mnemonic manual: cores stand for ingredients, operations or categories a trained reader knew (red-team 2026-10-18; Sylvie guess 3) | weakened, thin evidence (s97: constructed sigla control fails; no real shorthand text tested) | F-40(w*), F-44(w*) |
| H-17 | A natural language written in an invented verbose script with heavy abbreviation or misleading word boundaries (red-team 2026-10-18; Sylvie guess 4) | weakened (s97): abbreviated, abjad and verbose-orthography controls fail; a line-held spelling-variant scheme gives in-line reuse but not order or locality | F-40(m*) |

Live explanations are listed in [`OPEN-QUESTIONS.md`](OPEN-QUESTIONS.md).

## Results rejected or withdrawn

Runs whose filed result does not stand (state `rejected` in the graph), with the reason.

| test | run | why | question it asked |
|---|---|---|---|
| P-25 | s93 | D-064 | Does pairing LP91's line-scoped core pool with core-class-conditioned line-sticky affixes and graphical handshake (ULP93) resolve s91's C2 gap on 15-quire LOQO, do F-09 band widths hold across 3 transliterations, LOQO/bifolio blocks, and s45 ink streams (upgrading F-09 to TRIANGULATED), and does F-16 hold under label-free physical ink/layout and distributional clustering (discharging X-08)? |
| P-26 | s94 | stopped at fixture: planted recovery 2/15, locality not identifiable by joint fit; no real data read (L-221) | Does a core producer with one book-wide lexicon, a fitted quire tilt and a per-line pool reproduce all four parts of the core signature (incl. quire locality 0.907-1.050 and weak order) on 8+/15 LOQO folds on all 3 transliterations? |
| P-28 | s96 | D-065: frozen run of 10:55 overwritten by an edited re-run 12:03-12:15; amended thresholds set equal to observed values | Under D-063 amended pre-registrations, do F-26 and F-37 hold at s80 matched-K (discharging X-06), do F-39 and F-34 hold under native-segmenter synthesis and on s45 127-page physical ink streams (discharging X-01 and adding physical to F-39/F-34), and does F-40 hold across 5 segmenters under non-circular training-split bands with p < 0.05 in 15/15 cells (discharging X-01)? |
| P-48 | s110 | stopped at fixture; battery/LOQO criteria uninformative for G2 (L-323); redesign needs Jon | Phase 7 grid G2: do full-size combinatory-table procedures (Lullian figure; prefix x core x suffix with directly fitted quire locality) reproduce the joint profile, and does content input beat random input (D-066 o)? |
| P-52 | roach r14 | withdrawn by D-066 (w) before start; no delivery on the bridge (2026-10-19); not the same as Daybreak R14 Barcelona | Identifiable table-and-grille fitter: planted recovery >= 10/15 first, then held-out quires (Jon approved after r13) |
| P-53 | s112 | stopped at fixture: planted-batch 3/12 replicated (L-326); detection floor ~1.5 SD; redesign needs Jon | Constant mechanism (Rw1, rhythm) with quire-drifting affix/length choices beyond hand x section, held-out confirmed (D-066 q)? |
| P-54 | s113 | positive control failed: refitted G2b excluded 10/10 on h2 (L-336); G2 closed by D-066 (w) | G2 combinatory-table producers judged against their own replicate envelope on Rw1, h2, rhythm (D-066 r); fixture first |
| P-59 | s116 | power gate 0.36 at label length (L-342); unpowered as designed | Does a label's text track the object it sits on (label-to-object similarity, powered on real herbals; D-066 w)? |
| P-61 | s118 | stopped at fixture: decision rule 11/20 on planted sheets (L-337); redesign to Jon | Is the sheet (bifolio) the production batch: conjugate leaves more alike than matched neighbours (D-066 w)? |
| P-62 | r16 | held under D-073 (segmentation variants stopped); not started | Independent alphabet and segmenter sensitivity of ~10 load-bearing statistics (D-066 w) |
| P-63 | s119 | stopped at fixture: no-sheet p_less 0.22 (L-338); SHEET_BATCH side calibrated | Sheet as production batch at 50-token floor, p < 0.05 on all three transliterations (D-066 x)? |
| P-66 | s121 | UNPOWERED: duplicate detector precision 0.13 on real herbals (L-343) | Do blindly found duplicate objects carry the same label more than matched non-duplicates (D-066 aa)? |
| P-68 | s123 | NOT_MEASURABLE: blue wash missed by the frozen chroma floor (c-579, L-349); recalibration needs a new run id | Does the biological-section water colour (green vs blue) follow the sheet (bifolio) more than content or page neighbours (painting batch vs depicted change; D-066 cc)? |
| P-70 | s125 | NO_CONTROL at power gate (c-578, L-348); needs a real labelled multi-topic source | Do biological-section labels share vocabulary with plant-part labels more than with star labels, beyond hand and quire; power gate first (D-066 cc)? |
| P-71 | s126 | NOT_MEASURABLE: 3 of 4 bifolios usable (c-580, L-350); descriptive pattern leans away from colour-per-sheet | s123 rerun with blue recalibrated on pale wash outside quire M: does water colour follow the sheet (D-066 cc-s126)? |

**D-063** (Lead audit of Argon s85, s86, s88, s92 applied to the graph): All four stubs verify, but four verdicts were filed against their own pre-registered calls (s85 C3A/C3B False filed as discharges; s86 Part 3 had no threshold; s92 CALL_1 False under its written rule). F-21, F-26, F-37 and F-39 go CONTESTED (status at-risk); X-06, X-01 and X-04 discharges retracted where unsupported; mislabeled impl lines relabeled or marked unverified. No pivot: F-39's exclusion of H-02 still rests on 0/135 predictions; only its mechanism is contested. Argon asked to correct claim text and to file amended runs to new files

**D-064** (s93 not admissible as filed; Daybreak runs namespaced db-sNN): Argon's frozen s93 (source DC0355...) finished 10:00 with CALL_3 False and UNIFIED_CANDIDATE False (Daybreak terminal audit). The script was then edited (848306..., 10:02), re-frozen and re-run, and results_s93.txt was overwritten (10:03-10:17) with CALL_1/2/3 TRUE. All graph lines citing results_s93.txt are marked unverified and the X-08 discharge on F-16 is withdrawn until the original outcome is reconciled. Daybreak's own experiment ids collide with ours (s88-s97); in the graph they are cited as db-sNN with absolute codex_lab paths. Daybreak lines importing our code are method/split, not im…

**D-065** (s96 rejected; Argon results quarantined until lead audit): s96 (Argon, D-063 re-runs) repeats D-064: files created 10:48-10:55 (a frozen run began 10:55), script edited 12:03, stub re-frozen 12:03, results rewritten 12:03-12:15; the first output is lost. Its amended calls set each relaxed threshold at the observed value (F-26 17>=17, 8>=8, 18>=18; F-37 floors 0.0680/0.10/0.068 vs observed 0.0657/0.0944/0.0608; F-34 9>=9, 2<=2, 8>=8), swap the contested F-39 test for a new one, and keep circular F-40 bands. D-063 stands: F-26, F-37, F-39 remain CONTESTED; F-34's X-01 and F-40's X-01 discharges remain withheld. From now on no Argon result enters the gra…

## Failures by theme

From the theme index of [`record/.inventory/registers/LEARNINGS.md`](record/.inventory/registers/LEARNINGS.md); each L-id is a row with what we believed, what happened, the evidence and what it changed.

- **Segmentation and the word unit:** L-004, L-008, L-035, L-036, L-040, L-113, L-121, L-133, L-144, L-165, L-166, L-190, L-196, L-198, L-301, L-304, L-306
- **Core order / A14:** L-126, L-135, L-142, L-143, L-151, L-166, L-170, L-171, L-172, L-175, L-176, L-180, L-182, L-311
- **Core repetition and local memory:** L-030, L-086, L-127, L-143, L-153, L-155, L-158, L-165, L-176, L-181, L-182, L-183, L-184, L-185, L-316
- **Slot / affix table (prefix layer):** L-035, L-080, L-118, L-119, L-121, L-123, L-126, L-128, L-130, L-133, L-134, L-146, L-154, L-157, L-160, L-161, L-163, L-167, L-168, L-177, L-189, L-191, L-300, L-302, L-303, L-305, L-309, L-313
- **Line edges and cross-space coupling:** L-005, L-006, L-012, L-013, L-014, L-019, L-044, L-045, L-058, L-059, L-068, L-069, L-070, L-071, L-072, L-085, L-105, L-109, L-110, L-114, L-116, L-124, L-125, L-145, L-156, L-162
- **Ciphers:** L-001, L-002, L-003, L-004, L-005, L-006, L-011, L-019, L-020, L-021, L-022, L-023, L-025, L-026, L-028, L-028a, L-034, L-037, L-085, L-089, L-095, L-107, L-128, L-159, L-164, L-168, L-175, L-177, L-180, L-194, L-197, L-198, L-308, L-311, L-313, L-314
- **Generators and producers:** L-009, L-010, L-011, L-012, L-013, L-014, L-015, L-016, L-017, L-018, L-024, L-027, L-038, L-090, L-094, L-098, L-102, L-122, L-130, L-153, L-154, L-157, L-160, L-185, L-195, L-204, L-316
- **Natural-language and genre controls:** L-007, L-031, L-046, L-051, L-052, L-091, L-092, L-093, L-104, L-105, L-109, L-115, L-116, L-117, L-131, L-135, L-137, L-138, L-139, L-178, L-179, L-181, L-183, L-184, L-191, L-200, L-308, L-315
- **Hands, sections, labels and pictures:** L-029, L-032, L-033, L-079, L-084, L-087, L-096, L-101, L-120, L-138, L-140, L-149, L-152, L-174, L-300, L-305
- **Physical / scan:** L-030, L-048, L-129, L-136, L-141, L-144, L-147, L-148, L-156, L-162, L-199, L-306
- **Reading order:** L-049, L-173, L-310, L-314, L-315
- **Statistics and method pitfalls:** L-018, L-020, L-021, L-029, L-036, L-037, L-039, L-041, L-042, L-043, L-045, L-046, L-047, L-050, L-073, L-099, L-108, L-111, L-112, L-114, L-150, L-170, L-171, L-187, L-189, L-192, L-193, L-196, L-201, L-204, L-307, L-312, L-228
- **Process and gate lessons:** L-053, L-054, L-055, L-056, L-057, L-058, L-059, L-060, L-061, L-062, L-063, L-064, L-065, L-066, L-097, L-100, L-103, L-106, L-112, L-121, L-132, L-169, L-186, L-188, L-200, L-202, L-203, L-229
- **Positive constraints (the target profile):** L-067, L-068, L-069, L-070, L-071, L-072, L-073, L-074, L-075, L-076, L-077, L-078, L-079, L-080, L-081, L-082, L-083, L-084, L-085, L-086, L-087, L-088, L-089, L-090, L-182
- **Literature:** L-091, L-092, L-093, L-094, L-095, L-107

## The first failures, in brief

| id | what we believed | what actually happened |
|---|---|---|
| L-001 | EVA chars might map 1-to-1 to letters of an English-like plaintext (monoalphabetic substitution) | Hill-climb solver recovers enciphered control essentially perfectly (−2.254 vs −2.261 identity) but Voynich's best mapping scores −2.482 and is gibberish |
| L-002 | A homophonic (many-to-one) letter substitution into Latin, Italian or German, with Voynich word breaks kept, might read | Simulated-annealing solver recovers a 21-symbol homophonic Caesar at 100 % letter accuracy; Voynich lands 0.7–1.7 bits/char below every same-language ceiling and within ~0.1 bit of its own pseudo-Voynich null from k=8 up (Latin k=8: −3.753 vs null −3.813, ceiling −3.058) |
| L-003 | A periodic polyalphabetic (Vigenère-like) cipher could explain the oddities | Char index of coincidence 0.0766 is above English 0.0628; polyalphabetics depress IC, substitution preserves it (checked on the control) |
| L-004 | A letter-verbose cipher (several glyphs per plaintext letter) with Voynich words = plaintext words | Merging glyph pairs until h2 reaches the Latin level (~3.2–3.3) takes 28–32 merges and leaves 2.49–2.59 units per word, against 5–6 letters/word in Latin |
| L-005 | A position-blind verbose forward cipher of real Latin could reproduce the profile | It reproduces h2 (2.486 ± 0.041 vs 2.126) and the Zipf slope but fails word-length SD (4.08 vs 1.76), type count, repeats, and every line-position measure (JSD excess +0.0002 vs +0.1739) |
| L-006 | Greshko's Naibbe cipher might be the mechanism | Real Naibbe ciphertext matches h2 (2.080 vs 2.093) but shows first-glyph JSD 0.0006–0.0032 (Voynich 0.172), p-initial ×0.77–0.89, m-final ×0.96–1.14, edge-coupling excess +0.002 (Voynich +0.181), repeats 0.18 % (0.87 %) |
| L-007 | Voynich tokens could be syllables of a known-type language written plainly | Syllable-spaced controls get cross-space MI (+0.24 to +0.36) but residual word order rises to +0.25 to +0.54 (Voynich +0.042) and types fall to 1.1–2.6k (Voynich 7k) |
| L-008 | Spaces at the coupled edges are false word breaks; joining them would reveal prose-like word order | Joining y–q (J1) moves within-line token excess from +0.028 to +0.012 bits; joining the top-8 pairs raises cross MI to 0.359 and length SD to 4.81; PMI>1 joins −0.042. Dante inside a line is +0.536. Pre-registered DECISION: INCONCLUSIVE, direction against resegmentation |
| L-009 | A random-core three-slot nomenclator over a Latin herbal could reproduce the statistics (PLAN §1 promotion) | nomen_word / nomen_syll / nomen_lines give h2 3.178 / 3.764 / 3.204 vs 2.109; immediate repeats 0.00 % vs 0.84 %; only nomen_word/lines match length SD (1.59/1.60) |
| L-010 | A positional-numeral codebook could reproduce position lock cheaply | nomen_numeric poslock 1.606 (Voynich 1.661) but h2 3.32–3.66 and sd_len 0.985–1.005 (Voynich 1.788); the "codebooks reproduce length SD" sentence in TEAM-HANDOFF overstates this |
| L-011 | A Naibbe-style randomiser with random tables is a fair cipher control | naibbe_like: h2 4.080, 29,813 types, hapax 0.964 — nearly every token a hapax |
| L-012 | Timm–Schinner self-citation copying alone could explain the page | Copy-and-mutate simulators without rules: JSDfirst 0.0009–0.0052 (Voynich 0.1722), p-initial ×0.88–1.89, m-final ×0.81–1.14, repeats 2.24–5.98 % (0.87 %) |
| L-013 | The real Timm–Schinner generator (Java jar) might carry line edges | Real jar output matches h2 2.079, repeats 0.90 %, SD 1.60; its line edges reach p ×7.63 / m ×8.52 only in its own 29-line pages and fall to ×0.75 / ×0.93 when poured into the Voynich skeleton |
| L-014 | Schwartz's reuse/copy/coinage procedure reproduces "most summary statistics" | Ported procedure matches h2 2.103 and repeats 0.90 %; line edges reach only ×2.49 / ×3.57 against ×16 |
| L-015 | A section-seeded copy generator with two line rules could hit NMI, both edge multipliers and h2 together | One run hits NMI (0.291/0.327), another the ×16 edges, none all four; h2 1.76–1.82 vs 2.09; JSD(first,mid) 0.03–0.04 vs 0.17; repeats 1.2–1.6 %; seed variance hand-1 NMI 0.17–0.32 |
| L-016 | One of the already-filed producers might pass the frozen seven-band board | All five filed streams FAIL: C2 tuned misses h2/JSD/excess; b4 SIMcal misses 5–6 bands; Naibbe skeleton misses 5; D3 verbose misses all seven |
| L-017 | A word list plus an edge table plus two line rules (G1) is enough for the joint board | Held-out: seed list (L=200) misses h2 1.595, JSD 0.080, redup 2.75 %; circular (real vocabulary) misses h2 1.935 and JSD 0.099 by a hair; full skeleton misses only m-final ×7.43. Seeds s1/s2 miss only h2 + redup (not "the same three bands" as G_RESULTS says) |
| L-018 | G1's held-out misses might be a 41-page sample effect | Real Voynich passes all seven bands on G1's exact 41 held-out pages (h2 2.048, JSDf 0.1762) and in 200/200 random 41-page splits; G1 seed fails 3, circular 2, H1 4, K2 ×2/×5 fail 6/5 on the same pages |
| L-019 | The flow cipher plus the two measured line rules (H1) might joint-pass | RULED β=1.5: JSDf 0.0288, p ×7.22, m ×5.04, redup 0.12 %; DECISION: NO JOINT PASS (misses jsd_first_fg, p, m, redup) |
| L-020 | If Voynich is a flow-choice homophonic cipher, F4's frozen clustering should recover homophone classes | On Voynich class-over-token is −0.0052 (3-seed mean; null −0.0044), seed ARI 0.11, page-split 0.06, all at null; the control recovers only partly (type ARI 0.190). No DECISION line in the file; the printed classes are spelling families |
| L-021 | F4's Voynich negative counts against the cipher family | On the F3 control with m homophones per piece, truth type ARI falls 0.190 → 0.073 → 0.044 → 0.010 at m = 1/2/3/5 (7,610 types at m=3, hapax 0.70); cot gap over null 0.004 at m=2–3, under the 0.006 seed spread |
| L-022 | A richer class-recovery (J1v2, context + 2× spelling TF-IDF) that passes the m=3 gate (ARI 0.171) could yield decipherable classes on Voynich | J2 finds predictive classes (+0.018 to +0.025 bits held-out) but they are spelling/affix families (daiin/odaiin, shedy variants, ol variants); J3 collapsing 244 classes makes the a6 solver *worse* (−4.114 vs raw −3.787, below the pseudo-Voynich null −4.014) and moves metrics away from language |
| L-023 | A letter-level verbose cipher plus the M5 line layer could carry section vocabulary | CIPHER+layer: NMI 0.016/0.030; even with different Latin per section 0.008/0.007 (plain Latin same layout 0.448/0.303) |
| L-024 | The flow generator plus the M5 layer could carry word order | GEN+layer: NMI ok (0.215/0.179) but residual +0.008, h2 1.75, types ~1,900, repeats 2.29 % |
| L-025 | A homophonic word nomenclator with flow choice could hit the whole benchmark | ×2: NMI 0.370/0.270 and residual +0.045 (both go to zero on shuffled plaintext) but types 10,471, h2 2.51, m-final ×2.3; scaling to ×8 buys crossMI +0.269 and line-end JSD 0.079 at 18,624 types, h2 2.83, NMI 0.135/0.042 |
| L-026 | A stem codebook with a flow-chosen prefix slot could buy coupling cheaply | K3: types 21.5–24.7k, h2 2.79–2.87, NMI ≈0, residual ≤ +0.008; prefix not flow-chosen gives crossMI +0.001 |
| L-027 | The transferable word-order residual (F1 +0.04 on quire-split held-out pages; F3; K rows) separates encoded text from meaningless generation | N1: a meaningless flow generator with a global word-pair habit table at p=0.1 already gives +0.12 to +0.14 (3× the manuscript) with edge coupling and repeats in range; only the h2 check failed, and it penalised h2 for moving toward the manuscript. N2 (finer grid, h2 checked against the manuscript, p |
| L-028 | A lossy many-to-one nomenclator (K4) could meet NMI, residual, crossMI and line JSD inside the 7k-type / h2 2.1 budget | No K4 setting passes the registered bar, but it fails on different bands than K2/K3: shared codewords hold types at 5,076–5,613 and h2 at 2.23–2.31 *while* carrying crossMI +0.215 to +0.693 and residual +0.038 to +0.050 (both vanish on shuffled plaintext). What it misses is hapax (0.31–0.33 vs 0.68) |
| L-029 | Within-hand topic NMI (0.275 / 0.333) is strong evidence of content, "all rotation-null p=0.000" | b5 itself gives hand 2 a rotation p=0.048; the quire-block null gives hand 1 p=0.018 (the floor, 1/55) and hand 2 p=0.133; inside a single shared quire neither hand separates its sections (p=0.36 / 0.38); a real topic change in Augustine at hand-1 size reaches only p=0.09 |
| L-030 | Same-column previous-line copying (~1.9 pp excess, word-index proxy) supports Timm-style visual copying | With real x-coordinates on 223 folios the same/far ratio is 1.23 but column-specific excess is +0.41 pp [−0.10, +0.88], P(diff≤0)=0.068, significant only in section S (+1.02 pp, P=0.016); mostly recency plus line-position vocabulary |
