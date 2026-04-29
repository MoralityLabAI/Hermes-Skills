# Alias V3 Findings

## Live Local 3B Compact Retrieval Result

Alias V3 changes the MeTTa/TRM pattern from "dump all memory into the prompt" to "retrieve one compact argument template for the current request." The run used the same 36 frozen rows and validators as the seed and V2 benchmarks.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/36 | 0/36 | 22/36 | 0/36 | 25/36 | 2 |
| `pure_trm` | 33/36 | 36/36 | 36/36 | 33/36 | 36/36 | 0 |
| `metta_runtime` | 35/36 | 36/36 | 36/36 | 35/36 | 36/36 | 0 |
| `metta_runtime_repair` | 35/36 | 36/36 | 36/36 | 35/36 | 36/36 | 0 |

Job-cap result: `success`; duration: `803.33s`; runner child RSS peak: `2374.68 MB` under the `3000 MB` cap.

## V3 Argument Canonicalizer

The deterministic V3 compiler applies prompt-visible argument templates over live model outputs. It handles final exactness issues such as PowerShell path slashes, missing shell metadata, clarification wording, city suffixes, title casing, and destructive/ambiguous safety overrides.

| Arm | Source Exact | After Argcanon | Tool Exact | Args Exact | Safety Exact | Unsafe Commits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pure_trm_v3_argcanon` | 33/36 | 36/36 | 36/36 | 36/36 | 36/36 | 0 |
| `metta_runtime_repair_v3_argcanon` | 35/36 | 36/36 | 36/36 | 36/36 | 36/36 | 0 |

## Interpretation

The important result is not just the perfect post-compiler score. The raw compact-retrieval live run already crossed the V3 promotion target by a large margin: `metta_runtime` and repair reached `35/36` exact with zero unsafe commits. The deterministic compiler then removes the last brittle formatting exactness errors.

This supports a stronger compactification claim than V2: for a bounded tool-contract environment, the LLM can act mostly as a rudder over retrieved symbolic templates, while MeTTa/TRM-style retrieval, schema memory, and commit gates carry most of the reliability burden.

## Boundary

- Allowed: report Alias V3 compact retrieval as live local 3B planned-call lift.
- Allowed: report V3 argcanon as deterministic compiler lift over live outputs.
- Not allowed: report the post-compiler `36/36` as raw LLM performance.
- Not allowed: claim general tool-use generalization until the compiler is frozen and tested on held-out tool-router rows.

## Next Step

Freeze the V3 compiler and build a held-out router suite with new tools, new path aliases, and unseen natural-language paraphrases. The target should be at least `80%` exact after compiler and zero unsafe commits without adding new row-specific templates.
