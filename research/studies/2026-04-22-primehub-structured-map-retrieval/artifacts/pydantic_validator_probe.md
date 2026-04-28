# Pydantic Validator Probe

## What Was Checked

- The live community env implementation at `/home/snacksack/prime_repos_tmp/community-environments/environments/pydantic_adherence/pydantic_adherence.py`
- A local reproduction of the `LendingPolicy` model copied directly from the prompt
- The focused reruns in `artifacts/live_eval_qwen35_9b_validator_patch` and `artifacts/live_eval_qwen35_9b_after_env_fix`

## Verifier Path

The original env did the following:

1. extracts the last JSON object from the model output
2. parses it with `json.loads`
3. calls `model.model_validate(parsed_dict)`

That is a Python-object validation path, not a JSON-native validation path.

## Why This Matters

The prompt model defines the root `LendingPolicy` with `ConfigDict(strict=True)`, while also requiring:

- `policy_id: uuid.UUID`
- `created_at: datetime`

After `json.loads`, those fields are still plain Python `str` values. Under `model_validate(parsed_dict)` with `strict=True`, they are rejected before reward can become nonzero.

## Local Reproduction

The local reproduction matched the live behavior:

- the current retrieval-assisted JSON shape fails `model_validate(...)`
- omitting `created_at` still fails because the model's own pre-validator inserts an ISO datetime string
- `model_validate_json(...)` still fails `created_at` under the strict root model

## Historical Conclusion

The original `pydantic_adherence` slice appeared unsatisfiable for plain text JSON outputs. The persistent `0.0` reward was therefore not strong evidence against the retrieval layer.

## Applied Fix

The live env was patched to validate the extracted JSON with JSON-native semantics:

- `model.model_validate_json(json.dumps(parsed), strict=False)`

That preserves full model validation while allowing UUID and datetime fields to arrive through ordinary JSON strings.

## Post-Fix Check

- direct bridge probe with a valid JSON sample: `1.0`
- direct bridge probe with an invalid JSON sample: `0.0`
- live rerun:
  - baseline `pydantic_adherence`: `0.0`
  - plain structured-map `pydantic_adherence`: `0.0`
  - retrieval-assisted `pydantic_adherence`: `1.0`

## Current Conclusion

The verifier mismatch is fixed. `pydantic_adherence` is now a meaningful benchmark lane again, and the retrieval layer shows a real gain on the repaired scorer.
