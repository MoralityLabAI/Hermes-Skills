# Claim Audit

## Evidence Class

`no_model_validator_smoke`

`live_model_local_3b`

The seed smoke is an artifact-contract test for rows, validators, configs, and result schema.

The local Qwen2.5-3B Q4 seed run is a small live-model test on all 12 seed rows. It is still a seed smoke, not the final held-out benchmark.

## Allowed Claim

- The generated rows and validators can separate contract validity from semantic validity across mixed contract families.
- The 12-row local 3B seed run shows baseline `5/12`, pure TRM prompt `6/12`, MeTTa runtime `6/12`, and MeTTa runtime repair-prompt `8/12` exact success.
- The repair-prompt arm can be described as live-model repair gating over public validator feedback.

## Disallowed Claims

- Do not claim final benchmark improvement from the 12-row seed smoke.
- Do not claim TRM training lift.
- Do not claim small-model reasoning improvement.
- Do not mix this deterministic repair smoke with live model columns.
- Do not treat prompt-only MeTTa as a positive result on this seed slice; it tied baseline on exact rate.

## Next Evidence Upgrade

The next run should replace the seed with a held-out 50-row mixed-contract suite before reporting paper-level results.
