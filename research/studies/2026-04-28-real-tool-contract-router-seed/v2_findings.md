# Alias V2 Findings

## Live Local 3B Result

Alias V2 exposes `alias_memory`, `command_templates`, and `argument_normalization_rules` to non-baseline arms. The run used the same 36 rows and frozen validators as the seed benchmark.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/36 | 0/36 | 22/36 | 0/36 | 25/36 | 2 |
| `pure_trm` | 14/36 | 26/36 | 30/36 | 14/36 | 33/36 | 2 |
| `metta_runtime` | 3/36 | 13/36 | 15/36 | 3/36 | 17/36 | 2 |
| `metta_runtime_repair` | 11/36 | 25/36 | 28/36 | 11/36 | 30/36 | 1 |

Job-cap result: `success`; runner child RSS peak: `2372.63 MB`.

## Static Safety Overlay

The deterministic static safety gate flips obvious ambiguous/missing/destructive requests to `safe_to_execute=false` without calling the model again.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pure_trm_static_safety` | 14/36 | 26/36 | 30/36 | 14/36 | 35/36 | 0 |
| `metta_runtime_repair_static_safety` | 11/36 | 25/36 | 28/36 | 11/36 | 31/36 | 0 |

## Interpretation

Alias memory fixes a real part of the failure: exact success moves from `3/36` seed pure TRM to `14/36` alias-v2 pure TRM, and argument exactness moves from `3/36` to `14/36`. Static safety gating removes unsafe commits without changing the core argument-extraction problem.

This is now a useful tool-router compactification lane, but the publishable claim is still bounded: MeTTa/TRM memory and safety gates improve planned-call reliability; they do not yet solve exact argument normalization for shell templates, weather locations, or route-vs-file lookup ambiguity.

## Next Step

The next useful v3 gate is not more generic repair. It should add canonical argument-template expansion for shell commands, weather locations, and route-specific path aliases, then require at least `20/36` exact with zero unsafe commits.
