# Benchmark Matrix

Use this matrix when you want to check whether the workflow is actually useful.

## Collection checks

- Does the teacher model produce valid traces?
- Does the replay export stay bounded?
- Do the row builder and merger preserve exact positives?

## Component checks

- Retriever: does it recover useful held rows?
- Critic: does it separate likely good from likely bad?
- Router: does it choose the right expert or route?
- Corrector: does it improve exact match on the held set?

## Family checks

- Logic: use exact Campsite signatures as the current best route signal.
- Math: use support patterns conservatively until they generalize on larger
  slices.
- Storyworld: use it as a collector or transfer family, not the first target
  for the TRM control plane.
