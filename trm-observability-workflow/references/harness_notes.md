# Harness Notes

These are the key operational facts the workflow should remember.

## Collection

- The harness exports structured replays for downstream TRM training.
- Teacher-model collection is more useful when the trace contract is bounded.
- Logic and math should not share the same action contract.

## Training

- Retrieval is usually the weakest starting point.
- Critic and heuristic correction are often the first useful gains.
- Merge floors keep weak families out of the main corpus.

## Benchmarking

- Logic gains should be judged on held Campsite rows.
- Math gains should be judged on larger slices than the first few positives.
- Route policies should be validated on disagreements, not just aggregate exact
  match.
