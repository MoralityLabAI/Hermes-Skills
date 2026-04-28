# Experiment Log

## Run History

### Run 1

- run id: `live-eval-qwen35-9b-2026-04-22`
- date: `2026-04-22`
- model: `qwen35_9b`
- envs: `psycho_bench`, `ascii_tree`, `pydantic_adherence`
- command surface: `run_live_eval.py` with the first Primehub schema pack
- receipt: `artifacts/live_eval_qwen35_9b/structured_map_live_eval.results.json`
- result: mixed

Key outcome:

- retrieval-assisted improved `ascii_tree`
- retrieval-assisted stayed slightly below baseline on `psycho_bench`
- all arms were `0.0` on `pydantic_adherence`

### Run 2

- run id: `live-eval-qwen35-9b-validator-patch-2026-04-22`
- date: `2026-04-22`
- model: `qwen35_9b`
- envs: `psycho_bench`, `pydantic_adherence`
- command surface: `run_live_eval.py --env-id psycho_bench --env-id pydantic_adherence --output-dir ...\\live_eval_qwen35_9b_validator_patch`
- receipt: `artifacts/live_eval_qwen35_9b_validator_patch/structured_map_live_eval.results.json`
- result: hold

Key outcome:

- validator-aware retrieval memory did not move `pydantic_adherence` off `0.0`
- `psycho_bench` remained effectively unchanged versus the earlier live run
- the schema pack now records the exact verifier path and the known strict-type mismatch

### Run 3

- run id: `live-eval-qwen35-9b-after-env-fix-2026-04-22`
- date: `2026-04-22`
- model: `qwen35_9b`
- envs: `psycho_bench`, `pydantic_adherence`
- command surface: `run_live_eval.py --env-id psycho_bench --env-id pydantic_adherence --output-dir ...\\live_eval_qwen35_9b_after_env_fix`
- receipt: `artifacts/live_eval_qwen35_9b_after_env_fix/structured_map_live_eval.results.json`
- result: meaningful uplift on `pydantic_adherence`

Key outcome:

- the live community env was patched to validate `pydantic_adherence` with `model_validate_json(json.dumps(parsed), strict=False)`
- a direct bridge probe confirmed that a valid JSON sample now scores `1.0` and an invalid sample still scores `0.0`
- `retrieval_assisted` reached `1.0` on `pydantic_adherence`
- baseline and plain structured-map remained at `0.0` on `pydantic_adherence`
- `psycho_bench` stayed in the same range, with retrieval-assisted slightly ahead of plain structured-map in this rerun

### Run 4

- run id: `live-eval-qwen35-9b-ascii-threaded-2026-04-22`
- date: `2026-04-22`
- model: `qwen35_9b`
- envs: `ascii_tree`
- command surface: `run_live_eval.py --env-id ascii_tree --output-dir ...\\live_eval_qwen35_9b_ascii_threaded`
- receipt: `artifacts/live_eval_qwen35_9b_ascii_threaded/structured_map_live_eval.results.json`
- result: retrieval still wins under concurrent load

Key outcome:

- this run was intentionally threaded while another Hermes 9B job was active
- `ascii_tree` baseline: `0.0`
- `ascii_tree` plain structured-map: `0.0`
- `ascii_tree` retrieval-assisted: `0.8`
- retrieval remained robust even though the non-retrieval arms both emitted malformed closing structure

## Failure Mode

- Historical failure: the remote env implementation used to extract the last JSON object, parse it with `json.loads`, and call `model_validate(parsed)` on a root model with `ConfigDict(strict=True)`.
- That made text-only JSON unsatisfiable for UUID and datetime fields.
- The scorer has now been fixed, so this is no longer the active failure mode for the study.
- The earlier 27B live attempt was unusable because the endpoint timed out or returned HTTP 500 errors across the study tasks.

## Decision

- promote with scope limits

## Next Action

Operationalize the promotion:

- use retrieval by default on the exact-structure-sensitive structured-map lane
- keep measuring token cost separately before making any efficiency claim
- widen the held slice only after the next clean batch of post-fix runs
