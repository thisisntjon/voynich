# s129 clarifications (written 2026-10-19 10:51 PDT, after the freeze; no design change)

This file is not part of s129.prereg. It states what the frozen code and protocol already do, so the scoring rules cannot be re-chosen later. It also records Jon's review conditions (10:50). If this file and the frozen files disagree, the frozen files win, and the disagreement is reported.

## 1. Isolation (hashing shows integrity, not isolation)

- **The solver** (`solve` mode) reads only:
  - the transcription TSV (glyph IDs);
  - the three Latin training texts.
- It fixes the key by annealing before it opens the answer file. The open is at line 200, after `solve()` at line 198. The answer file is used only to compute the score.
- It never reads the key chart, the rubric, the image files or any Fontana folder file except the answer file at scoring time.
- **The transcribers** are told to open only `runs/s129/input/`. Two things are checked mechanically before scoring:
  - (a) a token check: every token in transcription_A.tsv and transcription_B.tsv must be `G<digits>`, `/`, `.` or `?`, with no letters or words;
  - (b) a path audit: the count of forbidden-path mentions (`yonichmanuscript`, `transcription_gt`, `alphabet`, `PROTOCOL`, `.py`) in each transcriber's tool-call log.
  Any hit is reported, and that agent's output is void.
- **Known residual exposure:**
  - The page image's file name (`bsb00013084_00007_max.jpg`) identifies the manuscript, so a model could recognise it from prior knowledge.
  - The transcribers output only arbitrary IDs, and the solver ignores ID names, so there is no plaintext channel. Recognition could still make A's reading more consistent than a naive reader's.
  - This is recorded as a limitation, not cleaned up after the fact.
- **The lead has read the key chart and the first 400 characters of the answer file** (rubric and the start of the continuation, 10:38). The lead does no transcription and makes no scoring choices beyond the frozen ones.

## 2. Transcriber B

- B gets copies of the five seeded crops (L02, L09, L13, L17, L19: full lines and halves) plus `inventory_A.md`. They go in a separate folder, `runs/s129/b_input/`, and B may open nothing else.
- B never gets A's line transcriptions.
- Before the copy, the lead checks that `inventory_A.md` holds no line transcriptions. Example locations given as line/word numbers are allowed; glyph sequences longer than one word are removed in a dated copy, and the original is kept.
- Agreement measures consistency between two readers. It does not measure correctness, since both could share a mistake. Correctness is measured only by step B against the plaintext.

## 3. What "accuracy" measures (frozen in `semiglobal_acc` and `norm`)

1. **Decoded text:** each glyph ID is mapped to one letter by the solved key. `?` tokens are dropped and do not count. Word gaps and points become spaces.
2. **Normalisation, applied the same way to both decoded text and answer:** lowercase; j→i, v→u, w→u; every non-letter becomes a space; only the letters `abcdefghiklmnopqrstuxyz` are kept.
3. **Spaces do not count:** all spaces are removed before comparison. Word division is not scored.
4. **Abbreviations:** the answer file is used exactly as written, with no expansion or contraction by the lead. Where the cipher abbreviates and the answer is expanded, or the reverse, the difference counts as edits against us.
5. **Score:** accuracy = 1 − (Levenshtein distance between the decoded letters and the best-matching contiguous stretch of the answer letters) / (number of decoded letters).
   - The answer's prefix (the plaintext rubric) and its suffix (the 1v continuation beyond the block) are free.
   - Nothing else is free.
6. **Reported with the score:**
   - the number of `?` dropped (many `?` shrink the denominator);
   - the decoded length;
   - null q99 from 100 permuted keys.
7. **CALL:**
   - KEY_RECOVERED: accuracy ≥ 0.80 and above null q99;
   - PARTIAL: 0.50 to 0.80;
   - FAILED: below 0.50.
   No other scoring method is applied to the primary call.

## 4. How outcomes may be described

- **Step A fails:** this protocol failed on this page within its budget. It does **not** show that agents cannot read manuscripts in general.
- **Step B fails with A passing:** this solver, with this transcription and this language model, did not recover the key within one attempt.
- **KEY_RECOVERED:** a known-answer validation of this image-to-transcription-to-solve pipeline on one Fontana page.
  - It justifies proposing one carefully bounded next step toward the Voynich, through Jon.
  - It is not a Voynich result. Fontana is a simple substitution, a kind the Voynich structure argues against (F-25, H-02).
- **One attempt:** no rerun, retune or rescoring after the solve output is seen.
