# if_summarize_judge With-MeTTa Findings

This run keeps the new summarization skill fixed and changes only whether the model gets the compact MeTTa profile catalog.

## Reward Snapshot

- `without_metta`
  - episodes: `3`
  - reward_total: `0.0`
  - avg_reward: `0.0`
  - profiles_seen: `{'one_comma': 3}`
- `with_metta_runtime`
  - episodes: `3`
  - reward_total: `0.0`
  - avg_reward: `0.0`
  - profiles_seen: `{'one_comma': 3}`

## Read

- `with_metta_runtime` minus `without_metta` avg reward: `0.0000`.
- control sample actions: Welschbillig Castle is the ruin of a water castle in the municipality of Welschbillig in the county of Trier-Saarburg in the German state of Rhineland-Palatinate.; Welschbillig Castle is the ruin of a water castle in the municipality of Welschbillig in the county of Trier-Saarburg in the German state of Rhineland-Palatinate.; Welschbillig Castle is the ruin of a water castle in the municipality of Welschbillig in the county of Trier-Saarburg in the German state of Rhineland-Palatinate.
- treatment sample actions: Welschbillig Castle is a ruin of a water castle in the municipality of Welschbillig in the county of Trier-Saarburg.; Welschbillig Castle is a ruin of a water castle in the municipality of Welschbillig, Germany.; Welschbillig Castle is a ruin of a water castle in the municipality of Welschbillig, Germany.

## Takeaway

The MeTTa catalog matched the base summarization skill on this slice.
