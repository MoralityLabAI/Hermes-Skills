# Learnings 3-27

This note captures the generalizability findings from the March 27 logic and
math passes.

## What held

- The TRM-augmented `Intellect-3-Logic` skill beat vanilla and generic skill
  arms on the smaller benchmark slice.
- The logic TRM arm generalized to the 109-row logic-only slice with exact
  match `0.3028`.
- Exact Campsite `(row_constraints, col_constraints)` signatures were the
  strongest router signal.
- The router signature gate generalized better than the coarse size-based
  structural rule.
- The hybrid architecture is worthwhile when TRMs are used as a commit-stage
  control plane rather than as a raw retrieval garnish.

## What did not hold

- The coarse structural gate overfit the logic family.
- Phrase-based support gates were too broad for Campsite logic.
- The math TRM lift was sparse and did not generalize as cleanly as the logic
  lift on larger slices.
- Learned KNN-style gates were weaker than the simple signature rule.

## Generalization read

The best current interpretation is:

- logic TRM support is real and repeatable
- the support lives in exact constraint signatures, not just in vague puzzle
  shape
- the logic skill contract should therefore route on signature-level policy,
  not only on prompt specialization

## Operational takeaway

The executable target is now:

- a Hermes skill contract for Campsite logic
- a signature-based route policy for TRM augmentation
- a benchmark loop that treats the contract as the canonical skill surface
