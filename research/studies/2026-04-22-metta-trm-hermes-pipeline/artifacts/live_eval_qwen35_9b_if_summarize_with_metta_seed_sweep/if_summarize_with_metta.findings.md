# if_summarize_judge With-MeTTa Findings

This run keeps the new summarization skill fixed and changes only whether the model gets the compact MeTTa profile catalog.

## Reward Snapshot

- `without_metta`
  - seeds: `[7, 11, 19]`
  - episodes: `3`
  - reward_total: `1.0`
  - avg_reward: `0.3333333333333333`
  - profiles_seen: `{'exact_10w_bullets': 1, 'one_comma': 1, 'single_question': 1}`
- `with_metta_runtime`
  - seeds: `[7, 11, 19]`
  - episodes: `3`
  - reward_total: `2.0`
  - avg_reward: `0.6666666666666666`
  - profiles_seen: `{'exact_10w_bullets': 1, 'one_comma': 1, 'single_question': 1}`

## Read

- `with_metta_runtime` minus `without_metta` avg reward: `0.3333`.
- control sample actions: Welschbillig Castle is the ruin of a water castle in the municipality of Welschbillig in the county of Trier-Saarburg in the German state of Rhineland-Palatinate.; What is the main point of the text about Gudme?; - Munich Literary Prize awards ten thousand euros to winners. - Winners include authors like Erich Kästner and Lion Feuchtwanger.
- treatment sample actions: Welschbillig Castle is a ruin of a water castle in the municipality of Welschbillig, Germany.; What is the main point of the text about Gudme?; - The Munich Literature Prize awards ten thousand euros to Bavarian authors annually. - Winners include Hans Carossa in nineteen twenty-eight and Janosch in nineteen seventy-five.

## Takeaway

The compact MeTTa profile catalog improved average judged reward on this multi-episode slice.
