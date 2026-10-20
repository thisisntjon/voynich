# scoreboard: one scoring pipeline for real text, controls and generators

PLAN.md Phase 0 item 2. Every metric of the a1 / a2 / a4b / a7 / b1 (T2) /
b3 (C3, C4) / b4 / b5 battery, computed from one `Corpus` object by one
`score()` call, with the originals' definitions, caps and seeds, so the
filed `results_*.txt` numbers reproduce (`tests/test_score.py`, 18 tests).

## Usage

```
cd .
python -m scoreboard.run --corpus voynich                  # ZL3b EVA, all metrics (~15 s)
python -m scoreboard.run --corpus voynich:glyph --corpus voynich:glyph+
python -m scoreboard.run --control latin_caesar            # flat Gutenberg control
python -m scoreboard.run --control italian_dante:verse     # its own line breaks (a2 convention)
python -m scoreboard.run --control latin_caesar:lines9     # wrapped into pseudo-lines of 9
python -m scoreboard.run --sections latin_augustine        # b5 CTRL layout (book labels)
python -m scoreboard.run --meta path/to/synth.meta.json    # synthetic corpus with sidecar
python -m scoreboard.run --control latin_caesar --skip-nmf --print --dry-run
python -m unittest tests.test_score -v                     # reproduction tests (~30 s)
```

Each run appends/updates `scoreboard/scoreboard.json["v2"][<corpus name>]`
with `metrics`, `params` (n_tokens, seed, windows), `corpus` summary,
`source`, a clock `timestamp`, and git-free `provenance` (sha256 of
score.py / corpus.py / score_v1.py / data/ZL3b-n.txt, library versions).
The v1 `entrants` list and `reproduction_pass` in the same file are left
exactly as the frozen v1 board wrote them.

From Python:

```python
from scoreboard.corpus import Corpus
from scoreboard.score_v2 import score, flatten
res = score(Corpus.from_voynich(), n_tokens=25000, seed=20261017, skip_nmf=False)
flatten(res)["position_all.enrich.fixed_first_ratio"]   # 17.89
```

## Corpus (scoreboard/corpus.py)

`Corpus(name, pages, has_lines, tokenization, source)`; each page is
`dict(page_id, section, hand, lang, quire, lines=list[list[str]])`, optional
`block` (grouping unit for the b5 nulls; defaults to page_id). Token-stream
metrics flatten pages -> lines -> tokens in order.

| constructor | what it builds |
|---|---|
| `Corpus.from_voynich(tokenization="eva"/"glyph"/"glyph+", subset=None, drop_unclear=True)` | ZL3b P* units via `corpora.voynich_lines`, one page per folio; section = `$I` code |
| `Corpus.from_control(name, lines=None/"verse"/int)` | `corpora.control` stream (flat, `has_lines=False`), the file's own lines (`a2.verse_lines`), or pseudo-lines |
| `Corpus.from_control_sections(name, header_re)` | `b5.control_chunks` layout: 40-token pages labelled by in-text headers, block = 200-token stretch |
| `Corpus.from_wordlist(words, line_len=None, page_len=30)` | any flat list, optionally wrapped |
| `Corpus.from_meta_json(path)` | sidecar `{"pages":[{"id","section","hand"?,"lang"?,"quire"?,"lines":[[tok,..],..]}]}` (format in the module docstring) |

Corpora without line structure get `None` for the line / column / NMF
metrics. Corpora without section / hand labels get `None` for the
corresponding NMI entries.

## Metrics (scoreboard/score.py)

Result keys (nested dict; `flatten()` gives dotted keys). "Original" is the
script and results file the function reproduces; the test column says what
`tests/test_score.py` checks and the tolerance (printed precision unless
stated).

