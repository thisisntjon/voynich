# Fontana GPU known-answer campaign result

Date: 2026-10-19 (America/Los_Angeles)

State: **executed and self-audited; not independently audited; not used successfully for Voynich meaning**

## Decision

The campaign produced a verified Fontana page-alignment framework and localized the current blocker to manuscript image-to-symbol recognition. It did **not** recover Fontana's hidden substitution key, and it did not run a Voynich semantic test.

The run stopped before its eight-hour cap because both preregistrations required stopping when real glyph recognition failed. Continuing would have meant tuning after seeing the held-out result.

## Checked outcomes

| Stage | State | Evidence | Result |
|---|---|---|---|
| Official BSB acquisition | Acquired and locally integrity-checked | `ACQUISITION_RECEIPT_V1.json` | 149 cipher images + 100 Schulte images; 249 total |
| Source alignment | Executed and checked | `alignment_anchor_verification.json` | PASS: 16 readable anchors spanning source folios 1-70; 16/16 agree with the original manifest labels |
| Generic GPU HTR of Schulte | Executed and measured | `transcription_ocr_accuracy_0007.json` | FAIL as gold: 0.4292 normalized character accuracy on 1,151 manually checked characters vs frozen 0.95 requirement |
| V1 cipher line detection | Executed and visually checked | `cipher_0007_blla_overlay.jpg` | Strong probe: 27 lines found on source folio 1v, including the 19-line cipher block |
| V1 connected-component glyph cutting | Executed and visually checked | `v1_segmentation_audit.json`, `cipher_0007_glyph_first120.jpg` | FAIL: 1,063 pieces for about 846 cipher characters, with both merges and detached fragments; the 95% one-crop gate cannot pass |
| V2 synthetic CTC recognition | Executed and checked | `v2_ctc/result.json` | PASS: 0.9961 character accuracy and 0.9251 exact-sequence accuracy on 10,000 never-generated synthetic lines |
| V2 transfer to real Fontana lines | Executed and checked | `v2_real_transfer_audit.json` | FAIL: 33/40 cipher audit lines decoded blank; remaining 7 emitted only 1-3 IDs; zero lines emitted a nontrivial sequence of 10+ IDs |
| Hidden substitution solve | Not run | frozen V2 stop rule | Correctly stopped before language-model mapping or held-out plaintext scoring |
| Voynich application | Not run | D-073 sequence | No external bridge survived, so no semantic prediction was opened |

## What is now established

1. **The Schulte transcription is alignable, but not by canvas number.** Its leaves contain explicit marginal references to the source folios, and a single transcription leaf can continue one source folio and begin another.
2. **Our generic medieval-document HTR model is not accurate enough to supply plaintext gold for Schulte's modern cursive.** Its output can support navigation only.
3. **Fontana's cipher lines can be detected reliably at page level on the probe.** The failure occurs below the line: the symbols contain detached strokes and touching neighbors, so connected components are not characters.
4. **The RTX 5080 and CRNN pipeline work.** The model learned the generated task almost perfectly. Its failure on the manuscript is domain transfer, not failure to optimize.
5. **No hidden-key recovery was achieved.** “Acquired,” “aligned,” and “synthetic gate passed” must not be promoted to “decoded” or “used successfully.”

## Reproducibility

Primary commands:

```powershell
<local-path> fontana_v1\measure_transcription_ocr.py
<local-path> fontana_v1\verify_alignment_anchors.py
<local-path> fontana_v1\v2_train_synthetic_ctc.py
<local-path> fontana_v1\v2_decode_real_lines.py
<local-path> fontana_v1\audit_v2_real_transfer.py
```

All active Python files compile under the local Comfy Python. V2 used seed `20261019`, one RTX 5080 process and two data-loader workers.

Preregistration hashes:

- V1: `B726650580DF9840D83C7CF913E4800920C36E1BD116BEDE8802480B68CA3F13`
- V2: `CA3BF4E178B32D8C812116DA59C1D8A13D672014A911F8C31F4530DCAA5F09A3`

## Next decision-changing action

Do not launch another broad OCR or cipher sweep. The next Fontana attempt should use a small manually segmented, semantically blind set of real Fontana cipher lines to adapt only the visual encoder, while preserving numeric inventory IDs and the same untouched folios 55-70. It should be frozen as a new run and must first show nonblank, stable ID sequences on a development-only audit. Until that succeeds, Fontana remains an acquired and aligned control, not a successful meaning bridge.

