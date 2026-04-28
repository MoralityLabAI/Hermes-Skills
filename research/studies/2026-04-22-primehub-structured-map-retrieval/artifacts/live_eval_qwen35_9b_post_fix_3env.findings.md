# Post-Fix 3-Env Snapshot

This note combines the post-fix `psycho_bench` and `pydantic_adherence` rerun with the threaded `ascii_tree` rerun.

Sources:

- `live_eval_qwen35_9b_after_env_fix/structured_map_live_eval.results.json`
- `live_eval_qwen35_9b_ascii_threaded/structured_map_live_eval.results.json`

## Reward Snapshot

- `ascii_tree`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `0.8`
- `psycho_bench`
  - baseline: `3.3283`
  - plain structured-map: `3.3061`
  - retrieval-assisted: `3.3311`
- `pydantic_adherence`
  - baseline: `0.0`
  - plain structured-map: `0.0`
  - retrieval-assisted: `1.0`

## Read

- `ascii_tree`: retrieval remained robust during a threaded run while the non-retrieval arms both failed formatting.
- `psycho_bench`: retrieval stayed near baseline and slightly ahead of plain structured-map.
- `pydantic_adherence`: after the scorer fix, retrieval produced a valid answer and the other two arms did not.

## Takeaway

The current evidence favors the retrieval-assisted lane across all three study envs. The strongest gains are now on exact structured validity, not just on lookup realism.
