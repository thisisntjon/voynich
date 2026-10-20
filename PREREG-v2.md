# PREREG v2 — joint family-discrimination benchmark (FROZEN)

Status: frozen at the line in §10; SHA-256 of this file, of `scoreboard/run_v2.py` and of
`tools/gibberish_to_meta.py` are in `scoreboard/PREREG-v2.sha256`. After the freeze this file
is not edited; a change is a PREREG v3 plus a re-score of every entrant. Nothing in this file
alters `scoreboard/score.py` (frozen v1 scorer, sha256 3a7b7c3e…), `PREREG.md` (v1) or any
results file.

## 1. Scope and what it supersedes

v2 is the instrument on which every family claim (L, C, G, X) and every entrant is judged
from the freeze on. It supersedes:

- `PREREG-v2-DRAFT.md` (16:13–18:24 drafts, never frozen): its M1–M19 table and in/out rule
  are replaced by §4 and §7 below; metrics that did not survive the n2/n3 audit are kept for
  reporting only (§4).
- the *decision* part of `PREREG.md` (v1): the family kill/favour criteria and the
  language/slot bar. The seven v1 bands themselves are carried over unchanged (§3); v1 stays
  the record of what the bands are and where they came from.
- the draft rule as implemented in `m4_phase1_board.py` (results_m4): same in/out arithmetic,
  now with the X family, the A/B verdict rule (§6) and the weight rules of §4.

Not in scope: decipherment claims (PLAN §0 blind-key standard still applies); labels
(scored separately, results_m6; Lindemann & Bowern register point); any band derived from a
new reading order of the folios.

## 2. Board transliteration

ONE board transliteration: **ZL3b EVA paragraph text** (`data/ZL3b-n.txt`, P* units via
`vparse.paragraph_text`, tokens containing `?` dropped: 207 pages, 4,130 lines, 34,857
tokens). Profile metrics are computed on the first 25,000 tokens inside `score.py`, as filed.

Mandatory robustness check for every verdict: re-score the manuscript on **RF1b** and
**IT2a** exactly as `m7_board_translit.py` does (same scorer, same bands, 25k sample) and
report the three rows side by side. A band or metric whose in/out verdict flips between ZL3b,
RF1b and IT2a is downweighted to zero for that verdict (draft robustness rule 1, kept).
results_m7 plain-EVA spread: h2 2.126–2.135, sd_len 1.691–1.777, JSDf 0.1748–0.1809,
p ×17.55–×19.4, m ×16.31–×16.51, excess +0.166–+0.181, redup 0.88–0.932 %: all seven hold on
all three EVA files.

**h2 and sd_len bands are alphabet-specific.** They are set at EVA character level. A
transliteration or collapse that writes multi-letter EVA glyphs as one symbol (ZL3b glyph+:
h2 2.397, sd_len 1.435; GC2a/v101: h2 2.540, sd_len 1.454; results_m7) is *not* on the band's
scale and is never used to pass or fail those two bands. Entrants are scored in EVA; a
producer that emits another alphabet must be mapped to EVA before scoring, and that map is
part of its disclosed parameters.

## 3. The seven v1 bands (unchanged) and the audit corrections

Scorer: `scoreboard/score.py` v1 loaded by path and called as `score_corpus(name, words,
lines)` with the g0 band checks copied verbatim (`g0_score_filed.py`, `m4_phase1_board.py`,
`scoreboard/run_v2.py:bands`). Conventions: seed 20261017; non-Voynich corpora cut to their
first 25,000 tokens (whole lines) before scoring; flat controls wrapped 8 tokens/line, 20
lines/page (m4 convention; v1's 9-word pseudo-lines are the v1 filed values' convention and
are not re-used).

| Band (score.py key) | Voynich ZL3b | Pass band |
|---|---|---|
| h2 | 2.126 | 1.98 ≤ h2 ≤ 2.28 |
| sd_len | 1.76 | 1.41 ≤ sd ≤ 2.11 |
| jsd_first_fg | 0.1759 | ≥ 0.10 |
| p_init_enrich | ×17.89 | ≥ ×8 |
| m_final_enrich | ×16.31 | ≥ ×8 |
| cross_excess_eva | +0.1809 | ≥ +0.09 |
| redup_pct | 0.896 % | 0.4 ≤ redup ≤ 1.8 % |

Joint pass = all seven. Known and accepted: Currier A alone fails `m_final_enrich` (×6.21,
results_m4; run_v2 on A gives ×6.21 again), which is why §6 makes A-only / B-only verdicts
explicit instead of hiding them.

