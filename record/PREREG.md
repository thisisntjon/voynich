# PREREG v1 — joint family-discrimination benchmark (FROZEN)

Frozen: 2026-10-17 (stamp in git/hg status + SHA256 in `scoreboard/PREREG.sha256`).
Any threshold change after an entrant is scored requires PREREG v2 and
re-scoring every entrant. Scorer: `scoreboard/score.py` v1
(`scoreboard/scoreboard.json`, reproduction_pass=true vs a1/a2/c3 filed values).
Conventions: ZL EVA paragraphs via corpora.voynich_lines(); profile N=25,000;
controls as 9-word pseudo-lines, 33k tokens (note: differs from a2 verse lines);
seed 20261017 everywhere unless an entrant documents otherwise.

## Entrants (v1 baseline already scored)

voynich_eva (target) · null_token_shuffled · ctrl_latin_caesar ·
ctrl_italian_dante. To add: C2 best filed config, C2+edge (below),
D3 verbose output, Naibbe sampler (C4 protocol), b4 SIMcal.
Entrants must supply (words, lines) in Voynich page/line skeleton where
applicable; generators disclose every tuned parameter + config count.

## Joint-pass thresholds (ALL must hold; derived from filed gaps)

| Metric (score.py key) | Voynich | Pass band | Filed failures it excludes |
|---|---|---|---|
| h2 | 2.126 | 1.98–2.28 | plain Latin 3.30; C2 sims 1.75–1.82 |
| sd_len | 1.76 | 1.41–2.11 | D3 verbose 4.08 |
| jsd_first_fg | 0.1759 | ≥ 0.10 | all sims/ciphers ≤ 0.04; nulls ≤ 0.002 |
| p_init_enrich | ×17.89 | ≥ ×8 | position-blind anything (≈×1) |
| m_final_enrich | ×16.31 | ≥ ×8 | same |
| cross_excess_eva | +0.1809 | ≥ +0.09 | generators/Naibbe ≤ +0.002 (Dante +0.145 passes alone — joint still discriminates) |
| redup_pct | 0.896% | 0.4–1.8% | b4 sims 2.2–6.0%; plain Latin 0.0% |

Secondary (report, no gate in v1): zipf, hapax_rate, jsd_last_lg,
cross_mi_glyph/excess, recur_le_{1,5,20,100} (v1 definition in score.py;
D5 filed values used a different denominator — do not mix).

## Family kill / favour criteria

- **Generation (null family):** favoured Tier-2 if one documented config
  (≤20 tried configs, all logged) joint-passes. Killed *as complete
  explanation* if best edge-augmented run still has cross_excess < +0.05
  or jsd_first_fg < 0.05. Partial passes retire nothing.
- **Verbose cipher:** position-blind variants already killed (D3, C4).
  Surviving variants must declare positional machinery; its free parameters
  count against it in reporting (params vs constraints hit table mandatory).
- **Language/slot:** any new segmentation/model must beat word-unigram
  held-out bits/token (D2: 10.728) on page-split test, else retired.
  Decipherment claims additionally need PLAN §0 blind-key standard.

## Edge-table augmentation spec (for C2 owner; do not edit c2 from this session)

Estimate P(first glyph | previous word's last glyph), EVA level, on TRAIN
pages only: page-level 80/20 split, seed 20261017, same split for all
entrants. During generation on held-out page skeletons, bias/copy-select
candidates by this table; report (a) table size (contexts × outcomes with
count ≥5), (b) whether table applies at draw time or post-hoc, (c) score.py
row on held-out skeleton vs full-skeleton. Fitting the table on test pages
invalidates the run. E2 ablation (n 41.8%, r 28.2%, y 19.1% of MI) is the
sanity target for which contexts matter.

## Known v1 limits

No topic/NMI metric (B5 Augustine contamination; v2 must add C1 quire null).
No held-out generator scoring yet (v1 descriptive on full skeleton).
Single transliteration (ZL). Folio order = current binding, not author order.
