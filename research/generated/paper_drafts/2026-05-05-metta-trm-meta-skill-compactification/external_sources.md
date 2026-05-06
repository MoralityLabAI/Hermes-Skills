# External Sources For Feature-Steering Extension

These sources informed the proposed VPD/tiny-LoRA extension. They support framing only; they are not local benchmark evidence.

## Goodfire VPD

- URL: https://www.goodfire.ai/research/interpreting-lm-parameters
- Date checked: 2026-05-06
- Relevant points:
  - VPD is described as a parameter-decomposition method that decomposes language-model parameters into simple subcomponents.
  - The method optimizes for subcomponents that preserve input-output behavior even under many ablations, including adversarially selected ablations.
  - Goodfire reports a proof-of-concept manual model edit using parameter subcomponents.
  - The public result is on a 67M parameter language model, not on the local TRM controllers in this repo.

## Goodfire Ember Feature Steering

- URL: https://www.goodfire.ai/blog/announcing-goodfire-ember
- Date checked: 2026-05-06
- Relevant points:
  - Ember exposes interpretable SAE features as a core interface.
  - Goodfire describes feature steering as tuning model internals to shape model behavior.
  - The blog distinguishes feature programming and conditional steering use cases.

## Goodfire SDK Feature API

- URL: https://docs.goodfire.ai/sdk-reference/features
- Date checked: 2026-05-06
- Relevant points:
  - The SDK documents feature search, inspection, contrast, reranking, activation extraction, and lookup.
  - This is activation-feature tooling, not the same object as VPD parameter subcomponents.

## Goodfire SDK AutoSteer

- URL: https://docs.goodfire.ai/sdk-reference/autosteer
- Date checked: 2026-05-06
- Relevant points:
  - AutoSteer generates feature edits from a natural-language behavior specification.
  - This suggests an analogy for MeTTa feature contracts, but the local proposal targets tiny LoRA adapters on TRM controllers rather than runtime steering of hosted LLMs.
