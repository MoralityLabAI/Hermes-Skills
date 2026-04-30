# MeTTa Multi-Signal Rollup

## Scope

This note compares the first two MeTTa bundles after compiling them into a multi-signal TRM scorecard instead of a single scalar reward lane.

## Structured Map Bundle

Source:

- `artifacts/primehub_structured_map_multisignal/metta_multi_signal_scorecard.summary.json`

Observed density:

- units: `12`
- signal targets: `63`
- average signals per unit: `5.25`
- label density vs single-reward baseline: `5.25x`

Main signal mix:

- selection: `6`
- success: `18`
- critic: `6`
- repair: `9`
- transport: `24`

Read:

- even the flat three-env structured-map lane is not really a one-label problem
- one synthetic training unit can carry selection, validity, critic, repair, and transport labels at the same time

## Constraint Summarization Bundle

Source:

- `artifacts/if_summarize_judge_multisignal/metta_multi_signal_scorecard.summary.json`

Observed density:

- units: `72`
- signal targets: `446`
- average signals per unit: `6.19`
- label density vs single-reward baseline: `6.19x`

Main signal mix:

- selection: `104`
- success: `108`
- critic: `36`
- repair: `54`
- transport: `144`

Read:

- profile-heavy envs benefit much more from MeTTa as a supervision compiler than flat envs do
- the main gain is not just more rows, but more orthogonal labels per row family

## Current Take

The realistic near-term upside from MeTTa is not "one huge benchmark jump." It is:

- denser TRM supervision from the same symbolic package
- cleaner separation of selection, verification, repair, and transport signals
- easier role-wise training instead of forcing everything into one reward channel

For the current bundles, MeTTa raised the available supervision surface from `1` scalar target per unit to roughly `5-6` labeled targets per unit.
