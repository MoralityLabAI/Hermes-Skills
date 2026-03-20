# Run Telemetry Standard

Use this format for Hermes-style training and benchmark runs.

## Required Fields

- `run_id`
- `phase`
- `step`
- `data_source`
- `ram_budget`
- `eta`
- `percent_complete`
- `progress_bar`
- `current_anchor`
- `current_train`
- `current_gap`
- `best_anchor`
- `best_train`
- `best_gap`

## Output Rules

- Print a compact card at run start.
- Print the card again after each meaningful stage or candidate.
- Keep the card stable across runs.
- Prefer `auto` over blank for unknown RAM budgets.
- Prefer `estimating` over blank for ETA.
- Use a short ASCII bar like `[######----]`.
- Keep the card small enough to tail live in Hermes UI or a terminal.
