# Audit: s101 tail-core prediction of specific visual attributes

**Audit date:** 2026-10-18 09:35 PDT  
**Terminal classification:** `VISION_LABELS_INVALID`  
**Manuscript text scored:** no

## Integrity and execution

The first invocation stopped before scoring because the optional SentencePiece Python package was absent. Amendment 1 replaced only the tokenizer wrapper with `PreTrainedTokenizerFast` over the already frozen `tokenizer.json`; no package or model was downloaded. The amended source, amendment, pre-score human annotations, model weights, embeddings, and transcription inputs were refrozen before computing any prompt score.

All 17 frozen inputs still match. The amended source SHA-256 is `C619861F9EFB25ABFF486EC9EF07361C18CC9843116C9DFF6598749FEA097F8B`. Result SHA-256 is `5B5DE0E85B28BC0CECD688A4BDC6AC1E45B98F3244EDA466CA50918389FFF0E6`; JSON SHA-256 is `582D376EDC48D7B275D7F35A9F5115F0519C1809153E6CEE0C83C2684F6FF3E5`.

The refrozen run took 10.08 seconds. Its only model computation was the eight prompt text embeddings and their contrast against the already saved masked image vectors. The generic tokenizer returned `token_type_ids`, which `SiglipModel.get_text_features` explicitly ignored. No validated axis remained, so the script produced no transcription result, no ridge fit, and no candidate core coefficients.

## Validation result

| Axis | Positive / negative annotations | AUC | Registered `.70` gate |
|---|---:|---:|---:|
| Flowers | 16 / 8 | `.5234` | Fail |
| Prominent root | 18 / 6 | `.5926` | Fail |
| Broad leaves | 15 / 9 | `.5852` | Fail |
| Branched stem | 16 / 8 | `.1172` | Fail, strongly reversed |

The annotations were fixed from a deterministic 24-page montage before prompt scores were calculated. None of the four registered prompt directions validates.

## Interpretation

This is a measurement failure, not a Voynich-text result. The tested zero-shot contrasts over rotation-averaged SigLIP image embeddings do not reliably recognize the four intended visual attributes in these stylized drawings. Reversing the branched-stem axis or rewriting prompts after seeing these AUCs would be post-hoc and is not allowed as s101 evidence.

The result closes this cheap semantic shortcut. A successor must use independently checked human annotations, objective pixel geometry, or a vision model validated on a separate set of comparable manuscript drawings before it may associate attributes with Voynich cores.

