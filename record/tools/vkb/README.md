# VKB — Voynich Knowledge Base (derived, rebuildable)

One SQLite file, `data/vkb/vkb.sqlite`, that holds every checkable fact the project has, joined by shared keys so relationships can be queried directly. It is **derived** (D-070): the canonical sources stay the registers (`.inventory/registers/`), the findings graph (`workflow/FINDINGS-GRAPH.yaml`), the `results_*.txt` files and the `data/` folders. Never edit the database by hand; fix the source and rebuild.

Build: `python tools/vkb/build.py` (runs every module in order into a fresh file, then `check.py`).
Check: `python tools/vkb/check.py` (coverage, contradictions, unverified load-bearing facts; exit 1 on FAIL).
Query: `python tools/vkb/query.py "<SQL>"` or open the file in any SQLite tool.

## Rules for every row
- `src` = where the fact came from as `path` or `path:line` (relative to the repo root, or absolute for outside files). A row without `src` is not allowed.
- `status` where present: `verified` (lead audit or replication), `unverified`, `quarantined` (D-065), `rejected`, `superseded`.
- Folio ids use ZL3b page ids (`f1r`, `f67r1`, ...). Run ids use the lead form `sNN`, Daybreak `db-sNN`, roach `rN`, Argon runs keep `sNN` with `owner` set.

## Modules (each owns its tables; `build.py` calls `build(conn)` on each)
| module | tables |
|---|---|
| `manuscript.py` | `folios`, `quires`, `loci`, `tokens` |
| `features.py` | `folio_features`, `finding_links` |
| `evidence.py` | `runs`, `claims`, `measurements`, `findings`, `finding_lines`, `hypotheses`, `points`, `assumptions`, `pending`, `learnings`, `decisions`, `open_questions` |
| `world.py` | `corpora`, `corpus_stats`, `sources`, `external_items` |

## Schema (column: meaning). Every table also has `src TEXT NOT NULL`.

**folios**: folio PK, quire, bifolio (conjugate pair id), conjugate (other folio of the bifolio), leaf_side (r/v), panel (foldout panel or NULL), section (Zandbergen illustration class), illus_type, hand_davis, currier_lang (A/B), n_lines, n_tokens (ZL3b paragraph text), n_label_loci, n_stars, image_path, msi (0/1), notes.
**quires**: quire PK, collation, leaves_present, missing_leaves, notes.
**loci**: translit, folio, line_id (ZL locus id), line_no, locus_type (P paragraph, L label, R radial, C circular, other code as in IVTFF), para_start (0/1), n_tokens, text.
**tokens**: translit, folio, line_id, pos (0-based in line), word, n_glyphs, slot_prefix, slot_core, slot_suffix (SlotSegmenter), a2_prefix, a2_core, a2_suffix (Seg_Affix2), line_initial, line_final.
**runs**: run_id PK, owner, script, script_sha, stub, stub_ok, stub_mtime, results, results_ctime, admissibility (admissible / admissible-with-scope / rejected / quarantined / not-assessable / hold), impl_independent (0/1), decision (D-xxx refs).
**claims**: claim_id PK, run_id, text, results, lines, verified, date, note.
**measurements**: id PK, claim_id, run_id, statistic (canonical name, see below), value REAL, ci_lo, ci_hi, p, n, folds_pass, folds_total, call_name, call_value, translit, segmenter, corpus (corpus_id or 'voynich'), scope (free text), line (source line).
**findings**: fid PK, title, status, load_bearing, absence, grade. **finding_lines**: fid, axis, by, ref, claim, agrees, unverified, resolved, note. **hypotheses**: hid PK, short, name, status. **points**: fid, hid, rel, strength, why. **assumptions**: xid PK, statement, status. **pending**: pid PK, run, owner, state, result, decides, question.
**learnings**: lid PK, belief, result, evidence, change, date. **decisions**: did PK, date, title, body, refs, state. **open_questions**: oid PK, question, source, state.
**folio_features**: folio, translit, feature, value REAL (NULL when undefined), n (the count the value rests on: tokens, adjacent pairs, line starts or loci). One row per folio x transliteration x feature; see "Folio features" below.
**finding_links**: fid, rel, target, note. The graph's `related` links (rel = the graph's rel, target = F-xx), `decisions` (rel `decision`, target D-xxx) and `rests_on` (rel `rests-on`, target X-xx); src = the item's line in workflow/FINDINGS-GRAPH.yaml.
**corpora**: corpus_id PK, name, kind (natural / voynich / encoded / gibberish / synthetic / constructed / images), language, genre, period, tokens, path, licence, url, used_in (run ids), note.
**corpus_stats**: corpus_id, statistic, value, p, ci_lo, ci_hi, n_tokens, segmenter, pipeline (which estimator: lead / roach / explore), label, scope, run_id, claim_id, note (same statistic names as measurements; Voynich itself is corpus `voynich-<translit>`). Compare values only within one pipeline and segmenter.
**sources**: source_id PK, kind (transliteration / image / physical / layout / comparandum / literature / dataset), title, url, licence, local_path, have (HAVE / PARTIAL / MISSING / FAKE), gap_note, questions.
**external_items**: path PK, location, kind, owner, intake_class (admissible / scope / not-admissible / data-only / unaudited), filed_as, note.

