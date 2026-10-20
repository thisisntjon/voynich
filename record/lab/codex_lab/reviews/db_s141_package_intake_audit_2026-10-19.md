# db-S141 package intake audit

**Date:** 2026-10-19 00:55 PDT  
**Package:** `<team-comms>`  
**Package SHA-256:** `848132082BB91B2DC7ED06C1D227270FF2B6A5E034F3EACAAFC6FC726B26C72A`  
**Disposition:** accepted in the narrow calibration scope below

## Checks

- Every member named in `PACKAGE-SHA256.tsv` matches its stated SHA-256 and byte size.
- The packaged script and preregistration match the freeze file.
- The live source/input hashes match the freeze (`freeze_ok=True`).
- An independent recomputation using the frozen code path returns 13 recovered identities, null mean 0.7357, q99 3.0, plus-one p = 0.000100.
- The exact 10,000-draw null has **maximum 5**, not 3. The report correctly labels 3 as q99; any wording calling 3 the null maximum is wrong.
- The package result and repeat result are byte-identical.

## Accepted use

Used successfully for **positive-control calibration of the mutual-top-five non-bijective graph rule on the Penn LJS 419 / Sloane 4016 labelled galleries**.

## Limits preserved

- S103 had already selected representation B using Penn/Sloane, so this is independent calibration of the graph rule, not the representation.
- Beasley places LJS 419 in the proposed alchemical-herbal sub-tradition; the result is not evidence of unrelated-family transfer relative to Canon Misc. 408.
- No Voynich page was scored or identified.
- This does not authorize a Voynich screen. Egerton crop and caption truth must pass their frozen independent gates first.

## Current blockers

- Egerton completed-manifest blind crop QC: packet delivered; no reviewer response found in <team-comms> at this checkpoint.
- Egerton full caption transcription: packet delivered; no first-reader response found.
- Egerton frozen 40-row second-reader caption QC: packet delivered; no response found, and comparison cannot occur before both reads exist.
- CE Voynich consumption correction: the independent audit remains `NEEDS_CORRECTION`; no corrected packet/final PASS was present in <team-comms> at this checkpoint.

