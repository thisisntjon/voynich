# Phase 1 instrument check — run_v2 sidecar path, ranges format, s15 reuse, real-line corpora, n7, sharing

Stamped 2026-10-17 20:00 PDT (clock read with `date`). Read-only investigation for `workflow/PLAN.md`
Phase 1 (s15, s17, s18, s19). No experiment run, nothing edited, nothing downloaded; the only commands run
were `python -I` one-liners that count lines/tokens in files already on disk and `run_v2.py --help`.
"Unverified" marks what was not checked.

## 1. How `run_v2.py --meta` loads a sidecar, and whether line breaks survive

- Loader: `scoreboard/run_v2.py:95-105` `load_meta` (its own copy of m4's loader), **not**
  `metrics_new.meta_json_pages` (`scoreboard/metrics_new.py:75-82`, which requires `id`). Dialect: page key
  `id`, falling back to `page`, falling back to the page index (`run_v2.py:100`); `section/hand/lang` default
  `"?"`, `quire` default `None`. Lines are copied verbatim as token lists, empty lines dropped (`:104`), pages
  with no lines dropped (`:105`). Nothing in run_v2 wraps or re-lines: the only wrappers in the pipeline are
  the sidecar builders (`tools/gibberish_to_meta.py:72-78`, 8×20) and m4's `natural_from_ext`
  (`m4_phase1_board.py:129-136`, 8×20 via `wrap_labelled`), neither of which run_v2 calls.
- Token cap: `subsample` (`run_v2.py:108-121`) keeps whole lines until 25,000 tokens (`--n-sample`); the last
  line is never split. `--lang` keeps pages whose sidecar `lang` equals the letter (`:135-139`), so a sidecar
  with `lang="?"` must be run without `--lang`.
- Where lines reach the metrics (`score_one`, `run_v2.py:153-217`): `lines = [ln for p in pages ...]` (`:155`)
  → `score.score_corpus(name, words, lines)` (`:169`) → `jsd_first_fg`, `jsd_last_lg`, `p_init_enrich`,
  `m_final_enrich` from `score.py:57-78` (lines with ≥3 words; first/last vs mid) and `cross_excess_eva` from
  `score.py:88-106` (within-line adjacent pairs; null = within-line shuffle, nrep 20, `Random(0)`).
  `x_edge_mi_word` = `metrics_new.extra_signatures` within-line pairs (`metrics_new.py:797-800`).
  `x_position_entropy` never looks at lines (`:836-845`). **Moran I** (`x_moran_I`) is computed on the token
  sequence with lines concatenated (`:818-821`), so a line break changes it only through token order; the
  within-line variant exists (`:823-829`) but run_v2 does not export it (`:181`). `info_samecol_minus_othercol`
  uses previous-line columns (`:409-437`); the bake-off's copy model uses the previous line (`:691-693`).
- **CHARWIN is not a run_v2 key.** The nearest is `bake_char3_minus_unigram` = markov3 − unigram_gt bits/token
  (`run_v2.py:208`), which is n5's CHARWIN with the sign flipped and a different estimator (n5: "unigram-GT-renorm
  − char3-WB, page split", `n5_signature_discrimination.py:8,122`); Voynich reads −0.526 in run_v2
  (`results_n7.txt:172`) vs +0.094 in n5. The PLAN's "CHARWIN on v2" must either name
  `bake_char3_minus_unigram` or call n5's function; it cannot cite both as one number.
- `jsd_last_lg` is computed (`score.py:74`) and kept only inside `row["v1_full"]` (`run_v2.py:175`), i.e. in the
  `<out>.json`, not in the printed table. s17's secondary statistic must be read from the JSON.
- Launch: `python -I -m scoreboard.run_v2` **fails** under `-I` (`No module named 'scoreboard'`, verified
  20:00); `python -I scoreboard/run_v2.py ...` works (`run_v2.py:37-40` inserts ROOT). PREREG-v2's docstring
  (`run_v2.py:3`) shows the `-m` form; the stub should use the file form.
- Verdict: a sidecar's line breaks survive unchanged to every edge metric. Proof command (no metrics run):
  ```
  python -I -c "import sys,json; sys.path.insert(0,'.'); from scoreboard import run_v2 as R; p='data/controls_realline/X.meta.json'; _,pg=R.load_meta(p); pg=R.subsample(pg,25000); a=[len(l) for q in pg for l in q['lines']]; d=json.load(open(p,encoding='utf-8')); b=[len(l) for q in d['pages'] for l in q['lines'] if l][:len(a)]; print('lines kept:',a==b,len(a),'tokens',sum(a))"
  ```
  plus the run header `# pages=.. lines=.. tokens=..` (`run_v2.py:293`) and `row["lines"]` in the JSON must
  equal the sidecar's non-empty line count (or the subsampled prefix). A re-wrap would show as a line-length
  histogram collapsing to one value (as `gib_pooled` does: 1,235 of 1,268 lines are exactly 8 tokens).

## 2. The `--ranges` file format

- Read at `run_v2.py:303-319`: `R["ranges"]` (required), `R.get("tight",{})`, `R.get("no_weight",[])`,
  `R.get("x_family")`, `R.get("rows")` (only to derive `types_25k` when missing), `R.get("run")`,
  `R.get("extend")` (printed only; the code uses the constant `EXTEND=0.10`, `:51,227`).
- `ranges[metric][family] = {"min","max",…}`; only `min`/`max` are used (`in_out`, `:223-227`); `n`, `members`,
  `source` are carried but ignored. Families are hard-coded `["L","C","G"]` plus `"X"` only when
  `x_family == "gibberish"` **and** some metric has an `X` entry (`:308-309`). Any other key under a metric
  (e.g. `"V41"`) is silently ignored, so family ranges and within-manuscript widths cannot share the family slot.
- `tight[metric][family]` is a file-supplied boolean (m4 rule: width < 0.5 × spread over all corpora,
  `m4_phase1_board.py:439,452`); `no_weight` is a flat list. Both drive the kill/favoured lines (`:350-363`).
- Both files on disk conform: `results_m4_phase1_board.json` (keys run, seed, n_sample, n_shuffles, extend,
  columns, rows[43], ranges[23 metrics], tight, verdict, no_weight[14], weighted, summary, missing, errors) and
  `n7_gibberish_ranges.json` (same plus `x_family: "gibberish"`, `n7: {built, from_file, x_source, note}`,
  `types_25k` and `info_bpe_adjacent` added, `no_weight` down to 7). n6 wrote two more in the same shape
  (`results_n6_ranges_A11k.json`, `results_n6_ranges_B23k.json`, `n6_ab_split.py:32-33,190-197`).
- What a results_s15 ranges file needs to be accepted by s18: a `ranges` dict with `L/C/G` (and `X` plus
  `x_family`) min/max per metric, copied from `n7_gibberish_ranges.json` (otherwise every family prints NA),
  plus `tight` and `no_weight`. The 41-page widths go in a **sibling top-level key** (e.g.
  `"within_manuscript": {metric: {lo, hi, width, n_splits, nrep, translit_range, p2_range}}`) that run_v2
  ignores; a one-line reader in s18 compares the manuscript's `OUT` margin with that width. Yes, one file can
  carry both; run_v2 will not read the widths, so s18's text must do that comparison itself.
- Naming hazard: `run_v2 --out results_s15.txt` would write `results_s15.json` (`run_v2.py:384`), so a ranges
  file called `results_s15.json` (PLAN Phase 1 wording) collides with the row JSON of any run_v2 call that uses
  that `--out`. n7 used `n7_gibberish_ranges.json`; s15 should use `s15_ranges.json` and keep
  `results_s15.txt` for the table.

## 3. Reusing `workflow/research/C-helpers/floors_v1_bands.py` for s15

- What it does (`floors_v1_bands.py:17-33`): loads `corpora.voynich_lines()` (ZL3b via vparse), groups lines
  by page, and per draw computes `score.profile_metrics(words)` + `score.line_metrics(lines)` +
  `score.edge_metrics(lines, eva, nrep=5)["excess"]` (the seven v1 bands only, EVA only). Draws: page bootstrap
  with replacement to token budgets 2k–35k (`:49-52`), Currier A pages (`:53-54`), and `NB` 41-page subsets
  without replacement, `Random(41)` (`:55-60`). `NB` defaults 60; C-constraints ran 40 (`C-constraints.md:18-21`,
  "each < 40 s", numbers never written to a results file). Summary = 2.5/97.5 percentiles vs band
  (`:34-46`), printed to stdout only.
- Changes needed for s15: (a) replace `metrics()` with `run_v2.score_one(name, pages, log)` on page dicts
  (n7's jackknife already does this, `results_n7.txt:91`), which restores edge-null nrep 20 (score.py default,
  `score.py:88`) and adds every v2 key; (b) use l1's split definition (200 subsets, seeds 1000..1199,
  `l1_heldout_g1_split.py:6-7,171`) rather than `Random(41)`, and keep the g1 held-out split (`Random(20261017)`)
  as split 0; (c) add the m7/p2 translit rows (`data/translit/*.meta.json` via `run_v2 --meta --n-sample
  1000000`, as n7 did, `n7_gibberish_family.py:330`) and p2's printed ranges; (d) write incrementally to
  `results_s15.txt` + `s15_ranges.json`, one split at a time, so a kill leaves a partial table.
