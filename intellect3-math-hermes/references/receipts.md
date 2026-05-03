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

## Skill-patch gym

- Artifact: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_skill_patch_gym_20260502/intellect3_math_skill_patch_gym.results.md`
- Patch bank: raw baseline, incumbent current skill, rejected 27B auditor patch, and four Codex-seeded candidate/controller patches.
- TRM export: `30` patch commit/veto rows from the observed 10-row smoke.
- Adoption gate: promote a patch only when held-out exact exceeds incumbent and fixes are at least regressions.

Read: this is the path toward a real gym.  The unit of optimization is no longer
"one better prompt"; it is a patch-search loop with MeTTa rule generation,
held-out evaluation, and TRM commit/veto learning.

## Patch-bank live benchmark

- Artifact: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_patch_bank_benchmark_27b_20260502_combined40/combined_patch_bank_benchmark.results.md`
- Model: `Qwen3.5-27B-Q4_K_M.gguf` on snacksack.
- Unique held-out rows: `40`
- Calls: `280`
- Incumbent current skill: `7/40`
- Qwen 27B auditor patch: `4/40`
- Raw baseline: `3/40`
- Codex candidate patches: `2/40` to `4/40`
- Global adoption result: no candidate patch clears the incumbent gate.
- Row-level export: `280` patch commit/veto rows, including one row-level
  `commit_patch` where the Qwen auditor patch fixes an incumbent miss.
- Row-level upper bound from this patch bank: `8/40` rows had at least one exact
  answer across all arms (`6` multi-patch exact rows plus `2` incumbent-only).
- Selector smoke: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_patch_selector_27b_20260503_combined40/patch_selector.results.md`
- Selector result: simple prior selection does not beat incumbent on test
  (`4/20` vs `4/20`), so the immediate bottleneck is patch diversity.

Read: this supports the gym direction.  Whole-patch adoption is currently
negative, and row-level candidate selection has only weak signal.  The next TRM
target is a per-row patch selector/commit gate, but it needs more diverse
candidate generators before selector learning can pay off.

## Diverse and repair patch probes

- Diverse bank artifact: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_diverse_patch_bank_20260503/patch_bank_v2.results.md`
- Diverse bank live shard: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_diverse_patch_bank_benchmark_27b_20260503_offset40/patch_bank_benchmark.results.md`
- Diverse bank result: verifier-like and solver-procedure variants remained
  flat on offset40; most arms scored `1/10`, and only one row had any exact
  answer.
- Repair bank artifact: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_repair_patch_bank_20260503/patch_bank_v3.results.md`
- Repair focused shard: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_repair_patch_bank_benchmark_27b_20260503_offset40/patch_bank_benchmark.results.md`
- Repair validation shard: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_repair_patch_bank_benchmark_27b_20260503_offset50/patch_bank_benchmark.results.md`
- Cross-validation summary: `research/studies/2026-04-22-metta-trm-hermes-pipeline/artifacts/intellect3_math_repair_patch_validation_27b_20260503/repair_patch_validation.results.md`

Read: near-miss repair is the first prompt family in this run that produced a
clear local lift (`2/10` vs incumbent `1/10`) by repairing `1009 -> 1008` on a
strict circular recurrence row and `1023 -> 1024` on a locker elimination row.
It did not validate as a global prompt (`0/10` vs incumbent `2/10` on the next
shard).  This strengthens the methodology claim: semi-failed outputs are useful
for repair TRM data, but the repair action must be gated by applicability.

## Use

Read these receipts with the local summary JSON files in this folder when you
need the current benchmark state for the skill.
