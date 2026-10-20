# Findings

*Generated from `workflow/FINDINGS-GRAPH.yaml` (snapshot 2026-10-19). Grades are computed by `tools/findings_graph.py`; terms are in `GLOSSARY.md`.*

Each finding is a tested property of how the text is built. None says what the text means. Standing findings come first, then findings at risk.

## Standing

### F-01

**Lines are units of the text**

The line start carries its own vocabulary, 20x a Latin prose line at matched size; separable from verse corpora at >=500 lines but not from single short verse hands. Reproduced from ink-detected lines, on public data with new code, and robust to drawing gaps.

- **Grade:** TRIANGULATED; agreeing axes: data, impl, method, order, physical (load-bearing); counted strictly (each run once): 5 axis/axes (data, impl, method, order, physical)
- **Novelty:** extends. Prior work: Currier 1976 (line as functional unit, cited via R&T); Vogt 2012, The line as a functional unit; Timm 2014, arXiv 1407.6639; Rozanova & Temerev 2026, arXiv 2608.17096 s3.6; Steckley & Steckley 2024, arXiv 2404.13069. What this adds: Matched-size comparison against Latin prose and verse corpora, reproduced on Kraken ink-detected lines and after drawing-gap removal.
- **Rests on:** X-03 (Line breaks in the transliteration are the scribe's lines: verified)
- **Claims:** c-306, c-313, c-316, c-317, c-330, c-331, c-349, c-359, c-409, c-318, c-319, c-348 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: ZL3b/RF1b/IT2a (agrees) — `results_s18.txt`
  - impl: roach r1, independent code on public data (agrees) — `runs/roach-r1r2-raw/results_r1.txt`
  - physical: s45 kraken ink-detected line breaks, 127 pages (agrees) — `results_s45.txt`
  - method: s65 drawing gaps removed or split (agrees) — `results_s65.txt`
  - order: s79: line-edge marking mirrors under reversal (one end of the line is marked) (agrees) — `results_s79.txt`

### F-02

**The line-start effect is paragraph gallows plus a line-start vocabulary; line ends are verse-like**

Line-final m/g flourishes are matched by rhymed verse, so line ends earn no credit; line starts do. Holds across all three transliterations, 14/15 LOQO quires, and s45 ink-detected lines (s86).

- **Grade:** SINGLE; agreeing axes: method; counted strictly (each run once): 1 axis/axes (method)
- **Novelty:** replicates. Prior work: Currier 1976; Timm 2014 (86% of paragraphs gallows-initial); Rozanova & Temerev 2026 s3.6 (paragraph-first vs ordinary lines); tavie/Stafford, voynich.ninja thread 4343 (2024); RN-Top PR #5 2026 (re-lining control); Ponzi line-position analyses (forum/blog). What this adds: Essentially a re-finding (our own prior-art review demotes it as replication); the only addition is a rhymed-verse control showing line-final m/g earns no credit.
- **Lines not counted:** 3 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-314, c-527 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: m5 line anatomy and s17 verse corpora (agrees) — `results_m5_line_anatomy.txt`
  - data: Argon s86 Part 3A 3 transliterations (ZL3b, RF1b, IT2a) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s86.txt`
  - split: Argon s86 Part 3A 15-quire LOQO (14/15 quires on all 3 transliterations) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s86.txt`
  - physical: Argon s86 Part 3A s45 kraken ink-detected lines on 127 Yale scan pages [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s86.txt`

### F-03

**Cross-space coupling is adjacent ordering, strongest in Currier B, and cheap to make**

Last glyph to next first glyph is coupled, B above every prose manuscript but inside short Latin verse at matched size, with no caesura or rhyme. Any skewed edge table regenerates it, so it constrains the mechanism only through which table and why A and B differ.

- **Grade:** TRIANGULATED; agreeing axes: data, external, impl; counted strictly (each run once): 3 axis/axes (data, external, impl)
- **Novelty:** extends. Prior work: Currier 1976; Smith & Ponzi 2019, Cryptologia 43.6, Glyph combinations across word breaks; Rozanova & Temerev 2026 (edge MI 0.197 bits; A 0.137, B 0.248); Parisel 2026, arXiv 2604.19762; Feaster 2022, CEUR 3313 (positional account of y.q/n.q). What this adds: Short Latin verse at matched size reaches B, and any skewed edge table regenerates the coupling, so it constrains little.
- **Claims:** c-307, c-325, c-327, c-308, c-350, c-387, c-372, c-300, c-358, c-368 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: 3 transliterations (agrees) — `results_s20.txt`
  - impl: roach r2 (marginal: B similar to Priapea) (agrees) — `runs/roach-r1r2-raw/results_r2.txt`
  - external: Rozanova and Temerev 2026: edge information stops at line breaks (agrees) — `data/external/papers/rozanova_temerev_2026_arxiv_2608.17096.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)

### F-04

**Word lengths follow a rhythm inside lines that stops at line breaks**

Neighbouring words in a line have related lengths (Moran I 0.157 vs shuffle q99 0.081); cross-line share <3 %; no language or human-gibberish control we built reproduces it, but Kalevala metrical verse does (15/15 blocks, c-456); no producer we built predicts it.

- **Grade:** TRIANGULATED; agreeing axes: data, impl, method, order, split (load-bearing); counted strictly (each run once): 5 axis/axes (data, impl, method, order, split)
- **Novelty:** extends. Prior work: Gaskell & Bowern 2022, Gibberish after all? (flattened word-length autocorrelation); quimqu & nablator, voynich.ninja 2025 (lag-1 r +0.16, line-break contrast); Vogt 2012 (second word shorter); Steckley & Steckley 2024 (line-position lengths). What this adds: A shuffle-controlled within-line Moran I with cross-line share under 3%, replicated by independent code; roach r12 shows Kalevala verse has it too (c-456).
- **Rests on:** X-03 (Line breaks in the transliteration are the scribe's lines: verified)
- **Lines not counted:** 1 of 9 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-295, c-305, c-320, c-328, c-329, c-335, c-336, c-360, c-409, c-414, c-380, c-456 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: 3 transliterations (agrees) — `results_s21.txt`
  - impl: Daybreak independent run (exact reproduction) (agrees)
  - impl: roach r3c, own code and segmenter, held-out pages: within-line only (agrees) — `runs/roach-r3/results_r3.txt`
  - physical: s45 ink-derived word gaps: same sign and above its null (0.254), but outside the pre-set band 0.109-0.170, so the band check FAILS (c-360); corrected from agrees: true on 2026-10-19 under D-088 (disagrees, resolved: direction and null test agree; only the pre-set magnitude band fails, so this line counts neither for nor against F-04) — `results_s45.txt`
  - method: s65 drawing-gap removal (agrees) — `results_s65.txt`
  - split: roach r3 held-out pages (agrees) — `runs/roach-r3/results_r3.txt`
  - order: s79: Moran order-free under every transform (agrees) — `results_s79.txt`
  - external: Voynich Ninja thread (quimqu, nablator 2025): global lag-1 word-length r +0.16, line-break contrast; per-line -0.07 reproduced and shown to be short-line bias (shuffle -0.153, excess +0.082) (agrees; not counted) — `runs/explore/wordlen_perline_bias_20261018.txt`
  - impl: roach r12 blind: within-line lag-1 length correlation positive on 12/15 (ZL) and 11/15 (IT) blocks, none across line breaks; Kalevala metrical verse 15/15, other natural texts <= 4/15 (agrees) — `runs/roach-r12/results_r12.txt`

### F-05

**Characters predict the text better than its word list does**

CHARWIN is positive (+0.094), outside every language (-0.45..-0.74) and encoded control; the sign is shared only by human gibberish. Its sign comes from the affix layer (s58) and needs core-dependent affixes (s67).

- **Grade:** CORROBORATED; agreeing axes: data, method; counted strictly (each run once): 2 axis/axes (data, method)
- **Novelty:** extends. Prior work: Bennett 1976 (h2 2.22 vs 3.01-3.37, via voynich.nu); Lindemann & Bowern 2021, character entropy; Gaskell & Bowern 2022 (gibberish similarity). What this adds: A held-out character-model-vs-word-list comparison whose positive sign no language or encoded control shares, traced to core-dependent affixes.
- **Lines not counted:** 2 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-293, c-315, c-398 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: 3 transliterations (agrees) — `results_n5.txt`
  - method: s38 canonical scorer re-run by voynich-08 (agrees) — `runs/s38/rescore_n5_voynich08.txt`
  - impl: Argon s75/s85 strictly normalized MDL bake-off on 15-quire LOQO (M1_char3_wb beats M0_unigram_renorm on 15/15 quires) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s85.txt`
  - split: 15-quire LOQO and s45 127-page ink-verified subsets (s88 Part 2) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s88.txt`

### F-06

**Cores carry held-out word-order structure (restated; the 'affixes carry none' half withdrawn by r5)**

A held-out next-word residual exists that a powered 7k-type habit generator does not reproduce; the affix streams carry none of it. Reddy and Knight report a comparable residual for B.

- **Grade:** TRIANGULATED; agreeing axes: data, impl, method, split (load-bearing); counted strictly (each run once): 3 axis/axes (data, impl, method)
- **Novelty:** extends. Prior work: Reddy & Knight 2011, What We Know About the Voynich Manuscript (8.85% residual next-word gain for B); Rozanova & Temerev 2026 Table 4 (token order 0.81%). What this adds: The residual is held out, survives a powered 7k-type habit generator, and sits in the core stream (the affix half was withdrawn by r5).
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk); X-07 (The 41 held-out pages are an uncontaminated test set: at-risk)
- **Lines not counted:** 1 of 5 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-301, c-351 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: ZL3b and IT2a; RF1b matched by generator (agrees) — `results_n6.txt`
  - split: held-out pages (agrees) — `results_n6.txt`
  - method: s39 core-only F1, interval excludes 0 on 3 transliterations (agrees) — `results_s39.txt`
  - external: Reddy and Knight 2011 residual next-word gain for B (agrees; not counted)
  - impl: roach r5 blind LOQO: core stream 13/15 quires (affix streams also 15/15, so the affix half is withdrawn) (agrees) — `runs/roach-r5/results_r5.txt`

### F-07

**Hand-1 section vocabulary beats the generator and a bifolio null at the permutation floor, consistent with Schwartz 2026's weak section tint**

NMI 0.275 against generator 0.09; sits at the 1/55 floor so it cannot be ranked under correction. Carried by prefixes over shared cores (s34).

- **Grade:** TRIANGULATED; agreeing axes: data, impl, split; counted strictly (each run once): 3 axis/axes (data, impl, split)
- **Novelty:** extends. Prior work: Montemurro & Zanette 2013, PLoS ONE (section keywords); Sterneck, Polish & Bowern 2021, Topic Modeling in the Voynich Manuscript; Schwartz 2026 s5.4 (0.2-0.3 bits/page tint, negative once quire is conditioned); Zattera 2022, CEUR 3313 (section differences are word-internal structure). What this adds: A within-hand-1 test against a generator and a bifolio null, with the signal carried by prefixes over shared cores; it agrees with Schwartz's weak tint rather than adding an independent content signal.
- **Claims:** c-302, c-291, c-338 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: 3 transliterations (agrees) — `results_n6.txt`
  - impl: Argon s34: section differentiation rides on prefixes (agrees) — `results_s34_morphology_syntax_geography.txt`
  - split: p1 physical $Q/$B bifolio-block null and n3b 50/50 split (agrees) — `results_p1_bifolio.txt`

### F-08

**The edge and coupling anomalies are not alphabet or boundary artefacts; entropy and type counts are**

h2 and type counts move with the alphabet and boundary rule; line-start JSD and coupling hold under 5-6 alphabets and 3 boundary rules.

- **Grade:** CORROBORATED; agreeing axes: method, seg; counted strictly (each run once): 2 axis/axes (method, seg)
- **Novelty:** extends. Prior work: Lindemann & Bowern 2021 (h2 depends on transcription and alphabet); Rozanova & Temerev 2026 (glyph, token and space units); Zattera 2022 (slot alphabet). What this adds: Line-start JSD and edge coupling shown stable across 5-6 alphabets and 3 boundary rules while h2 and type counts move.
- **Lines not counted:** 1 of 3 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-298, c-325, c-326, c-373, c-365 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - seg: 3 boundary rules (agrees) — `results_p2.txt`
  - method: 5 alphabets (agrees) — `results_s30_phase2_deltas.txt`
  - impl: Argon s51 six-alphabet bake-off [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s51_o051_o052_p4u2_closures.txt`

### F-09

**Within-manuscript widths are known (41-page splits, 52-bifolio & 15-quire blocks, and physical ink)**

Every match claim now has a stated margin (jsd_first, coupling, Moran, h2, CHARWIN, prefix gain, MM_K100, and R_within(1) intervals overlap across 3 transliterations, 41-page splits, 52-bifolio & 15-quire blocks, and s45 127-page physical ink streams, s93).

- **Grade:** SINGLE; agreeing axes: split; counted strictly (each run once): 1 axis/axes (split)
- **Novelty:** extends. Prior work: Rozanova & Temerev 2026 (quire-bootstrap intervals; leave-one-quire-out for entropy). What this adds: Margins for eight metrics across transliterations, 41-page splits, bifolio and quire blocks and physical ink streams; internal calibration with little external novelty.
- **Lines not counted:** 3 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-312, c-310, c-535 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: 41-page resplits (agrees) — `results_s15.txt`
  - data: Argon s93 Part 2 3 transliterations (ZL3b, RF1b, IT2a 41-page & 20-bifolio 500-draw CIs) (agrees; not counted) — `results_s93.txt`
  - method: Argon s93 Part 2 15-quire LOQO block bootstrap (1.44-2.74x width) and 52-bifolio 20-sheet block subsampling (0.67-1.13x width) (agrees; not counted) — `results_s93.txt`
  - physical: Argon s93 Part 2 s45 127-page Kraken ink-detected stream ZL3b_ink127 (0.82-1.10x width; 8/8 metrics overlap) (agrees; not counted) — `results_s93.txt`

### F-10

**Period practice allows a 7k-type text only as a verbose homophonic cipher**

15th-c. keys: ~80 % of nomenclators under 100 entries, 96 % use nulls, none reaches 7k types. A word-level code at 7k types is unhistorical.

- **Grade:** SINGLE; agreeing axes: external; counted strictly (each run once): 1 axis/axes (external)
- **Novelty:** extends. Prior work: Megyesi et al., HistoCrypt 2021 and 2022 (DECODE key statistics); Megyesi et al. 2022, Cryptologia (keys with nomenclatures); Timm 2025, voynich.ninja Naibbe thread (token-budget argument); Tranchedino keys c.1475 (via Pelling). What this adds: Applies the published period key-size profile to the 7k-type count to rule out a word code; all inputs are published.
- **Claims:** c-309 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - external: literature review B-prior-art section 5 (agrees) — `workflow/research/B-prior-art.md`

### F-11

**Under a prefix/core/suffix segmentation (not validated on planted books, c-592), the line signatures live in the affixes**

Removing affix material removes ~96 % of the measured rhythm excess (an ablation, not a causal share); the next word's prefix takes most positive word-to-word dependency; the slot layer survives a second segmenter (4/5 calls).

- **Grade:** TRIANGULATED; agreeing axes: external, seg, split (load-bearing); counted strictly (each run once): 3 axis/axes (external, seg, split)
- **Novelty:** extends. Prior work: Stolfi word grammar (voynich.nu); Zattera 2022, CEUR 3313 slot model; Smith & Ponzi 2019; Rozanova & Temerev 2026 (edge MI concentrated in the boundary glyph pair); Parisel 2026 (cross-boundary MI 0.230). What this adds: An ablation placing about 96% of the rhythm excess and most next-word dependency in the affixes; rests on X-01 (no tested segmenter is adequate on planted books, c-592).
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 2 of 6 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-335, c-336, c-337, c-352, c-353, c-413, c-367 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s33/s34 [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s33_line_scales_interlock.txt`
  - split: Argon s36/s37 out-of-sample SlotSegmenter fitted on 166 pages (agrees)
  - data: 3 transliterations [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s33_line_scales_interlock.txt`
  - seg: s76 Zattera 12-slot model: 4 of 5 slot calls hold (X-01 discharge withdrawn 2026-10-19: this segmenter is NOT ADEQUATE on planted books, vx01 A1 c-592) (agrees) — `results_s76.txt`
  - external: Zattera 2022 slot model; Stolfi grammar (agrees) — `data/external/papers/zattera_2022_ceur3313_paper10.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)
  - external: Rozanova and Temerev 2026, split-free: last glyph of word t to first glyph of word t+1 carries 0.197 bits (5.7%), above every continuous-text control (0.018-0.120), 88-93% destroyed by within-line shuffling; the whole previous word predicts the next first glyph no better than its last glyph (lines 409-446). Supports the edge half; does not test the prefix/core/suffix split itself (X-01 not discharged). Lead-verified 2026-10-19 11:21 (agrees) — `data/external/papers/rozanova_temerev_2026_arxiv_2608.17096.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)

### F-12

**Cores carry weak order, weaker than language and mostly weaker than letter-in-core ciphers**

Restated 2026-10-18 after s80 and roach r4. At matched inventory size, held-out core->core MI excess is positive (+0.045 at K=100 on ZL3b; +0.05..+0.06 RF1b/IT2a), below every matched language at K=200-400, below all 12 planted letter-in-core ciphers at K=100-200 but inside their range at K=50. The earlier 'below shuffle' (A14) was the sign of a full-inventory statistic that is negative even for language (c-420).

- **Grade:** TRIANGULATED; agreeing axes: data, impl, method, seg, split (load-bearing); counted strictly (each run once): 4 axis/axes (data, impl, method, seg)
- **Novelty:** extends. Prior work: Rozanova & Temerev 2026 Table 4 (token order 0.81% vs prose 2-10%); Stellar 2026 (dI(1) 5.4x below Latin); Reddy & Knight 2011; Zandbergen, voynich.nu syntax page (no repeated phrases). What this adds: A matched-inventory core-level comparison against planted letter-in-core ciphers and languages; note R&T's whole-token sign for Currier A is negative.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Claims:** c-337, c-355, c-393, c-394, c-413, c-418, c-419, c-420 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: s80 on ZL3b/RF1b/IT2a at matched K (agrees) — `results_s80.txt`
  - method: s80 two pooling methods, two estimators (agrees) — `results_s80.txt`
  - seg: s76/s80 Zattera segmenter: positive, +0.07..+0.10 (X-01 discharge withdrawn 2026-10-19: this segmenter is NOT ADEQUATE on planted books, vx01 A1 c-592) (agrees) — `results_s76.txt`
  - impl: roach r4 blind: weak (+0.013..+0.016 at K<=50, null at K=100), far below its ciphers (agrees) — `runs/roach-r4/results_r4.txt`
  - split: held-out pages (agrees) — `results_s80.txt`
  - method: Daybreak db-s91/db-s92 (imports our metrics): core order mostly off-diagonal (CI positive 9/9) but exact class tables do not transfer between quires (0/9); db-s91 uses the reused 41-page held-out set (X-07) (agrees) — `lab/codex_lab/experiments/results_s92_offdiagonal_core_transfer.txt`

### F-13

**The same core recurs at short range, the opposite of language**

Cores repeat more than chance within ~20 tokens, strongest for rare cores and inside lines; natural language and word codes show fewer adjacent repeats than chance. Holds under Zattera (R(1) 1.20).

- **Grade:** TRIANGULATED; agreeing axes: data, external, impl, order, seg (load-bearing); counted strictly (each run once): 5 axis/axes (data, external, impl, order, seg)
- **Novelty:** replicates. Prior work: Timm 2016, Co-Occurrence Patterns in the Voynich Manuscript (consecutive identical words 0.95% vs Quran 0.01%); Timm 2014 (repeats peak within nearby lines); Rozanova & Temerev 2026 (near-identical neighbours 1.12 vs prose 0.43-0.56); D'Imperio 1978 (repeated words); Gaskell & Bowern 2022 (repeated words). What this adds: Essentially Timm 2016's observation re-found; we add only a shuffle-normalised core-level R(d) (strongest for rare cores), which rests on the at-risk core split X-01.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 1 of 6 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-382, c-383, c-413, c-354 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: 3 transliterations (agrees) — `results_s56.txt`
  - seg: s76 Zattera R(1) 1.20 (X-01 discharge withdrawn 2026-10-19: this segmenter is NOT ADEQUATE on planted books, vx01 A1 c-592) (agrees) — `results_s76.txt`
  - impl: Argon s70 canonical segmentation: R(1) 1.170, rare 1.843 [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s70.txt`
  - order: s79: R(1..3,5) order-free under line, glyph and page reversals (agrees) — `results_s79.txt`
  - impl: roach r5 blind: R_within(1) 1.32 (ZL3b), 1.34 (IT2a) vs Latin 0.13; across lines 0.52 (agrees) — `runs/roach-r5/results_r5.txt`
  - external: Split-free whole-word cousins: Timm 2016, consecutive identical words 0.95% vs Quran 0.01% (library VL00131:336-356); Rozanova and Temerev 2026, near-identical-neighbour ratio 1.12 vs Latin narrative 0.43 (Table, line 700). Lead-verified R&T 2026-10-19 11:21; Timm via x01-published-first.md (agrees) — `data/external/papers/rozanova_temerev_2026_arxiv_2608.17096.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)

### F-14

**The prefix stream carries short-range memory (strongest one word back) and restarts at each line; an exact one-step frame law is not established**

A word's prefix depends on its own core and the previous prefix, little further back; the memory resets at line breaks and weakens across gallows words. Sign holds under three segmenters; size depends on the prefix boundary. Only Rugg's table-and-grille shows it among reference classes, about five times too strongly.

- **Grade:** TRIANGULATED; agreeing axes: data, impl, method, order, seg, split (load-bearing); counted strictly (each run once): 5 axis/axes (data, impl, method, order, seg)
- **Novelty:** extends. Prior work: Dominik 2026, Line-Conditioned Orthographic Organization (predecessor-class gain 0.041-0.064 nats; line reset labelled exploratory); Rozanova & Temerev 2026 Table 5 (edge drop at line breaks); Stolfi word grammar (consecutive-word correlation, qualitative). What this adds: A held-out lag profile and line-reset test for the prefix stream, plus reference classes (only the Rugg grille shows it).
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk); X-03 (Line breaks in the transliteration are the scribe's lines: verified) — weighted half while at risk
- **Lines not counted:** 1 of 7 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-352, c-410, c-413, c-414 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: 3 transliterations (agrees) — `results_s69.txt`
  - method: s40 held-out bigram gain (agrees) — `results_s40.txt`
  - seg: s76 Zattera: positive, a sixth of the size (X-01 discharge withdrawn 2026-10-19: this segmenter is NOT ADEQUATE on planted books, vx01 A1 c-592) (agrees) — `results_s76.txt`
  - impl: roach r3a: positive interval, below the 0.05 size bar (agrees) — `runs/roach-r3/results_r3.txt`
  - split: held-out pages (agrees) — `results_s69.txt`
  - order: s79: M1 order-free under line reversal; line reset negative under every transform (agrees) — `results_s79.txt`
  - external: Dominik 2026 (library VL00735), first-character word classes, no split: predecessor class improves held-out prediction 0.041-0.064 nats/token (lines 20-26); line-boundary drop (+0.107 within-line vs -0.027 across recorded line breaks) is labelled exploratory by the author (lines 160-174), so this line is unverified until a pre-registered reset test (agrees; not counted) — `data/external/library/corpus/papers/VL00735.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)

### F-15

**Prefix and suffix are chosen together with the core**

Affixes depend on the core (+1.38 bits independently; +1.79 bits frame-core coupling); core-class affixes fix the word-type count and the CHARWIN sign, free assembly makes ~65 % too many types.

- **Grade:** TRIANGULATED; agreeing axes: impl, method, seg, split (load-bearing); counted strictly (each run once): 3 axis/axes (impl, method, seg)
- **Novelty:** extends. Prior work: Stolfi word grammar (dependencies between slot choices, qualitative); Timm 2014 (frequency predictable from similar spellings); Zattera 2022 (rare slot combinations). What this adds: The first quantitative number (+1.38 bits; split-free s131 restatement) and the type-count consequence of free assembly.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk)
- **Lines not counted:** 1 of 6 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-370, c-379, c-398, c-406, c-407, c-414, c-381, c-623 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s51 frame-core coupling [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s51_o051_o052_p4u2_closures.txt`
  - impl: roach r3b affix-given-core gain (agrees) — `runs/roach-r3/results_r3.txt`
  - method: s67 ablation (agrees) — `results_s67.txt`
  - seg: s76 own-core prediction M7 > M1 (X-01 discharge withdrawn 2026-10-19: this segmenter is NOT ADEQUATE on planted books, vx01 A1 c-592) (agrees) — `results_s76.txt`
  - split: LOQO 15 quires (s67) (agrees) — `results_s67.txt`
  - seg: s131 split-free restatement on raw characters (first 2 / middle / last 2, no SlotSegmenter): all three part pairs dependent beyond a within-length shuffle on ZL3b, RF1b and IT2a (B;M about 1.35 bits, M;E about 1.29, B;E about 0.47; p 0.005); free assembly over-makes types 1.76-1.80x; planted-free control NOT_RESTATED (agrees) — `runs/s131/results_s131_f15_splitfree.txt`

### F-16

**Currier A/B coincides with Davis's scribe split; within B, the Hand 2 vs Hand 3 slot divergence is section**

Hand 1 writes all of A, hands 2 and 3 write B; Parisel's folio switch is the hand; slot profiles are hand-associated on unstratified Currier B, but inside Section H (Herbal-B) under nested LOLO/LOQO Hand 2 and Hand 3 show zero positive slot divergence (s77: the H2 vs H3 difference in s60 is Section Bio vs Stars/Herbal, not per-scribe grammar). Confirmed without Davis's $H labels by unsupervised k=2 clustering on s45 121-page physical scan geometry + distributional features (98.35% vs Currier A/B, 96.69% vs H1 vs H2/3; physical scan z(words/line)=+4.84, z(lines/page)=+8.25) and $H-blind Herbal-B LOBO quire/cluster transfer (s93).

- **Grade:** CORROBORATED; agreeing axes: method, split; counted strictly (each run once): 2 axis/axes (method, split)
- **Novelty:** extends. Prior work: Currier 1976 (languages A/B and hands); Davis 2020, How Many Glyphs and How Many Scribes?; Farrugia, Layfield et al. 2022 (scribes by computational linguistics); Sterneck et al. 2021; Timm 2026, One Hand, Five Labels (disputes five scribes). What this adds: Within Herbal-B the Hand 2 vs Hand 3 slot difference is section, and unsupervised clustering on scan geometry recovers A/B without Davis's labels.
- **Rests on:** X-08 (Davis's hand assignments are correct: unverified)
- **Lines not counted:** 3 of 6 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-374, c-408, c-506, c-507, c-510, c-536 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s51 hands vs Currier [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s51_o051_o052_p4u2_closures.txt`
  - method: s68 Parisel switch within hand (agrees) — `results_s68.txt`
  - split: Argon s60 held-out classification (agrees) — `results_s60.txt`
  - split: Argon s77 nested LOLO/LOQO inside Herbal-B: zero H2 vs H3 divergence once section is matched; s60 H2/H3 shift is Section (Bio vs Stars/Herbal) (agrees) — `results_s77.txt`
  - physical: Argon s93 Part 3 $H-blind unsupervised k=2 on s45 121-page physical scan layout + distributional vectors (98.35% vs A/B, 96.69% vs H1 vs H2/3; scan z(wpl)=+4.84, z(lpp)=+8.25) & $H-blind Herbal-B LOBO quire/cluster transfer (6/6 null) (agrees; not counted) — `results_s93.txt`
  - external: Davis hand assignments (agrees; not counted)

### F-17

**Quire M (the sole Biological quire) uses a 1.43-1.47x narrower vocabulary than token-matched global draws; the other 14 quires do not**

No producer reproduces the narrowness; Quire M (Hand 2, Biological, the sole Bio quire) has a 1.43-1.47x tighter active lexicon than global expectation while the other 14 quires match token-matched global draws (s66).

- **Grade:** TRIANGULATED; agreeing axes: data, impl, seg, split (load-bearing); counted strictly (each run once): 3 axis/axes (data, impl, split)
- **Novelty:** extends. Prior work: Montemurro & Zanette 2013 (local keyword clustering); Schwartz 2026 s5.4 (quire conditioning removes the section gain); Timm & Schinner 2019 (local self-citation). What this adds: Token-matched global draws show only Quire M (Biological) is narrower (1.43-1.47x); the other 14 quires match global expectation.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk)
- **Claims:** c-406, c-505, c-504 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: s67 LOQO (agrees) — `results_s67.txt`
  - impl: Argon s66 quire seams (agrees) — `results_s66.txt`
  - seg: s66/s67 whole-word type counts (Glob/ObsW 1.43-1.47x on Quire M, 1.01-1.03x on other 14 quires; no segmenter) (agrees) — `results_s66.txt`
  - data: s111 subject vs quire: same-subject pages in different quires are no more alike than different-subject pages (powered subject arm 11/15, combined p 0.83); batch arm underpowered (agrees) — `results_s111.txt`

