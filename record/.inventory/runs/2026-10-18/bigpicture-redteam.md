# Big-picture red team: is the strategy sound?

Stamp: 2026-10-18 20:54 PDT (from `date`). Read-only; this is the only write. Sources: the PLAN.md stage line and phase log 15:43-20:45; FINDINGS-MAP (generated 20:45); the GRAPH `pending` table; D-066 (a)-(t-A0); the learnings-audit top 10; audit-external-D and audit-external-E §2; vparse.py; tools/gibberish_to_meta.py; the s90 header; L-320..L-330. "Unverified" means not checked on disk.

## 1. Are we in the weeds? Yes.

There are 356 `results_*.txt` files. Since 13:00, five designs have stopped at a fixture or data gate: s94, s108, s110, s112 and s105. Most other runs fit producer families to a joint profile. That kind of test cannot separate meaningful text from meaningless text. Today's one result that bears on the goal is s115-A0 (c-559). It shows that our meaning-side nulls had about 40% power.

| item | gain toward a reading | cost | call |
|---|---|---|---|
| s115 A1b, then A2 | highest: the only live anchor route | low, then medium (power at r 0.09) | **continue** under the A0 gate |
| MSI f17r/f116v | medium: new evidence that does not depend on a transcription | low | continue |
| glyph full run | medium-high: the only test of EVA (2c) | medium (GPU) | continue as an alphabet gate |
| roach mirror O-067 | integrity only | low | continue |
| s113 G2 envelope | low: "a procedure can make this" was already shown by Timm and Rugg | medium; s110 failed its fixture | **stop/park** |
| roach r14 grille fitter | low: H-05 is already 4.0/0 | roach time (scarce) | **deprioritise** |
| roach r15 (blind s114) | low: writing sessions alone predict quire drift (2e) | roach time | **stop** |
| s105 (hold) | high if unblocked: plant identities are cribs | blocked by data | hold; acquisition only |
| s108 (hold) | low | none | **close** |
| contact map O-068 | medium: reading order | v1-v5 failed every gate | keep parked |

## 2. Blind spots that could invalidate many results at once

**a. ZL3b centrism.** X-09 is marked "verified" because results agree across ZL3b, RF1b and IT2a. ZL3b and RF1b share Zandbergen's lineage, and all three are EVA. That is about 1.5 independent readings, all in one alphabet. Exposed: every finding graded `data` on agreement between transliterations. How far RF1b and ZL3b differ token by token is unverified.

**b. Segmenter dependence (X-01): this one bites.** X-01 is at-risk and 20 findings rest on it. Its only decider, P-28 (s96), was rejected (D-065), and no replacement is scheduled. L-190 shows the core collapse depends on the segmenter. Audit D found 39 to 2,920 stem types depending on the rule. Most exposed: F-39..F-50, the quire-locality "key" (L-321), and the G1/G2 gates.

**c. EVA as an unproven alphabet: this bites too.** h2 depends on the alphabet, and F-08 concedes as much. Yet the band h2 in [2.023, 2.234] gates G1 and G2, and h2 drives F-25, F-35, F-39, F-45, F-47 and the cases against H-02, H-03 and H-17. Scan-derived glyph counts agree with EVA per word only 0.337 of the time (L-325). The GC2a and glyph+ sidecars are on disk, but the battery has never been re-scored under a merged alphabet as a gate.

**d. Code from the same tree.** Roach is the only `impl` source. Daybreak and Argon lines import vparse, metrics_new and s70 (audit D). Several TRIANGULATED grades get their `impl` axis from a single roach run. A bug in a shared definition would pass every one of those replications. The lead and roach estimators already disagree on Rw1 (z +2 vs +21, L-321), and nobody has explained why.

**e. Nulls that keep the layout.** s114 permutes quire labels within hand x section, which treats folios as exchangeable. It ignores the resemblance between folios written in the same session, ink or exemplar. Any session-level drift therefore gives DRIFT_REAL, so p 0.0001 says almost nothing about mechanism. F-50 is exposed.

**f. Labelling by the same model.** s115-A1 is two passes of one model (L-328), so its kappa measures consistency, not validity. The s101 vision labels were invalid (L-199). A1b has to label blind to A1, and one category should be checked against a published catalogue.

**g. The gibberish control: this bites.** `tools/gibberish_to_meta.py:39` re-wraps the handwritten Gaskell & Bowern lines at 8 tokens per line. The source files keep the writers' own lines, about 4 words each, so the re-wrap destroys the line structure. n7, which counts against H-08, imports these re-wrapped files. s90 used the real lines, but its gibberish legs are unmatched and descriptive: 79-480 tokens per writer. Real-line gibberish gives word-length Moran I +0.119, close to Voynich's +0.141, while every language comes out negative (c-315). So H-08's 3.5 against-weight leans on F-04, and real gibberish reproduces F-04.

