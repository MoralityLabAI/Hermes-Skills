# Workflow

This skill packages the end-to-end TRM observability loop.

## Phase 1: Get the harness

1. Use the local checkout if `TRM_HARNESS_ROOT` is already set.
2. If not, recover the expected repo layout from `references/snapshot_manifest.json`.
3. Verify the harness root contains the runner, row builder, merger, trainer,
   and benchmark scripts.

## Phase 2: Collect traces

1. Pick the teacher family and the env family.
2. Run the teacher model through the harness.
3. Export the replay JSONL.
4. Summarize the run immediately.

## Phase 3: Build row data

1. Convert the replay JSONL into TRM rows.
2. Preserve the exact-positive flag, family label, route label, and action
   target.
3. Keep the row format narrow and deterministic.

## Phase 4: Merge corpora

1. Merge only families that clear the minimum exact-positive floor.
2. Do not contaminate the main training corpus with weak batches.
3. Recompute the merged corpus summary after every change.

## Phase 5: Train and bench

1. Train retriever, critic, router, and correction components separately.
2. Bench each component on held rows.
3. Promote a component only if it improves held-out exact match or route
   choice.

## Phase 6: Generalize

1. Start with logic if you want the cleanest routing signal.
2. Move to math only after the logic contract is stable.
3. Expand to other families only after the row format and merge floor are
   holding.