### F-18

**Drawings explain only part of the edge marking; layout does not inflate the line findings**

Drawing gaps are weak edges; excluding or splitting at gaps moves A1/A5 at most 6 %, and fair pre-word remaining space shows only a uniform rightward slope across MID and MARGIN (OBSTACLE - MID difference includes 0, s70). Labels are reachable by a class-conditioned generator.

- **Grade:** SINGLE; agreeing axes: method; counted strictly (each run once): 1 axis/axes (method)
- **Novelty:** extends. Prior work: Steckley & Steckley 2024 (before-drawing tokens shorter); Zandbergen, voynich.nu writing page (line-initial column written first); Feaster 2022 (rightward distributions). What this adds: Drawing gaps move the line findings at most 6%, and a fair remaining-space control shows no obstacle effect.
- **Lines not counted:** 3 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-339, c-340, c-341, c-409, c-513 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - physical: Argon s35 codicology [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s35_physical_codicology_quire_network.txt`
  - method: s65 gap exclusion (agrees) — `results_s65.txt`
  - physical: Argon s70 fair pre-word remaining space R90(j) conditioned on (page, j, L) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s70.txt`
  - impl: Argon s35 (voynich-08 s65 is separate code) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s35_physical_codicology_quire_network.txt`

### F-19

**Transliterated spaces are physical ink gaps (kappa 0.87); commas are intermediate gaps**

Ink gaps on 127 scanned pages agree with the certain spaces (kappa 0.87); commas are intermediate gaps; gallows pen-lifts are not gaps.

- **Grade:** TRIANGULATED; agreeing axes: data, method, physical (load-bearing); counted strictly (each run once): 2 axis/axes (data, method)
- **Novelty:** extends. Prior work: Rozanova & Temerev 2026, A Glyph Is Not a Letter ... a Space Is Not a Space (separator hierarchy); Zandbergen 2022, transliteration (uncertain spaces as commas). What this adds: Ink gaps measured on 127 scans agree with certain spaces (kappa 0.87); commas are intermediate gaps; gallows pen-lifts are not gaps.
- **Rests on:** X-03 (Line breaks in the transliteration are the scribe's lines: verified)
- **Claims:** c-384, c-385, c-386, c-356, c-364 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - physical: s47 ink gaps (agrees) — `results_s47.txt`
  - data: ZL3b spaces (agrees) — `results_s47.txt`
  - method: P4-U1 comma regimes (agrees) — `results_p4u1_space_regimes.txt`

### F-20

**Tested plant-label and repeated-label cribs show no supported text link**

Pharma sketches match their herbal partners in images, but their labels share no text with the partner page, though the test finds a planted link.

- **Grade:** CORROBORATED; agreeing axes: external, method; counted strictly (each run once): 2 axis/axes (external, method)
- **Novelty:** new. Prior work: Published pharma-to-herbal plant matches used as inputs (Zandbergen; Stolfi; Petersen). What this adds: A planted-control test of label-to-partner-page text links; no published test of this kind in our records.
- **Lines not counted:** 2 of 5 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-371, c-377, c-388, c-389 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: s48 image embeddings, s53 part-level matching (agrees) — `results_s53.txt`
  - impl: Argon s53 text-side labels (agrees; not counted) — `results_s53_p4a1_p4e1_anchors_and_errors.txt`
  - data: 3 transliterations and whole-word/core-stem variants (agrees; not counted) — `results_s53_p4a1_p4e1_anchors_and_errors.txt`
  - external: Daybreak db-s114 (own code, no imports from this tree): Stolfi 1998 label catalogue, 239 loci, 27 repeated types; repeated labels agree on plant/root/container class 20/31 = null median (p 0.63); ghost-row correction (rev2 stub 5/5, rerun byte-identical, audit-external-B 2026-10-18): 6/15, p 0.745; independence of 14/15 remaining pairs unverified (catalogue .X. positions) (agrees) — `lab/codex_lab/experiments/results_s114_repeated_label_object_consistency.txt`
  - external: s128-p72: published human matches (Zandbergen/Stolfi/Petersen), eye-checked, 18 pairs; NO_LINK p 0.72 at power 0.958; Egerton control 200/200 (agrees) — `results_s128_20261019T090659.txt`

### F-22

**New rare cores are only weakly edited from nearby forms, and many are segmenter boundary shifts**

A new rare core has a one-glyph relative nearby ~2 % more often than chance, a seventh of a copy-and-edit producer and below Latin. Many rare cores satisfy alternative-boundary reparses (A21; 28-41 % disappear under an independent segmenter in s77, and Canon+Comp leaves only 1.15-1.29 % of held-out tokens as M5 distal roots in s70); 18-23 % of U1 B2 splits sit at raw commas while 90-96 % of standard B2 splits have zero physical ink-space elevation, and LOQO unseen-core gain is carried by sub-glyph allomorphy and two-core concatenation (s77).

- **Grade:** CORROBORATED; agreeing axes: physical, split; counted strictly (each run once): 2 axis/axes (physical, split)
- **Novelty:** extends. Prior work: Timm 2014, How the Voynich Manuscript was created; Timm & Schinner 2019, A possible generating algorithm (words made by small edits of nearby words). What this adds: The edit-from-neighbour effect is about 2% over chance, a seventh of a copy-and-edit producer, and many rare cores are segmenter boundary shifts.
- **Lines not counted:** 2 of 5 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-400, c-401, c-404, c-508, c-509, c-511, c-512 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: s62 on training pages never scored by s59 (agrees) — `results_s62.txt`
  - impl: Argon s63 boundary reparse [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s63.txt`
  - seg: Argon s70 canonical segmentation: edit-1 excess 1.005 (null), 1.15-1.29 % M5 distal tokens [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s70.txt`
  - physical: Argon s77 raw comma and s47 ink-gap alignment of B2 splits (3.62 % vs 3.32 % ink-space rate) (agrees) — `results_s77.txt`
  - split: Argon s77 16-quire LOQO 6-model component ablation under SlotSegmenter and Seg_Affix2 (X-01 discharge withdrawn 2026-10-19: this segmenter is NOT ADEQUATE on planted books, vx01 A1 c-592) (agrees) — `results_s77.txt`

### F-24

**The per-word random-table cipher leaves the prefix stream orderless**

Greshko's Naibbe rebuilt from his own tables gives no prefix order; Voynich's is the most ordered of any class. Confirmed on 15-quire LOQO across three segmenters (s81, s85).

- **Grade:** CORROBORATED; agreeing axes: data, method, split; counted strictly (each run once): 2 axis/axes (data, split)
- **Novelty:** extends. Prior work: Greshko 2025, Cryptologia, The Naibbe cipher; Rozanova & Temerev 2026 s3.9 (Naibbe edge MI 0.006). What this adds: Rebuilt from Greshko's own tables, Naibbe leaves the prefix stream orderless, where Voynich is the most ordered class tested.
- **Lines not counted:** 2 of 5 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-405, c-428, c-523 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: s64 rebuild from the author's tables (agrees) — `results_s64.txt`
  - data: 3 transliterations (agrees) — `results_s64.txt`
  - split: s81 15-quire LOQO default Naibbe (0/15 folds match s69 call pattern) (agrees) — `results_s81.txt`
  - impl: Argon s85 Part 2C 15-quire LOQO across SlotSegmenter, Zattera, and Seg_Affix2 (default M1_ex -0.0001..+0.010, 0-3/15) (agrees; not counted) — `results_s85.txt`
  - seg: Argon s85 Part 2C SlotSegmenter, Zattera, and Seg_Affix2 [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s85.txt`

### F-25

**Plain letter-in-core and verbose-homophonic ciphers reach the weak core order but miss h2, rhythm and prefix memory**

Re-scored by s82 with core order at matched K (the old full-inventory target was biased, s80). 25/36 P4-D1 and 25/81 s50 instances match the core-order curve; none matches all five targets. h2 is too high in every curve match (2.17-2.85 vs 2.11), within-line rhythm and the one-word prefix memory are absent. The solver still reads the family (s50); the construction, not the solver, is the limit (D-057).

- **Grade:** CORROBORATED; agreeing axes: data, method (load-bearing); counted strictly (each run once): 2 axis/axes (data, method)
- **Novelty:** extends. Prior work: Lindemann & Bowern 2021 (h2 bounds); Bennett 1976; Timm 2025, voynich.ninja (verbose-cipher token budget); Rozanova & Temerev 2026 (Naibbe order and entropy). What this adds: Letter-in-core and verbose homophonic instances scored on five targets at matched K: they reach the core order but miss h2, rhythm and prefix memory.
- **Lines not counted:** 1 of 5 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-411, c-412, c-357, c-427, c-520, c-521 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: s82 matched-K re-score of both families on GPU (agrees) — `results_s82.txt`
  - method: s50 solver ladder (construction conflict) (agrees) — `results_s50.txt`
  - impl: Argon s72 wider L4w grid (flips CHARWIN -0.24..-0.40) & blind 6-language ID (42/42 pass null gate) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s72.txt`
  - data: 3 transliterations as targets (agrees) — `results_s82.txt`
  - method: s43 null-cipher twins (agrees) — `results_s43.txt`

### F-27

**Tested framings fail the joint battery**

Edge-pitch music, glyph-class superimposition, independent streams, liturgy and charms, copied-without-understanding drift and historical conlangs all fail.

- **Grade:** SINGLE; agreeing axes: method; counted strictly (each run once): 1 axis/axes (method)
- **Novelty:** new. Prior work: Friedman/Tiltman synthetic-language hypothesis (Tiltman 1967); Bowern & Lindemann 2021 (constructed-language discussion). What this adds: Several framings (edge-pitch music, superimposition, independent streams, liturgy and charms, copying drift, conlangs) scored on one joint battery.
- **Lines not counted:** 2 of 3 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-332, c-333, c-334, c-346, c-347, c-363, c-370 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: s24 music, s34 superimposition (agrees) — `results_s24.txt`
  - impl: Argon s37 genres, s51 selector [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s37_affix_cadence_and_genres.txt`
  - data: 3 transliterations (ZL3b, RF1b, IT2a) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s51_o051_o052_p4u2_closures.txt`

### F-28

**No antidotary, alphabetical or zodiac order**

Every planted comparator is recovered; the manuscript is null on all six across all three transliterations.

- **Grade:** TRIANGULATED; agreeing axes: data, external, impl, method; counted strictly (each run once): 2 axis/axes (data, external)
- **Novelty:** new. Prior work: Zandbergen, voynich.nu (zodiac month labels); D'Imperio 1978 (recipe section). What this adds: Planted-control tests for antidotary, alphabetical and zodiac ordering, all null on three transliterations.
- **Claims:** c-375, c-376 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s52_p4comp1 (agrees) — `results_s52_p4comp1_antidotary_zodiac.txt`
  - method: 6 independent comparator tests (antidotary, alphabetical, circular zodiac, month/constellation) (agrees) — `results_s52_p4comp1_antidotary_zodiac.txt`
  - data: 3 transliterations (ZL3b, RF1b, IT2a) (agrees) — `results_s52_p4comp1_antidotary_zodiac.txt`
  - external: Daybreak db-s118: the Antidotarium graph resemblance is generic, not source-specific (verdict GENERIC_OR_NON_SPECIFIC) (agrees) — `lab/codex_lab/experiments/results_s118_antidotarium_source_specificity.txt`

### F-29

**The scoring board measures the two-layer architecture, not where the cores come from**

An ordered affix wrapper over any core pool reaches most of the board, so cipher-vs-generator pairs under a shared wrapper tie by construction (L-130).

- **Grade:** SINGLE; agreeing axes: method; counted strictly (each run once): 1 axis/axes (method)
- **Novelty:** extends. Prior work: Parisel 2026, Evidence of Layered Positional and Directional Constraints (critique of acceptance-band batteries); Rozanova & Temerev 2026 (Naibbe and self-citation ports tie on weak order). What this adds: Shows that a shared ordered affix wrapper makes cipher and generator tie on the board by construction.
- **Lines not counted:** 3 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-361, c-303, c-304, c-342, c-343, c-344, c-345, c-362, c-366 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s36 two-layer operator [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s36_two_layer_operator_core.txt`
  - method: Phase 3 tie (s35) (agrees) — `results_s35.txt`
  - split: 166->41 held-out page evaluation [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s36_two_layer_operator_core.txt`
  - data: 3 transliterations (ZL3b, RF1b, IT2a) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s36_two_layer_operator_core.txt`

### F-31

**About half the line rhythm is predicted on reused pages, none on held-out quires**

Length-blind line automata reproduce ~50 % of the within-line rhythm on the reused 41 pages but fail the s67 LOQO rule (0-2/15) across all three transliterations.

- **Grade:** SINGLE; agreeing axes: none; counted strictly (each run once): 0 axis/axes (none)
- **Novelty:** new. Prior work: Vogt 2012 (line-position word lengths); Steckley & Steckley 2024 (line-position lengths). What this adds: Length-blind line automata reproduce about half the in-line rhythm on reused pages and none on held-out quires.
- **Lines not counted:** 3 of 3 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-417, c-516 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: Argon s74 LOQO [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s74.txt`
  - impl: Argon s74 [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s74.txt`
  - data: 3 transliterations (ZL3b, RF1b, IT2a) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s74.txt`

### F-32

**Page drift and cross-page carryover depend on the bound page order, mostly within quires**

The only constraints that need the bound order. A global page shuffle destroys the drift (rho -0.61 -> -0.02) and the carryover; a within-quire shuffle keeps most of the drift.

- **Grade:** CORROBORATED; agreeing axes: data, order; counted strictly (each run once): 1 axis/axes (data)
- **Novelty:** extends. Prior work: Layfield & Davis 2026, Singulion Structure, Digital Medievalist 19 (bound order not original); Timm 2026, The challenge of analyzing a dynamic text; Stolfi 2026, voynich.ninja (no large drifts). What this adds: Page-shuffle tests showing drift and carryover need the bound order, mostly within quires.
- **Rests on:** X-04 (Bound page and quire order is the reading order: unverified)
- **Lines not counted:** 1 of 3 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-421, c-519 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - order: s79 T3 global and within-quire shuffles (agrees) — `results_s79.txt`
  - data: 3 transliterations (agrees) — `results_s79.txt`
  - impl: Argon s75 Part 3: seams not fully reset (prefix z -4.36, line length z +3.50) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s75.txt`

### F-33

**No strong link between plant pictures and core vocabulary; affix frames associate with pictures**

With text masked out of the pictures and hand, quire and bifolio controlled, page pairs with similar plants do not share more cores (r 0.007..0.053, none p < 0.05) at a power that detects r ~0.23. Frames associate on all three transliterations (s78); s86 localizes the frame-picture link to the gallows/ch/sh slot complex (moving into cores under Zattera's 12-slot cut while stripped q/o/y/d/s frames drop to null) plus physical page/obstacle layout geometry (D_layout r=+0.095, p=0.0005).

- **Grade:** CORROBORATED; agreeing axes: data, physical; counted strictly (each run once): 1 axis/axes (data)
- **Novelty:** extends. Prior work: Montemurro & Zanette 2013; Sterneck et al. 2021 (topics follow scribe plus illustrated subject); Zattera 2022 (section differences are word-internal, not vocabulary); Schwartz 2026 (herbal section shows no tint). What this adds: An image-similarity test with hand, quire and bifolio controlled: cores do not follow plants, affix frames do.
- **Lines not counted:** 2 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-424, c-526 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - physical: s78 masked scan embeddings (DINOv2, SigLIP) vs transliteration (agrees) — `results_s78.txt`
  - data: 3 transliterations (agrees) — `results_s78.txt`
  - impl: Argon s86 Part 2 partial-Mantel layout/bifolio decomposition [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s86.txt`
  - seg: Argon s86 Part 2E SlotSegmenter, Canon+Comp, and Zattera 12-slot comparison [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s86.txt`

### F-35

**Syllabary, abjad and root-and-pattern encodings cannot give the manuscript's letter predictability**

All 29 encodings tested miss h2 (lowest 2.174 vs band 2.05-2.15) and every CHARWIN is negative across all three transliterations; the closure does not rest on core order.

- **Grade:** SINGLE; agreeing axes: none; counted strictly (each run once): 0 axis/axes (none)
- **Novelty:** extends. Prior work: Lindemann & Bowern 2021 (abbreviation and vowelless Hebrew do not give low h2); Bennett 1976 (Hawaiian closest); Dominik 2025, Arabic root morphology claim (contradicted). What this adds: 29 syllabary, abjad and root-and-pattern encodings all miss h2 and give negative CHARWIN.
- **Lines not counted:** 3 of 3 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-514 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s73 Part 1 [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s73.txt`
  - method: two independent targets (h2, CHARWIN) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s73.txt`
  - data: 3 transliterations as targets (ZL3b, RF1b, IT2a) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s73.txt`

### F-36

**Voynich word stems align to a reference vocabulary above null on half-splits only (cause unresolved; the denom_b-floor explanation is unsupported, D-063), not on 15-quire LOQO or G_word**

Restated after s84 and s88. Argon's word-stem code solver aligns Voynich stem graphs +60.1/+81.6/+35.3 bits above the best 6-draw null (+8.4) on half-splits; planted word codes rank #1 at every rung. Voynich misses the 'null + mean gap' bar (+106), as does the planted Latin control. s84 and s88 Part 3 attributed this half-split gain to the max(4500, n_pairs_b) denominator floor on 17.4k halves (D-063 found that attribution unsupported, so the cause is unresolved; scoring +40.6..+144.4 on order-free interleaved halves too, where 20-null p95 reaches +13.5..+29.2 and winning languages flip across segmenters), while on 15-quire LOQO (-14.04..-6.94) and the de-aliased G_word gate (5/6 planted W3 pass vs 0/9 Voynich, 0/75 P4-D1, 0/240 nulls) Voynich fails across all 3 segmenters.

- **Grade:** SINGLE; agreeing axes: split (load-bearing); counted strictly (each run once): 1 axis/axes (split)
- **Novelty:** extends. Prior work: Hauer & Kondrak 2016/2018 (algorithmic source-language identification; code noted missing in text_structure.md); published natural-language readings (none pass a blind fixed-key test, L-091). What this adds: A planted-control-calibrated stem-alignment solver that fails on LOQO and on the de-aliased gate.
- **Rests on:** X-04 (Bound page and quire order is the reading order: unverified)
- **Lines not counted:** 3 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-515, c-429, c-530 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s73 Parts 2-3 (half-split numbers verified; verdict relabelled) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s73.txt`
  - split: s84 order-free 15-quire LOQO vs 105 nulls: 0/15 folds above null p95, no stable language (agrees) — `results_s84.txt`
  - order: Argon s88 Part 3: 3 segmenters (SlotSegmenter, Zattera, Seg_Affix2) on half-splits, 15-quire LOQO (-14.04..-6.94), and de-aliased G_word gate (5/6 W3 pass vs 0/9 Voynich, 0/75 P4-D1, 0/240 nulls) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s88.txt`
  - data: 3 transliterations (ZL3b, RF1b, IT2a) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s88.txt`

### F-38

**A two-layer slot-plus-context language model beats the bar on 15-quire LOQO across three segmenters**

Strictly normalized over Sigma+, M3 (slot + position + scribe) and M5 (full mixture) beat M1_char3_wb on 15/15 held-out quires across all 9/9 (transliteration x segmenter) cells (+0.20..+0.28 bits/token on LOQO, +0.31..+0.49 on 166->41), and M4 (slot + s69 prefix chain) wins 15/15 on SlotSegmenter and 12-14/15 on Zattera and Seg_Affix2 (s75, s85).

- **Grade:** SINGLE; agreeing axes: none; counted strictly (each run once): 0 axis/axes (none)
- **Novelty:** extends. Prior work: Zattera 2022, CEUR 3313 (slot grammar F1); Stolfi word grammar; Dominik 2026, Structural Decipherment Without Lexical Recovery (cross-validated morphology). What this adds: Strictly normalised held-out bits per token for slot-plus-context models across quires and segmenters; every line is POST-HOC unverified.
- **Rests on:** X-07 (The 41 held-out pages are an uncontaminated test set: at-risk); X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 4 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-518, c-522 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s75 Part 2 [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s75.txt`
  - split: Argon s85 Part 1 15-quire LOQO (15/15 quires in all 9/9 cells) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s85.txt`
  - seg: Argon s85 Part 1 SlotSegmenter, Zattera 12-slot, and Seg_Affix2 (X-01 discharge withdrawn 2026-10-19: this segmenter is NOT ADEQUATE on planted books, vx01 A1 c-592) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s85.txt`
  - data: 3 transliterations (ZL3b, RF1b, IT2a) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s85.txt`

### F-45

**Period-documented ciphers over period recipe texts do not reproduce the manuscript; low h2, positive length rhythm and in-line reuse must come from the encoding itself**

s102: Latin, Venetian/Tuscan and southern German recipe texts under substitution+nulls, homophonic+nulls, a 200-word nomenclator and a line-held nomenclator: 0/12 cells match. All fail in-line core reuse, the slot battery (<= 1/15), the within-line length rhythm (negative excess everywhere vs about +0.07) and h2 (3.2-4.7 vs 2.02-2.23). The planted decoder recovers every cell and the manuscript run as a control passes, so the test can pass.

- **Grade:** CORROBORATED; agreeing axes: data, method; counted strictly (each run once): 1 axis/axes (data)
- **Novelty:** extends. Prior work: Greshko 2025 (period-plausible verbose cipher); Megyesi et al. 2021/2022 (period key profile); Timm 2025, voynich.ninja (token budget). What this adds: Period-documented ciphers over period recipe texts fail all targets while the planted decoder recovers every cell.
- **Claims:** c-439 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: s102 three period plaintexts in three languages (agrees) — `results_s102.txt`
  - method: s102 four period encodings scored on signature, battery, rhythm and h2 (agrees) — `results_s102.txt`

### F-47

**Spec-built verbose table encodings of real recipe text fail; shuffled input fits the line rhythm better than real word order**

s104 (grid G1): line-row syllabary, a 100-core nomenclator with a first-order prefix wheel and line-held suffixes, and abbreviate-then-nomenclator, over Latin, Venetian/Tuscan and southern German recipe text: 0/9 cells and 0/9 shuffled twins pass the core signature, slot battery and h2 (2.64-4.02 vs 2.02-2.23). Real word order gives negative within-line length rhythm in the nomenclator cells; six shuffled twins give positive rhythm.

- **Grade:** CORROBORATED; agreeing axes: data, method; counted strictly (each run once): 1 axis/axes (data)
- **Novelty:** extends. Prior work: Greshko 2025 (Naibbe); Megyesi et al. 2021/2022; Timm 2025, voynich.ninja (token budget). What this adds: Spec-built verbose tables over real recipe text fail, and shuffled input fits the rhythm better than real word order.
- **Claims:** c-447 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: s104 three spec-built constructions, each with a shuffled-input twin (agrees) — `results_s104.txt`
  - data: three recipe plaintexts in three languages (agrees) — `results_s104.txt`

## At risk

### F-21

**Glyph-confusion enrichment sits in the generator range, below visually copied Latin**

Confusion enrichment sits in the generator range, below copied Latin; in-line repeats match bag-of-words. Holds across all three transliterations, three segmenters, 14-15/15 LOQO quires, and s45/s47 physical ink-verified tokens (s86).

- **Grade:** SINGLE; agreeing axes: impl; counted strictly (each run once): 1 axis/axes (impl)
- **Novelty:** new. Prior work: Timm 2014 and Timm & Schinner 2019 (copying as self-citation, a different sense of copying). What this adds: Confusion-pair enrichment sits in the generator range, below copied Latin; no published visual-copy error test is in our records.
- **Lines not counted:** 5 of 6 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-378, c-527, c-436 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s53 error battery (agrees) — `results_s53_p4a1_p4e1_anchors_and_errors.txt`
  - data: Argon s86 Part 3B 3 transliterations (ZL3b, RF1b, IT2a) (agrees; not counted) — `results_s86.txt`
  - seg: Argon s86 Part 3B SlotSegmenter, Zattera 12-slot, and Canon+Comp (agrees; not counted) — `results_s86.txt`
  - split: Argon s86 Part 3B 15-quire LOQO [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (disagrees, resolved: s95 (c-436): per-quire R_P1 has no power; size-matched copied-Latin control spans 0.15-1.3 and does not separate copied from composed Latin; the split axis neither supports nor refutes F-21; not counted) — `results_s86.txt`
  - physical: Argon s86 Part 3B s45/s47 physical ink-verified tokens (agrees; not counted) — `results_s86.txt`
  - split: s95 size-matched per-quire copied-Latin control (C1 False 8/5/5 of 15, C2 0/15) (agrees; not counted) — `results_s95.txt`

### F-23

**No lexical producer predicts held-out pages or quires**

Local memory 0/6, independent affix wrapper 1-2/6, joint whole-word 0-1/6, constrained assembly fails 14-15/15 quires. Confirmed on 15-quire LOQO across all four producers (0/180 impl cells), three segmenters in both rescore and native modes (0/300 seg cells), and the s45 127-page physical ink-verified subset (0/88 >=4-page quire folds, s88).

- **Grade:** CONTESTED; agreeing axes: data, physical, seg, split (load-bearing); counted strictly (each run once): 3 axis/axes (data, physical, split)
- **Novelty:** extends. Prior work: Schwartz 2026 (generator misses 2-3 of 22 statistics); Rozanova & Temerev 2026 (Naibbe and self-citation ports miss edges and hapax); Parisel 2026 (grille and slot generator fail the joint criterion); Gaskell & Bowern 2022 (samples too short for page/quire structure). What this adds: Leave-one-quire-out held-out prediction across four producer families and three segmenters (status at-risk).
- **Rests on:** X-07 (The 41 held-out pages are an uncontaminated test set: at-risk)
- **Lines not counted:** 1 of 8 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-396, c-397, c-398, c-399, c-402, c-403, c-406, c-529 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: held-out 41 pages (s57, s58, s61) (agrees) — `results_s57.txt`
  - split: LOQO 15 quires (s67) (agrees) — `results_s67.txt`
  - data: 3 transliterations (agrees) — `results_s61.txt`
  - split: Argon s88 Part 2A 15-quire LOQO on all 4 producers (0/180 cells across ZL3b/RF1b/IT2a) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s88.txt`
  - seg: Argon s88 Part 2B 15-quire LOQO across SlotSegmenter, Zattera, and Seg_Affix2 in rescore and native modes (0/300 cells) (agrees) — `results_s88.txt`
  - physical: Argon s88 Part 2C s45 127-page ink-verified subsets ink_lines_127 and ink_full_127 (0/88 >=4-page quire folds, 0/96 all-quire folds) (agrees) — `results_s88.txt`
  - method: Argon s101 power audit: the original LOQO criterion recovers a planted true s57/s58/s61/s67 producer on only 0-2/15 folds, so these exclusions are uninformative (disagrees (unresolved)) — `results_s101.txt`
  - impl: roach r13 blind: refitted copy-and-vary recovered 8/15 (weak), oracle 13/15; real 1/15 is not an exclusion (disagrees (unresolved)) — `runs/roach-r13/results_r13.txt`

### F-26

**The manuscript sits between word code and generator, outside both on wrapper-free features**

Blind identifiability separates families as built (21/24) but not tuned producers or generator/message twins. Voynich lies between word-code and generator centroids, and outside both on matched-K core order, short-range core reuse, cross-page core coverage and prefix predictability (s55, confirmed at matched K=50, 100, 200 and canonical coverage in s85).

- **Grade:** SINGLE; agreeing axes: method; counted strictly (each run once): 1 axis/axes (method)
- **Novelty:** extends. Prior work: Gaskell & Bowern 2022, Gibberish after all?; Amancio et al. 2013, PLoS ONE; Timm & Schinner 2019; Schwartz 2026. What this adds: Blind family identification places Voynich between word-code and generator centroids and outside both on wrapper-free features (at-risk).
- **Rests on:** X-06 (A plug-in MI excess can detect core order at the core-inventory size used: flipped) — weighted half while at risk
- **Lines not counted:** 2 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-390, c-391, c-392, c-393, c-394, c-524 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: s49 identifiability on 30 known texts (agrees) — `results_s49.txt`
  - method: s55 layer-split features (agrees) — `results_s55.txt`
  - method: Argon s85 Part 3A matched-K (K=50,100,200) & canonical coverage re-evaluation across 32 corpora [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (disagrees (unresolved); not counted) — `results_s85.txt`
  - data: 3 transliterations [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s85.txt`

### F-30

**Neither a weakened table-and-grille nor constrained assembly predicts held-out quires**

Under the pre-registered LOQO rule the weakened grille (global and per-scribe) scores 0/15 on all three transliterations, although it matches the prefix-memory call pattern on ZL3b and RF1b. Holds under Zattera 12-slot and boundary-free Seg_Affix2 segmenters (0-3/15, s85).

- **Grade:** CONTESTED; agreeing axes: data, external, impl, split (load-bearing); counted strictly (each run once): 2 axis/axes (data, external)
- **Novelty:** replicates. Prior work: Parisel 2026, arXiv 2604.19762 (Cardan grille never meets the joint criterion); Rugg 2004 and Rugg & Taylor 2016 (claim success); Zandbergen 2021, The Cardan grille approach taken to the next level. What this adds: Nothing beyond re-finding Parisel's grille failure: our weakened and per-scribe LOQO exclusion has no power (c-454, c-542), and the x01 check says to cite Parisel.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 1 of 7 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-415, c-416, c-523 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: Argon s71 LOQO 15 quires (agrees) — `results_s71.txt`
  - data: 3 transliterations (agrees) — `results_s71.txt`
  - impl: Argon s71 (voynich-08 s67 rule, separate code) (agrees) — `results_s71.txt`
  - seg: Argon s85 Part 2B Zattera 12-slot and Seg_Affix2 on 15-quire LOQO (WTG and CA < 8/15 in 18/18 cells) (X-01 discharge withdrawn 2026-10-19: this segmenter is NOT ADEQUATE on planted books, vx01 A1 c-592) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s85.txt`
  - method: Argon s101 power audit: the original LOQO criterion recovers a planted true s71 weakened table-and-grille on only 1-4/15 folds, so the exclusion is uninformative (disagrees (unresolved)) — `results_s101.txt`
  - impl: roach r13 blind: refitted table-and-grille recovered 0/15 (uninformative), oracle 14/15; real 0/15 is not an exclusion (disagrees (unresolved)) — `runs/roach-r13/results_r13.txt`
  - external: Parisel 2026: a Cardan grille generator (Rugg 2004) tested across its parameter space cannot reach the cross-boundary MI and end-to-start rate together (abstract lines 22-25; generator lines 284-290). Lead-verified 2026-10-19 11:21 (agrees) — `data/external/papers/parisel_2026_arxiv_2604.19762.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)

### F-34

**A line-held affix table reproduces the prefix memory on held-out quires, but the sticky Naibbe cipher predicts none of them**

Line-sticky Naibbe (Latin, Italian) matches the s69 call pattern on 13-15/15 held-out quires on all three transliterations (and under Seg_Affix2 and Zattera in s85); default, line-lock and page-lock do not. All variants predict 0/15 quires across 72/72 (transliteration, segmenter, variant) cells: type ratio and flow entropy (P4, P5) fail everywhere, and the s55 wrapper-free distance is outside Voynich's own range.

- **Grade:** CONTESTED; agreeing axes: data, external, method, split (load-bearing); counted strictly (each run once): 3 axis/axes (data, external, method)
- **Novelty:** extends. Prior work: Greshko 2025, The Naibbe cipher; Rozanova & Temerev 2026 (default Naibbe misses edges, near-repeats and hapax). What this adds: A line-sticky Naibbe variant reproduces the prefix-memory call pattern but predicts no held-out quire.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 2 of 9 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-428, c-523 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: s81 15-quire LOQO, stickiness fitted on training quires (agrees) — `results_s81.txt`
  - data: 3 transliterations (agrees) — `results_s81.txt`
  - method: two plaintext languages, six table variants (agrees) — `results_s81.txt`
  - seg: Argon s85 Part 2C SlotSegmenter, Zattera, and Seg_Affix2 on 15-quire LOQO (0/15 LOQO in 72/72 cells; line-sticky matches s69 signature on 13-15/15 Slot/Seg_Affix2 folds and matches Zattera ~5x scale) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (disagrees, resolved: scope: holds under SlotSegmenter and Seg_Affix2 (13-15/15), fails under Zattera; X-01 stays at-risk; not counted) — `results_s85.txt`
  - impl: Argon s85 Part 2C independent LOQO implementation (agrees; not counted) — `results_s85.txt`
  - impl: roach r6 blind: fixed line-held affix table fits 0/15 held-out quires (ZL, IT); affixes do not reset at line breaks (X 1.050/1.069) and suffix order decays (disagrees (unresolved)) — `runs/roach-r6/results_r6.txt`
  - impl: roach r9 blind: a drifting affix table also fits 0/15 held-out quires (ZL, IT); Latin shows the same within-page drift (disagrees (unresolved)) — `runs/roach-r9/results_r9.txt`
  - method: Argon s101 power audit: line-sticky C2 (s69 call match) recovers a planted instance 15/14/15 (sticky75) and 9/13/15 (fit); C1 battery 0/15 uninformative (agrees) — `results_s101.txt`
  - external: Rozanova and Temerev 2026, default (non-sticky) Naibbe of Latin: edge MI 0.006 vs Voynich 0.197 bits, near-repeat ratio 0.82 vs 1.12, single-occurrence words 41% vs 70% (lines 696-698); bears on the Naibbe half only. Lead-verified 2026-10-19 11:21 (agrees) — `data/external/papers/rozanova_temerev_2026_arxiv_2608.17096.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)

### F-37

**Tested transposition and single-null-glyph schemes do not explain the text**

Interleave, reverse-half, boustrophedon, columns 2-6, diagonals, core shifts and single null strips are disfavoured (48/48 power gate). Confirmed at s80 matched-K (K=50, 100, 200) in s85: 0/20 non-standard trajectories, 0/8 shifts Delta != 0, and 0/22 glyph deletions reach the language floor (+0.068..+0.196), and deleting 'o' in the s67 CA generator produces the same core-type merge (-24%) and +0.017 MM_K100 bump as in Voynich (+0.010).

- **Grade:** SINGLE; agreeing axes: none; counted strictly (each run once): 0 axis/axes (none)
- **Novelty:** extends. Prior work: Parisel 2025, Directionality of the Voynich Script (LTR vs RTL); Megyesi et al. 2021 (96% of 15th-c. keys use nulls). What this adds: Power-gated tests of interleave, reversal, column, diagonal and single-null-glyph schemes, all disfavoured.
- **Rests on:** X-06 (A plug-in MI excess can detect core order at the core-inventory size used: flipped) — weighted half while at risk
- **Lines not counted:** 3 of 3 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-517, c-524 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: Argon s75 Part 1 re-frozen run [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s75.txt`
  - method: Argon s85 Part 3B s80 matched-K (K=50,100,200) re-score & s67 CA 'o'-deletion control [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (disagrees (unresolved); not counted) — `results_s85.txt`
  - data: 3 transliterations [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s85.txt`

### F-39

**Plaintext letters or syllables spread over homophone cores leave too little same-core repetition (robust across independent segmenters); their excess core order depends on how affixes are stripped**

Under a line-held affix table, homophonic letter/syllable/chunk-in-core ciphers selected on training quires predict 0/15 held-out quires across all 3 segmenters (0/135 in s88); their matched-K core order exceeds Voynich's 95% CI upper bound by +0.08..+0.28 bits at K=100 across all 21 (granularity x reading-order) cells while R(1) stays below 1 (0.34-0.89 vs 1.16-1.21), independent re-segmentation breaks HLT's synthetic prefix-core boundary, and on the solver side (s86) an unsupervised Line-Suit HMM + SA solver achieves 6/6 Top-1 blind language ID on planted HLT ciphers while rejecting real Voynich across all 3 transliterations.

- **Grade:** TRIANGULATED; agreeing axes: data, impl, method, split (load-bearing); counted strictly (each run once): 2 axis/axes (data, impl)
- **Novelty:** extends. Prior work: Rozanova & Temerev 2026 (Naibbe has more order and fewer near-repeats than Voynich); Timm 2025, voynich.ninja (verbose-cipher token budget); Greshko 2025. What this adds: Syllable and chunk homophone ciphers with a line-held table, scored across segmenters and against a blind solver.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 4 of 8 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-430, c-525, c-528 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: s83 15-quire LOQO, configuration selected on training quires (agrees) — `results_s83.txt`
  - data: 3 transliterations (agrees) — `results_s83.txt`
  - method: matched-K core order (s80 pipeline) and R(1), independent of the s67 battery (agrees) — `results_s83.txt`
  - impl: Argon s86 Part 1 Line-Suit HMM + SA solver ladder & blind 6-language ID on HLT ciphers (6/6 Top-1 on planted HLT vs 0/8 on controls and Voynich) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s86.txt`
  - seg: Argon s88 Part 1: 0/135 LOQO folds across SlotSegmenter, Zattera 12-slot, and Seg_Affix2 (All7 0/15 in 9/9 cells; independent segmenters break HLT prefix-core boundary) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s88.txt`
  - seg: audit 2026-10-18 (lead): excess-order / low-R(1) mechanism under Zattera and Seg_Affix2: HLT MM_K100 below Voynich (Ex_vs_Voy -0.064) and R_win 1.06-1.36 (results_s88.txt:58, 92, 113) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (disagrees, resolved: r8 (independent): the low-recurrence half holds under both segmenters; the excess-order half is segmenter-dependent; F-39 restated to the robust half; not counted) — `results_s88.txt`
  - order: Argon s88 Part 1: T1 line reversal and T2 token reversal preserve MM_K100 (+0.126..+0.318 > Voynich CI_hi +0.044) and R_win(1) (0.34..0.89 < Voynich 1.16..1.21) in 21/21 cells [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s88.txt`
  - impl: roach r8 blind: homophonic ciphers under a per-line table have lower immediate core recurrence than Voynich under both independent segmenters (14-15/15); higher core order only under S1 (agrees) — `runs/roach-r8/results_r8.txt`

### F-40

**The core layer matches no tested reference class; none of the 23 tested natural texts (prose, verse, list, medical-table) reuses words in-line (a Lullian combinatory letter-table does, s107), and none of the 4 tested pool generators has its weak order**

Across 23 natural texts in 7 genres (4 list-genre: glossary, antidotary, cookery books, herbal; 5 prose; 4 verse; 10 ritual/tabular/abbreviated), 38 human gibberish writers, and constructed texts (Steganographia, Enochian, Lingua Ignota, Lull), 0 texts reuse words inside a line more than chance (0.009-0.538, p >= 0.996), whereas Voynich cores repeat 1.13-1.22x inside lines (p <= 0.01) and 0.26-0.86x across line breaks while carrying weak positive order (+0.019..+0.110 at K=100), and all 4 pool generators fail core order (-0.023..+0.025) and cross-line avoidance (0.92-1.03). [Correction 2026-10-19, db-s-core-return-20261019, audited: the 0.26-0.86x cross-line figure is against a page-token shuffle; with whole lines reordered within pages, no residual cross-line suppression is detected (core O/E 1.06-1.18), so cross-line avoidance and the generators failing it are not discriminating evidence. Core order and in-line reuse are unaffected.] Confirmed across 5 segmenters incl. Zattera, Seg_Affix2, Canon+Comp, and unsegmented RawWord (15/15 Voynich vs 0/20 generators, 0/31 reference texts), 4 uniform reading-order transforms (36/36), and s45/s47 physical ink-verified lines & spaces (21/21 1:1 ink-aligned cells, 87.5-90.5% physical ink-space separation on repeated-core pairs, s92).

- **Grade:** TRIANGULATED; agreeing axes: data, impl, method, split (load-bearing); counted strictly (each run once): 4 axis/axes (data, impl, method, split)
- **Novelty:** extends. Prior work: Timm 2016 (consecutive identical words); Timm 2014; Rozanova & Temerev 2026 (prose near-neighbour 0.28-0.56; Species Plantarum 2.57x; self-citation port has weak order); Gaskell & Bowern 2022; Stellar 2026. What this adds: Exact in-line reuse against a shuffle across 23 natural texts, gibberish writers and constructed texts; contested by the R&T catalogue and Timm-Schinner port.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 7 of 19 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-431, c-432, c-433, c-434, c-531, c-532, c-533, c-438 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: s87 13 natural texts on real or Voynich-length lines, words and stems (agrees) — `results_s87.txt`
  - impl: roach r5: Latin prose R_within(1) 0.13 vs Voynich 1.32 (agrees) — `runs/roach-r5/results_r5.txt`
  - data: 3 transliterations (agrees) — `results_s87.txt`
  - split: s87 amendment 1: 15 blocks, corrected held-out order sample (agrees) — `results_s87_amend1.txt`
  - method: s89: 10 more texts with line-level repetition (ritual, tabular, abbreviated): 0/10, all fail in-line reuse (agrees) — `results_s89_amend1.txt`
  - method: s90: human gibberish (38 writers) and constructed texts: none reuses words in-line; power check passes (agrees) — `results_s90.txt`
  - seg: Argon s92 Part 1: 5 segmenters (SlotSegmenter, Zattera, Seg_Affix2, Canon+Comp, RawWord): Voynich 15/15 pass C1 vs 0/20 generators, 0/31 primary reference texts, 0/60 stem re-segmentations (agrees; not counted) — `results_s92.txt`
  - order: Argon s92 Part 2: 36/36 uniform reading-order cells (T0_standard, T1_line_rev, T2_tok_rev, T3_full_page_rev) pass C1; T4_boustrophedon cancels directional flux in 9/9 [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (agrees; not counted) — `results_s92.txt`
  - physical: Argon s92 Part 3: s45 127 clean Yale scan pages (21/21 1:1 & clean-127 cells pass C1) & s47 physical ink-gap audit (87.5-90.5% physical ink-space call rate on adjacent repeated cores) (agrees; not counted) — `results_s92.txt`
  - physical: audit 2026-10-18 (lead): most physical stream ZL3b_ink_full_127 fails in-line reuse in 2/3 segmenter cells (Rw 1.056 p 0.066; 0.979 p 0.69; results_s92.txt:285-287) [POST-HOC 2026-10-19: results overwritten after stub re-stamp, phase8-1-rerun-audit.md; stops counting until a blind replication passes] (disagrees, resolved: partial: holds under Zattera (Rw 1.086 p 0.017); small sample (127 pages); F-40 rests on s87/s89/s90/r5 independently; not counted) — `results_s92.txt`
  - method: s97 hard-way natural texts (abbreviated Latin, unpointed Hebrew and Arabic, verbose Latin/Italian re-spelling, sigla): 0/6 reach the signature + battery on any segmenter (agrees) — `results_s97.txt`
  - impl: roach r7 blind, 3 core definitions: no reference text (Forme of Cury, Litany, Manzoni) shows in-line reuse with cross-line avoidance (agrees) — `runs/roach-r7/results_r7.txt`
  - seg: roach r7: full four-part conjunction per quire 0-2/15 under independent core definitions; in-line reuse 9/15 (S1) but 4/15 under an MDL core definition (disagrees, resolved: scope: F-40 is a whole-text and reference-class claim; the per-quire conjunction is not replicated and in-line reuse depends on the core definition (X-01 stays at risk)) — `runs/roach-r7/results_r7.txt`
  - data: s107 tabular texts: Tacuinum and De gradibus fail (b) (Rw1 0.03-0.64, p=1.0); Llull Tabula generalis 1515 (957 OCR tokens) shows (b)+(c) under all three segmenters, full signature False (disagrees, resolved: scope: holds for prose, verse, lists and medical tables; a combinatory letter-table repeating identical cells shows in-line reuse; the full signature still matches no reference text) — `results_s107.txt`
  - data: roach r11 blind: 11 more reference texts (litanies, refrains, recipes, synonym list, abbreviated Latin, unpointed Hebrew) show (b) on 0 blocks; Voynich itself 6/15 blocks under S1 (agrees) — `runs/roach-r11/results_r11.txt`
  - external: Rozanova and Temerev 2026 Table 4 (lines 440-447): Species Plantarum records have edit-1 near-identical neighbours 2.57x vs Voynich 1.12, so a published list genre shows near-repeats. Different statistic (adjacent edit-1, not line-bounded same-core R_within). Its order is strong (1.348 bits, 15.8%) where Voynich is weak (0.067, 0.81%), so the joint reuse plus weak-order profile is not matched (disagrees (unresolved); not counted) — `data/external/papers/rozanova_temerev_2026_arxiv_2608.17096.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)
  - external: Rozanova and Temerev 2026 lines 671-679, 694-697: Timm-Schinner self-citation generator port reproduces token order 0.5-0.6% (Voynich 0.79%) and edit-1 1.06-1.23 (Voynich 1.12), but not edge-glyph MI (0.006-0.009 vs 0.197 bits) or hapax share (59-60% vs 70%) (disagrees (unresolved); not counted) — `data/external/papers/rozanova_temerev_2026_arxiv_2608.17096.txt` (not in this repository; see `MISSING-EVIDENCE.tsv`)
  - method: EXPLORATORY Opus 2026-10-19 13:30 (D-085, O-086): cross-line avoidance is line-edge vocabulary. With a position-preserving null (line-final core vs line-initial cores of OTHER lines, same page), cross-break identical-core O/E is 1.08/1.18/1.08 (slot core, ZL3b/RF1b/IT2a) and 0.93-0.94 (a2 core), against 0.60-0.66 under the s87-style page shuffle, which reproduces F-40 R_cross. In-line reuse survives the position-preserving null (slot core O/E 1.17-1.20, words 1.20-1.26, a2 core 1.07-1.09; no p computed). So criterion C1(c) R_cross<R_within, and the generators failing it, are an artefact of the null (disagrees (unresolved); not counted) — `runs/explore/rcross_edge_null_20261019.txt`
  - method: db-s-core-return-20261019 (Astra, frozen 20:34:45Z, independent result audit PASS; exact s87 amend1 22,500-token inputs ending f96r/f99r): with complete lines reordered within their pages, cross-break identical-core repeats are 64/75/75 against null means 60.4/63.6/65.7 (O/E 1.06/1.18/1.14, lower-tail p .73/.97/.91, residual-suppression criterion met 0/3); the page-token shuffle gives 113.1/111.9/115.3 (p 1/1001). Opus derivation from results.json: the null 95% lower bounds 47/50/51 correspond to O/E about 0.78, so residual suppression as strong as the F-40 page-shuffle 0.56-0.67 would have fallen outside them (disagrees, resolved: scope (Opus 2026-10-19T20:40Z): the page-token cross-line deficit does not establish avoidance beyond the line composition kept by whole-line reordering. Not shown: equivalence, absence of every ordering effect, or that edge vocabulary alone causes it. In-line reuse is invariant to this null and stands. Reused inputs, not whole-book; three transliterations of one manuscript) — `lab/runs/db-s-core-return-20261019/REPORT.md`

### F-41

**A per-line core pool reproduces in-line reuse out of sample (its cross-line avoidance match is uninformative, db-s-core-return), but not mild quire locality with weak order**

s91 fits a line-scoped producer per LOQO fold (quire lexicon from training, per-line pool, transition, cross-line penalty). Parts (b) and (c) of the F-40 signature hold on 45/45 held-out quires with the copy parameter at 0, so pool size alone produces the in-line reuse. The full signature holds on 21/45 folds (8, 6, 7 of 15; failures locality 21, order 5): generated text is too quire-local. The s67 slot battery fails (0-1/15 folds). Parameters are not identified. In s93 Part 1, replacing the per-quire lexicon with a shared cross-quire lexicon at fixed hyper-parameters (LP93: conc=5000, alpha=8, rho=0, lam=0.42, pen=0.85, not fitted per fold) lifts locality to 0.975-0.976 and C1 to 14-15/15 (while fixed alpha=8 overshoots R_within(1) to 3.07-3.24), and pairing LP93 with training-quire core-class line-sticky affixes, graphical handshake, and cadence (M4_ULP93_Cadence) lifts P7 to 11-12/15, P5 to 14-15/15, P1 to 14/15, de-aliased C2 to 10-12/15, and unmodified legacy s67 C2_leg from 0/15 to 5/15, 6/15, 4/15 (still short of >=8/15).

- **Grade:** TRIANGULATED; agreeing axes: data, impl, method, split; counted strictly (each run once): 3 axis/axes (data, impl, method)
- **Novelty:** new. Prior work: Timm & Schinner 2019 (self-citation generator); Schwartz 2026 (reuse/copy/coinage generator). What this adds: A per-line pool producer fitted per LOQO fold reproduces in-line reuse with copying off, but not quire locality with weak order.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 2 of 7 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-435, c-534 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: 15-quire LOQO, fit on training quires only (agrees) — `results_s91.txt`
  - data: 3 transliterations (agrees) — `results_s91.txt`
  - method: Argon s93 Part 1: fixed shared-lexicon LP93 (C1 14-15/15, Rw1 3.07-3.24) + core-class line-sticky affixes + handshake + cadence (legacy C2_leg 4-6/15 vs 0/15 in s91; de-aliased C2 10-12/15) (agrees; not counted) — `results_s93.txt`
  - impl: roach r10 blind: per-line pool, drifting pool and copy-recent generators match 1-3/15 held-out quires; all miss quire locality most; copy rate 0.02 (agrees) — `runs/roach-r10/results_r10.txt`
  - method: Argon s101 power audit: LP91 C1 core signature recovers a planted LP91 7/5/14 (weak); C2 0-2/15 uninformative (agrees) — `results_s101.txt`
  - method: EXPLORATORY Opus 2026-10-19 13:30 (D-085, O-086): cross-line avoidance is line-edge vocabulary. With a position-preserving null (line-final core vs line-initial cores of OTHER lines, same page), cross-break identical-core O/E is 1.08/1.18/1.08 (slot core, ZL3b/RF1b/IT2a) and 0.93-0.94 (a2 core), against 0.60-0.66 under the s87-style page shuffle, which reproduces F-40 R_cross. In-line reuse survives the position-preserving null (slot core O/E 1.17-1.20, words 1.20-1.26, a2 core 1.07-1.09; no p computed). So criterion C1(c) R_cross<R_within, and the generators failing it, are an artefact of the null; F-41 reproducing cross-line avoidance out of sample is therefore not informative (disagrees (unresolved); not counted) — `runs/explore/rcross_edge_null_20261019.txt`
  - method: db-s-core-return-20261019 (Astra, frozen 20:34:45Z, independent result audit PASS; exact s87 amend1 22,500-token inputs ending f96r/f99r): with complete lines reordered within their pages, cross-break identical-core repeats are 64/75/75 against null means 60.4/63.6/65.7 (O/E 1.06/1.18/1.14, lower-tail p .73/.97/.91, residual-suppression criterion met 0/3); the page-token shuffle gives 113.1/111.9/115.3 (p 1/1001) (disagrees, resolved: scope (Opus 2026-10-19T20:40Z): the page-token cross-line deficit does not establish avoidance beyond the line composition kept by whole-line reordering. Not shown: equivalence, absence of every ordering effect, or that edge vocabulary alone causes it. In-line reuse is invariant to this null and stands. Reused inputs, not whole-book; three transliterations of one manuscript) — `lab/runs/db-s-core-return-20261019/REPORT.md`

### F-42

**Uncommon cores recur slightly more within a quire than across quires (+0.003 to +0.005), with no page-order direction**

Daybreak db-s95..db-s97, db-s106 (imports our loaders/metrics, so not impl): same-quire pages predict tail-core repeats better than global frequency and than cross-quire identity, by small real deltas of about +0.003 to +0.005 (c-594, c-596; the +0.039/+0.059 figures were fixture values, corrected 2026-10-19); earlier and later pages predict each other equally (db-s96 C4_FORWARD_DIRECTIONAL False), so the pool persists without forward transmission. Scale verdict QUIRE_REGISTER_POOL (db-s97). Relevant to F-41/s94: the generator should have a shared head plus a quire-local tail.

- **Grade:** CORROBORATED; agreeing axes: method, split; counted strictly (each run once): 2 axis/axes (method, split)
- **Novelty:** extends. Prior work: Timm 2014 (repeats peak within nearby lines); Timm & Schinner 2019 (copying from earlier text implies a direction); Montemurro & Zanette 2013 (local keyword clustering). What this adds: Same-quire tail-core repetition beats global frequency by a small delta (+0.003 to +0.005) and is symmetric in page order, against forward transmission.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Claims:** c-593, c-594, c-595, c-596 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: Daybreak db-s95 tail transfer and db-s96 forward vs backward quire tail prediction (agrees) — `lab/codex_lab/experiments/results_s96_forward_quire_tail_prediction.txt`
  - method: Daybreak db-s97 codicological scale (quire/register pool) and db-s106 cross-fit (agrees) — `lab/codex_lab/experiments/results_s97_tail_core_codicological_scale.txt`

### F-43

**Less-frequent label cores retrieve their own page's paragraph vocabulary, but only under one core representation**

Daybreak db-s109: label cores retrieve the body vocabulary of their own page (MRR 0.630 vs null q99 0.588, p 0.002). The segmenter-free version (db-s111) fails its gate, so the link depends on the core representation.

- **Grade:** CONTESTED; agreeing axes: data, method, seg; counted strictly (each run once): 3 axis/axes (data, method, seg)
- **Novelty:** new. Prior work: Schwartz 2026 (label register: o-initial labels, label types on several pages). What this adds: Label cores retrieve own-page body vocabulary under one representation only; the split-free version fails its gate.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Claims:** c-455, c-548, c-597, c-598 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - method: Daybreak db-s109 label to page-body retrieval (agrees) — `lab/codex_lab/experiments/results_s109_label_page_body_retrieval.txt`
  - seg: Daybreak db-s111 segmenter-free label anatomy fails its gate (disagrees (unresolved)) — `lab/codex_lab/experiments/results_s111_segmenter_free_label_anatomy.txt`
  - data: s109 frequency-matched cross-section label test: ok-/ot- enrichment not real (OR 1.29, p 0.93); recurring adjacent pairs p 0.0001 but mostly single-glyph columns (agrees) — `results_s109.txt`
  - seg: db-s110: label anchor holds under Canon+Comp only (RawWord MRR 0.379 < q99) (agrees) — `lab/codex_lab/experiments`

### F-44

**Rare label cores do not sit in the body lines physically nearest the label**

s99: across 57 rare-core label events on 24 pages (ZL3b, Rozanova word boxes), the lines carrying the label core are not nearer the label than chance (mean normalized distance rank 0.544 vs 0.500, p 0.90); frame, common-core and moved-page controls are null; the planted fixture is detected (p .0005). Minimum detectable shift 0.088, so gradients of about 0.09 or more are excluded. Few herbal labels qualify; f66r gives 14 events.

- **Grade:** SINGLE; agreeing axes: physical; counted strictly (each run once): 1 axis/axes (physical)
- **Novelty:** new. Prior work: none found in our records. What this adds: Rare label cores are not physically nearest the label, with a stated minimum detectable shift of 0.088.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 1 of 2 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-437 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - physical: s99 Rozanova word-box distances on 24 pages (agrees) — `results_s99.txt`
  - seg: s99 Zattera direction check (n 8, underpowered) (agrees; not counted) — `results_s99.txt`

### F-46

**Prefix choice is close to first-order; a line-held table leaves far more lag-2 prefix dependence than the manuscript has**

s98: lag-2 prefix dependence given the intervening prefix (cross-fitted CMI against an exact first-order null) is positive on only 4-5/15 held-out quires in Voynich, about 0.3x the s81 line-held table's, which shows it on 10-12/15; a first-order control shows 0/15. A weak residue remains. Suffixes show more lag-2 structure (6/15, 1.6-2.7x s81).

- **Grade:** TRIANGULATED; agreeing axes: data, impl, split; counted strictly (each run once): 2 axis/axes (data, impl)
- **Novelty:** extends. Prior work: Dominik 2026 (predecessor-class gain); Stellar 2026 (whole-token lag >= 2 MI at floor). What this adds: A cross-fitted lag-2 prefix CMI against an exact first-order null, with a line-held table overshooting it.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Claims:** c-440 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - split: s98 15-quire LOQO, cross-fitted on training quires (agrees) — `results_s98.txt`
  - data: 3 transliterations (agrees) — `results_s98.txt`
  - impl: roach r6: affix streams are not one table per line; adjacent-line sharing above page level, decaying suffix order (agrees) — `runs/roach-r6/results_r6.txt`

### F-48

**Affix mixtures drift slowly within a page, but ordinary Latin drifts the same way, and no table mechanism (fixed, line-held, drifting) fits held-out quires**

roach r9: nearby lines on a page share prefixes and suffixes more than the quire baseline, decaying with line distance (S(1) 1.15-1.23, S(2-4) 1.10-1.19, p=0.005, ZL3b and IT2a); across page breaks it is not significant. A pure drifting table, a line-held table, a per-word table and first-order chains each match 0/15 held-out quires; Latin passes the same drift call 9/15. Drift is a property of the text, not evidence for a table or device.

- **Grade:** CORROBORATED; agreeing axes: data, impl; counted strictly (each run once): 1 axis/axes (data)
- **Novelty:** extends. Prior work: Timm 2014 and Timm 2016 (similar words in nearby and same-position lines); tavie, voynich.ninja thread 4343 (vertical line effects). What this adds: Affix mixtures drift within a page, but ordinary Latin drifts the same way, so drift is not evidence for a table.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Claims:** c-448 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - impl: roach r9 independent code, blind, LOQO, exact p from 200 quire shuffles (agrees) — `runs/roach-r9/results_r9.txt`
  - data: ZL3b and IT2a (agrees) — `runs/roach-r9/results_r9.txt`

### F-49

**Period medical tables avoid in-line repetition like prose; only a Lullian combinatory table repeats cells within a line**

s107: the Tacuinum sanitatis entries (BnF lat. 9333) and Constantinus's De gradibus give R_within(1) 0.03-0.64 (p=1.0) under three segmenters. Llull's 1515 Tabula generalis (957 OCR tokens, 4-letter cells) gives 1.66-6.50 (p=0.001) with cross-line avoidance, by repeating identical cells across printed columns. No text matches the full signature; the battery could not be scored (division by zero on short texts).

- **Grade:** SINGLE; agreeing axes: data; counted strictly (each run once): 1 axis/axes (data)
- **Novelty:** extends. Prior work: Rozanova & Temerev 2026 (Species Plantarum catalogue near-repeats 2.57x); Stolfi 2026, voynich.ninja (asks for non-European herbal controls). What this adds: Period medical tables (Tacuinum, De gradibus) and Llull's Tabula generalis as in-line reuse controls.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Claims:** c-451, c-610, c-613 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: s107 three tabular texts, three segmenters, s97 gate reproduced (agrees) — `results_s107.txt`
  - data: Daybreak db-S138: of the external controls only the Llull 1515 table reproduces the echo-direction signature (1 adequate control family; CREMMA and gibberish inadequate, <100 echoes); roach-12B rerun bit-identical and Llull reimplementation exact (c-617) (agrees) — `lab/codex_lab/results/db_s138_echo_direction_controls.json`
  - data: Daybreak R14 Barcelona BC Ms 3075 physical combinatory table (217 rows): within-row identity 0.1415 vs null 0.1045 (p 0.0001), across-row 0/196, LOIO 6/6; a second table with in-row reuse and row reset. Scorer not independently rerun (roach-12B checked the transcription input only, c-620) (agrees) — `lab/codex_lab/experiments/r14_bc3075_real_20261019/r14_bc3075_real_result.json`

### F-50

**Affix and word-length choices drift by quire beyond hand and section; constancy of the core mechanism is not shown**

s114: a whole-book omnibus over 43 folio features, with quire shuffled within hand x section cells, gives p 0.0001 on ZL3b, RF1b and IT2a, led in all three by sfx:al, pfx:ch, pfx:che, sfx:o, sfx:ol and h1. In-line core reuse and line rhythm are not shown constant across quires (MDE 0.7-0.8 SD; p 0.045 ZL3b, ~0.07 RF1b/IT2a).

- **Grade:** CONTESTED; agreeing axes: data; counted strictly (each run once): 1 axis/axes (data)
- **Novelty:** extends. Prior work: Currier 1976 (A/B); Davis 2020 (scribes); Timm 2026, The challenge of analyzing a dynamic text (gradual change); Kinnison 2026, ED-defined folio regimes; Gonzalez 2026, gradient model of A/B. What this adds: A whole-book omnibus with quire shuffled inside hand x section cells shows quire drift beyond hand and section.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Claims:** c-558, c-591 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: s114 whole-book omnibus, three transliterations (lead run; same tree) (agrees) — `results_s114_20261018_195048.txt`
  - impl: roach r15b blind replication (own code): CALL NO DRIFT by frozen rule; ZL p 0.0009, IT p 0.0006 hit, RF1b p 0.054 misses 0.05 (disagrees (unresolved)) — `runs/roach-r15/results_r15b.txt`

### F-51

**The two leaves of one sheet (bifolio) are more alike in word-form features than matched same-quire pages; this does not show why (batch, shared exemplar or subject). Prior work not yet read - Dominik 2026, VL00805 (agrees in direction with Layfield & Davis 2026, whose only significant contrast is conjoint vs facing pages, uncontrolled)**

s120: conjugate pages (the two leaves of one sheet, often far apart in bound order) are closer in 43 folio word-form features than same-quire pages at the same bound distance in the same hand x section cell (p 0.0001 on ZL3b, RF1b, IT2a; 35 sheets). It survives removing layout features (p 0.0001). Positional drift alone predicts no difference.

- **Grade:** CORROBORATED; agreeing axes: data, method; counted strictly (each run once): 2 axis/axes (data, method)
- **Novelty:** extends. Prior work: Layfield & Davis 2026, The Application of LSA to the Voynich Manuscript, DHQ (conjoint 0.433 vs facing 0.298); Layfield & Davis 2026, Singulion Structure, Digital Medievalist 19; Timm 2026, lingbuzz 010143 (accepts within-bifolium similarity); Dominik 2026, Recovering Voynich Manuscript Bifolium Conjugacy from Textual Similarity (Zenodo; catalogue says not yet used). What this adds: Compares conjugate leaves with same-quire pages at matched bound distance inside hand x section cells, on three transliterations, with layout features removed.
- **Rests on:** X-01 (SlotSegmenter's prefix/core/suffix are the right units: at-risk) — weighted half while at risk
- **Lines not counted:** 1 of 4 (POST-HOC or unverified; they count again only after the named replication)
- **Claims:** c-560 (`.inventory/registers/CLAIMS.md`)
- **Evidence lines:**
  - data: s120 three transliterations, cell-matched strata (lead run; same tree) (agrees) — `results_s120_20261018_211618.txt`
  - method: descriptive sensitivity without page-layout features (agrees) — `runs/s120/sens_20261018_211725.txt`
  - external: Layfield & Davis 2026 (LSA, Tables 10-13 via WebFetch): conjoint 0.433 > facing 0.298 (p 0.000) but conjoint vs same-leaf p 0.168 and Table 13 p 0.283/0.148, no hand or section control; central-conjoint effect in 3/9 quires. Direction agrees only; audit-table5.md (agrees; not counted) — `.inventory/registers/LEARNINGS.md`
  - data: Table 5 conjoints (audit-table5): identical T; dropping f115r (two scribes per Davis) T -0.151/-0.152/-0.160, p 0.0001 x3 (agrees) — `.inventory/runs/2026-10-18/audit-table5.md`
