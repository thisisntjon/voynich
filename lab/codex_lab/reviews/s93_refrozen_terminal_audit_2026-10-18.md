# S93 refrozen terminal audit

**Date:** 2026-10-18  
**Run:** fresh refrozen s93/P-25, distinct from the earlier incomplete/mutated attempt  
**Terminal status:** complete, overall `PARTIAL / SEE FAILING CALLS ABOVE`  
**Scientific classification:** promising component mimic; not a unified producer under the newer acceptance gate

## Integrity

- Start: 09:45:06 PDT; finish: 10:00:20 PDT; printed runtime 911.37 seconds.
- Process PID 16920 ran at BelowNormal priority with one Torch thread and disappeared after writing the complete overall marker.
- Startup and terminal source SHA-256: `DC0355C7DC8B94132D4C933698DEA10D6E33224A3D46DB9C3A9454121745331C`.
- Stub SHA-256: `B01A9BBD03E45DDA36D4BB76656B25E731EEE0C370A122C812AB0A1516506CD9`.
- Terminal result SHA-256: `86C074B58D369C213E439159072183F21F503D48B1CB779710D109AFE2AC5A98`.
- The one-line stub contains the terminal source hash, and the result reports `stub_match=True`.

The run is admissible as a newly frozen version. It does not repair the historical record of the earlier s93 start; that attempt remains terminal and incomplete under its own startup hash.

## Part 1: what passed

Under the script's registered historical calls, M4 passes:

- four-part core signature on `14/15`, `15/15`, and `15/15` folds;
- dealiased `>=5/6` battery on `12/15`, `10/15`, and `10/15` folds;
- legacy `>=5/6` battery on `5/15`, `6/15`, and `4/15` folds;
- the pooled prefix-memory signature on all three transcriptions.

This is the strongest evidence so far that combining a line-scoped core producer, core-conditioned frames, a one-step frame handshake, and a weak cadence filter can reproduce several previously separate held-out signatures at once.

## Why this is not the accepted unified producer

The new magnitude-aware gate was written because the older count calls admit severe overshoot. S93 demonstrates that problem directly:

| Transcription | Real all-core Rw1 | M4 mean Rw1 |
|---|---:|---:|
| ZL3b | about 1.20 | 3.0674 |
| RF1b | about 1.20 | 3.1645 |
| IT2a | about 1.20 | 3.2386 |

The producer creates roughly 2.6 times the manuscript's immediate recurrence ratio. M2, M3, and M4 have the identical mean Rw1 in each transcription, so the frame handshake and cadence additions do not repair the core recurrence mechanism.

The displayed dealiased battery column is labeled `P1/P2k/P3g/P4/P5/P7`: it uses the global-band P3 fallback (`P3g`), whereas the current acceptance gate requires fold-specific P3. The run also lacks:

- training-defined top-20 occurrence uniquification and separate `Rw1_tail_u20`;
- the two-page prospective `(quire, section)` warmup;
- warmup-local versus cross-quire tail-identity log loss;
- inner-LOQO calibration of recurrence, cadence, prefix gain, reset, type ratio, and header JSD;
- an A1–A5 report under the current gate.

The frozen source has an internal specification inconsistency. Its top preregistration prose and printed model label say six cadence candidates, `gamma=1.25`, and `rho=.55`; the executable generator uses four candidates, weight `exp(-.58*distance)`, and length response `.42`. The source itself was frozen, so this is not post-start mutation, but `stub_match=True` does not establish consistency between prose and execution.

Strict reading: `CALL_1=True` under the historical gate; `UNIFIED_CANDIDATE=False` under the current gate.

## Part 2

The eight registered F-09 metrics retain overlapping intervals across the reported transcription, subsample/quire/bifolio, and scan-aligned axes, so `CALL_2=True` under its frozen rule. This supports robustness of the measured architecture. The axes reuse the same manuscript and much shared code, so “triangulated” should be read as multi-axis robustness, not independent evidence of meaning or historical mechanism.

## Part 3

`CALL_3=False` and X-08 is not discharged:

- minimum label-free clustering accuracy is `.8095` versus the `.85` gate;
- minimum NMI is `.3337` versus `.40`;
- physical layout separation passes (`z=+3.86` words/line; `+8.17` lines/page);
- the Herbal-B null fails because the IT2a unsupervised partition produces a split (`D_sym=+.1647`, `p=.0353`).

The result therefore does not establish a label-free physical/distributional scribe regime independent of section and quire structure.

## Decision consequence

S93 materially improves the producer evidence but also supplies the clearest reason to run s98. S98 is not a weaker repeat of s93: it replaces the over-recurrent pool with calibrated one-transition revisits, separates shared head from quire-local tail, and scores later pages after a frozen two-page warmup. Under D-056, the defensible disposition is to permit that one bounded successor and stop further producer multiplication unless it clears the current gate or yields a specific new failure diagnosis.
