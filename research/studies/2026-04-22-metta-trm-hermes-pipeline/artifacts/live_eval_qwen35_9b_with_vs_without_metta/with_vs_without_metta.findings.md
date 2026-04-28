# With-MeTTa Vs Without-MeTTa Findings

This slice isolates the retrieval memory source while keeping the base structured-map prompt fixed.

## Reward Snapshot

- `psycho_bench`
  - without_metta: `3.328333333333333`
  - with_metta: `3.3033333333333332`
- `ascii_tree`
  - without_metta: `0.7999999999999999`
  - with_metta: `0.7999999999999999`
- `pydantic_adherence`
  - without_metta: `1.0`
  - with_metta: `1.0`

## Read

- `psycho_bench`: `with_metta` underperformed `without_metta` by `0.0250`.
- `ascii_tree`: `with_metta` matched `without_metta`.
- `pydantic_adherence`: `with_metta` matched `without_metta`.

## Takeaway

The non-MeTTa control remains stronger on this slice.
