# vx01 A1 disclosure 1: segmenter scores on DEV books were computed and written (2026-10-18, PDT)
Plan: PLAN-X01-v5.1 sha256 af4fee6b847caca46afd2456818d510e817cb09699b91034270ac7f4a6a75393. New file; nothing existing edited.

## What happened
1. `vx01_a1_known_answer.py --dev-path-test` (frozen file, SHA256 5c408207c9668f203e3f716caa1d4db1412ea1943fc4c6707aac0eaa00b39d9e), run 2026-10-18 22:54 PDT (05:54:38Z), DEV seeds only, scored all 8 segmenter rows on 9 dev books (1 per transliteration x {G1, G2, NULL}) and WROTE the scores:
   - `runs\vx01_a1_dev\path_test_20261019T055438Z\a1_scores.csv` SHA256 46c1371d644dc426d67d546a21944c59601b2aa702fd13fde24217820011d686 (72 score rows + header)
   - `runs\vx01_a1_dev\path_test_20261019T055438Z\results_path_test.txt` SHA256 e1ab2a5cb26ec01d4ad69f6207409aa03af33b5e6be3b57c5fe3d1cce512049d (per-cell roll-up)
   I earlier reported that the path test "prints no scores". That was wrong as a description of the run: it printed none to the console, but it wrote real scores to these two files. Plan 3a/4 says dev books are for the oracle check only, so this is a deviation. I did not open those two files.
2. Also NOT logged in any dev log: right after, I ran a short ad hoc check from stdin (no vx01 file; Python on Skynet) on ONE dev book (ZL3b G1, dev seed 20261111). Per segmenter it counted word types left unparsed (None) and types whose parts do not join back to the word. That is where "Zattera parses 294 of 20,991 types (1.4%)" came from; Canonical had 49 types that do not join back. I read and reported these counts. They are not accuracy scores, but they are information about segmenters on a dev book. A third stdin run only listed imported module files (no scores).

## Status
- These numbers were seen (item 2) or written (item 1). They are DEV-only, UNVERIFIED and are NEVER evidence for any call.
- No code changed after either run. All five A1 files were frozen at 22:56 PDT with the hashes the IV checked; the path test ran on the frozen known_answer file (5c408207).
- No A1 rule, threshold, seed or the Zattera-hybrid dependency was changed after they were seen, and none will be (Eve/IV hard rule).
