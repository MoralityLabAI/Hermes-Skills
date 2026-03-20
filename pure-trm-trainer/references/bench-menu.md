# TRM Bench Menu

Use these named benches when you want to compare TRM controller behavior across fixed evaluation slices.

## Active Benches

| Name | Purpose | Source | Launcher | Watcher |
| --- | --- | --- | --- | --- |
| `trm-routerBench` | Persistent-tesseract slice; generalization search over a fixed anchor set | `persistent-tesseract` | `scripts/run_trm_bench.py --bench routerbench` | `scripts/watch_trm_routerbench.py` |
| `trm-primeHubEnvs` | Reasoning-intensive subset of PrimeHub envs | `primehub-reasoning-subset` | `scripts/run_trm_bench.py --bench primehub-envs` | `scripts/watch_trm_routerbench.py --run-dir <run_dir>` |
| `trm-primeHubBaseline` | PrimeHub env slice with explicit baseline-vs-router comparison fields | `primehub-reasoning-subset-vs-baseline` | `scripts/run_trm_bench.py --bench primehub-baseline` | `scripts/watch_trm_routerbench.py --run-dir <run_dir>` |

## Adding A New Bench

1. Add a new spec file in `references/`.
2. Give it a stable `run_id`.
3. Set `data_source` and `anchor_set` explicitly.
4. Add the bench name to `scripts/run_trm_bench.py`.
5. Add the bench row to this table.
6. Keep the status card contract unchanged.
