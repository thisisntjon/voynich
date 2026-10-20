# External Voynich Research Hubs — Scouted Dossier (2026-10-17)

**Scouted by**: `Skynet Antigravity Voynich Lead <session>`  
**Workspace**: `.`  
**Purpose**: Cross-reference the four primary external Voynich research hubs against our local holdings (`data/external/`) and our empirical experiment board (`a1`–`m7`, `l1`), ensuring zero duplication of debunked claims and direct alignment with community structural benchmarks.

---

## 1. The Voynich Ninja (`https://www.voynich.ninja`)

### Live Hub Audit & Active Subforums (Scouted 2026-10-17)
- **Structure**: MyBB technical research forum compartmentalized into:
  - *Voynich Structure and Encoding* (`fid=11`): Text analysis (`fid=29`), Codicology & Paleography (`fid=53`), Statistics (`fid=30`), Historic codes & ciphers (`fid=31`), Comparisons with languages (`fid=32`).
  - *Voynich Background and Contents* (`fid=10`): History (`fid=18`), Carbon dating & materiality (`fid=19`), Imagery (`fid=12`: Botanical `fid=23`, Astrological `fid=24`, Cosmological `fid=25`, Biological `fid=26`, Pharmaceutical `fid=27`, Starred paragraphs `fid=28`), Page ordering (`fid=51`), Language A & B / hands (`fid=52`).
- **Active Empirical Threads (Oct 16–17, 2026 RSS & Live Feed)**:
  1. **Thread 6215 — *Chronological Path Stability/Uncertainty Analysis*** (`npcompl33t`, Oct 17, 2026):
     - Runs a 4,800-fit `ElPiGraph` principal-curve + MDS ensemble across **207 Voynich pages** and **50 pooled physical bifolia**, plus an adapted `scEGRET` structural discontinuity check across `1 -> 3a -> 3b -> 4 -> 5a -> 2` (Hands / Currier A-B progression).
     - **Key findings**:
       - Hand `3a` (Herbal B) and `3b` exhibit a sharp gap around `f58` where two inner bifolia of Quire H (4 folios) are historically missing.
       - Rosettes pages (`f85v2`, `f86v4`, `f86v3`, `f86v5`, `f86v6`, `f85r2`) form an isolated cluster and do not bridge cleanly to `5a` (`f58r`–`f58v`, `f65v`).
       - Pooled bifolia (50 sheets) stabilize trajectory variance compared to noisy single pages (`f57v`, `f65r`, `f66v`, `f99r`).
     - **Direct link to our work**: Directly motivates our `l1_heldout_g1_split.py` Part B intra-section recto/verso and adjacent-page continuity test.
  2. **Thread 5081 — *Greshko Naibbe Cipher (2025)*** (cached locally at `data/external/naibbe-greshko/voynich_ninja_thread5081.txt`, 87 KB):
     - Documents Marco Ponzi's and René Zandbergen's critiques of Michael Greshko's 6-table stateful biglyphic card/dice cipher (`Naibbe`): specifically, its line-integrity deficiencies and character conditional-entropy excess unless forced by flow-weighted homophone choice (`f3_flow_choice.py`, `h1_flow_lines.py`).
  3. **Other Oct 2026 Empirical Threads**:
     - Thread 6035: *Structural reading of the zodiac pages (`f70v2`–`f73v`)* (`Koen G`, Oct 17, 2026).
     - Thread 6211: *Folio `f57v` Four Ring Cipher Layout Analysis* (`ReneZ`, Oct 16, 2026).
     - Thread 6212: *Do plant contours influence glyph choice?*; Thread 4416: *Vertical dependency*.

---

## 2. Voynich.nu — René Zandbergen's Reference Archive (`https://www.voynich.nu`)

