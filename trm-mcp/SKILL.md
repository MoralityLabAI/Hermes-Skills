---
name: trm-mcp
description: "Use when designing or applying TRM workflows over any MCP server or resource set, especially to optimize lookup efficiency, index quality, routing, and low-token retrieval over large MCP surfaces instead of relying on raw long-context reasoning."
---

# TRM-MCP

Use this skill when the problem is better solved by training or applying TRMs over an MCP surface than by repeatedly scanning raw resources.

This skill is for:

- MCP resource indexing
- lookup and retrieval workflows
- low-token routing over large MCP surfaces
- TRM training rows built from MCP queries, hits, misses, and repair outcomes
- efficiency optimization where the goal is fewer tool calls, fewer loaded tokens, and better first-hit retrieval

## Local references

- Design pattern: `references/design.md`
- Popular example: `references/filesystem_example.md`
- Popular example: `references/github_example.md`
- Popular example: `references/postgres_example.md`

## Local scripts

- `scripts/build_skill_prompt.py`
- `scripts/build_mcp_trm_rows.py`
- `scripts/extract_codex_mcp_traces.py`
- `scripts/build_filesystem_example.py`
- `scripts/build_github_example.py`
- `scripts/build_postgres_example.py`
- `scripts/build_primehub_schema_example.py`
- `scripts/build_example_matrix.py`

## Core idea

Treat an MCP as a structured memory surface:

1. enumerate resources, templates, and stable handles
2. derive lookup units, not just raw documents
3. train TRMs on index, route, retrieve, and verify tasks
4. optimize for `hit quality / token cost / call count / latency`

Do not train one vague general TRM over the whole MCP if the lookup surface is heterogeneous. Prefer specialist TRMs by resource family or query shape.

## TRM-MCP flow

Follow the `TRM_MCP_INDEX -> TRM_MCP_ROUTE -> TRM_MCP_RETRIEVE -> TRM_MCP_VERIFY -> FINAL` flow:

1. `TRM_MCP_INDEX`
   Normalize the MCP surface into lookup rows:
   - resource URI
   - template parameters
   - title or label
   - short semantic summary
   - stable query cues
   - expected answer shape

2. `TRM_MCP_ROUTE`
   Predict which MCP family should be queried first:
   - resource list
   - resource template
   - direct read
   - follow-up find or grep
   - no lookup needed

3. `TRM_MCP_RETRIEVE`
   Retrieve the best resource, URI, template, or exemplar lookup action.
   Optimize for first useful hit, not exhaustive recall.

4. `TRM_MCP_VERIFY`
   Check that the chosen resource actually matches the question, scope, and answer contract.
   Reject near-misses early.

5. `FINAL`
   Execute the minimal MCP action path or emit the minimal lookup plan.

## Training rules

- Train index TRMs on resource descriptors, not full raw payloads.
- Train router TRMs on query-to-family decisions.
- Train retriever TRMs on exact useful URI or template hits.
- Train verifier TRMs on hard negatives:
  - right family, wrong resource
  - right resource, wrong parameterization
  - semantically close but scope-mismatched
- Keep rows short. If a row needs the full raw document, the representation is wrong.

## Efficiency objective

Score systems on:

- correct first-hit rate
- average MCP calls per solved task
- average tokens loaded before the first useful answer
- latency to first useful resource
- abstain or escalate quality when the MCP surface is weak

Prefer a slightly lower recall system if it materially reduces token load and call count while preserving downstream success.

## Design rules

- Split by MCP family when schemas differ materially.
- Prefer lookup-key prediction over answer-string memorization.
- Cache stable handles and template arguments when they recur.
- Train on failure traces, not only successes.
- Use verifier TRMs to kill seductive near-misses before they waste long-context budget.
- If the MCP surface changes frequently, retrain index or verifier layers first.

## When not to use this skill

- When the MCP surface is tiny and direct scanning is cheaper.
- When the task needs deep synthesis over a small number of already-known resources.
- When the bottleneck is answer generation quality rather than lookup efficiency.

## Operational rule

Use `scripts/build_skill_prompt.py --mcp-name ... --mode ...` when you want a compact runtime prompt for the current MCP lookup role.

Use `scripts/build_mcp_trm_rows.py --input ... --out-dir ...` when you need to turn MCP lookup traces into TRM-ready route, retrieve, and verify rows.

Use `scripts/extract_codex_mcp_traces.py --input ... --out-dir ...` when you need to mine real MCP tool-call traces out of Codex session JSONL before building TRM rows.

Use `scripts/build_filesystem_example.py --out-dir ...` when you need a concrete, popular `filesystem` MCP example pack with realistic traces plus built TRM rows.

Use `scripts/build_github_example.py --out-dir ...` when you need a concrete, popular `github` MCP example pack with issue, PR, and code-search retrieval rows.

Use `scripts/build_postgres_example.py --out-dir ...` when you need a concrete, popular `postgres` MCP example pack with schema, table, and query-template retrieval rows.

Use `scripts/build_primehub_schema_example.py --out-dir ...` when you need a Primehub-specific schema lookup pack for structured-map tasks such as `psycho_bench`, `ascii_tree`, and `pydantic_adherence`.

Use `scripts/build_example_matrix.py --out-dir ...` when you want all bundled popular examples built together plus one merged TRM-MCP corpus.