**h. Multiple testing.** BH is applied only within a round (criterion 7). Nothing corrects across roughly 130 runs. The map also adds up findings that share data, alphabet and segmenter as if they were independent: H-01's 17.5 is perhaps 4-5 correlated observations of one EVA text. The borderline calls are exposed: db-S127 at p = 1/31, the floor of its null, and s114 Test B at p 0.045.

**i. vparse: no repo finding is affected.** `vparse.py:10,31` defines `load(strict_spaces=False, path=DATA)`, and DATA is ZL3b. The danger is a positional call: `load(str(path))` sets strict_spaces instead of path, which deletes commas and silently loads ZL3b. That happened in Argon's first pillar5 run (audit E §2). My repo grep finds no positional calls. Audit E notes the limit: per-transliteration blocks were not diffed. Fix: a keyword-only wrapper in a new module (D-071 bars editing vparse).

## 3. Standing findings I would bet against

1. **F-33 (TRIANGULATED, standing).** A0 found its null uninformative about meaning, but the map still counts F-33 against H-06. F-20 and F-44 are in the same position (F-44's MDE is 0.088, against a true r of about 0.09). All three should be at-risk.
2. **F-40, "no human writing reuses words in-line."** The gibberish leg is underpowered (2g), and Llull already breaks the claim (F-49, db-S138). Litanies, charms and recipe formulae ("ana ... ana") are untested at core level.
3. **F-16, "A/B is scribes."** It rests on X-08, which is unverified, while H-13 is marked confounded. That cannot be TRIANGULATED.
4. **H-01 "disfavoured" at 17.5.** The total double-counts (2h), sits inside one alphabet (2c), and rests on 6 hard-way controls (s97).
5. **F-21, "composition, not copying."** One axis stands against Davis's copying model (unverified on disk).
6. **F-10.** A universal claim about period cryptography taken from one external source.

## 4. What outside experts would say (from the published literature; not checked on disk unless noted)

- **Bowern and Lindemann (2021):** low h2 is largely an effect of the transcription alphabet, and the word statistics fit a language written in an unusual orthography. **Gaskell and Bowern (2022, on disk):** human gibberish resembles Voynichese on most of their metrics. Both are treated here as controls, not as rival accounts to beat on our battery under a merged alphabet.
- **Timm and Schinner:** self-citation predicts quire-local vocabulary (F-17, F-42), drift through the book (F-50) and in-line near-repeats (F-13). Yet H-07 carries 7.0 against it "as built". Timm would ask for his own generator to be run at full size on the s87 signature. L-013 ran it on line edges only, and the JRE has since been deleted (TOOLS.md:137).
- **Davis:** there are five scribes. The bifolios were written unbound, so the bound order is not the reading order (X-04). Scribes copying an exemplar would produce F-50 without any generator.
- **Zandbergen:** EVA is a transcription convention, not an alphabet hypothesis. The binding history and the zodiac month names (O-029, logged but unused) are the external evidence that matters. He would read F-01, F-02 and F-11 as rediscoveries of Currier (1976), Stolfi and Zattera. Whether we cite them is unverified.
- **In short:** distributional statistics cannot separate meaning from mechanism at this book size (A0). Anchors, alphabet and physical evidence can.

## Ranked stop / continue / start

**Stop:**
1. r15.
2. s113 G2.
3. s108.
4. r14; release roach.
5. Any new producer-family grid until 2b and 2c are discharged.

**Continue:**
1. s115 A1b, then A2, under the A0 power gate.
2. MSI on f116v and f17r.
3. The glyph full run, as an EVA sensitivity gate.
4. The roach mirror (O-067).
5. s105, acquisition only.

**Start:**
1. A frozen sensitivity run, executed by roach as `impl`. It covers about 10 load-bearing statistics (h2, Rw1, rhythm, prefix memory, core order, quire locality) under EVA, a merged alphabet and GC2a. Segmenter-free word identity is its X-01 decider.
2. Move F-33, F-20 and F-44 to at-risk. Correct the map weights for dependence, and keep one BH ledger across the whole program.
3. Run Timm's own generator at full size on the s87 signature. Get real-line gibberish at Voynich length.
4. Add a "prior literature" field to each F row in FINDINGS-GRAPH.yaml, rather than a new file (D-058).
5. A keyword-only vparse wrapper.
