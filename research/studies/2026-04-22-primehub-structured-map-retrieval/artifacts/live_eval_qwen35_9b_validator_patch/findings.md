# Validator-Aware Live Eval Findings

Model:

- `qwen35_9b`
- endpoint: `http://snacksack-ms-7d32.tail3156cd.ts.net:8082/v1`

Slice:

- `psycho_bench`
- `pydantic_adherence`

Arms:

- `baseline`
- `plain_structured_map`
- `retrieval_assisted`

## Outcome

The validator-aware retrieval memory did not change the `pydantic_adherence` result. It remained `0.0` across all arms, while `psycho_bench` stayed effectively unchanged from the earlier run.

## Reward Snapshot

- `psycho_bench`
  - baseline: `3.3483`
  - plain structured-map: `3.3033`
  - retrieval-assisted: `3.3283`
- `pydantic_adherence`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `0.0`

## Interpretation

- The richer retrieval memory did make the prompt more faithful to the real validator path.
- The unchanged `0.0` on `pydantic_adherence` is consistent with the verifier using `json.loads` plus `model_validate(parsed_dict)` under `strict=True`.
- This means the benchmark slice is currently better treated as a verifier-design issue than a prompt-design issue.

## Operational Note

The retrieval-assisted prompt became more expensive on `pydantic_adherence` without any reward gain, so this env should not be used as a promotion gate for TRM retrieval work until the verifier is fixed.
