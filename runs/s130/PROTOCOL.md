# s130 protocol: Fontana reading-feasibility pilot

Jon's brief (2026-10-19 11:17) follows s129 STEP_A_GATE=FAIL (agreement 0.7066 against 0.95; c-621, L-369). Owner: lead voynich-08 / b3796192. This pilot only: it involves no solve and no plaintext. The answer file is not read by anything in this run.

## Question

Does either cheap reading aid let two blind readers agree on Fontana's cipher glyphs at 0.95, line by line?

## Pilot lines and gate

- **Pilot lines:** L14 and L17 of the s129 block, drawn with `random.Random(130).sample(range(1,21),2)`.
- **Scoring:** `python -I s130_reading_pilot.py agree A.tsv B.tsv ROUTE`. Per-line token agreement is 1 − Levenshtein/max(len), with `.` treated as a word gap, exactly as in s129.
- **A route passes only if** agreement is at least 0.95 on **both** lines and all tokens are valid (`G<digits>`, `/`, `?`).
- **Otherwise** the route is recorded as failed and stops. There are no retries and no re-scoring.
- **Fixture** (`fixture_output.txt`): identical inputs give PASS; 10%-perturbed inputs give FAIL.

## Route R1: exemplar inventory (image crops instead of text descriptions)

- **R1a** (fresh agent) gets `r1a_input/`: all 20 original s129 line crops plus their halves and the overview. It writes:
  - (1) `r1a_boxes.tsv`, with rows `ID<TAB>Lnn<TAB>x0<TAB>x1`: 2-3 example boxes per ID, in full-line-crop pixel columns (images are 2470 px wide);
  - (2) `r1a.tsv`, the transcription of L14 and L17 with its IDs.
- R1a may use Python on its own input images to locate boxes.
- The lead runs `sheet r1a_boxes.tsv r1a_input r1b_input/exemplar_sheet.png`. The sheet shows image crops labelled by ID, with no shape text.
- **R1b** (fresh agent) gets `r1b_input/`: the exemplar sheet, the L14/L17 crops, and the separator rules below. No text descriptions. It writes `r1b.tsv`.
- **Gate:** `agree r1a.tsv r1b.tsv R1`.

## Route R2: enhanced crops with the s129 text inventory

- **R2a and R2b** (two fresh agents, independent) each get `r2_input/`:
  - `inventory_A.md`, the s129 text inventory;
  - the L14/L17 crops after autocontrast (cutoff 1), unsharp mask (2, 120, 2) and 3× Lanczos upscaling. Each line comes whole, plus 4 abutting segments with no overlap.
- They write `r2a.tsv` and `r2b.tsv`.
- **Gate:** `agree r2a.tsv r2b.tsv R2`.

## Separator rules (given to every reader)

- `/` marks a word gap. A point counts as a word gap.
- `?` marks one unreadable glyph.
- Long under- and overlines are ignored.

## Isolation

- Each reader opens only its own input folder and writes only its own output file.
- No reader sees another reader's output, the s129 transcriptions, the key chart, the plaintext, the yonichmanuscript folder, or the web.
- The lead (who has seen the key chart) does no reading.
- **Checks before scoring:** token validity, and a count of forbidden-path mentions in each reader's tool log. Any hit voids that reader.

## Outcomes

- A route passes: propose a full s129-style rerun to Jon. Run nothing without his approval.
- Both routes fail: record that these two aids, on these two lines, did not make agent reading reliable. That is a statement about this protocol only.
