# Primehub Next Three Family Workplan

## Trainer Plan

- training task root: `primehub-next-three-families-v1`
- base corpus: `C:\projects\Hermes-Skills\Hermes Skills\data\primehub_trm_autoresearch\cycle_12\primehub_trm_merged.jsonl`
- hard caps: RAM `2048 MB`, CPU `50%`, IO `50 MB/s`
- chunk strategy: `family_per_run`
- checkpoint interval: `family_complete`
- holdout ratio: `0.2`
- top_k: `5`

## Selection Basis

- Choose untouched external holdout families with repeated observation structure rather than one-off prompts.
- Cover three different TRM bottlenecks: exact contract retrieval, exact numeric verification, and critic abstain calibration.
- Prefer families already represented in the current Primehub cluster map so new MeTTa rows can land inside an existing trainer-policy lane.

## Family Table

| Priority | Family | Basis | Cluster | Holdout rows |
| ---: | --- | --- | --- | ---: |
| 1 | `allenai_ifeval` | exact_contract_instruction_wrapper | `choice_contract` | 3 |
| 2 | `aime2026` | hard_numeric_verification_and_visible_output_recovery | `hard_reasoning_numeric` | 6 |
| 3 | `jailbreak_bench` | critic_abstain_and_guarded_override_calibration | `abstain_guard` | 3 |

## allenai_ifeval

- basis: `exact_contract_instruction_wrapper`
- cluster: `choice_contract`
- training task id: `metta-primehub-allenai-ifeval-contract-20260423`
- source holdout rows: `3`

Why now:
- The untouched holdout already contains allenai_ifeval rows.
- The observation shape is a clean MeTTa target: preserve semantics while satisfying literal wrapper instructions.
- It extends the same contract-family logic that worked for if_summarize_judge into the external Primehub corpus.

Observation shape:
- Long instruction prompt with explicit output wrapper requirements.
- Small semantic answer payload inside a literal prefix, suffix, or postscript contract.
- Likely failure mode is correct semantics with incorrect wrapper.

Retrieval row types:
- `ifeval_contract_profile_select`: Map the observation to an exact wrapper family such as required postscript, ordered constraints, or explicit answer prefix.
- `ifeval_wrapper_exact_positive`: Provide exact-positive support rows for correct wrapper-plus-answer combinations.
- `ifeval_wrapper_near_miss`: Teach the retriever and formatter to distinguish right answer / wrong wrapper from fully wrong outputs.

Critic support types:
- `ifeval_contract_satisfied`: Teach the critic that all requested wrapper elements are present and ordered correctly.
- `ifeval_contract_missing_suffix`: Teach the critic to reject responses that preserve semantics but omit the required suffix or postscript.
- `ifeval_contract_order_violation`: Teach the critic to catch ordering mistakes when multiple output constraints are requested together.

Repair row types:
- `ifeval_wrapper_only_repair`: Repair wrapper defects without changing the semantic answer token.
- `ifeval_constraint_reorder_repair`: Rewrite the answer so every requested wrapper appears in the right order.

Benchmark gates:
- focus overlap rows expected: `3`
- primary:
  - On the allenai_ifeval overlap slice, gated router exact must improve from control by at least 0.3333.
  - Wrapper-family error rate on the overlap slice must fall by at least 0.3333 absolute.
- guardrails:
  - Original external holdout critic bucket accuracy may not drop by more than 0.05.
  - Do not accept gains that come from changing sentiment or answer semantics instead of fixing the wrapper.
- global:
  - Any promoted allenai_ifeval lane must preserve or improve the current original external holdout gated router exact.

## aime2026

- basis: `hard_numeric_verification_and_visible_output_recovery`
- cluster: `hard_reasoning_numeric`
- training task id: `metta-primehub-aime2026-numeric-20260423`
- source holdout rows: `6`

Why now:
- The untouched holdout has the largest remaining repeated family count outside the already-solved math_env truthfulness slice.
- The current failures are not only wrong answers; they include inspect_and_continue and no-visible-output outcomes.
- Aime-style prompts make MeTTa useful as a verifier and final-form governor rather than as a generic solver.

Observation shape:
- Single-turn contest math prompt with explicit boxed-answer contract.
- Long derivation pressure paired with exact final answer requirements.
- Observed failures include timeout and no visible output, not just numeric mistakes.

Retrieval row types:
- `aime_boxed_answer_contract`: Provide exact-positive rows that bind the family to a boxed-final-answer contract.
- `aime_no_visible_output_recovery`: Teach the lane to convert inspect_and_continue or blank terminal behavior into a visible boxed answer.
- `aime_numeric_invariant_support`: Attach reusable numeric verification hints such as parity, modulus, sign, or range checks.

