# s132 protocol: Fontana combined reading pilot

Approved by Jon 2026-10-19 (~11:31) after s130 (R1 0.936/0.915, R2 0.80/0.797; c-622, c-624, L-372). Owner: lead voynich-08 / b3796192. Design, gate and modes are in the docstring of s132_combined_pilot.py. CONVENTIONS.md is given to both readers.

## Readers

- **C1a** (a fresh agent) gets c1a_input/: enhanced 3x crops of all 20 lines plus 4 abutting segments per line (segment k covers x [1852(k-1), 1852k), the last runs to 7410), and CONVENTIONS.md.
  - It writes c1a_boxes.tsv: at least 2 example boxes per ID, in enhanced pixels, with an ID allowed a single box only if it is marked `single` (one instance on the whole page).
  - It also writes c1a.tsv: its transcription of L05 and L15.
- The lead runs `sheet c1a_boxes.tsv c1a_input c1b_input/exemplar_sheet.png`. If it prints SHEET_INVALID, the run stops as failed (no fix-up).
- **C1b** (a fresh agent) gets c1b_input/: the sheet, CONVENTIONS.md, and the enhanced L05/L15 crops. It writes c1b.tsv.

## Gate

- `agree c1a.tsv c1b.tsv C1`: 0.95 on both lines. One attempt.

## Isolation

- Each reader opens only its own input folder and writes only its own outputs, plus zoom files in the session scratchpad. No web, no key chart, no plaintext, no earlier transcriptions.
- Audit: tools/audit_reader_isolation.py on each reader's real transcript.

## Outcomes

- A pass earns only a proposal to Jon for a full rerun on all 20 lines.
- A fail is recorded, and Fontana reading pilots stop. The finding is about this protocol on these lines only.
