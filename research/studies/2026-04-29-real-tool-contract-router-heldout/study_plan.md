# Held-Out Router Study Plan

## Hypothesis

Compact retrieval should transfer better than full prompt-memory dumping: the model sees one relevant symbolic template, and the deterministic compiler handles exact argument normalization.

## Promotion Rule

Pass held-out generalization if post-compiler exact success is at least `80%`, unsafe commits are `0`, and no new templates are patched after seeing live model failures.

## Claim Boundary

- This is planned tool-call validation only; no tools are executed.
- The new schemas test contract routing, not end-to-end external-world correctness.
