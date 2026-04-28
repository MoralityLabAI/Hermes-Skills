# Symbolic Closure Threshold Suite

Generated: `2026-04-26T15:15:45.702130+00:00`

This deterministic eval asks when a MeTTa/TRM circuit can make the LLM an idea spinner rather than the executor. It uses synthetic proposal tiers and no model calls, so it should be read as a control-plane threshold test, not a live benchmark.

## Aggregate

| Env family | Scale class | LLM direct avg | MeTTa/TRM circuit avg | Min exact circuit tier | Read |
| --- | --- | ---: | ---: | --- | --- |
| `ascii_tree_deep` | `symbolically_closed_if_nodes_present` | 0.4979 | 0.5729 | `partial_semantic` | Exact formatting can be circuit-owned once the proposal contains the complete node set. |
| `choice_contract` | `symbolically_closed` | 0.2500 | 0.5000 | `partial_semantic` | The LLM only needs to expose a recoverable label; execution is contract extraction. |
| `intellect3_camp_gate` | `symbolically_amplifiable` | 0.6406 | 0.6719 | `partial_semantic` | A plausible grid with the right symbolic signature can be projected to the canonical gate solution. |
| `math_answer_search` | `scale_sensitive_boundary` | 0.2500 | 0.2500 | `full_candidate` | Without an exact candidate or a separate solver, the circuit cannot create the missing answer. |
| `tool_contract_router` | `symbolically_closed` | 0.2500 | 0.5000 | `partial_semantic` | Intent plus schema atoms are enough for the circuit to repair arguments and commit exact JSON. |

## Tier Detail

| Env | Tier | Direct | Circuit | Circuit note | Gate |
| --- | --- | ---: | ---: | --- | --- |
| `ascii_tree_deep` | `full_candidate` | 1.0000 | 1.0000 | exact_tree | `node_list_to_canonical_tree` |
| `ascii_tree_deep` | `none` | 0.0583 | 0.0583 | partial_tree | `node_list_to_canonical_tree` |
| `ascii_tree_deep` | `partial_semantic` | 0.7000 | 1.0000 | exact_tree | `node_list_to_canonical_tree` |
| `ascii_tree_deep` | `weak_surface` | 0.2333 | 0.2333 | partial_tree | `node_list_to_canonical_tree` |
| `choice_contract` | `full_candidate` | 1.0000 | 1.0000 | exact | `choice_token_extract` |
| `choice_contract` | `none` | 0.0000 | 0.0000 | mismatch | `choice_token_extract` |
| `choice_contract` | `partial_semantic` | 0.0000 | 1.0000 | exact | `boxed_choice_extract` |
| `choice_contract` | `weak_surface` | 0.0000 | 0.0000 | mismatch | `choice_token_extract` |
| `intellect3_camp_gate` | `full_candidate` | 1.0000 | 1.0000 | exact_grid | `camp_signature_min_edit_projection` |
| `intellect3_camp_gate` | `none` | 0.0000 | 0.0000 | grid_shape_failure | `camp_signature_min_edit_projection` |
| `intellect3_camp_gate` | `partial_semantic` | 0.8750 | 1.0000 | exact_grid | `camp_signature_min_edit_projection` |
| `intellect3_camp_gate` | `weak_surface` | 0.6875 | 0.6875 | partial_grid | `camp_signature_min_edit_projection` |
| `math_answer_search` | `full_candidate` | 1.0000 | 1.0000 | exact | `exact_candidate_select` |
| `math_answer_search` | `none` | 0.0000 | 0.0000 | mismatch | `exact_candidate_select` |
| `math_answer_search` | `partial_semantic` | 0.0000 | 0.0000 | mismatch | `exact_candidate_select` |
| `math_answer_search` | `weak_surface` | 0.0000 | 0.0000 | mismatch | `exact_candidate_select` |
| `tool_contract_router` | `full_candidate` | 1.0000 | 1.0000 | exact_json | `intent_schema_arg_repair` |
| `tool_contract_router` | `none` | 0.0000 | 0.0000 | json_parse_failure | `intent_schema_arg_repair` |
| `tool_contract_router` | `partial_semantic` | 0.0000 | 1.0000 | exact_json | `intent_schema_arg_repair` |
| `tool_contract_router` | `weak_surface` | 0.0000 | 0.0000 | json_parse_failure | `intent_schema_arg_repair` |

## Interpretation

- The compactification threshold is low for tool routing and choice contracts: partial symbolic atoms are enough for exact execution.
- Structure tasks become compactifiable once the proposal contains complete observable atoms, even if formatting is wrong.
- Logic-grid tasks are amplifiable when signatures constrain the repair manifold.
- Raw math remains the boundary case: without an exact candidate or external solver, the circuit cannot synthesize the missing answer.

## Resource Profile

- Model calls: `0`
- Runtime profile: `deterministic Python-only pass; no model or training subprocess`
