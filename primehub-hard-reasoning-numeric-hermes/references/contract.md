# Primehub Hard Reasoning Numeric Contract

Use this skill on tasks where the model has to carry a small chain of arithmetic or symbolic state correctly.

Failure modes this skill targets:

- skipping a required intermediate constraint
- landing on a plausible but unchecked value
- emitting an approximate explanation instead of the exact final value

Preferred reasoning order:

1. name givens and unknown
2. reduce to a tiny sequence of computations
3. solve once
4. verify by substitution, parity, sign, range, or a second quick computation
5. emit only the final exact answer
