# Noisy Camp-Gate Graph Router Script

Generated: `2026-04-29T19:04:35.887491+00:00`

Evidence class: `no_model_prompt_constraint_graph_router`

This control parses only prompt-visible dimensions, anchors, row quotas, and column quotas, then uses the same public solver as the local 3B extraction benchmark.

## Arm Summary

| Arm | Rows | Packet Valid | Packet Exact | Solve Exact | Solve Rate | Avg Cell Acc |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `canonical_packet_solver` | 12 | 12 | 12 | 12 | 1.0000 | 1.0000 |
| `metta_graph_router_script` | 12 | 12 | 12 | 12 | 1.0000 | 1.0000 |

## Failures

No graph-router failures.

## Method Read

- `metta_graph_extract` shows how far a 3B can go when the prompt frames extraction as gates.
- `metta_graph_router_script` shows the threshold where typed script gates can own extraction and make the LLM optional for execution.
- This does not claim trained TRM lift; it marks candidate gates for future TRM data collection.
