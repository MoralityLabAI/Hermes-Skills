# Schema Lookup Design

## What Ran

On 2026-04-22, the structured-map retrieval study generated:

- `structured_map_prompt.psycho_bench.txt`
- `trm_mcp_prompt.retrieve.txt`
- `primehub_schema_pack/primehub_schema_surface.json`
- `primehub_schema_pack/primehub_schema_mcp_traces.jsonl`
- `primehub_schema_pack/rows_rerun/mcp_trm_rows.summary.json`

## What The Trial Proved

- The base `primehub-structured-map-hermes` prompt can be exported with a concrete env binding (`psycho_bench`) and critic-only runtime gate.
- The `trm-mcp` retrieve prompt can be exported with a concrete target surface label (`primehub_schema`).
- A real `primehub_schema` lookup surface can now be built from the structured-map contract plus live benchmark replays for `psycho_bench`, `ascii_tree`, and `pydantic_adherence`.
- `build_mcp_trm_rows.py` can be rerun directly on the generated Primehub-specific traces and produces a stable row set.

## Primehub-Specific Pack Snapshot

From `primehub_schema_pack/primehub_schema_surface.json` and `primehub_schema_pack/rows_rerun/mcp_trm_rows.summary.json`:

- resource descriptors: 6
- env schema resources:
  - `mcp://primehub_schema/env/psycho_bench`
  - `mcp://primehub_schema/env/ascii_tree`
  - `mcp://primehub_schema/env/pydantic_adherence`
- template resources:
  - `mcp://primehub_schema/templates/minimal_example?env=...`
- traces: 6
- rows: 18
- task families:
  - `mcp_route`: 6
  - `mcp_retrieve`: 6
  - `mcp_verify`: 6
- bucket counts:
  - `exact_positive`: 15
  - `negative`: 3

The pack is grounded in actual replay prompts from:

- `qwen35_27b_psycho_bench_q0048.jsonl`
- `qwen35_27b_ascii_tree_q0033.jsonl`
- `qwen35_27b_pydantic_adherence_q0049.jsonl`

## Current Limitation

This still does not prove that the retrieval layer improves live structured-map performance.

What it proves is narrower:

- the lookup surface is now real and task-specific
- the route, retrieve, and verify rows are no longer generic MCP placeholders
- the study can move to held policy evaluation instead of design-only setup

## Next Required Build

Run a held evaluation where the policy can consult `primehub_schema` before answering `psycho_bench`, `ascii_tree`, and `pydantic_adherence` tasks, then compare:

- exact schema adherence
- first useful lookup hit rate
- lookup calls per task
- malformed output rate

That held evaluation has now been run for the 9B endpoint. See:

- `live_eval_qwen35_9b/structured_map_live_eval.results.md`
- `live_eval_qwen35_9b/findings.md`

The current evidence is mixed rather than promotion-ready.

## Decision

Hold.

The study now has a real Primehub schema surface, a Primehub-specific TRM-MCP corpus, and a first live comparison. Promotion is still blocked because the live evidence is mixed.

## Validator-Aware Follow-Up

The schema pack was then rebuilt with validator metadata for `pydantic_adherence`, including:

- `validation_path`
- `validator_notes`
- `known_verifier_gaps`
- `example_status = best_effort_shape_only`

Those additions were motivated by the actual env implementation at:

- `/home/snacksack/prime_repos_tmp/community-environments/environments/pydantic_adherence/pydantic_adherence.py`

That verifier does:

- extract the last JSON object from text
- parse it with `json.loads`
- call `model.model_validate(parsed_dict)`

Because the root model uses `ConfigDict(strict=True)`, the parsed JSON dict cannot satisfy the `uuid.UUID` and `datetime` field expectations for `policy_id` and `created_at`.

The focused rerun is in:

- `live_eval_qwen35_9b_validator_patch/structured_map_live_eval.results.json`
- `live_eval_qwen35_9b_validator_patch/findings.md`

Outcome:

- `psycho_bench`
  - baseline: `3.3483`
  - plain structured-map: `3.3033`
  - retrieval-assisted: `3.3283`
- `pydantic_adherence`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `0.0`

That intermediate result correctly identified a verifier bug.

## Upstream Fix

The live community env at `/home/snacksack/prime_repos_tmp/community-environments/environments/pydantic_adherence/pydantic_adherence.py` was then patched to validate extracted JSON with:

- `model_validate_json(json.dumps(parsed), strict=False)`

instead of validating the parsed Python dict directly under strict root semantics.

This restores JSON-native behavior for UUID and datetime fields while keeping the benchmark focused on whether the final JSON object is compatible with the model.

## Post-Fix Live Slice

The focused rerun is in:

- `live_eval_qwen35_9b_after_env_fix/structured_map_live_eval.results.json`
- `live_eval_qwen35_9b_after_env_fix/findings.md`

Outcome:

- `psycho_bench`
  - baseline: `3.3283`
  - plain structured-map: `3.3061`
  - retrieval-assisted: `3.3311`
- `pydantic_adherence`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `1.0`

That makes `pydantic_adherence` useful again as a retrieval-sensitive benchmark lane. The retrieval layer is no longer blocked by the verifier mismatch; it now produces a real uplift on the fixed scorer.

## Threaded Ascii Check

To avoid piling a full three-env rerun on top of an active Hermes 9B workload, the missing `ascii_tree` lane was threaded separately:

- `live_eval_qwen35_9b_ascii_threaded/structured_map_live_eval.results.json`

Outcome:

- `ascii_tree`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `0.8`

The non-retrieval arms both failed with malformed closing structure in that threaded run, while the retrieval-assisted arm still produced a usable tree. So the post-fix three-env picture remains favorable to retrieval even under load.