Audit corrections (docs/AUDIT-2026-10-17.md §2, items 11–14), stated here so no later reader
takes the v1 wording as current:

1. **Bake-off retirement bar.** Any slot/lexicon model must beat word-unigram held-out
   bits/token on the **d2 page split** (seed 20261017, 80/20) with a **properly normalised
   comparator**: the bar is **11.15 bits/token** (char-3 Witten–Bell 11.151 on the page
   split; renormalised unigram-GT 11.245; results_m3), **not 10.728**. The 10.728 figure is
   d2's flat-UNK unigram, which is not a distribution over strings (results_m3). A model that
   beats only 10.728 is not retired-proof and is reported as "below the flat-UNK number".
2. **Prose cross-space coupling.** L predicts `cross_excess_eva` in **0.04–0.15** (Caesar
   +0.037, Dante +0.145, Alice +0.106, prose controls +0.036 to +0.145; results_c3,
   audit item 11), **not ≈0**.
   The draft's "≈0 for prose" (M13) is withdrawn.
3. **Hapax share** (`x_hapax_10k`, `hapax_rate`) **is reported and carries no weight**:
   Caesar 0.652, Dante 0.677, Voynich 0.686 at 10k tokens (results_m0); the published 40–60 %
   does not hold at matched size.
4. **M6 premise-refuter is relative, not absolute.** The plan's premise (sequence carries
   little information) is refuted only if Voynich's adjacent-word MI after BPE re-segmentation
   exceeds the **bigram-pseudo-Voynich null (0.851 bits, results_m0 `[bpe_resegmented]`)**
   by at least the margin that separates the language controls from that null
   (Caesar 0.945, Dante 0.897 → margin 0.05–0.09). Voynich's 1.176 exceeds the null by
   0.325, i.e. more than the L controls do; this is **within-word structure** (BPE merges
   re-create the glyph slots), so it does not fire the refuter and is not evidence for L on
   its own. No absolute threshold (the draft's 0.6) is used.

## 4. Extra metrics that survive from the draft

Scored by `scoreboard/metrics_new.py` through `run_v2.py`, same keys as results_m4 so the
family ranges in `results_m4_phase1_board.json` apply.

Weighted (subject to the overlap rule of §7):

| key | metric | note |
|---|---|---|
| x_edge_mi_word | edge MI, last glyph → next word's first glyph, shuffle-corrected | Voynich 0.188 (all), 0.127 (A), 0.240 (B) |
| types_25k | word types in the first 25,000 tokens | **scored jointly with x_edge_mi_word** (draft M19): a producer that reaches the edge range only by leaving the type range fails both; Voynich 7,025 types at 34.9k, ~5.4k at 25k |
| x_position_entropy | within-word glyph position entropy (bits, max 2.32) | Gaskell–Bowern's separating metric |
| x_ltr_minus_rtl | held-out bits/char, ltr minus rtl, order-3 char model | Parisel asymmetry |
| x_moran_I, lex_*, slot_*, info_mi_adjacent, info_samecol_minus_othercol, bake_char3_minus_unigram | as in m4 | currently no weight because L/C/G ranges overlap (results_m4 §4); they regain weight only if a re-derived ranges file separates them |

**No content weight** (reported in every row, never counted):

- **held-out word-order residual (F1)**: results_n2 shows a 4 % word-pair habit generator
  reproduces the manuscript's residual on ZL3b, RF1b and IT2a (OVERALL: DIES);
- **page-level MI** (`info_mi_page`): results_n3 shows the same generator reproduces it
  (pageMI FALLS on ZL3b and RF1b, NOT EVIDENCE on IT2a);
- hapax share (§3 item 3); `info_bpe_adjacent` (M6 premise check only, §3 item 4).

**Hand-1 within-hand NMI vs section** (b5 chunks, NMF random_state 0) is reported with
*both* the quire-block null (c1: hand 1 p = 0.018) and the bifolio null (§5). It counts as a
content signal only if it clears both (p < 0.05 on each) **and** exceeds the n2 habit
generator at p = 0.04 (seed-mean, three seeds; results_n3 threshold rule). On results_n3 it
clears the quire-block null and beats the generator on ZL3b and IT2a but not RF1b, so it is
currently *transliteration-fragile* and carries no weight until the bifolio null is run and
the RF1b failure is explained. Hand-2 NMI fails its own null (p 0.133) and is not evidence.

## 5. Nulls required for every page-contiguous label

Any statistic that uses a page-contiguous label (section, hand, quire, Currier language,
bifolio) must report all four nulls, and a signal that dies under any of them is reported as
"physical-neighbourhood similarity", not content:

1. **permutation** — labels permuted among pages (b5 `perm-null`, 2,000 draws, seed
   20261017);
2. **rotation** — the page-label sequence rotated by every offset, fake sections stay
   contiguous (b5 `rotation-null`; p = share of offsets ≥ observed);
3. **quire-block** — unit = a contiguous run of one section inside one quire; section labels
   reassigned among blocks, exact enumeration (c1 `block_test`; hand 1 has 11 blocks);
4. **bifolio** — unit = the bifolio `($Q, $B)` of the current binding as `p1_bifolio_null.py`
   Part B defines it (IVTFF `$Q` quire and `$B` bifolio variables; both folios of a sheet are
   one unit); labels are permuted among bifolio units, 2,000 draws, seed 20261017; NMI and
   centroid gap use c1's `block_test` definitions. Decision as in p1 Part B: SURVIVES if NMI
   p < 0.05 and centroid p < 0.05; NMI-ONLY if only NMI; DIES otherwise. Sheet cohesion
   (same-bifolio minus different-bifolio TF-IDF cosine, within-section bifolio-label
   shuffles) is reported alongside as NEIGHBOURHOOD / NO_SHEET_EFFECT.
   `results_p1.txt` on disk is the output of `p1_order_sensitivity.py`, not of the bifolio
   script; the bifolio null has **not** been run at the freeze.

## 6. A/B verdict rule

Every entrant and the manuscript are scored three times: **all-paragraph text**, **Currier A
pages only**, **Currier B pages only** (page field `lang` in the sidecar; IVTFF `$L` for the
manuscript: 11,231 A tokens, 23,078 B tokens). A verdict (kill, favoured, joint pass, in/out
count) **holds only if it holds on all three**; otherwise it is stated as **A-only** or
**B-only** and never as a verdict on the manuscript. An entrant that models only one language
must say so and is judged on that subset plus "all"; it cannot be favoured overall.

## 7. Families, control sets and the in/out rule

| family | control set (sidecar or loader) |
|---|---|
| **L** natural language, 21 corpora | `corpora.CONTROLS` (latin_caesar, latin_augustine, italian_dante, german_faust, german_kafka, english_alice) + `corpora_ext.NATURAL` (hebrew_torah, arabic_quran, greek_herodotus, czech_bible_kralicka_1613, occitan_croisade_albigeoise, oldfrench_roland, mhg_nibelungenlied, mhg_parzival, catalan_tirant, turkish_kanun_medeni_1926, latin_macer_floridus, latin_pliny_herbal, hawaiian_fornander, tagalog_urbana_feliza_1864, tagalog_florante_1838), wrapped 8 × 20 |
| **C** codebook / nomenclator | `data/controls_synthetic/nomen_*.meta.json` (nomen_word, nomen_syll, nomen_lines, nomen_numeric, nomen_numeric_lines, nomen_numeric_sylls, and the k4 shared-codeword lossy nomenclators nomen_k2_x2, nomen_k2_x8 and any further `nomen_k*`) |
| **G** generators | markov1, rugg_grille, timm_schinner, timm_schinner_ownlines, schwartz_reuse, c2_best, and the n2 habit generator at p = 0.04 (`n2hab_*` sidecars, three seeds) |
| **X** human gibberish (new) | the 38 Gaskell–Bowern volunteer texts, converted by `tools/gibberish_to_meta.py` into `data/controls_gibberish/gib_<writer>.meta.json` (writer id as `hand`, section `gib`, 8 tokens/line, 20 lines/page, lowercase a–z only, hyphenation at source line ends joined, `_` page rules dropped) plus `gib_pooled.meta.json` (all writers in file order, one page block per writer) |

Gibberish sizes, from the converter run at the freeze (`python -I tools/gibberish_to_meta.py`):
38 writers, **10,023 tokens in total**, per writer 79 (DC_24) to 480 (DC_15); the pooled
corpus has 10,023 tokens. Because of this the X ranges are built in two parts:
per-writer min/max over the 38 files for the metrics `score.py` defines at that size (h2,
sd_len, jsd_first_fg, p/m enrichment, cross_excess_eva, redup_pct, x_position_entropy) and
the pooled corpus for every sample-size-dependent extra (`extra_signatures` fold split,
bake-off, lexicon growth, types_25k are undefined on a 3-page file). X values are therefore
at 10k tokens, not 25k, and any X in/out on h2/types is flagged "size-mismatched" in the
report. The X ranges are written into a ranges JSON with top-level `"x_family": "gibberish"`;
`run_v2.py` prints X as NA unless that flag is present, because the "X" rows of
results_m4 mean "other, no family" (§8).

In/out rule (draft, kept; implemented in `m4_phase1_board.py` and `run_v2.py`): for family F
and metric k, Voynich is **in** if it lies in [min − 0.1 w, max + 0.1 w] of F's controls,
w = max − min, else **out**. A metric whose **L, C, G and X ranges all overlap** (non-empty
intersection of the four) carries no weight; with the current four families the overlap test
is over all four, not the draft's three. "Tight" = range width < half the spread over all
corpora. **Kill**: ≥ 3 weighted outs on tight ranges, and no single documented parameter
change in that family's control brings them in without pushing another out. **Favoured**:
strictly fewer weighted outs than every rival by ≥ 2. Otherwise undecided. Both verdicts
need §6 (all three text subsets) and §2 (three EVA files).

Metrics undefined for a control (abjad controls carry no p/m glyphs → `inf`; small files →
`nan`) are NA, not out, and the per-family NA count is printed next to the out count (REDTEAM
row 20). A control built from the manuscript (timm_schinner seeded with a Voynich line,
markov1 fitted on Voynich glyphs, schwartz_reuse, c2_best) is named as such in every range
line; the G family's "in" on h2/redup/position entropy is partly by construction (REDTEAM
row 6) and that caveat travels with every G verdict.

