# Constraints map — what is established, with the connections

> Superseded 2026-10-18 16:02 PDT as the status source: see FINDINGS-MAP section 1 / D-068. Dated notes below mark dots 21 and 34 and the s94/s96 'running' lines. Other known stale lines: dot 16's 'cores do not follow each other in an ordered way (A14)' predates the A14 flip at matched K (c-419, +0.045 at K=100); dot 21's rhythm '0.156' is 0.157244 in c-328.

Stamped 2026-10-17 21:05 PDT from `date`; A1 size clause added 2026-10-17 21:09; A13–A15 and dots 8–9 added 2026-10-17 21:54 from Argon's s33/s34/s35; Sylvie's corrections applied 2026-10-17 22:08; A16–A19 and dot 11 added 2026-10-17 23:38; A3/A18 updated 2026-10-17 23:54 (s51); Phase 3 outcome 2026-10-17 22:21; s34/s44 2026-10-17 22:23; replication correction to A3 2026-10-17 22:35; s39–s42 and P4-D1/P4-U1 2026-10-17 22:44; s43 2026-10-17 22:58; dots 34–38 and section C update added 2026-10-18 12:07 PDT (s81–s95, D-063); current grades live in `workflow/FINDINGS-MAP.md`. One page. Only results that are pre-registered or hash-frozen,
verified against their result file, and not withdrawn. Every number has a CLAIMS id in
`.inventory/registers/CLAIMS.md`; the file named is the source. Nothing here reads the manuscript.
Dead leads live in `.inventory/INDEX.md` ("Do NOT resume"); this page lists only what stands.

## A. Established constraints (Tier 3 each)