- Caveats at 41 pages (~6.8k tokens): `x_hapax_10k` is NaN below 10k tokens (`metrics_new.py:810-814`);
  `types_25k` is just the type count; `lexicon_growth` needs ≥2,000 tokens (`:190`); bake-off folds are
  leave-one-quire-out when every page has a quire (`:647-651`), so some folds hold one page.
- Runtime: `score_one` on full Voynich (34.9k tokens) takes ~27 s (`results_n7_voy_all.txt:7-12`: v1 1.3,
  extra 6.2, info 2.3, lex 6.1, slot 0.3, bake 10.3) and ~9 s on 10k tokens (`results_n7_gib_pooled.txt`).
  At 6.8k tokens ≈ 5–8 s per split → 200 splits ≈ 20–30 min CPU, plus 3 translit rows (~30 s each) and the v1
  part (<2 min). Memory stays that of one corpus (<1 GB, C-constraints §4 table); unlike m4 it holds no
  47-corpus JSON, so it should not repeat the 703 s/OOM kill, but it occupies the single board-scale slot
  (E §2b item 4) for the half hour. Estimate unverified until the first 10 splits are timed.

## 4. Real-line corpora on disk for s17

| Corpus | Path | Tokens | Lines real? |
|---|---|---|---|
| Gaskell–Bowern gibberish, pooled | `data/controls_gibberish/gib_pooled.meta.json` (82 pages, 1,268 lines, 10,023 tokens) | 10,023 | **No**: wrapped 8×20 by `tools/gibberish_to_meta.py:14,72-78`; 1,235/1,268 lines are exactly 8 tokens. The **source** files `data/external/gaskell-bowern-gibberish/danielgaskell-voynich-main/voynich-main/data/gibberish_transcriptions/Gibberish - <WRITER>.txt` (38 files) do carry the volunteers' own lines: 1,617 lines, 1–19 tokens, mode 6–7; `_____` rules mark page breaks and a trailing `-` marks hyphenation. |
| Nibelungenlied Hs. A | `data/controls/mhg_nibelungenlied.txt` | 78,706 (whitespace count; `corpora_ext.tokenize` may differ) | Yes as edited long-lines: 9,300 text lines of 2–14 tokens (mode 8–9), 39 `## N. Aventiure` headers; the m4 path re-wraps them (`natural_from_ext`), the sidecar path keeps them. s2's U1 part already scored them natively: 2,985 lines/25,007 tokens, JSDf 0.0924 vs 0.0020 re-lined (`results_s2_u123_controls.txt:9-10`). |
| Dante, Commedia | `data/controls/italian_dante.txt` (Gutenberg, UTF-8 verified) | 97,793 in 14,543 non-blank body lines | Yes as verse lines (5–9 words, hendecasyllables), not manuscript lines. Loader `scoreboard/corpus.py:155-170` → `a2_position.verse_lines` (`a2_position.py:53-59`: lines ≥3 words, first 5,000). s2 native: 3,000 lines/21,529 tokens, JSDf 0.0324 (`results_s2_u123_controls.txt:15-16`). |

