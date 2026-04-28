# Skill Research Brief

## Metadata

- Skill name: primehub-structured-map-hermes
- Track: task-skill
- Family: primehub
- Base contract version: Primehub-Structured-Map-v1
- TRM infusion type: retrieve
- Related overlay or workflow: trm-mcp; trm-observability-workflow
- Benchmark or environment family: psycho_bench; ascii_tree; pydantic_adherence
- Owner: Hermes Skills research
- Date: 2026-04-22

## Research Question

Can a retrieval-oriented TRM layer fetch the right schema or env-rule fragment early enough to reduce token and call cost without hurting exact structured output quality?

## Hypothesis

Structured-map tasks are a good fit for lookup-unit retrieval because the main failure mode is often selecting or preserving the wrong schema rule rather than generating long-form reasoning.

## Base Contract

Preserve the existing structured-map contract: detect the required schema, plan the keys or indices, emit only schema-conforming lines, verify structure, and return only the structured payload.

## TRM Intervention

Use `trm-mcp` as a schema lookup layer over a compact MCP-like surface of env rules, schema exemplars, and answer-shape descriptors. The retrieval layer should propose the minimal useful rule set before the structured-map prompt executes.

## Evidence Plan

- teacher trace source: Primehub structured-map replays plus any future schema-lookup traces captured through the observability harness
- row builder or data path: `scripts/run_primehub_trm_rollup.py` for baseline family traces; `trm-mcp/scripts/build_mcp_trm_rows.py` for route, retrieve, and verify supervision rows
- benchmark slice: `psycho_bench`, `ascii_tree`, and `pydantic_adherence`
- primary metric: exact schema-adherence success rate
- secondary metrics: first useful retrieval hit rate, average lookup calls, tokens loaded before first useful schema, malformed-line rate
- failure gates: lower exact adherence than plain structured-map baseline; retrieval near-misses that inject wrong schema; no measurable efficiency gain

## Promotion Rule

State the exact condition for:

- promote: retrieval keeps or improves exact schema adherence on meaningful held slices without introducing regressions on the other target envs. Efficiency gains are preferred but not required when the main win is exact structured validity.
- hold: exact adherence is preserved but the live win is too small, too inconsistent, or too expensive to justify rollout
- reject: schema adherence drops, wrong-schema retrievals recur, or the retrieval layer adds cost without benefit

## Notes

Treat `trm-mcp` as a schema-selection aid, not as a replacement for the final structured-map formatter.

## Current Decision

Promote with scope limits.

Scope:

- promote `primehub-structured-map-hermes + trm-mcp` for exact-structure-sensitive Primehub lanes
- use the fixed JSON-native `pydantic_adherence` scorer
- treat the current gain as a structure-validity win, not as a token-efficiency win

Reason:

- `ascii_tree`: retrieval-assisted `0.8` while non-retrieval arms failed in the threaded rerun
- `psycho_bench`: retrieval-assisted stayed slightly above plain structured-map and near baseline
- `pydantic_adherence`: retrieval-assisted reached `1.0` after the live scorer fix while baseline and plain structured-map remained at `0.0`
