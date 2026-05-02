# Math Receipts

Packaged benchmark evidence for `Hermes/Intellect-3-Math-v1`.

## Hybrid summary

- Rows: `200`
- Vanilla exact match: `0.085`
- Generic skill exact match: `0.07`
- Math skill exact match: `0.06`
- TRM-augmented math skill exact match: `0.07`
- TRM path route mix: `math_skill 191`, `math_skill_trm 9`

## Router summary

- Gate exact match: `0.09`
- Oracle exact upper bound: `0.11`
- Support gate exact match: `0.11`
- Support gate route-choice accuracy: `1.0`

## MeTTa self-improvement smoke

- Artifact: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_metta_self_improve_27b_20260502/intellect3_math_metta_self_improve.results.md`
- Model: `Qwen3.5-27B.Q4_K_M.gguf` on snacksack, OpenAI-compatible completions with Qwen no-think prefill.
- Held-out rows: `10`
- Baseline exact: `0/10`
- Current skill exact: `3/10`
- 27B-drafted MeTTa prompt exact: `2/10`
- Commit decision: `reject_patch_keep_current_skill`

Read: the MeTTa self-improvement layer is useful here as a patch generator plus
commit/veto gate, not as an automatic prompt replacement.  For Intellect-3-Math,
adopt a self-improved skill patch only when held-out exact improves and fixes
are at least regressions.

## Use

Read these receipts with the local summary JSON files in this folder when you
need the current benchmark state for the skill.
