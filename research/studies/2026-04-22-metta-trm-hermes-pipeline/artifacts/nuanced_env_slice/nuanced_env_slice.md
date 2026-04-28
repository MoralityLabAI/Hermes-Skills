# Nuanced Env Slice

## Recommendation

- `core_ready`: `psycho_bench`, `if_summarize_judge`
- `expanded_ready`: add `allenai_ifeval` as a supporting contract-compliance member
- `blocked_high_value`: `clbench` once the 400-path is fixed
- keep `simpleqa`, `simpleqa_verified`, and `truthfulqa` out of this psycho-like slice

## Bundle Summary

| Bundle | Envs | Purpose |
| --- | --- | --- |
| `core_ready` | `psycho_bench`, `if_summarize_judge` | Highest-signal nuanced slice that is already benchmarkable. |
| `expanded_ready` | `psycho_bench`, `if_summarize_judge`, `allenai_ifeval` | Add a supporting IF boundary env without diluting the core. |
| `blocked_high_value` | `clbench` | Promote after the current 400-path is repaired. |
| `research_candidates` | `ifbench`, `ifeval` | Research-env follow-ons after the live nuanced slice is stable. |

## Env Review

| Env | Status | Source | Nuance Family | Best Reward | Tokens | Notes |
| --- | --- | --- | --- | ---: | ---: | --- |
| psycho_bench | core_ready | community | psychometric_self_model | 3.3233333333333333 | 1082 | Closest current benchmark to symbolic self-modeling under a strict flat output contract and partial-credit scoring. |
| if_summarize_judge | core_ready | research | constraint_summarization_judged | 0.0 | 950 | Long-context summarization with held-out structural constraints and an LLM judge gives richer failure modes than short QA or plain IF tasks. |
| allenai_ifeval | supporting_ready | community | instruction_compliance | 0.0 | 864 | Useful supporting contract benchmark for strict instruction execution, though less semantically nuanced than `psycho_bench`. |
| clbench | blocked_high_value | research | rubric_judged_long_context | 0.0 | 0 | Potentially the highest-value psycho-adjacent benchmark because it scores long-context task completion against explicit rubrics. |
| ifbench | research_candidate | research | instruction_compliance | - | - | Research-env IF task with strict/loose scoring that can widen the slice later. |
| ifeval | research_candidate | research | instruction_compliance | - | 864 | Canonical IF benchmark that can act as a contract-compliance check in the research env stack. |
| simpleqa | exclude_simple | research | short_fact_qa | - | 435 | Very short factual QA surface with little structural or judgment nuance. |
| simpleqa_verified | exclude_simple | research | short_fact_qa | - | 435 | Same basic issue as `simpleqa`: answerability and correctness matter, but the task is too short and discrete to test nuanced symbolic infusion. |
| simpleqa_verified_2 | exclude_simple | community | short_fact_qa | 0.0 | 435 | Verified factual QA remains too low-context and too binary for the current goal. |
| truthfulqa | exclude_simple | community | multiple_choice_truthfulness | 1.0 | 447 | Important benchmark, but the current multiple-choice wrapper is too discrete to play the `psycho_bench` role. |

## Exclusion Rule

- Favor long-context, judged, or partial-credit tasks with visible structural failure modes.
- Deprioritize short single-answer factual or multiple-choice tasks, even when they are important benchmarks elsewhere.

## Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\build_nuanced_env_slice.py"
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_nuanced_slice_baseline.py" --bundle core_ready --dry-run
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\run_nuanced_slice_baseline.py" --bundle expanded_ready
```