## Canonical statistic names (extend here, never ad hoc)
`Rw1` (R_within(1)), `Rc1` (R_cross(1)), `core_order_K100`, `core_order_K200`, `quire_locality`, `h2`, `rhythm_excess` (within-line lag-1 word-length excess over shuffle), `lag2_prefix_residue`, `battery_folds` (s67), `loqo_folds`, `kappa`, `auc`, `mde`, `odds_ratio`, `S1_affix_share`, `S24_affix_share`, `planted_recovery_folds`.
Added by `evidence.py` (2026-10-18): `jsd_first` (line-initial first-glyph JSD or its excess), `jsd_last`, `sd_len`, `redup_pct`, `hapax`, `cross_excess` (cross-space / edge coupling MI excess), `x_edge_mi_word`, `x_moran_I` (within-line word-length Moran I), `charwin`, `nmi`, `p_init_enrich`, `m_final_enrich`, `mrr`, `ari`, `zipf_slope`, `chi2`, `f1_residual` (held-out word-order residual), `mantel_r`, `core_repeat_R1` (same-core repeat ratio R(1), s56/s70 style), `prefix_order_gain` (held-out prefix-stream bigram/order gain, bits), `edit1_parent_ratio`, `core_core_excess` (core->next-core ordering excess at full inventory); row kinds `call` (call_name/call_value) and `verdict` (printed VERDICT, `->` outcome, an upper-case outcome word, or a lower-case `verdict: x` in the claim text).
Added 2026-10-18 (parse coverage pass): `z` (a printed z-score; it takes only the number(s) right after it), `dAIC` (delta AIC), `core_repeat_Rd` (repeat ratio R(d) or R_w(d) at d > 1 or an unstated d; the d is in `scope`), `mattr`, `p_value` (a printed p in a clause that names no canonical statistic; the p is in column `p`, value NULL).

## Folio features (`features.py`)
Computed fresh from `tokens` and `loci` (no run script is imported, D-071). Text features use the paragraph loci (`locus_type` P) of the folio in that transliteration; `L_P` = its lines, `T` = its tokens (n = |T|). Glyphs = `corpora.to_glyphs(word, GLYPHS)` (the `n_glyphs` rule). Rankings for the affix and edge features are fixed on all ZL3b P tokens and reused for RF1b and IT2a. Seeds are crc32(translit|folio|feature), so a rebuild reproduces every value. Descriptive inputs for exploratory queries, not filed measurements.
| feature | formula |
|---|---|
| `n_tokens`, `n_lines` | \|T\|, \|L_P\| |
| `mean_wlen` | mean `n_glyphs` over T |
| `ttr_50` | size-matched type/token ratio: mean over 50 random subsamples of 50 tokens (without replacement) of distinct words / 50; NULL if n < 50 |
| `h1` | plug-in glyph unigram entropy, bits: -sum p(g) log2 p(g) over the glyphs of T |
| `h2` | conditional glyph entropy H(next \| previous), bits, over bigrams inside words padded with a boundary symbol at both ends (`_w_`), so it does not depend on word order: -sum p(a,b) log2 p(b\|a) |
| `h1_50`, `h2_50` | the same on the `ttr_50` subsamples (mean of 50), the size-matched forms; NULL if n < 50 |
| `pfx:<p>` | share of T whose SlotSegmenter prefix is p, for the 10 commonest non-empty ZL3b slot prefixes |
| `sfx:<s>` | the same for the 10 commonest non-empty slot suffixes |
| `Rw1` | in-line core reuse, roach R5b style: rate_obs = share of adjacent same-line pairs (both cores non-empty) with identical cores; null = exact expectation under a within-folio permutation of the cores, sum_c m_c(m_c-1) / (M(M-1)) (M = non-empty core tokens of the folio); Rw1 = rate_obs / null. n = pairs |
| `Rw1_line` | the same observed count over its exact expectation under a within-line shuffle: sum over lines of pairs_l x sum_c m_lc(m_lc-1) / (L_l(L_l-1)); > 1 means identical cores sit next to each other more than elsewhere in the same line |
| `lag1_wlen` | pooled lag-1 Pearson r of word length (glyphs) over adjacent pairs in the same line, lengths centred on the folio mean and scaled by the folio variance |
| `rhythm_excess` | `lag1_wlen` minus its mean over 200 within-line shuffles of the lengths (the shuffle keeps each line's lengths); NULL below 10 pairs |
| `init:<g>` | share of P lines whose first word starts with glyph g, for the 6 commonest ZL3b line-initial glyphs; n = line starts |
| `final:<g>` | share of P lines whose last word ends with glyph g, 6 commonest ZL3b line-final glyphs |
| `label_share` | (loci of type L or R) / all loci of the folio, all locus types |
| `n_stars` | `folios.n_stars` (runs/s100 star classes; quire T only, NULL elsewhere) |

Exploratory scan over these: `python -I tools/vkb/queries/folio_relationship_scan.py` (feature x quire / hand / language / section / side / bifolio position / n_stars, permutation p within hand and within section, BH q; feature x feature partial on n_tokens). Its output is labelled EXPLORATORY and is never filed.