Sidecar in the `id` dialect (the shape `gib_pooled` already uses, one page block):
```
{"name": "mhg_nibelungenlied_realline", "tokenization": "latin", "source": "...", "pages": [
 {"id": "nib_av01_p000", "section": "1. Aventiure", "hand": "HsA", "lang": "?", "quire": "?",
  "para_start": [true, false, ...],
  "lines": [["ns","ist","in","alten","maeren","wnders","vil","geseit"], ["von","helden","lobebaern", ...]]}]}
```
`para_start` is the k5 field (E §2a) and is optional; `quire` must be a real label on every page or `"?"`
(a mix makes `_folds` fall back to 10-page blocks, `metrics_new.py:647-651`). A name without a family prefix
scores as family `-` (`run_v2.py:124-132`); pass `--family L` (or `X` for the gibberish).

## 5. n7's effect on the bands

- Regained weight (`no_weight` m4 → n7, column "noW y->n", `results_n7.txt:107-116`): **x_moran_I, lex_beta,
  lex_rate_late_early, lex_edit1_excess, slot_occupancy_pc, slot_table_likeness, slot_core_crowding,
  bake_char3_minus_unigram** — the eight the peer named (Moran I, three lexicon, three slot, bake-off).
- Every one of those eight has `x_source = "pooled + 38 jackknife"` (`n7_gibberish_ranges.json` → `n7.x_source`):
  an X range of width ≈ one writer's leverage on one 10k-token corpus (e.g. lex_beta 0.9716–1.0538,
  slot_table_likeness 0.8925–0.9010), all flagged `tight` for X. They regained weight only because that sliver
  does not overlap L/C/G; TEAM-HANDOFF.md:29 records that every corpus on the board, all 21 L controls
  included, is OUT of it, and reads the X-vs-L lean as "SIZE-DEPENDENT". These eight plus the other
  pooled-jackknife keys (x_edge_mi_word, x_ltr_minus_rtl, info_mi_adjacent, info_samecol_minus_othercol,
  x_hapax_10k [n=1], info_mi_page, info_bpe_adjacent) are the artefacts that must not set a band.
