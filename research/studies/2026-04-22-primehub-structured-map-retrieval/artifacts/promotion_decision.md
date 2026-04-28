# Promotion Decision

## Decision

Promote with scope limits.

## Promotion Scope

- Promote `primehub-structured-map-hermes + trm-mcp` for exact-structure-sensitive Primehub lanes.
- Use the fixed JSON-native scorer for `pydantic_adherence`.
- Treat the current result as a structured-validity promotion, not an efficiency promotion.

## Evidence

- `ascii_tree`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `0.8`
- `psycho_bench`
  - baseline: `3.3283`
  - plain structured-map: `3.3061`
  - retrieval-assisted: `3.3311`
- `pydantic_adherence`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `1.0`

## Why This Is Not A Full Rollout

- token cost still increases on the retrieval-assisted arm
- the held slice is still small
- the strongest wins are on exact format validity, not on lookup efficiency

## Operational Rule

- default to the retrieval-assisted lane when the task is schema-fragile and exact output structure matters
- keep plain structured-map available for comparison runs
- keep measuring cost separately before claiming retrieval is the cheaper path
