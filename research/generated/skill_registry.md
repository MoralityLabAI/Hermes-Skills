# Hermes Skill Registry

Generated from `C:\projects\Hermes-Skills\Hermes Skills`.

## Summary

- Total skills: 17
- domain-research: 3
- meta-skill: 2
- task-skill: 9
- trm-operations: 1
- trm-overlay: 2

## Domain-Research

| Skill | Family | TRM Role | Pairings | Refs | Scripts |
| --- | --- | --- | --- | ---: | ---: |
| hermes-bluebeam-research | bluebeam | domain-probe-surface | trm-observability-workflow | 1 | 1 |
| metta-trm-hermes-pipeline | hermes | general-hermes-research | trm-observability-workflow | 0 | 18 |
| pixie-mechinterp | mechinterp | domain-probe-surface | trm-observability-workflow | 1 | 0 |

## Meta-Skill

| Skill | Family | TRM Role | Pairings | Refs | Scripts |
| --- | --- | --- | --- | ---: | ---: |
| metta-composition-hermes | metta-trm | trm-aware-skill-composition | metta-eval-optimizer-hermes, trm-observability-workflow, trm-mcp | 1 | 1 |
| metta-eval-optimizer-hermes | metta-trm | gate-circuit-eval-optimizer | trm-observability-workflow, trm-mcp | 1 | 1 |

## Task-Skill

| Skill | Family | TRM Role | Pairings | Refs | Scripts |
| --- | --- | --- | --- | ---: | ---: |
| intellect3-logic-hermes | intellect3 | candidate-for-routing-or-observability | trm-observability-workflow, trm-public-rationale-chain | 8 | 4 |
| intellect3-math-hermes | intellect3 | candidate-for-routing-or-observability | trm-observability-workflow, trm-public-rationale-chain | 8 | 4 |
| primehub-abstain-guard-hermes | primehub | candidate-for-trm-observability | trm-observability-workflow | 1 | 2 |
| primehub-choice-contract-hermes | primehub | candidate-for-trm-observability | trm-observability-workflow | 1 | 2 |
| primehub-constraint-summarize-hermes | primehub | candidate-for-trm-observability | trm-observability-workflow | 1 | 2 |
| primehub-hard-reasoning-logic-hermes | primehub | candidate-for-trm-observability | trm-observability-workflow, trm-public-rationale-chain | 1 | 2 |
| primehub-hard-reasoning-numeric-hermes | primehub | candidate-for-trm-observability | trm-observability-workflow | 1 | 2 |
| primehub-internal-action-hermes | primehub | candidate-for-trm-observability | trm-observability-workflow | 1 | 2 |
| primehub-structured-map-hermes | primehub | candidate-for-trm-observability | trm-observability-workflow, trm-mcp | 1 | 2 |

## Trm-Operations

| Skill | Family | TRM Role | Pairings | Refs | Scripts |
| --- | --- | --- | --- | ---: | ---: |
| trm-observability-workflow | trm | teacher-trace-to-training-loop | - | 5 | 2 |

## Trm-Overlay

| Skill | Family | TRM Role | Pairings | Refs | Scripts |
| --- | --- | --- | --- | ---: | ---: |
| trm-mcp | trm | retrieval-routing-layer | - | 4 | 9 |
| trm-public-rationale-chain | trm | bounded-public-trace-layer | - | 1 | 1 |

## Research Questions

- `hermes-bluebeam-research`: What domain-specific contract is stable enough to benchmark and later infuse with TRM?
- `intellect3-logic-hermes`: Does the Hermes contract or TRM routing beat the plain path on held Intellect-3 evidence?
- `intellect3-math-hermes`: Does the Hermes contract or TRM routing beat the plain path on held Intellect-3 evidence?
- `metta-composition-hermes`: Can TRM-infused Hermes skills be safely composed into MeTTa circuits without confusing critic, formatter, verifier, and action roles?
- `metta-eval-optimizer-hermes`: Can MeTTa gate circuits turn task-skill forks into better eval, curation, and TRM-training pipelines?
- `metta-trm-hermes-pipeline`: What measurable gain justifies the current general-hermes-research design?
- `pixie-mechinterp`: What observable structure can this skill surface before a stronger benchmark contract exists?
- `primehub-abstain-guard-hermes`: Does the Hermes contract improve exactness or stability on the named Primehub slice?
- `primehub-choice-contract-hermes`: Does the Hermes contract improve exactness or stability on the named Primehub slice?
- `primehub-constraint-summarize-hermes`: Does the Hermes contract improve exactness or stability on the named Primehub slice?
- `primehub-hard-reasoning-logic-hermes`: Does the Hermes contract improve exactness or stability on the named Primehub slice?
- `primehub-hard-reasoning-numeric-hermes`: Does the Hermes contract improve exactness or stability on the named Primehub slice?
- `primehub-internal-action-hermes`: Does the Hermes contract improve exactness or stability on the named Primehub slice?
- `primehub-structured-map-hermes`: Does the Hermes contract improve exactness or stability on the named Primehub slice?
- `trm-mcp`: Does TRM routing improve first useful MCP hit quality at lower token and call cost?
- `trm-observability-workflow`: Are the collected traces and row families strong enough to support training and benchmarking?
- `trm-public-rationale-chain`: Does a bounded public rationale help small-model quality without violating the task contract?