### Local Mirror & IVTFF Holdings (`data/external/voynich-nu-ivtff/` & `data/external/cribs/`)
- **Holdings verified on disk (`4.0 MB` across 11 files in `data/external/voynich-nu-ivtff/`)**:
  - `ZL3b-n.txt` (`data/ZL3b-n.txt`, `1.53 MB`, Zandbergen-Landini EVA v3b — frozen primary corpus in `vparse.py`).
  - `RF1b-e.txt` & `RF1b-er.txt` (Friedman First Study Group / Takeshi Takahashi EVA transliterations).
  - `IT2a-n.txt` (Interlinear archive in EVA).
  - `GC2a-n.txt` & `voyn_101.txt` (Glen Claston `v101` alphabet).
  - `FG2a-n.txt` (Frogguy alphabet), `CD2a-n.txt` (Currier/D'Imperio), `VT0e-n.txt`, `LSI_ivtff_0d.txt` (Landini-Stolfi Interlinear), `ivtff.xlsx` & `000_README.txt` (IVTFF v1.7 format specification).
  - `data/external/cribs/` (Stolfi/Zandbergen `f068r1`–`r3`, `f070v1`–`f073v` zodiac/month/star label crib files).
- **How our experiments use it**:
  - `m7_board_translit.py` (`results_m7_board_translit.txt`) explicitly audited our frozen PREREG v1 bands across `ZL3b`, `RF1b`, `IT2a`, `ZL3b_glyphplus` (`@NNN;` ligatures collapsed to single characters), and `GC2a` (`v101`):
    - **Finding**: Across EVA transliterations (`ZL3b`, `RF1b`, `IT2a`), `h2` moves by $\le 0.010$ bits (`2.095`–`2.105`) and `cross_excess_eva` moves by $\le 0.015$ bits (`+0.172`–`+0.181`). All 7 frozen bands hold identically across EVA transliterations.
    - Changing unit granularity (`ZL3b_glyphplus` or `GC2a` `v101`) raises `h2` to `2.397`–`2.540` because 1-char digram tokens (`ch`, `sh`, `cth`, `cph`, `cfh`) remove deterministic intra-digram transitions.

---

## 3. TheVoynich.org — Structured Research Register (`https://thevoynich.org`)

### Evidentiary Spine & Community Claim Database (Scouted 2026-10-17)
- **Live Snapshot (`2026-10-07`, Spine Reference `2026-08-30`)**:
  - **691 discrete findings** graded against a 6-tier evidentiary spine: **77 Confirmed**, **140 Supported**, **138 Candidate**, **224 Observed**, **70 Falsified**, **42 Parked**.
  - **1,362 community claims** scraped from 41 `voynich.nu` survey pages (`claims.json`, `1.77 MB`), filtered by `COMFILTER-001` (`SlopFilter`: `350` consistent with spine, `47` contradicted by Tier 1/2, `965` untested/unfalsifiable).
- **Tier 1 Confirmed Structural Spine (`T1-001` through `T1-007`)**:
  - `T1-001`: 4-state FSM grammar holds across all 226 folios (0 violations in 114,507 transitions).
  - `T1-002`: 77 forbidden glyph transition pairs have zero genuine occurrences (apparent violations are compound stitch points).
  - `T1-003`: 6 hard positional constraints (`q` initial-only `99.1%`, `m` final-only `95.2%`, `y` boundary-pinned, etc.). Natural Latin fails 8/8 positional checks (`KD-001`).
  - `T1-004` & `T1-005`: 28 structural operators account for `95.9%` of transitions; compound reclassification reduces apparent vocabulary by `19.8%` (`KD-003` kills the "~600-word lexicon" claim).
  - `T1-006` & `T1-007`: `0/10,000` random sequences pass combined constraints (`KD-002` kills random hoax); scrambling text destroys structure.
- **Tier 2 Supported Findings (`T2-001` through `T2-008`) & Alignment with Our `M4`/`M5`/`M6` Results**:
  - `T2-001`: Three distinct grammatical registers — running discourse, short labels (`m6_labels.py`), and circular bands (`m1_astro_split.py`).
  - `T2-002` & `T2-003`: Gallows plume (`k/t` vs. `p/f`) is a binary positional/paradigm switch (`KD-004` kills "gallows are root carriers"). **Our `m5_line_anatomy.py` sharpens this**: `p/f` enrichment is specifically **paragraph-initial** (`49.3%` on paragraph-first lines, $83.2\%$ total gallows, $\text{JSD} = 0.5486$), whereas ordinary line starts (`n=3,311`) are enriched in `d/y/s/t` ($\text{JSD} = 0.1468$).
  - `T2-004` & `T2-005`: Currier A/B is a suffix-dialect difference (`y` in A vs. `edy` in B) neutralized after prefix (`o`/`qo`/`ch`/`sh`), with Hand 1 = `100%` A and Hand 2 = `100%` B.
  - `T2-006`: Section boundaries never fall within a leaf (`0/8`).
  - `T2-007`: **Bifolio recto/verso pairs are significantly more similar than random pairs ($p < 10^{-6}$)**. Tested against section-preserving nulls in `l1_heldout_g1_split.py` Part B.
- **Known Dead (`KD-001` to `KD-015`)**:
  - `KD-001` Simple Latin substitution/transposition cipher; `KD-002` Unstructured random hoax; `KD-003` ~600-word lexicon; `KD-004` Gallows as lexical roots; `KD-005` Shaft count = quantity; `KD-006`–`KD-008` Circles = gears/clocks/volvelles; `KD-009` Single-manuscript copy; `KD-013`–`KD-015` Ukrainian (Stojko 1978), Hungarian (Nevem 2026), Ruthenian (Angel M. 2018).

---

## 4. Academic & Computational Literature (ACL / arXiv / CEUR-WS / Lingbuzz)

### Local Holdings in `data/external/` & Mapping to Our Experiments
| Paper / Repository | Local Path in `data/external/` | Core Mechanism / Benchmark | Tested in Our Repo (`.`) |
| :--- | :--- | :--- | :--- |
| **Bowern & Lindemann (2021)** *Annual Review of Linguistics* + **Lindemann & Bowern (2020)** *arXiv:2010.14697* | `bowern-lindemann-entropy/` (`992 MB` repo + PDFs) | Low $h_2 \approx 2.1$ bits/char alongside normal Zipfian word-frequency distribution across 200+ historical/natural/cipher corpora | Reproduced and extended to 43 corpora $\times$ 23 metrics in `m4_phase1_board.py` (`results_m4_phase1_board.txt`) |
| **Gaskell & Bowern (2022)** *Gibberish After All?* (CEUR-WS Vol. 3313, Paper 6) + **Paper 4** | `gaskell-bowern-gibberish/` (`78 MB` repo + `ceur_ws_3313_paper6.pdf`, `paper4.pdf`) | Playful vs. algorithmic gibberish baselines (`ctl_gibberish.py`) | Integrated as `gibberish_playful_*` and `gibberish_algo_*` controls in `m0`–`m4` (`ctl_gibberish.py`) |
| **Zattera (2022)** *A Voynich Slot Grammar* (CEUR-WS Vol. 3313, Paper 10) | `zattera_2022_ceur3313_paper10.pdf` | 12-slot morphological rigid template explaining low $h_2$ | Tested via rigid slot-grammar and prefix+stem decomposition in `c2`, `m5`, `k3_prefix_flow.py` |
| **Timm & Schinner (2014 / 2019)** *arXiv:1407.6639* Self-Citation Generator | `timm-schinner-generator/` (`VoynichTextGenerator.jar` + `timm_schinner_2014_arxiv_1407.6639.pdf`) | Autocorrelated copy-with-modification stream | Tested in `b4_selfcite_sim.py` (`results_b4.txt`), `d2_grid_generator.py`, and included as `gen_selfcite` in `m4_phase1_board.py` |
| **Greshko (2025)** *Naibbe Cipher* | `naibbe-greshko/` (`greshko_2025_naibbe_cipher.pdf` + code) | Stateful 6-table biglyphic card/dice homophonic substitution | Tested in `c4_naibbe_lines.py`, extended with flow-weighted homophone choice in `f3_flow_choice.py`, `h1_flow_lines.py`, `k1_joint_producer.py` |
| **Montemurro & Zanette (2013)** *PLOS ONE* | `montemurro_zanette_2013_plosone.pdf` | Long-range topical keyword information network across sections | Tested via section NMI and residual word-to-word MI in `c2_section_generator.py`, `e2_pair_residual.py`, `k1`–`k3` |
| **Schwartz (2026)** Preprint (`bootloops.ai/voynich.pdf`) | `schwartz-2026-preprint/` | Recent 2026 computational structural preprint | Audited against frozen scoreboard bands |
| **Rozanova & Temerev (2026)** *arXiv:2608.17096* + **Parisel (2026)** *arXiv:2604.19762* | `rozanova_temerev_2026_arxiv_2608.17096.pdf`, `parisel_2026_arxiv_2604.19762.pdf`, `voynich-glyph-bboxes/` | Line/glyph layout segmentation across 223 folios and 2026 structural modeling | Cross-checked with our line-anatomy (`m5`) and label (`m6`) analyses |