## 8. Sidecar format and family assignment

Sidecar `.meta.json` (as `scoreboard/corpus.py:from_meta_json` and `m4:load_meta` read it):

```
{"name": "<corpus name>", "tokenization": "eva", "source": "<free text, every tuned parameter>",
 "pages": [{"id": "f1r", "section": "H", "hand": "1", "lang": "A", "quire": "A",
            "lines": [["tok", "tok", ...], ...]}, ...]}
```

`id` and `lines` are required; `section`, `hand`, `lang`, `quire` default to `?`; a page key
`page` is accepted for `id`; extra keys are kept. `lang` must be `A` or `B` for the §6 subsets
to exist; a sidecar without `lang` can only be scored on "all" and cannot carry a verdict.

Family by filename prefix (`run_v2.py:family_of`; `--family` overrides and the override is
printed): `nomen_` → C; `markov1`, `rugg`, `timm`, `schwartz`, `c2`, `n2hab` → G;
`gib_` → X; anything else is reported without a family (results_m4 called this "X = other";
v2 prints `-`).

## 9. Pre-registration of entrants

Before an entrant is scored, a stub is frozen: `<script>.prereg.sha256` holding the SHA-256
of the script whose docstring states (a) the metric(s), (b) the threshold or the family-range
test, (c) what counts as kill/survive, exactly as `n1_habit_table.prereg.sha256`,
`n2_habit_fine.prereg.sha256` and `n3_content_signals.prereg.sha256` did. The results file
must print that hash and the ranges-file name on its first lines. A run whose script hash
does not match its stub is reported, not scored. Entrants disclose every tuned parameter and
the number of configurations tried (≤ 20, all logged; v1 rule kept).

