# Primehub Abstain Guard Contract

This skill exists because some envs want:

- conservative reasoning under uncertainty
- but also exact contract output when the candidate answer is obvious

The guarded override should be rare and narrow.

Allow override only when all of these hold:

1. the contract is explicit
2. the candidate set is small
3. the repaired answer is exact and verifiable

Otherwise preserve abstention.
