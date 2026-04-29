# Held-Out Alias V3 Findings

## Live Local 3B Result

This held-out suite keeps the same tool-call contract but changes the surface distribution: new aliases, unseen paraphrases, new shell templates, and new planned-tool schemas for tasks, notes, and browser-like actions.

| Arm | Exact | Contract | Tool Exact | Args Exact | Safety Exact | Unsafe Commits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `baseline` | 0/32 | 0/32 | 21/32 | 0/32 | 25/32 | 2 |
| `pure_trm` | 30/32 | 31/32 | 31/32 | 30/32 | 31/32 | 0 |
| `metta_runtime` | 31/32 | 32/32 | 32/32 | 31/32 | 32/32 | 0 |
| `metta_runtime_repair` | 31/32 | 32/32 | 32/32 | 31/32 | 32/32 | 0 |

Job-cap result: `success`; duration: `1412.44s`; runner child RSS peak: `2374.93 MB` under the `3000 MB` cap.

## Deterministic Argcanon Result

The same generic V3 compiler used on the seed suite was applied to the held-out live outputs.

| Arm | Source Exact | After Argcanon | Tool Exact | Args Exact | Safety Exact | Unsafe Commits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pure_trm_v3_argcanon` | 30/32 | 32/32 | 32/32 | 32/32 | 32/32 | 0 |
| `metta_runtime_repair_v3_argcanon` | 31/32 | 32/32 | 32/32 | 32/32 | 32/32 | 0 |

## Interpretation

This clears the held-out promotion rule: post-compiler exact success is `100%`, unsafe commits are `0`, and the raw compact-retrieval arms already exceed the `80%` target. The remaining raw misses were narrow exactness failures: one Windows path slash variant and one clarification wording variant.

The useful claim is now stronger than the seed result: compact retrieved symbolic templates transfer to a held-out tool-contract suite with new tools. The bounded claim remains important: this is planned-call correctness, not actual external tool execution.

## Next Step

Freeze this compiler version and make the next suite adversarial: same schemas, but paraphrases designed not to contain the obvious alias words. That is the real test of whether retrieval can be semantic rather than phrase-triggered.
