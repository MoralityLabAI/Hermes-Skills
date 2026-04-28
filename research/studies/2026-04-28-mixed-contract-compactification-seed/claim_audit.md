# Claim Audit

## Evidence Class

`no_model_validator_smoke`

This study does not contain live model calls. It is an artifact-contract test for rows, validators, configs, and result schema.

## Allowed Claim

The generated rows and validators can separate contract validity from semantic validity across mixed contract families.

## Disallowed Claims

- Do not claim benchmark improvement.
- Do not claim TRM training lift.
- Do not claim small-model reasoning improvement.
- Do not mix this deterministic repair smoke with live model columns.

## Next Evidence Upgrade

The next run should be a local 3B `live_model` or `replay_from_live_log` result over the same row IDs, with the same validator script and arm names.