- The per-writer X ranges (h2, sd_len, jsd_first_fg, p_init_enrich, m_final_enrich, cross_excess_eva,
  redup_pct, x_position_entropy; 38 corpora of 79–480 tokens) are real per-corpus ranges but are (a)
  small-sample inflated (jsd_first 0.0526–0.356; TEAM-HANDOFF:29 "gibberish's high JSD is small-sample
  inflation") and (b) computed on 8×20 pseudo-lines, so the X edge ranges say nothing about real gibberish lines.
  `types_25k` X is NA (`results_n7.txt:104`).

## 6. Sharing hazards

- `run_v2.py` writes only `--out` and `<out>.json` (`run_v2.py:371-388`; docstring `:23`). `scoreboard.json`
  writers are `scoreboard/score.py:28` (`main()` truncates), `scoreboard/run.py:34,131` (read-modify-write),
  `g0_score_filed.py:39` (appends). E §2a's line "run_v2 writes scoreboard.json" described the plan, not the
  file as written.
- Files Phase 1 reads that another session may write: `n7_gibberish_ranges.json` and `results_n7_*` (rebuilt
  by any rerun of `n7_gibberish_family.py`, which also globs `data/controls_gibberish/gib_*.meta.json`,
  `:218`, so a real-line gibberish sidecar dropped there would join a rerun's X family: put it in
  `data/controls_realline/`); `results_m4_phase1_board.json` (m4 rerun); `data/controls_synthetic/*.meta.json`
  (globbed by m4 `:167`, n5 `:204`, n7 `:332`; keep Phase 1 sidecars out of it); `scoreboard/score.py`,
  `metrics_new.py`, `run_v2.py` (hashed in `scoreboard/PREREG-v2.sha256`; any edit breaks every Phase 1
  provenance line, `run_v2.py:367-369`); `data/translit/*.meta.json` (read-only by rule).
- Prefix collision already realised: another session wrote `s1_v2_joint_producers.py` →
  `results_s1_v2_joint.txt` (19:39) and `s2_u1_u2_u3_controls.py` → `results_s2_u123_controls.txt` (19:50),
  later duplicated byte-for-byte as `results_s25_*`/`results_s26_*` (TEAM-HANDOFF.md:55-56). The PLAN's prefix
  table reserves s1/s2 for Phase 3; the s1/s2 files on disk are not those experiments.
- `results_s2_u123_controls.txt` Part 1 is a U1 pre-test on the same two texts s17 names, with v1
  `score.py` functions and 25k caps; it is a prior result, not a Phase 1 output, and was not run on v2.

## Decisions needed before the phase plan

1. s17's gibberish row: build a new real-line sidecar from the 38 source files (`data/controls_realline/
   gib_pooled_realline.meta.json`, page = `_____` block, hyphens joined) — `gib_pooled` is 8×20 and cannot serve.
2. CHARWIN on v2: name `bake_char3_minus_unigram` (sign-flipped, page-fold estimator) as the v2 proxy, or add an
   n5 call for CHARWIN proper; the s17/s18 stubs must say which, since they differ by 0.6 bits on Voynich.
3. s15 output naming: `results_s15.txt` + `s15_ranges.json` (ranges + `within_manuscript` sibling key, L/C/G/X
   copied from n7), replacing the PLAN's `results_s15.json`, which collides with run_v2's row JSON.
4. Band weights for s18: carry n7's `no_weight` as is (eight metrics weighted on a pooled-jackknife X range), or
   restore m4's list for the X family until a per-corpus X range exists; the s18 verdict line depends on it.
5. s17 vs the existing s2/s26 U1 part: cite it as prior and re-score both texts through `run_v2 --meta` (v2 keys,
   jsd_last from the JSON, no 5% skip), or accept its v1 numbers and spend s17 only on the gibberish and -am rows.
6. Runtime/launch rules for the stubs: `python -I scoreboard/run_v2.py` (not `-m`); s15 takes the single
   board-scale slot for ~30 min; `--family L` on every real-line sidecar; `--lang` only where the sidecar sets it.
