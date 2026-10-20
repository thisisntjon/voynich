# vx01 A1 disclosure 1 addendum: time of the unlogged stdin check (Zattera 1.4% figure)
Date 2026-10-18 PDT. Adds to `vx01_a1_DISCLOSURE_1_dev_scores.md` (e2a980d2eae8c7ac20e33d0af58fa25fe3ece9226e545d57f9c2047fba3f2f0c), which is not edited.
- Exact second: NOT KNOWN. No log, output file or saved bytes exist for that check.
- Bounds, from my own transcript order plus file times on Skynet (mtime, PDT):
  - It ran right AFTER the path test, whose last output `runs\vx01_a1_dev\path_test_20261019T055438Z\results_path_test.txt` and console file `voynich-backups\vx01_work\dev2.out` were last written at **22:55:16**.
  - It ran right BEFORE the import-listing check, whose output `voynich-backups\vx01_work\imports_a1.txt` was written at **22:55:52**.
  - So the check ran between **22:55:16 and 22:55:52 PDT** on 2026-10-18.
- That window falls after every frozen A1 file was last written (22:54:28) and before the A1 stubs (22:56:06). It changed no file (IV 4d).
