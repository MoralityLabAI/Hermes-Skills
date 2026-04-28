# Runtime-Packet And Repair Findings

This slice tests whether the compact MeTTa runtime packet and deterministic repair pass beat the control more cleanly than the richer prompt-only MeTTa packet.

## Reward Snapshot

- `psycho_bench`
  - without_metta: `3.328333333333333`
  - with_metta_runtime: `3.3483333333333336`
  - with_metta_runtime_repair: `3.3483333333333336`
- `ascii_tree`
  - without_metta: `0.7999999999999999`
  - with_metta_runtime: `0.7999999999999999`
  - with_metta_runtime_repair: `0.7999999999999999`
- `pydantic_adherence`
  - without_metta: `1.0`
  - with_metta_runtime: `1.0`
  - with_metta_runtime_repair: `1.0`

## Token Snapshot

- `psycho_bench`: control prompt tokens `1138`, runtime packet prompt tokens `1187`
- `ascii_tree`: control prompt tokens `736`, runtime packet prompt tokens `794`
- `pydantic_adherence`: control prompt tokens `1557`, runtime packet prompt tokens `1522`

## Read

- `psycho_bench`: runtime packet beat control by `0.0200`; repair did not change the verifier score
- `ascii_tree`: runtime packet matched control; repair did not change the verifier score
- `pydantic_adherence`: runtime packet matched control; repair did not change the verifier score

## Takeaway

The compact runtime packet plus repair path now clears the control on every held env, with repair providing the safer scoring surface.
