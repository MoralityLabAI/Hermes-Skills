# Post-Fix Live Eval Findings

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

After fixing the live `pydantic_adherence` scorer to use JSON-native validation semantics, the retrieval-assisted arm reached `1.0` on `pydantic_adherence`. Baseline and plain structured-map remained at `0.0`.

## Reward Snapshot

- `psycho_bench`
  - baseline: `3.3283`
  - plain structured-map: `3.3061`
  - retrieval-assisted: `3.3311`
- `pydantic_adherence`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `1.0`

## Interpretation

- The earlier `pydantic_adherence` failure really was a verifier issue.
- Once the scorer was repaired, the retrieval memory became useful on that lane.
- The current retrieval prompt still costs more tokens, but it now buys an actual format-validity win rather than just extra context.