| key | function | definition | original | tested on |
|---|---|---|---|---|
| `profile.tokens/types/hapax/mean_len/sd_len/alpha/h1/h2/h3/zipf/redup_pct/top10_pct` | `profile(words, n)` | first 25k tokens; h2 = H(pair)-H(char) on `" ".join(words)+" "`; sd = population SD; zipf = log-log slope over top-1000 ranks; redup = adjacent identical pairs /(n-1) %; top10 = token share of 10 most frequent types % | a1_profile.py -> results_a1.txt | voynich, voynich:glyph, voynich:glyph+, latin_caesar, italian_dante |
| `h2_all_tokens` | `h2_underscore(words)` | same h2 on `"_".join` of all tokens (b3/b4 variant) | b3 C4 orig / b4 h2 | dante verse (b4 CTRL_dante h2) |
| `position_all.{first_glyph,last_glyph,length}.jsd_first/jsd_last/null_*` | `position(lines, n_null=30)` | all lines with >=3 words; JSD(line-initial feature, mid) and JSD(line-final, mid); within-line shuffle null, seeds 0..29 (`null_*_mean/std`) and first 20 (`null20_*`) | a2_position.py -> results_a2.txt | voynich (3 features x 6 numbers), italian_dante:verse |
| `position_all.enrich.fixed_first_ratio` (p), `fixed_last_ratio` (m), `max_first_glyph/ratio`, `max_last_glyph/ratio`, `first_table`, `last_table` | `position()` | edge rate / mid rate; fixed p and m for Voynich comparability; generalised = max ratio among glyphs with >=20 edge occurrences; tables = a2's top-10 lists | a2 main ("x17.89", "x16.31", "g x25.47") | voynich (all 20 printed ratios) |
| `position_body.*` | `position_body(corpus)` | same on lines 2+ of each page, null mean over 20 draws, plus h2 (underscore), repeat % (pairs/tokens), `samecol_edit_le1` (b4.samecol_rate over all page lines), tokens | b4_selfcite_sim.py VOYNICH row -> results_b4.txt | voynich (10 numbers), dante CTRL row via position_all |
| `page_first_gallows.*` | `page_first_gallows(corpus)` | share of page-first lines whose first glyph is k/t/p/f vs other lines; p/f only | a2 main last block | raw corpus exact; standard corpus +-1.5 pp (see REPRODUCTION.md) |
| `near_copy.matched_w10/w40.*` | `near_copy_matched(corpus, W, seed=0)` | a4b: every 2nd token of (lang,section,hand) groups >=400; nearest Levenshtein (cap 4) in W preceding tokens vs a same-group window >1500 away; exact / d=1 / d<=1 shares and ratios | a4b_selfcite_matched.py -> results_a4b.txt | voynich W=10, W=40 (18 numbers) |
| `near_copy.unmatched_w10/w40.*` | `near_copy_unmatched(words, W, N=12000, seed=0)` | a4.measure: first 12k tokens, far window >=2000 away | a4_selfcite.measure as used in results_a4b.txt control rows | latin_caesar, italian_dante W=10 |
| `abbreviation.rho/top50_len/token_mean_len/ratio` | `abbreviation(words, n)` | first 25k; Spearman(freq, length) over types with freq>=3; mean length of top-50 types / mean token length | a7_abbrev.py -> results_a7.txt | voynich, voynich:glyph+, latin_caesar, italian_dante |
| `column_copy.*` | `column_copy(corpus, seed=20261017)` | b1 T2: per page, lines >=3 words; token at j of line i vs j-1..j+1 of line i-1 (same column), j+4..j+6 (off column), j-1..j+1 of line i-4 (far; random line when i<4); exact and edit<=1 %; col/far, col/off | b1_docx_tests.py T2 -> results_b1.txt | voynich (counts + 8 numbers) |
| `final_restriction.n_ge90/top` | `final_restriction(words, n)` | first 25k; per glyph with >=200 occurrences, share word-final; count >=0.9; top-6 | b3_slot_claims.py C3 -> results_b3.txt | voynich, latin_caesar, italian_dante |
| `shuffle_h2.h2/word_shuffled/d_word_shuffle/char_shuffled/d_char_shuffle` | `shuffle_h2(words, n, seed=7)` | first 25k; h2 after word-order shuffle and after within-word char shuffle (Random(7)) | b3 C4 | voynich exact; controls +-0.01 (rng state, see REPRODUCTION.md) |
| `nmf.section/hand/lang.nmi/perm_mean/perm_p99/rot_mean/rot_max/rot_p` | `nmf_topics(corpus, k=8, chunk=40, nperm=200, seed=0)` | 40-token chunks over the page-ordered stream, TF-IDF + NMF(8, nndsvda, rs=0), argmax cluster; NMI vs label; block-permutation null (200, default_rng(0)) and rotation null | b5_nmf_topics.py -> results_b5.txt VOYNICH ZL3b | voynich (3 x 6 numbers) |
| `nmf.within_hand.<hand>.*` | same | per hand: sections with >=30 chunks, >=2 sections; NMF refit with k = n_sections+2 (selects hand 1 {H,P}, hand 2 {B,H,T} on ZL3b, the sets b5 hard-coded) | b5 "within hand" lines | voynich hands 1, 2 |
| `nmf.section.*` on `--sections` corpora | same | b5 CTRL rows | b5 CTRL italian_dante / latin_augustine | nmi + rotation exact; perm null +-0.005 |

Seeds: a2 null seeds 0..n-1, a4/a4b seed 0, b3 Random(7), b5
default_rng(0) and NMF random_state=0 are pinned to the originals; `seed`
(default 20261017) is used by b1 T2 (its original SEED) and recorded.

Runtime: full `score()` on the Voynich corpus 11-15 s (NMF ~2 s); the
whole test suite ~30 s. `skip_nmf=True` / `--skip-nmf` drops the b5 block.

## v1 compatibility

The frozen v1 scorer (PREREG v1; sha256
`3a7b7c3e...` recorded in `PREREG.sha256` for `scoreboard/score.py`) is
kept byte-identical as `scoreboard/score_v1.py`, and `score.py` re-exports
its functions (`score_corpus`, `profile_metrics`, `line_metrics`,
`edge_metrics`, `perseveration`, `main_v1`), so `g0_score_filed.py` and
`scoreboard.json["entrants"]` keep working unchanged. v1's extra metrics
(cross-space MI, perseveration) are not duplicated in v2; call
`score_corpus` for them.
