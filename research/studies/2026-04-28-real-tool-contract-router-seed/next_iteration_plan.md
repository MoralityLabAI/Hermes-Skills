# Next Iteration Plan

## Finding

The seed benchmark shows schema and route-control lift, but not exact tool-call success.

| Arm | Exact | Contract | Tool Exact | Args Exact | Unsafe Commits |
| --- | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/36 | 0/36 | 22/36 | 0/36 | 2 |
| `pure_trm` | 3/36 | 25/36 | 30/36 | 3/36 | 2 |
| `metta_runtime` | 4/36 | 29/36 | 29/36 | 4/36 | 2 |
| `metta_runtime_repair` | 4/36 | 29/36 | 29/36 | 4/36 | 1 |

## Diagnosis

The model often selects the right tool family but invents repository paths, shell command templates, titles, or location strings. That means the next useful MeTTa/TRM layer is not another generic repair prompt; it is explicit schema-memory plus argument-normalization memory.

## V2 Additions

- Add `METTA_ALIAS_MEMORY` for canonical repository paths such as `research/studies`, `research/generated`, and paper-pack subpaths.
- Add `TRM_ARGUMENT_EXTRACT_LITERAL` to preserve literal strings from the user request instead of paraphrasing.
- Add `METTA_COMMAND_TEMPLATE_VALIDATE` for safe PowerShell command templates.
- Add `TRM_CLARIFY_OR_REJECT_ROUTE` for ambiguous scheduling and destructive shell requests.
- Score route-only and argument-exact metrics separately, with exact success as the final metric.

## Promotion Rule

Promote this lane only if the next run reaches zero unsafe commits and at least `12/36` exact success without reducing tool-route exactness below the current `29/36` MeTTa-runtime result.

## V2 Outcome

Alias V2 plus static safety meets the initial promotion rule on the `pure_trm_static_safety` arm: `14/36` exact, `30/36` tool-route exact, and `0` unsafe commits. This should be promoted as a bounded tool-router compactification lane, not as solved tool use.

The v3 promotion rule should be stricter: at least `20/36` exact, zero unsafe commits, and no regression below `30/36` tool-route exactness.

## V3 Outcome

Alias V3 compact retrieval clears the stricter promotion rule on raw live 3B outputs: `metta_runtime` and `metta_runtime_repair` reached `35/36` exact, `36/36` tool-route exact, and `0` unsafe commits. The deterministic V3 argument-canonicalizer then reached `36/36` exact with `0` unsafe commits over those same live outputs.

The next rule should shift from seed-suite promotion to generalization: freeze the V3 compiler, add held-out rows with unseen paraphrases and new aliases, and require at least `80%` exact after compiler with zero unsafe commits and no row-specific patching.
