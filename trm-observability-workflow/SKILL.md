---
name: trm-observability-workflow
description: "Use when you need to bootstrap the harness repo, collect teacher traces, turn them into TRM rows, merge corpora, or rerun logic/math TRM training and benchmarks."
---

# TRM Observability Workflow

Use this skill when you need the full loop:

1. sync or clone the harness repo
2. collect teacher-model traces
3. convert traces into TRM row format
4. merge corpora and apply family floors
5. train or benchmark logic/math TRM components

## Local references

- Workflow guide: `references/workflow.md`
- Row format guide: `references/row_format.md`
- Benchmark matrix: `references/bench_matrix.md`
- Harness notes: `references/harness_notes.md`
- Snapshot manifest: `references/snapshot_manifest.json`

## Local scripts

- `scripts/show_workflow.py`
- `scripts/bootstrap_harness.py`

## Workflow

### 1. Bootstrap the harness

- Prefer the local checkout path from `TRM_HARNESS_ROOT` when it exists.
- Otherwise use the snapshot manifest in this skill tree to recover the
  expected repo layout and artifacts.
- Confirm the repo has the collector, row builder, merger, trainer, and bench
  scripts before starting a run.

### 2. Collect teacher traces

- Pick the env family first: logic, math, storyworld, or a collector-only
  replay family.
- Run the teacher model with the harness config for that family.
- Keep the trace contract bounded and environment-aware.
- Export the replay JSONL and summarize it immediately.

### 3. Build rows

- Convert the replay JSONL into TRM training rows.
- Keep exact positives, negatives, route labels, and family labels.
- Drop weak families until they clear the minimum exact-positive floor.

### 4. Merge corpora

- Merge only families that are strong enough for the current corpus.
- Keep the family floor strict enough to avoid contaminating training with
  signal-poor batches.
- Recompute summary counts after every merge.

### 5. Train and bench

- Train retriever, critic, router, and correction components separately.
- Bench each component on held rows before promoting it.
- For logic, treat exact Campsite signatures as the current strongest route
  signal.
- For math, treat the support pattern as advisory until the router shows a
  stable gain on a larger slice.

## Decision rules

- If collection is weak, fix the collector first.
- If rows are noisy, fix the row builder before training.
- If retriever or critic underperform, do not widen the corpus yet.
- If the router is unstable, use a simpler rule before trying a learned gate.
- If a component wins on a small slice, validate it on a larger held-out slice
  before calling it a generalization.
