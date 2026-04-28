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
  - reward_total: `1.0`
  - avg_reward: `0.3333333333333333`
  - profiles_seen: `{'exact_10w_bullets': 1, 'one_comma': 1, 'single_question': 1}`
- `with_metta_runtime_repair`
  - seeds: `[7, 11, 19]`
  - episodes: `3`
  - reward_total: `3.0`
  - avg_reward: `1.0`
  - profiles_seen: `{'exact_10w_bullets': 1, 'one_comma': 1, 'single_question': 1}`
  - env_info_samples: `[{'constraint': 'Write a one-sentence summary of the following text that contains exactly one comma. Write only the sentence, nothing else.', 'constraint_type': 'one_comma', 'judge_score': 1.0, 'judge_response': 'FASTPATH one_comma commas=1'}, {'constraint': 'Summarize the following text as a single question that captures its main point. Write only the question, nothing else.', 'constraint_type': 'single_question', 'judge_score': 1.0, 'judge_response': 'FASTPATH single_question sentences=1'}, {'constraint': 'Summarize the following text in exactly 2 bullet points. Each bullet must be exactly 10 words. Write only the bullet points, nothing else.', 'constraint_type': 'exact_10w_bullets', 'judge_score': 1.0, 'judge_response': 'FASTPATH exact_10w_bullets counts=[10, 10]'}]`

## Read

- `with_metta_runtime` minus `without_metta` avg reward: `0.0000`.
- `with_metta_runtime_repair` minus `with_metta_runtime` avg reward: `0.6667`.
- control sample actions: Welschbillig Castle is the ruin of a water castle in the municipality of Welschbillig in the county of Trier-Saarburg in the German state of Rhineland-Palatinate.; What is the main point of the text about Gudme?; - Munich literary prize offers ten thousand euros cash award. - Winners include famous authors like Erich Kästner and Lion Feuchtwanger.
- treatment sample actions: Welschbillig Castle is a ruin of a water castle in the municipality of Welschbillig in the county of Trier-Saarburg.; What is the main point of the text about Gudme?; - The Munich Literature Prize awards ten thousand euros to Bavarian authors annually. - Winners include Hans Carossa in 1928 and Christine Wunnicke in 2020.
- repair sample actions: Welschbillig Castle rose over Roman remains, and later wars left it a ruin.; What is the main point of the text about Gudme?; - The Munich Literature Prize awards ten thousand euros to Bavarian.
- Winners include Hans Carossa in 1928 and Christine Wunnicke in.
- repair-applied seeds: 7, 19

## Takeaway

The compact MeTTa runtime packet matched control on this rerun, and deterministic repair cleared the remaining structural misses.