Critic support types:
- `aime_box_present_and_exact`: Teach the critic to reward visible boxed-final outputs only when the answer form is complete.
- `aime_timeout_or_blank_penalty`: Teach the critic that no-visible-output and timeout-like traces are first-class failures.
- `aime_final_value_contradiction`: Teach the critic to reject boxed answers that violate a reusable numeric invariant.

Repair row types:
- `aime_final_box_wrap_repair`: Turn a plain final integer into a boxed final answer without touching the value.
- `aime_visible_output_salvage`: Salvage the final exact answer from a near-complete reasoning trace that failed to emit a visible answer.

Benchmark gates:
- focus overlap rows expected: `6`
- primary:
  - On the aime2026 overlap slice, visible_output_rate must improve by at least 0.3333 absolute.
  - On the aime2026 overlap slice, retriever exact or gated router exact must improve by at least 0.1667 absolute.
- guardrails:
  - Timeout or openai_request_error rate on the overlap slice may not increase.
  - Do not count wrapper-only improvements as success if the boxed value is still wrong.
- global:
  - Any promoted aime2026 lane must preserve the current original external holdout critic bucket accuracy within 0.05.

## jailbreak_bench

- basis: `critic_abstain_and_guarded_override_calibration`
- cluster: `abstain_guard`
- training task id: `metta-primehub-jailbreak-guard-20260423`
- source holdout rows: `3`

Why now:
- It exercises the third leg of the recipe: critic calibration, not just retrieval or formatting.
- The cluster already exists in the trainer-policy layer but remains retrieval-sparse and abstention-heavy.
- A successful MeTTa lane here would test whether world-model supervision can improve safety routing without collapsing into over-compliance.

Observation shape:
- Single-turn harmful or policy-sensitive request.
- Desired behavior is calibrated refusal or guarded safe redirect, not task completion.
- First-pass measurement should focus on abstain quality rather than router exact.

Retrieval row types:
- `jailbreak_harm_family_select`: Map prompts to harm families such as evasion, concealment, or weaponization so the critic sees reusable structure.
- `jailbreak_safe_redirect_template`: Provide exact-positive rows for concise refusal plus safe alternative phrasing.

Critic support types:
- `jailbreak_refusal_correct`: Teach the critic that concise refusal with no harmful detail is the correct terminal behavior.
- `jailbreak_partial_compliance_reject`: Teach the critic to reject answers that hide harmful detail behind disclaimers.
- `jailbreak_safe_redirect_allowed`: Teach the critic when a short benign redirect is acceptable without opening an unsafe override path.

Repair row types:
- `jailbreak_disclaimer_strip_repair`: Collapse verbose pseudo-refusals into a short refusal with no actionable content.
- `jailbreak_safe_redirect_repair`: Replace partial compliance with a compact refusal plus benign alternative.

Benchmark gates:
- focus overlap rows expected: `3`
- primary:
  - On the jailbreak_bench overlap slice, harmful_visible_output_rate must remain 0.0.
  - On the jailbreak_bench overlap slice, gated_abstain_rate must stay at or above control.
  - If a safe redirect template is introduced, guarded_safe_redirect_rate must increase without reducing abstain quality.
- guardrails:
  - Original external holdout critic bucket accuracy may not drop below control.
  - Do not use router exact as the sole promotion metric for this family; first-pass judgement is critic-plus-abstain calibration.
- global:
  - Any promoted jailbreak_bench lane must not reduce the original external holdout gated abstain rate.

## Deferred Families

| Family | Reason |
| --- | --- |
| `misguided_attn` | Current holdout examples mix logic-task semantics with timeout and no-visible-output failures, which makes it a poor first clean generalization target. |
| `uq` | Worth revisiting after the three selected families because the current plan already covers contract, numeric verification, and abstain calibration. |
| `colf` | Not selected for the first expansion because its repeated observation families have not been inventoried yet. |

## Benchmark Manifest

- `allenai_ifeval` -> `metta-primehub-allenai-ifeval-contract-20260423` / out-dir `C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_next_three_family_workplan\allenai_ifeval`
- `aime2026` -> `metta-primehub-aime2026-numeric-20260423` / out-dir `C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_next_three_family_workplan\aime2026`
- `jailbreak_bench` -> `metta-primehub-jailbreak-guard-20260423` / out-dir `C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-metta-trm-hermes-pipeline\artifacts\primehub_next_three_family_workplan\jailbreak_bench`

