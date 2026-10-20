# PREREG v2 freeze note

Written 2026-10-17 19:27 PDT (system clock), session <session>.

## What was done

- Wrote `PREREG-v2.md` (frozen; sha256 f8c42d76…) in the ten-section order asked for: scope,
  one board transliteration (ZL3b EVA, m7-style RF1b/IT2a re-score mandatory, h2/sd_len
  alphabet-specific), the seven v1 bands unchanged plus the four audit corrections (bar 11.15
  not 10.728; prose coupling 0.04–0.15; hapax no weight; M6 refuter relative to the 0.851
  bigram null), surviving extras with F1 residual and page MI at zero weight and hand-1 NMI
  gated on quire-block + bifolio nulls, the four nulls, the A/B verdict rule, families
  L/C/G/X with the in/out rule, the sidecar spec and prefix rule, the entrant stub rule,
  and the freeze line.
- Wrote `tools/gibberish_to_meta.py` and ran it with `python -I` from the project root:
  38 Gaskell–Bowern writer files -> `data/controls_gibberish/gib_<writer>.meta.json` plus
  `gib_pooled.meta.json`. Total 10,023 tokens; per writer 79 (DC_24) to 480 (DC_15).
- Wrote `scoreboard/run_v2.py` (CLI in PREREG-v2 §9). Tested on
  `data/controls_synthetic/nomen_k2_x2.meta.json` with `--ranges results_m4_phase1_board.json`
  and on `--voynich --lang A`; both run end to end. Also ran it on `gib_pooled` and on one
  single-writer file (`gib_DC_15`): the single file is too short for
  `metrics_new.extra_signatures` and the bake-off (fold split), which is why §7 builds the
  X ranges from per-writer v1 bands plus the pooled corpus for the extras.
- Wrote `scoreboard/PREREG-v2.sha256` (no BOM, LF) hashing PREREG-v2.md, run_v2.py and
  gibberish_to_meta.py; `sha256sum -c` passes.

## Changes against the draft, made to keep v2 consistent with the results files

1. M13 "L predicts ≈0" replaced by 0.04–0.15 (audit item 11).
2. M6 absolute 0.6-bit trigger replaced by the margin over the 0.851 bigram null (audit 12).
3. M14 hapax 40–60 % dropped; hapax reported, no weight (audit 13).
4. v1 language/slot bar 10.728 replaced by 11.15 on the d2 page split with a normalised
   comparator (results_m3, audit 14).
5. M6/M7 (adjacent and page MI) and the F1 residual: no content weight (results_n2, n3).
6. M8 within-hand NMI: counts only if it clears quire-block AND bifolio nulls and beats the
   n2 habit generator; on results_n3 it is transliteration-fragile (RF1b FALLS).
7. The overlap test for "no weight" is over four families (L, C, G, X), not three.
8. "X" in results_m4 meant "other, no family"; v2 X = gibberish. run_v2 reads an X range
   only from a ranges file carrying `"x_family": "gibberish"`, so the m4 file prints X = NA.
9. Robustness rule 1 (glyph-collapsed tokenization) is dropped as a board scale: results_m7
   shows h2/sd_len move by construction under glyph+ and v101; RF1b/IT2a replace it.
10. The bifolio null is specified from `p1_bifolio_null.py` Part B; `results_p1.txt` on disk
    is from `p1_order_sensitivity.py`, so the bifolio null is still unrun at the freeze.
11. Controls are wrapped 8 x 20 (m4 convention) rather than v1's 9-word pseudo-lines.

## Not done / open

- No X ranges file exists yet; building it (score the 38 gib_ files + gib_pooled with run_v2,
  take min/max, write a ranges JSON with `"x_family": "gibberish"`) is the next run.
- n2hab_* sidecars for the G family are named in §7 but no such sidecar is on disk.
- Nothing else in the folder was edited; PREREG.md, PREREG-v2-DRAFT.md, scoreboard/score.py
  and all results files are untouched.

## Addendum (coordinator, 2026-10-17 19:28 PDT)
- The bifolio-null statement above ("results_p1.txt on disk is p1_order_sensitivity output, bifolio null unrun") was true at freeze time. At 19:24 the decryption session reran `p1_bifolio_null.py` unchanged to `results_p1_bifolio.txt`; order output moved to `results_p1_order.txt`. Rerun reproduces hand-1 p=0.000, hand-2 p=0.012, Part D +1.02 pp; Part D CI is [+0.03, +1.98] P=0.021, not the earlier filed [+0.48, +1.78]. The frozen PREREG-v2.md text is unchanged (hash f8c42d76…); this note is the correction of record.
- No X (gibberish) ranges file exists yet; m4's ranges file prints X = NA. First v2 run is to score the 39 `gib_*` sidecars and write a ranges JSON carrying `"x_family": "gibberish"`.
