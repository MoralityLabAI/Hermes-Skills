# Claim Audit

## Evidence Class

- `no_model_proposal_tier_smoke` verifies the validator and projection threshold behavior.
- `live_model_local_3b` applies the same frozen rows and validator to local 3B completions when result receipts exist.

## Allowed Claims

- The suite is leakage-safe with respect to target grids: prompts contain constraints but not answers.
- Prompt-derived signatures and adjacency rules are sufficient to solve each frozen micro-row uniquely.
- Projection may be described as symbolic closure over public constraints.
- Live local 3B rows can be reported because row IDs, validators, and a job-cap receipt are present.
- Prompt-derived MeTTa projection scored 9/12 exact versus raw MeTTa runtime 0/12.
- Public-constraint solver replay scored 12/12 exact; report it as symbolic solver closure, not model lift.
- Constraint extraction plus deterministic schema repair scored 12/12 repaired solve exact for `metta_schema_extract`.

## Disallowed Claims

- Do not call projection success a latent-reasoning improvement.
- Do not compare this directly to the old 27B receipt replay without noting the old replay used answer-derived signatures.
- Do not claim trained TRM lift; this study tests runtime framing and deterministic MeTTa projection.
- Do not claim broad natural-language puzzle extraction yet; the extraction prompts are still structured and should be followed by paraphrased/noisy prompt variants.