| # | Constraint | Number (ZL3b unless stated) | Holds on | Source | Ids |
|---|---|---|---|---|---|
| A1 | **Line is a unit of the text, not of prose layout.** (Independently replicated 22:33 on public data and new code: c-349; reproduced from ink-detected line breaks on 127 scanned pages, c-359.) Real 15th-c. Latin prose lines show almost no line-initial profile; Voynich's is 20× larger at matched size. Size clause (s32): separable from pooled Latin verse and every verse/epic corpus at ≥500 lines; NOT separable from two single short verse/formulaic hands at 114–201 lines. | line-initial JSD excess: Voynich +0.173 (Currier A +0.135 [0.119, 0.150], B +0.218 [0.195, 0.242] at 773 lines, s44); CREMMA prose +0.008, largest prose ms +0.058; max real-line language +0.091 (Nibelungenlied); pooled Latin verse +0.094 (492 lines); Priapea/Sortes at 114–201 lines +0.13–0.14 inside the all-pages and A intervals, below B; re-lining → ≈0 | 3 transliterations; 21 Latin mss; 5 real-line corpora | results_s18.txt, results_s17.txt, results_s32.txt, results_s2 | c-306, c-313, c-316, c-317, c-330, c-331 |
| A2 | **The line-initial effect is mostly paragraph-initial gallows plus a line-start word vocabulary (y/d/t/s); the line-final set (m/g + flourish) is *not* distinctive against rhymed verse.** | paragraph-first JSD 0.515 vs 0.179 other; verse line-final excess 0.16–0.22 > Voynich 0.08 | ZL3b; 4 verse corpora | results_m5_line_anatomy.txt, results_s17.txt | m5 rows, c-314 |
| A3 | **Cross-space coupling (last glyph → next first glyph) is adjacent ordering, not position, and it is strongest in Currier B.** Correction 22:35 (independent replication + own s18 per-ms files): B is above every pooled real-line row and every prose manuscript, but short Latin verse manuscripts reach it (Priapea 0.21–0.25, Latin8236 0.17–0.18); at matched size B is NOT separable from the Priapea (s51, c-387): B couples like metrical Latin, A like prose, but B has no caesura or rhyme echo (s52, c-372), so the coupling is not a verse effect. | B +0.22–0.24 above every pooled real-line row; short Latin verse 0.17–0.25; A +0.10–0.13, above every prose control; survives (hand, section, slot) null 103–105 % | 3 transliterations | results_s20.txt, results_s30, results_s2 | c-307, c-325, c-327 |
| A4 | **Any skewed edge table regenerates the coupling.** A table fitted on A, on B, on held-out pages, or rank-mapped from Dante or a Latin syllable list all reach ≥ +0.15. Reaching the coupling by handing a table proves nothing about the family. | +0.15 to +0.67 | — | results_s2 Part 2B, results_s30 Part 1B | c-308, c-325 |
| A5 | **Within-line word-length ordering.** Neighbouring words inside a line have related lengths; the effect survives removing repeats (96 %), has <3 % cross-line share, and none of the evaluated real-line language or human-gibberish corpora reproduces it (the gibberish pool is 38 writers, ~10k tokens, short samples, and the 64 control files include related variants: strong against the evaluated controls, limited generalisation; Sylvie review 22:07). | within-line Moran I 0.157 vs line-shuffle q99 0.081 (p 0.001); gibberish 0.098 (p 0.73); Latin pools −0.03..+0.04; verse −0.12..−0.15; best generator 0.129 | 3 transliterations; 64 sidecars | results_s21.txt, Daybreak c-320/c-329, results_n5/n7 | c-295, c-305, c-320, c-328, c-329 |
| A6 | **Character model beats word list on held-out pages** (the text is more predictable from characters than from its word inventory), outside every encoded, meaningless and language control; sign shared only by human gibberish. | CHARWIN +0.094; languages −0.45..−0.74; gibberish +0.36 | 3 transliterations | results_n5.txt, results_s17.txt | c-293, c-315 |
| A7 | **Held-out word-order residual exists and a powered 7k-type habit generator does not reproduce it.** | F1 +0.046 [+0.036, +0.056]; generator +0.027 (2 of 3 transliterations miss) | ZL3b, IT2a (RF1b matches) | results_n6.txt | c-301 |
| A8 | **Hand-1 section vocabulary holds against the powered generator and a bifolio null**, but sits at the 1/55 permutation floor and cannot be ranked under correction. | NMI 0.275, bifolio p 0.000; generator 0.09 | 3 transliterations | results_n6.txt, results_p1_bifolio.txt | c-302, c-291 |
| A9 | **Entropy and type counts are unit-specific; the edge and coupling anomalies are not.** | h2 2.10 (EVA) → 2.38 (glyph+) → 2.51 (GC2a); types 4.5k–8.4k under boundary variants; jsd_first ≥ 0.18 and coupling positive under all | 5 alphabets, 3 boundary rules | results_s2 3A, results_p2.txt, results_s30 2A–2B | c-298, c-325, c-326 |
| A10 | **Within-manuscript widths are known** (41-page splits), so a "match" now has a stated margin. | jsd_first [0.145, 0.216]; coupling [0.148, 0.209]; Moran [0.109, 0.170]; h2 [2.054, 2.152] | ZL3b | results_s15.txt, s15_ranges.json | c-312 |
| A11 | **Period-practice bound.** 15th-c. keys: ~80 % of nomenclatures under 100 entries; 96 % use nulls; no period code reaches 7k types. A 7k-type ciphertext is period-plausible only as a verbose homophonic cipher. | Timm bound: 1.528 letters/token → 53k plaintext letters | literature + ZL3b | B-prior-art §5, results_s2 2C | c-309, L-107 |
| A12 | **Gibberish family on the board: generation still favoured; A/B agree.** | G favoured all/A/B; X-vs-L size-dependent | PREREG-v2 rule | results_n7.txt | c-303, c-304 |
| A13 | **The within-line rhythm (A5) is broad across the manuscript and localises to the affix slots under the project's segmentation.** Present in Currier A and B (B stronger), hands 1–3 and 5, and the paragraph sections; removing SlotSegmenter prefix+suffix material removes ~96 % of the measured excess and preserving their sequence keeps ~90 %. Caveats (Sylvie review 22:07): the segmenter was fitted on the same transcription, its cores/affixes are operational units, and the ablation changes the statistic's normalisation, so "96 % removed by this ablation" is supported and "96 % of the cause" is not; support is broad, not uniform over every hand/section/transliteration. | A 0.117, B 0.169; affix sequence keeps 90 %; cores alone p 0.228 | 3 transliterations | results_s33_line_scales_interlock.txt (Argon, re-run 21:38) | c-335, c-336 |
| A14 | **[FLIPPED 2026-10-18 03:27 (s80, c-419/c-420): at matched inventory size cores DO order, weakly (+0.045 at K=100), below languages and mostly below letter-in-core ciphers; the full-inventory negative sign occurs for real languages too. Restated as finding F-12 in FINDINGS-GRAPH]** **[AT RISK 2026-10-18 02:58: flips positive under Zattera's segmenter with ~100 core types (s76, c-413); may be a sparse-inventory artifact; size-matched test s80]** **The largest excess word-to-word dependencies concentrate on the next word's prefix; core→core ordering sits below its shuffled baseline.** Not "99 % of sequential information": the next-prefix column is ~86 % of the positive excess entries, pairwise MIs overlap, and a negative excess means below the within-line shuffle, not negative MI or meaningless cores (Sylvie review 22:07). Section vocabulary is carried by prefixes over a shared core pool (top-50 cores cover 80–85 % of tokens). | next-prefix column +0.317 bits; C1→C2 −0.0315 (z −5.14); prefix NMI 0.292; MI(sec; P\|core) +0.055 | 3 transliterations; A/B; hands | results_s34_morphology_syntax_geography.txt (Argon) | c-337, c-338 |
| A15 | **Physical layout: the margin line is the unit; sheets cluster on glyph rates; labels are reachable by a class-conditioned generator.** Drawing gaps inside a line are weak edges, not full ones (revised 2026-10-18 01:33 after Steckley & Steckley 2024 and a re-read of s35 2C: before a drawing -m endings 2.42 % vs 0.92 % mid-line; after it o/y/d/s starts 74 % vs 58 % at true line starts; but gallows starts 0.27 % vs 22 % and -m/-g 2.8 % vs 17.7 % at the margin); bifolios cluster on h2 and glyph rates but not on coupling or Moran; same-leaf recto/verso closer than conjoint sheet; m1 recency survives bifolio nulls; an 837-type label generator reproduces q1 (it was conditioned and tuned to the label statistics, so it shows reachability, not the historical production method). Physical rows use transcription-aligned boxes; the pixel-derived boundary test is a separate, not-yet-run step. | m/g-final 2.8 % vs 17.7 %; h2 bifolio z +6.80; recency z +8.82; q1 z +5.11 | ZL3b (+RF1b/IT2a parts) | results_s35_physical_codicology_quire_network.txt (Argon) | c-339, c-340, c-341 |
| A16 | **The cores carry the content-like order, and they order like words, not letters.** The held-out word-order residual lives in the core stream (affix streams carry none); core→core ordering sits below its shuffle, which planted letter-in-core ciphers never do (+0.06..+0.15) and word-level codes and Dante do. | core-only F1 interval excludes 0 on 3 transliterations; Voynich cores −0.0315 vs letter-in-core +0.06..+0.15 (12/12 clear) | 3 transliterations; 6 plaintext languages | results_s39.txt, results_p4d1_core_order.txt | c-351, c-355 |
| A17 | **A two-layer producer reaches most of the board, whatever its cores are.** An ordered affix wrapper over a core pool reaches F1 on 9/9 cells, the rhythm on ZL3b and the character-model sign on ZL3b/RF1b, with copied cores and with Latin-stem cores alike. Wrapper fitted on Voynich affix transitions (rhythm partly by construction). | F1 +0.055..+0.073; Moran G 0.168 / L 0.156 vs 0.157 (ZL3b); IT2a CHARWIN missed by both | 3 transliterations × 3 seeds | results_s36_two_layer_operator_core.txt (Argon) | c-361 |
| A18 | **Neither layer is padding; tested framings fail.** Plain ciphers with one layer as nulls fail (s43); edge-pitch music (s24), glyph-class superimposition (s34), liturgy/charms, copied-without-understanding drift and historical conlangs (s37) all fail the joint battery. Independent superimposed streams fail a selector that passes its planted control (Argon s51, c-370): frame and core are coupled within words (+1.79 bits). | e.g. liturgical Moran −0.055; drift lifts core Moran to 0.090 vs 0.035 | 3 transliterations; CREMMA genres | results_s43.txt, results_s24.txt, results_s34.txt, results_s37_affix_cadence_and_genres.txt | c-332–c-334, c-346, c-357, c-363, c-370 |
| A19 | **The word unit is physical.** Ink gaps on 127 scanned pages agree with the transcribers' certain spaces (κ 0.87; 0.81 where pairing is not by construction); uncertain spaces (commas) are physically intermediate gaps; gallows pen-lifts are not gaps, so the s38 gallows-split stream (Moran −0.074) is not the scribe's segmentation. Gallows words do interrupt the cross-space coupling (s37). Comma treatment must be stated: it moves the coupling (c-350). | κ 0.866 [0.845, 0.884]; medians 1.86 / 0.94 / 0.37 of threshold | 127 Yale pages, ZL3b | results_s47.txt, results_s45.txt, results_p4u1_space_regimes.txt | c-384, c-385, c-386, c-356, c-364 Scope (2026-10-18 02:33): the ink gaps come from s45's alignment to ZL lines, so this is agreement with the transcription's spaces, not transcription-free boundary discovery (s47_ink_space_agreement.py, results_s47.txt). |
| A20 | **Operational slot profiles are associated with Davis hand.** On the reused 166→41 split, hand-trained models distinguish Hand 2 from Hand 3 inside Currier B. On Top-50 cores shared in training, Hand-2→Hand-3 transfer costs `+0.643 / +0.604 / +0.700` bits and reverse transfer `+0.264 / +0.283 / +0.177`; symmetric penalties are `+0.426 / +0.414 / +0.415` (`p=0.0020` under 500 unstratified page-label permutations). H2-vs-H3 classification is `19/20 / 18/20 / 16/20` on Top-50 cores and `18/20 / 19/20 / 16/20` on all tokens. Hand remains confounded with section, quire, layout and core mixture, so this is not a causal or linguistic per-scribe grammar. The pages are held out within s60 but reused project-wide; the within-hand 80/20 check also reuses the global segmenter and slot vocabularies. | Top-50 `D_sym +0.426/+0.414/+0.415` | ZL3b, RF1b, IT2a | `results_s60.txt`; `s60_scribe_slot_rules.py` | `c-506`, `c-507` (supersede `c-500`, `c-501`) |
| A21 | **Under s63's operational parser, many rare/unseen core strings satisfy alternative-boundary or two-core-split heuristics; this does not establish their historical origin.** Exclusive B1 is `82.6–85.1%` of first-on-page non-top-20 core events, but combines candidate reparses with configured boundary-unit shifts and is also high in the s59 C-minus control (`60.6–64.2%`) and character shuffle (`45.4–46.0%`). Among strictly unseen held-out tokens, exclusive B1 is `64.2–71.7%`, exact two-training-core string splits are `20.1–25.2%`, and uncaptured distal strings are `5.8–6.9%`. S63 inspects no comma locations. Approximate density matching explains part of the old N3 contrast, but no 73% share was computed; a joint structural mixture improves held-out cross-entropy by `0.075–0.157` bits/core without identifying the responsible component. | B1 `82.99%` for ZL3b rare events | ZL3b, RF1b, IT2a | `results_s63.txt`; `s63_rare_core_boundary_and_subglyph.py` | `c-508`, `c-509` (supersede `c-502`, `c-503`) |

## B. What the constraints say together (the dots)

1. **A1 + A5 + A3** describe one object: a text whose *lines* carry structure at three scales, the
   line start (vocabulary), the inside of the line (word-length rhythm), and the word boundary (edge
   coupling, in B). None of the three is reproduced by scribes writing real prose lines, by rhymed verse,
   or by volunteers writing gibberish on real lines. Whatever produced the text produced it line by line.
2. **A4 kills the easiest explanation of A3.** The coupling is real ordering, but it is *cheap*: any
   skewed last/first table makes it. So A3 constrains the mechanism only through *what table* and *why
   it differs between A and B*, not through its size. A is language-like on this statistic; B is not.
3. **A5 + A6 + the gibberish sign** point the same way: the two signatures that no language has are the
   ones human meaningless production partly shares (sign of A6, whole-stream value of A5), yet the
   *within-line* ordering of A5 is beyond gibberish too. The producer is disciplined in a way neither
   language nor free gibberish is: a procedure with a per-line rhythm.
4. **A7 + A8 pull the other way**: there is held-out word-order structure and a hand-1 section vocabulary
   that a 7k-type habit generator with the right entropy does not fake. That is the residue a content
   hypothesis can still stand on, and it is thin (A8 at the floor).
5. **A9 + A11** fix the shape of any cipher candidate: 20–30 glyphs, ~7k word types with 68 % hapax,
   h2 ≈ 2.1 only under EVA, a plaintext of ~50k letters if verbose. A word-level code at 7k types is
   unhistorical; a verbose homophonic cipher with nulls is the only period-plausible encoded shape, and
   it must also produce A1, A5 and A7.
6. **A2** removes a false target: line-final flourishes are what verse does too. Entrants should not be
   credited for line ends.
8. **A13 + A14 + A6 are one picture: a two-layer word.** A core drawn from a shared pool, and an operator layer
   (prefix, suffix) that carries the within-line rhythm, the word-to-word coupling and the section vocabulary.
   Every line-level signature we have lives in the operator layer; the core layer is close to orderless
   (different cores do not follow each other in order, though the same core recurs nearby: dot 16). A mechanism now has to produce an operator stream with per-line cadence
   over a core stream with none. That is the shape the superimposed-streams check (s34_superimposed_streams,
   queued) tests directly, and the shape any cipher or generator entrant must now reproduce.
10. **The two layers have different jobs (22:45; s39, s40, s41, P4-D1).** The cadence lives in the affixes; the only
   content-like ordering (the held-out word-order residual) lives in the cores, and the cores order like words, not like
   letters (planted letter-in-core ciphers sit far above shuffle, Voynich cores sit below it; only word-level codes reach
   it). The prefix stream is itself strongly ordered and matches neither Latin nor any generator. The coupling runs from
   core-final glyphs into the next prefix in both Currier languages. Best-supported shape: a lexical core stream under a
   positional operator layer (Sylvie's candidate 2, with word-level cores). Plaintext in the affixes with null cores (s43 N1) reaches F1 but not CHARWIN or the rhythm, and puts F1 in the wrong layer; plaintext in the cores with null affixes (N2) reaches nothing. Neither layer is padding.
9. **A15 closes the "layout artefact" family of objections** from the physical side: drawing gaps carry only part of the edge marking (no line-start gallows, few
   line-final -m/-g, but more -m and o/y/d/s than mid-line; revised 2026-10-18 01:33), so the full line signatures belong
   to the scribe's margin lines. They do not inflate A1/A5: excluding or splitting at gaps moves them at most 6 % (s65, c-409). Labels drop out of the content case
   (reached by a meaningless class-conditioned generator), which thins A8 further.
7. **Phase 3 outcome (22:19, results_s35.txt): tie at this design.** The cipher mechanism (s10) is the first entrant
   to reach the character-model advantage (A6) and the generator (s28) the first to reach the word-order residual
   (A7), each failing the other; neither approaches the within-line rhythm (A5: 0.00 and 0.06 vs 0.157). No
   registered lean; the within-line rhythm stays the one property no built mechanism reproduces.
   | entrant | CHARWIN | F1 | Moran | source |
   |---|---|---|---|---|
   | s10 cipher (L) | positive, reached (HOLD) | missed (FAIL, powered) | ≈0, missed (HOLD) | results_s10.txt, results_s35.txt |
   | s28 generator (G) | negative, missed (HOLD) | reached 2/3 (FAIL, underpowered) | +0.06, missed (HOLD) | results_s28.txt, results_s35.txt |

## B2. Prior art the map builds on (not claimed as new)

Word-length autocorrelation and the human-gibberish comparison: Gaskell & Bowern 2022. Structured word components: Stolfi's
grammar (2000), Zattera's slot model (2022). True line endings vs drawing interruptions: Ponzi 2019. What this project adds is
the quantitative package (matched nulls, ablation, reconstruction, subgroup comparison, pre-registration); a first-ever claim for
that package is not established (Sylvie review 22:07; unverified against the sources by this session).

Prior-art check 2026-10-18 01:48 (team register `lab/workflow/research/published-findings-register.md`,
lines 17-18, plus our copy of Rozanova & Temerev 2026): (1) Within-line word-length dependence with cross-line pairs
dropped (A5) is not found in the sources read. Gaskell & Bowern's wordlen_autocorr runs over one flattened vector, and the
1944 Friedman transcript dropped line ends. (2) The analogous separated contrast for edge-glyph coupling IS published:
Rozanova & Temerev score shuffle-corrected edge information at intra-line separators vs continuation line breaks
(`data/external/papers/rozanova_temerev_2026_arxiv_2608.17096.txt` lines 435-464; line break -0.036 [-0.072, -0.002]).
So A3/A6-style "the coupling stops at the line break" is prior art, while the word-length form is not found (bounded search).
(3) Reddy & Knight 2011 report a residual next-word gain of 8.85 % relative for Voynich B (English 151 %), the closest
published analogue of our F1 residual.

11. **A17 is the turning point for method (L-130).** The board measures the two-layer architecture, not the source of the
   cores, so cipher-vs-generator entrant pairs under a shared wrapper tie by construction. Progress now needs tests outside
   the board: identifiability on known texts (s49), solver feasibility on planted ciphers (s50), an image-based anchor map
   (s48); the word unit itself is now settled as physical (s47, A19).

12. **A/B is also a scribe split (c-374).** Davis hand 1 writes all the Currier A; hands 2 and 3 write B. No hand writes both at
   size, so every A-versus-B difference on this map is equally a scribe difference. Alphabet choice does not move the anomalies
   (c-373, A9).

13. **No internal anchor (D-053).** Pharma sketches do resemble their herbal partners in images (s53, P 0.0005), but their labels
   share no text with the partner page (s54), even though the test finds a strong planted link. Labels are not copies of
   the plant's herbal text.

14. **Where the manuscript lands among known text classes (s49, c-390–c-392).** Between a word-level code and a procedural
   generator, and far from verbose letter ciphers, natural language on real lines, and human gibberish. The statistics separate
   families as built (21/24) but not producers tuned to Voynich, and not generator-vs-message twins. Together with A16 (cores
   order like words), the live space is a word-level lexical system or a generator; letter-level encodings of a known
   language are disfavoured by three independent tests (P4-D1, s43, s49).

15. **Outside the taxonomy (s55, c-393/c-394).** Without line-edge features, code and generator cannot be told apart, and the
   manuscript lies outside both on three wrapper-free features together: its core→core sequential order sits further below shuffle than any built text, its cores recur across pages less than any
   code, and its prefix stream is more predictable than any code or generator. Any mechanism must reproduce that joint profile.

16. **Local memory (s56, c-382/c-383; corrects an earlier 'cores repel' reading).** The same core recurs at short range more
   than chance, strongest for rare cores (×1.76) and inside lines, decaying over about 20 tokens. Natural language and word
   codes do the opposite (adjacent repeats are rare). Different cores do not follow each other in an ordered way (A14), but
   recent cores come back. That is a producer with local memory, copying and varying recent forms, which favours candidate 1
   (self-citation) over a word-level code and gives any generator a quantitative shape to match.

17. **Argon's s52–s54 (held-out clean, stubs OK; Argon ids c-375–c-381).** No antidotary, alphabetical or zodiac-planet
   structure: every planted comparator is recovered and the manuscript is null on all six (s52_p4comp1). Its errors look
   like composition, not visual copying: confusion enrichment sits in the generator range, below copied Latin, and in-line
   word repeats match the bag-of-words rate (s53_p4a1_p4e1). A length-blind wrapper reaches only about 35 % of the
   within-line rhythm, so the rest needs explicit persistence of length state from word to word (s54_core_syntax). That
   persistence is consistent with the local memory in dot 16.
   *Update 2026-10-18 12:07 PDT (F-21):* the composition-not-copying reading is now SINGLE and at risk. Argon's s86 held it on only
   8/6/6 of 15 quires, and s95 (c-436) shows the per-quire statistic cannot separate copied from composed Latin, so the
   split evidence neither supports nor refutes it; it no longer weighs strongly against copying without understanding (H-10).

18. **Local memory is not the producer (s57, c-396/c-397).** A copy-and-vary model fitted to the burstiness of dot 16
   reproduces that burstiness and the vocabulary size, then fails all six predictions on the held-out pages in all three
   transliterations. It produces no within-line rhythm (0.02 against 0.16), no prefix-stream order and the wrong
   character-model sign. Repetition is a property of the core layer. The order lives in the slot layer, so the next test is
   the two-layer wrapper with these cores, predicted on held-out pages (s58).

19. **The two layers are not independent (s58, c-398/c-399).** A counted affix wrapper fitted on the training pages
   gives the manuscript's positive character-model sign on held-out pages, so that sign belongs to the affix layer. It does
   not give the rhythm, the prefix persistence or the distinct line starts, and choosing affixes without regard to the core
   makes about 65 % too many word types. The scribe chose prefix, core and suffix together, with a state that lasts longer
   than one word. That matches s54's tight affix-core lock. Next test: a joint word-level choice (s61).

20. **Rare cores are only weakly derived from nearby forms (s59, s62; c-400, c-401, c-404).** On fresh pages, a new rare
   core has a one-glyph relative nearby about 2 % more often than chance. That is real but small, a seventh of a
   copy-and-edit producer and below ordinary Latin or Italian. Herbal pages show none. Exact repeats cluster locally (dot 16),
   but new forms mostly do not come from editing the previous words. (s59's tentative 'no excess' is superseded.)

   > Note 2026-10-18 16:02 PDT (dot 21): this is the F-23 exclusion. D-068 (s101, c-454, L-224): its LOQO criteria recover planted true producers on only 0-4/15 folds, so the exclusion is uninformative; F-23 is at-risk until roach r13 replicates. See FINDINGS-MAP section 1 / D-068.

21. **No lexical producer predicts held-out pages (s57, s58, s61; c-396-c-399, c-402/c-403).** Three producers were
   fitted on 166 pages and held to the same six predictions on 41: local memory 0/6, an independent affix wrapper 1-2/6,
   joint whole-word choice with longer prefix state 0-1/6. None reaches the within-line rhythm (best 0.08 against 0.156).
   The character-model sign comes out positive only when words are built from parts, and negative when whole words are
   drawn, yet free assembly makes far too many words. So the scribe built words from parts under tight constraints, and
   the line rhythm comes from a state none of these contexts carry. Producer building on this split has stopped (D-056).

22. **The per-token random-table cipher is excluded (s64, c-405).** Greshko's Naibbe, rebuilt from his own tables,
   leaves the prefix stream orderless. Voynich's prefix stream is the most ordered of any class tested, so any scheme that
   picks its affix table afresh for each word is out. A variant that keeps one table along a line or page is untested.

23. **Four producers, one shared gap (s67, c-406/c-407).** Tested quire by quire, a producer that builds words from
   parts, with prefixes and suffixes chosen by the core's class and a fitted length rhythm, still fails 14-15 of 15
   quires. Its ablations confirm two rules: the affixes depend on the core's class (this fixes the word count and the
   character-model sign), and the length rhythm can be planted but not predicted. Two properties stay out of reach of every
   producer: the prefix stream's own order (+0.10 bits, never above 0.04 in any model) and the narrow vocabulary each quire
   uses. These are now the central things to explain.

24. **Parisel's folio switch is the scribe (s68, c-408).** The o/e choice after ch/sh looks like a two-state switch per
   folio, but inside each scribe the folios vary smoothly. The two states are hand 1 versus hands 2 and 3, which joins
   dot 12: what is called Currier A and B is, on every measure so far, a difference between scribes.

25. **What the prefix stream remembers (s69, c-410).** Each word's prefix depends on its own core and on the previous
   word's prefix, and on almost nothing further back. That one-word memory restarts at every line break, passes through
   gallows words weakened, and leaves only a faint line-level trace. No code or generator we built shows it. The one
   reference class that does is Rugg's table-and-grille, which has five times too much. So the slot layer behaves like a
   short-memory rule applied word to word within the line, which is what the four producers lacked.

26. **The solver can read the family; the family cannot make the manuscript (s50, c-411/c-412).** Our solver recovers
   planted verbose-homophonic ciphers at every rung, up to unknown segmentation and the closest buildable match. But no
   member of that family reproduces the manuscript's letter predictability, core order and line rhythm together. That is
   evidence against this kind of encipherment as built, not proof, and it says nothing about whether the manuscript can be
   read (D-057). With A20, slot profiles are hand-associated (not shown to be causal per-scribe grammars); with A21, many 'rare cores' are artefacts
   of where the segmenter puts the boundary.

27. **The slot picture mostly survives a second segmenter; core order may not (s76, c-413).** Under Zattera's published
   12-slot model the prefix memory, its line reset, the core-borne prefixes and local core repetition all hold, though the
   prefix memory is much weaker. The claim that different cores follow no order (A14) reverses: with about a hundred core
   types, cores do order. Our segmenter makes thousands of core types, and the order statistic may simply be blind at that
   size. Until s80 checks it at matched size, A14 and the conclusions that lean on it (P4-D1, s50) are provisional.

28. **Independent replication on roach (r3, c-414).** With its own code and segmenter, roach confirms that prefixes and
   suffixes depend on the core, and that the word-length rhythm lives inside lines and stops at line breaks. Prefix order
   replicates in direction but is smaller, as under Zattera's segmenter (dot 27). Its size depends on where the prefix
   boundary is drawn, but its sign does not.

29. **Core order is weak, not absent, and far below any letter cipher (roach r4, c-418).** Blind, at matched inventory
   size, the manuscript's cores show a small positive order with a few dozen classes and none at a hundred. Planted ciphers
   that put plaintext letters in the cores show 6 to 50 times more at every size. The negative control was not clean, so
   "below shuffle" (A14 as worded) cannot be claimed. The exclusion of letter-in-core ciphers rests on the relative gap,
   which holds.

30. **Core order flips (s80, c-419/c-420).** Pooling cores to the same inventory size for every text shows that
   Voynich cores do follow each other in order, weakly: less than any of six languages and less than the planted
   letter-in-core ciphers at 100-200 classes, but inside the cipher range at 50. The old 'below shuffle' came from a
   statistic that reads negative for Dante too. By the pre-registered rule, letter-in-core ciphers are reopened.

31. **Reading order barely matters (s79, c-421).** The rhythm, core repetition, prefix memory and its line reset survive
   any page order, line order or direction; line-edge effects mirror. Only the page drift and a cross-page carryover
   need the bound order, mostly within quires.

32. **Plain ciphers fail for new reasons (s82, c-427).** With core order measured correctly, ciphers that hide letters in
   the cores, and verbose ciphers with filler cores, can produce the weak core order. They still fail: their glyph
   sequences are far less predictable than the manuscript's, and they have no line rhythm and no prefix memory. A
   cipher carrying text would need all three added.

33. **Second independent replication (roach r5, c-425/c-426).** The cores carry held-out word order on 13 of 15 quires,
   but so do the prefixes and suffixes, so 'the affixes carry none' (A16) goes. Same-core repeats cluster inside lines
   (1.32, Latin 0.13) and fall below chance across line breaks.

*Dots 34–38 added 2026-10-18 12:07 PDT from s81–s95 and the lead audit D-063. Grades and contested status: `workflow/FINDINGS-MAP.md`.*

   > Note 2026-10-18 16:02 PDT (dot 34): F-34 is CONTESTED, not CORROBORATED (roach r6 0/15, s98; D-067, L-212), and X-01 is at risk. The line-held table was replaced by a drifting state (D-067), and the drifting table then failed 0/15 (r9, L-217); working model 'multi-scale state'. See FINDINGS-MAP section 1 / D-068.

34. **The slot layer has a working mechanism; the cipher arm is closed (s81 c-428, s83 c-430; D-061).** A line-held affix
   table reproduces the prefix memory on held-out quires (F-34, CORROBORATED, rests on the at-risk segmenter X-01). Every
   cipher built with plaintext letters or syllables in the cores fails held-out quires: plain (s82), homophonic under a
   line table (s83) and sticky Naibbe (s81). Homophone cores give too much core order and too little repetition (F-39);
   after D-063 that mechanism is CONTESTED because under Zattera and Seg_Affix2 the cipher's core order falls below the
   manuscript's (s88). The exclusion itself (0/135 predictions) stands.

35. **The core layer matches no reference class (s87, s89, s90; c-431–c-434; F-40).** No natural, list, ritual, tabular,
   gibberish or constructed text tested reuses words inside a line the way the manuscript does, and no generator has its
   weak order. Argon's s92 physical-ink line for this does not discriminate (D-063), so F-40 stands on s87/s89/s90/r5
   with the segmenter assumption X-01 at risk.

36. **A per-line core pool gets half the signature (s91, c-435; F-41).** Fitted on training quires, it reproduces in-line
   reuse and cross-line avoidance on 45/45 held-out quire runs, but the full four-part signature on only 21/45 (too
   quire-local) and the slot battery on 0–1/15. [D-064, 2026-10-18 12:10: s93 not admissible — its result file was overwritten by an edited re-run; the frozen run failed CALL_3] Argon's s93 (c-534) reports a shared-lexicon pool with line-sticky affixes
   reaching the core signature on 14–15/15 folds; s94 (running) tests one book-wide lexicon with a fitted quire tilt.

37. **Two earlier constraints are contested (D-063).** Dot 14's 'outside both word code and generator on wrapper-free
   features' (F-26) and the s75 exclusion of transposition and single null-glyph schemes (F-37) failed their own
   pre-registered matched-K calls in s85 (C3A, C3B False). Both are CONTESTED until Argon's amended s96 (P-28) is filed.

38. **F-21 is underpowered (s95, c-436).** See the update under dot 17.

## C. What is still open that bears on the picture

Updated 2026-10-18 01:17 PDT. Closed since the last revision: O-045 (two-layer producers reach F1 at manuscript size, s36 c-361), O-048
(lines s45, words s47), O-051 (repaired selector, no independent stream, s51), and the s37 framings (liturgy, copied
without understanding, conlangs: all fail, c-363).

Still open:
- **Why each quire's vocabulary is narrow** (Argon's s66), and whether a weakened table-and-grille mechanism reproduces the
  one-word prefix memory of dot 25 on held-out quires. The line rhythm can be planted but not yet predicted.
- **s50 done:** solver power shown on planted controls; no matched L4 could be built (dot 26). Open: language ID and a
  wider L4 construction aimed at the h2/A14 conflict; the Voynich run stays gated on a matched L4.
- **How rare-core strings arise historically remains open.** S63 shows that many are sensitive to SlotSegmenter's operational boundaries and that exact two-core string splits are common, but it inspects no commas and establishes no production mechanism. The decisive follow-up is independently fitted segmentation, alignment against actual comma/ink-gap positions and preregistered component-ablation prediction on new material.
- **Whether s60's hand-associated slot profiles persist after section/quire matching and a clean nested fit.** The current Currier-B permutation is across pages rather than within section or quire, and the reused 41-page and within-hand 80/20 evaluations are not untouched validation. A causal per-scribe claim remains open.
- O-043 (the producer behind the affix-borne coupling; s58 bears on it) and O-024 (null glyphs, untested beyond s31).
- Musical notation (s24, D-046) and glyph-class superimposition (s34, s51) are tested and not supported.

*Update 2026-10-18 12:07 PDT:* closed since 01:17 — the quire-vocabulary question (s66), the weakened grille on held-out quires (s71: 0/15),
language ID and the wider L4 (s72), O-024 (s75, now CONTESTED as F-37). Open now: what produces the core layer with weak order
and mild quire locality (s94, running [superseded 2026-10-18 16:02 PDT: s94 stopped at its fixture, L-221]); whether F-26, F-37, F-39 and F-34 survive the D-063 amended tests and whether the
segmenter assumption X-01 can be discharged (Argon s96, P-28, running [superseded 2026-10-18 16:02 PDT: s96 rejected, D-065]); a whole-corpus power check for F-21 (s95). Live list:
`.inventory/registers/OPEN.md` and `workflow/FINDINGS-MAP.md` §6.

## D. What no number here does

None reads a word. There is no independently grounded crib, nothing predicts content on held-out
material, and planted-key recovery works only for cipher families the text has already failed (a6, F3,
F4). Tier 1 needs an anchor this pipeline does not supply.