Commands a session uses (project root, system Python 3.11):

```
python -m scoreboard.run_v2 --meta <sidecar.meta.json>          --ranges results_m4_phase1_board.json --out results_<prefix>.txt
python -m scoreboard.run_v2 --meta <sidecar.meta.json> --lang A --ranges results_m4_phase1_board.json --out results_<prefix>_A.txt
python -m scoreboard.run_v2 --meta <sidecar.meta.json> --lang B --ranges results_m4_phase1_board.json --out results_<prefix>_B.txt
python -m scoreboard.run_v2 --voynich [--lang A|B]              --ranges results_m4_phase1_board.json --out results_<prefix>_voy[_A|_B].txt
```

## 10. Freeze

Frozen 2026-10-17 19:27 PDT (system clock, `date`), session b3796192, Windows system Python 3.11.9 with
numpy/scipy/sklearn. Hashes in `scoreboard/PREREG-v2.sha256` (`sha256sum` format, no BOM).
Tests run before the freeze: `run_v2 --meta data/controls_synthetic/nomen_k2_x2.meta.json --ranges
results_m4_phase1_board.json` and `run_v2 --voynich --lang A --ranges results_m4_phase1_board.json`
(both complete; Voynich A: v1 joint FAIL on m_final_enrich ×6.21, matching results_m4), plus
`run_v2 --meta data/controls_gibberish/gib_pooled.meta.json` (h2 3.962, sd_len 2.703, JSDf 0.005,
redup 0.50 %, position entropy 2.243, edge MI 0.028, Moran I +0.119 at 10,023 tokens; descriptive,
not a band).
