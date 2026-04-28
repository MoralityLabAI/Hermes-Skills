# Live Eval Findings

Model:

- `qwen35_9b`
- endpoint: `http://snacksack-ms-7d32.tail3156cd.ts.net:8082/v1`

Arms:

- `baseline`
- `plain_structured_map`
- `retrieval_assisted`

## Outcome

The retrieval-assisted arm produced a real gain on `ascii_tree`, a small regression against the baseline on `psycho_bench`, and no gain on `pydantic_adherence`.

## Reward Snapshot

- `psycho_bench`
  - baseline: `3.3483`
  - plain structured-map: `3.3033`
  - retrieval-assisted: `3.3283`
- `ascii_tree`
  - baseline: `0.3943`
  - plain structured-map: `0.0`
  - retrieval-assisted: `0.8`
- `pydantic_adherence`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `0.0`

## Interpretation

- The added schema memory helps when the main failure mode is selecting or preserving the right output shape, as in `ascii_tree`.
- The same retrieval context is not automatically helpful on `psycho_bench`, where the baseline already follows the numbered line contract reasonably well.
- `pydantic_adherence` still needs stronger schema-specific repair or validator-aware prompting. Retrieval alone is not enough.

## Operational Note

The earlier `qwen35_27b` live run was not usable because the endpoint produced timeouts or HTTP 500 errors across the study tasks. The 9B run is the first usable live comparison.
