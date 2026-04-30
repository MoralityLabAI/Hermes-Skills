# MeTTa Ablation Decision

## Decision

Promote the enriched MeTTa treatment narrowly for continued Hermes skills research. Do not treat it as the global default yet.

## Benchmark Sequence

First run, using the thinner compiled packet:

- `psycho_bench`
  - `without_metta`: `3.3283`
  - `with_metta`: `3.3033`
- `ascii_tree`
  - `without_metta`: `0.8`
  - `with_metta`: `0.8`
- `pydantic_adherence`
  - `without_metta`: `1.0`
  - `with_metta`: `1.0`

Richer packet rerun, after adding stronger env-specific fields and matching the control prompt scaffold:

- `psycho_bench`
  - `without_metta`: `3.3283`
  - `with_metta`: `3.3311`
- `ascii_tree`
  - `without_metta`: `0.8`
  - `with_metta`: `0.8`
- `pydantic_adherence`
  - `without_metta`: `1.0`
  - `with_metta`: `1.0`

## Read

- The MeTTa path is now genuinely benchmark-competitive, not just structurally valid.
- The critical fix was not more generic symbolic machinery. It was richer env-specific contract atoms plus a cleaner A/B prompt shape.
- The current improvement is narrow. Only `psycho_bench` moved, and the gain is small.

## Remaining Cost

The MeTTa arm used more prompt tokens on the richer rerun:

- `psycho_bench`: `1459` total vs `1399`
- `ascii_tree`: `873` total vs `806`
- `pydantic_adherence`: `1822` total vs `1748`

So this is a correctness and maintainability win first. It is not yet a cost-efficiency win.

## Next Iteration

- run a wider held slice beyond these three envs before calling it a default overlay
- trim prompt verbosity while preserving the richer symbolic fields that fixed `psycho_bench`
- test whether some compiled fields should stay in retrieval memory while others move into offline row generation instead of runtime injection
