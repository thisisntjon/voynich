# s129 protocol: Fontana folio 1v known-answer (D-077; D-072 step 2)

Frozen before any transcription exists. Owner: lead voynich-08 / b3796192. Approved by Jon 2026-10-19 (Fontana transcription; "go" 10:41).

## Question

Can our pipeline get from page images to a recovered plaintext on a 15th-century cipher whose answer we hold, with no key given? The steps are: an agent transcribes the glyphs, then the cipher is solved from ciphertext only.

## Inputs (hashed in s129.prereg)

- The cipher page: BSB bsb00013084_00007, full resolution (`input/bsb00013084_00007_max.jpg`), with 20 line crops cut by ink projection. Each line has a full crop and left/right zoom halves (`input/line_NN*.png`), plus an overview of the block.
- The rubric at the top of the page is plaintext Latin. It is excluded from every crop.
- Ground truth: `C:/Users/thisi/Desktop/yonichmanuscript/fontana_v1/transcription_gt_0007_manual.txt`, a manual reading of Schulte canvas 7 plus its 1v continuation on canvas 9 (1,151 characters). Alignment anchor: canvas 7 = 1v.
- Only the solver reads the ground truth, in `solve` mode, after the key is fixed.
- Language model: Latin quadgrams from Caesar, Augustine and Pliny (data/controls). Macer Floridus is held out for the fixture.

## Blinding

- The transcribers are fresh agents.
- They may open only `runs/s129/input/` and write only their own output file.
- They must never open anything under `C:/Users/thisi/Desktop/yonichmanuscript/` or any Schulte or plaintext file.
- They must never see Fontana's alphabet figure, which is the key, and they get no Latin letter labels.
- Glyph IDs are arbitrary (G01, G02, ...).
- The lead has seen the key figure, so the lead does no transcription.

## Step A: transcription and agreement gate

- **Transcriber A** (fresh agent) builds a glyph inventory from the 20 lines. It writes `transcription_A.tsv` (one row per line: `Lnn<TAB>tokens`; IDs separated by spaces; `/` = word gap; `?` = unreadable; `.` = point) and `inventory_A.md` (each ID with a shape description and the line/position of two examples).
  - Variant shapes that may be the same character get separate IDs unless they are clearly the same stroke sequence. The solver allows many IDs to map to one letter.
- **Transcriber B** (a separate fresh agent) gets `inventory_A.md` and the crops of lines L02, L09, L13, L17 and L19 (drawn with `random.Random(129).sample(range(1,21),5)`). B never sees A's TSV. B writes `transcription_B.tsv` for those 5 lines with A's IDs.
- **Gate:** `python -I s129_fontana_known_answer.py agree transcription_A.tsv transcription_B.tsv` must print `STEP_A_GATE=PASS`, meaning token agreement of at least 0.95.
- **Fail:** stop. Record `Fontana bridge closed for agent-only reading`. Try no second transcription method without Jon.

## Step B: ciphertext-only key recovery

- `python -I s129_fontana_known_answer.py solve transcription_A.tsv` runs simulated annealing, 24 restarts × 40,000 moves, seed 129.
- Score: 1 − semi-global letter edit distance / decoded length. Ground-truth prefix and suffix are free, to cover the rubric and continuation.
- Null: 100 permuted keys, reported as q99.
- **CALL rules:**
  - KEY_RECOVERED if accuracy is at least 0.80 and above null q99;
  - PARTIAL if accuracy is 0.50–0.80;
  - FAILED below 0.50.
- **Fixture, before data:** `fixture_output_v2.txt` shows CONTROL_PASS (planted keys K=25/35/45 with 3% noise: 0.970/0.964/0.958; shuffled negative 0.099).
  - The v1 fixture failed on a smoothing bug, since fixed: unseen contexts were uniform. That output is kept as `fixture_output_v1_flat-smoothing-bug.txt`.

## Limits and stop

- One attempt. 4 h wall. CPU at low priority. No tuning after the solve output is seen. Results go to new files only.
- **Outcomes:**
  - A and B both pass: the first external bridge survives, and D-072 step 3 may be proposed to Jon.
  - A passes and B fails: our decoding tools cannot recover a known substitution from an agent transcription. Stop using them for meaning.
  - A fails: reading is the bottleneck.
