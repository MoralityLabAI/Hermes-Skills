# Primehub Structured-Map Retrieval Study

## Goal

Test whether a `trm-mcp` style retrieval layer can reduce schema lookup cost for `primehub-structured-map-hermes` while preserving exact structured outputs.

## Pairing

- Base skill: [primehub-structured-map-hermes](C:/projects/Hermes-Skills/Hermes Skills/primehub-structured-map-hermes/SKILL.md)
- Overlay: [trm-mcp](C:/projects/Hermes-Skills/Hermes Skills/trm-mcp/SKILL.md)
- Workflow support: [trm-observability-workflow](C:/projects/Hermes-Skills/Hermes Skills/trm-observability-workflow/SKILL.md)

## Baseline Cross-Ref

Use the shared TRM benchmark spine when comparing this scoped retrieval win against the broader Hermes baseline:

- [trm_infused_baseline_summary_table.md](C:/projects/Hermes-Skills/Hermes Skills/research/generated/trm_infused_baseline_summary_table.md)
- [trm_infused_baseline_crossref.md](C:/projects/Hermes-Skills/Hermes Skills/research/generated/trm_infused_baseline_crossref.md)
- [trm_infused_baseline_crossref.json](C:/projects/Hermes-Skills/Hermes Skills/research/generated/trm_infused_baseline_crossref.json)

## Target Environments

- `psycho_bench`
- `ascii_tree`
- `pydantic_adherence`

## Current Evidence Inputs

- [contract.md](C:/projects/Hermes-Skills/Hermes Skills/primehub-structured-map-hermes/references/contract.md)
- [design.md](C:/projects/Hermes-Skills/Hermes Skills/trm-mcp/references/design.md)
- [filesystem_example.md](C:/projects/Hermes-Skills/Hermes Skills/trm-mcp/references/filesystem_example.md)
- [bench_matrix.md](C:/projects/Hermes-Skills/Hermes Skills/trm-observability-workflow/references/bench_matrix.md)

## Planned Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\primehub-structured-map-hermes\scripts\build_skill_prompt.py" --env-name psycho_bench --role-mode critic_only
python "C:\projects\Hermes-Skills\Hermes Skills\trm-mcp\scripts\build_skill_prompt.py" --mcp-name primehub_schema --mode retrieve
python "C:\projects\Hermes-Skills\Hermes Skills\trm-mcp\scripts\build_primehub_schema_example.py" --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\artifacts\primehub_schema_pack"
python "C:\projects\Hermes-Skills\Hermes Skills\trm-mcp\scripts\build_mcp_trm_rows.py" --input "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\artifacts\primehub_schema_pack\primehub_schema_mcp_traces.jsonl" --out-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\artifacts\primehub_schema_pack\rows_rerun" --mcp-name primehub_schema
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\run_live_eval.py" --env-id psycho_bench --env-id pydantic_adherence --output-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\artifacts\live_eval_qwen35_9b_validator_patch"
python "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\run_live_eval.py" --env-id psycho_bench --env-id pydantic_adherence --output-dir "C:\projects\Hermes-Skills\Hermes Skills\research\studies\2026-04-22-primehub-structured-map-retrieval\artifacts\live_eval_qwen35_9b_after_env_fix"
```

## Artifact Contract

Store new outputs under:

- `research/studies/2026-04-22-primehub-structured-map-retrieval/artifacts/`
- expected first artifacts:
  - `structured_map_prompt.psycho_bench.txt`
  - `trm_mcp_prompt.retrieve.txt`
  - `schema_lookup_design.md`
  - `primehub_schema_pack/primehub_schema_surface.json`
  - `primehub_schema_pack/rows_rerun/mcp_trm_rows.summary.json`
  - `pydantic_validator_probe.md`
  - `pydantic_env_fix.md`
  - `live_eval_qwen35_9b/structured_map_live_eval.results.md`
  - `live_eval_qwen35_9b/findings.md`
  - `live_eval_qwen35_9b_validator_patch/findings.md`
  - `live_eval_qwen35_9b_after_env_fix/findings.md`
  - `live_eval_qwen35_9b_post_fix_3env.findings.md`

## Current Live Result

The first usable live comparison is the 9B run in [findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/artifacts/live_eval_qwen35_9b/findings.md):

- retrieval-assisted improved `ascii_tree` from `0.3943` baseline to `0.8`
- retrieval-assisted was slightly below baseline on `psycho_bench`
- all three arms remained at `0.0` on `pydantic_adherence`

The focused validator-aware rerun is in [live_eval_qwen35_9b_validator_patch/findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/artifacts/live_eval_qwen35_9b_validator_patch/findings.md):

- `psycho_bench` stayed effectively unchanged after the richer retrieval memory
- `pydantic_adherence` remained at `0.0` in all arms
- the zero on `pydantic_adherence` is now traced to the verifier path, not just a weak prompt

After the live env fix, the current best signal is in [live_eval_qwen35_9b_after_env_fix/findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/artifacts/live_eval_qwen35_9b_after_env_fix/findings.md):

- the live community scorer now validates `pydantic_adherence` with JSON-native semantics
- `retrieval_assisted` reaches `1.0` on `pydantic_adherence`
- baseline and plain structured-map still sit at `0.0`, which makes `pydantic_adherence` a useful discriminator again

The threaded `ascii_tree` rerun is in [live_eval_qwen35_9b_ascii_threaded/structured_map_live_eval.results.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/artifacts/live_eval_qwen35_9b_ascii_threaded/structured_map_live_eval.results.md), and the combined post-fix picture is summarized in [live_eval_qwen35_9b_post_fix_3env.findings.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/artifacts/live_eval_qwen35_9b_post_fix_3env.findings.md).

## Current State

The earlier verifier mismatch has been fixed in the live community env. See [pydantic_validator_probe.md](C:/projects/Hermes-Skills/Hermes Skills/research/studies/2026-04-22-primehub-structured-map-retrieval/artifacts/pydantic_validator_probe.md).

## Decision

Promote with scope limits.

What is promoted:

- `primehub-structured-map-hermes + trm-mcp` for exact-structure-sensitive lanes where schema selection is the main failure mode

What is not promoted:

- any claim that retrieval reduces token cost
- any claim that retrieval is universally better on all Primehub envs without further held slices

Primary evidence:

- `ascii_tree`: retrieval `0.8`, baseline `0.0`, plain structured-map `0.0`
- `psycho_bench`: retrieval `3.3311`, plain structured-map `3.3061`, baseline `3.3283`
- `pydantic_adherence`: retrieval `1.0`, baseline `0.0`, plain structured-map `0.0`

## Decision Boundary

Keep the promotion scoped unless later runs show a repeatable efficiency gain or the same adherence lift on additional held slices. `pydantic_adherence` can now be used again as a promotion signal, but only against the fixed JSON-native scorer.
