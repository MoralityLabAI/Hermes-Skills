# Skill Research Brief

## Metadata

- Skill name: metta-trm-hermes-pipeline
- Track: domain research
- Family: symbolic compiler
- Base contract version: MeTTa-TRM-Pipeline-v1
- TRM infusion type: compound
- Related overlay or workflow: trm-mcp; trm-observability-workflow
- Benchmark or environment family: primehub structured-map lanes plus a curated psycho-like nuanced slice led by `psycho_bench` and `if_summarize_judge`
- Owner: Hermes Skills research
- Date: 2026-04-22

## Research Question

Can a small, deterministic MeTTa package contract serve as the symbolic source of truth for Hermes skill rules and compile into TRM artifacts that are usable at runtime and in studies?

## Hypothesis

Schema-heavy Hermes lanes will benefit from a symbolic authoring layer when the compiler output is narrow, auditable, and easy to inject into retrieval or critic flows.

## Base Contract

Keep MeTTa authoring simple:

- one manifest
- one atom per line
- deterministic extraction
- JSON bundle outputs for TRM consumers

## TRM Intervention

Compile MeTTa packages into:

- retrieval packets
- critic hints
- trace labels

Later phases can add:

- row builders
- negative generators
- symbolic repair planners

## Evidence Plan

- package sources:
  - `metta-trm-hermes-pipeline/examples/primehub_structured_map`
  - `metta-trm-hermes-pipeline/examples/if_summarize_judge_constraints`
- compiler: `metta-trm-hermes-pipeline/scripts/compile_metta_package.py`
- proof artifact: generated bundle in this study folder
- primary metrics:
  - successful deterministic compilation into the expected artifact set
  - live `with_metta` vs `without_metta` reward comparison on `psycho_bench`, `ascii_tree`, and `pydantic_adherence`
  - successful emission of a compact runtime packet, offline TRM rows, and deterministic repair outputs from the same symbolic source
  - explicit curation of a broader nuanced slice with ready, blocked, and excluded env groups grounded in local env code and replay evidence
  - successful profile-aware packet compilation for `if_summarize_judge`, including multi-family runtime metadata, synthesized profile rows, and a replay-grounded repair probe
- secondary metrics:
  - artifact readability
  - env coverage
  - downstream usability for TRM overlays
  - token overhead relative to the non-MeTTa control
- failure gates:
  - ambiguous package contract
  - brittle parsing
  - unusable artifact schema
  - MeTTa treatment losing to the non-MeTTa control on held envs

## Promotion Rule

State the exact condition for:

- promote: the package contract compiles reliably, the bundle is usable by at least one real Hermes + TRM lane, and `with_metta` matches or beats `without_metta` on the held structured-map slice without giving back exact-structure wins
- hold: the contract compiles and runs live, but the MeTTa treatment needs another iteration before replacing the current non-MeTTa control
- reject: the contract is too noisy, too ambiguous, or too hard to operationalize

## Current Decision

- status: promoted (narrow)
- current evidence:
  - first packet:
    - `psycho_bench`: `with_metta` `3.3033` vs `without_metta` `3.3283`
    - `ascii_tree`: tie at `0.8`
    - `pydantic_adherence`: tie at `1.0`
  - richer packet rerun:
    - `psycho_bench`: `with_metta` `3.3311` vs `without_metta` `3.3283`
    - `ascii_tree`: tie at `0.8`
    - `pydantic_adherence`: tie at `1.0`
  - compact runtime packet live eval:
    - `psycho_bench`: `with_metta_runtime` `3.3483` vs `without_metta` `3.3283`
    - `ascii_tree`: tie at `0.8`
    - `pydantic_adherence`: tie at `1.0`
    - repair-assisted rescoring: no reward change on this clean slice
- implication: the symbolic package format is viable and the compact runtime packet is now the strongest MeTTa runtime infusion artifact in the repo, though the main lift still comes from one env and token cost is not uniformly lower
- current infrastructure:
  - runtime packet compiler implemented
  - offline row compiler implemented
  - deterministic repair pass implemented
  - nuanced slice builder implemented
  - nuanced baseline runner implemented
  - first profile-aware Hermes skill implemented for `if_summarize_judge`
- implication: the next meaningful gain should come from harder held evals, narrower runtime packets, and training/repair leverage rather than more prompt inflation
- current broader-slice view:
  - `core_ready`: `psycho_bench`, `if_summarize_judge`
  - `expanded_ready`: add `allenai_ifeval`
  - `blocked_high_value`: `clbench`
  - excluded from the psycho-like slice: `simpleqa`, `simpleqa_verified`, `simpleqa_verified_2`, `truthfulqa`
  - `if_summarize_judge` implementation status:
    - profile-aware bundle compiled
    - runtime packet emitted with `17` profiles
    - profile rows synthesized: `68`
    - repair probe passed on a recorded one-comma observation
    - initial live remote benchmark exposed a scorer-path failure, not a clean comparison:
      - all episodes hit the same seeded `one_comma` prompt
      - plausible probe answers also scored `0.0`
    - scorer path corrected with:
      - bridge-side judge setting passthrough
      - configurable judge timeout
      - deterministic structural fastpath in the live env
      - seeded sweep runner
    - corrected live remote seeded benchmark:
      - seeds: `7`, `11`, `19`
      - `without_metta`: avg reward `0.3333`
      - `with_metta_runtime`: avg reward `0.6667`
      - per-seed: `one_comma` `0.0 -> 1.0`, `single_question` `1.0 -> 1.0`, `exact_10w_bullets` `0.0 -> 0.0`
    - targeted repair rerun:
      - `without_metta`: avg reward `0.3333`
      - `with_metta_runtime`: avg reward `0.3333`
      - `with_metta_runtime_repair`: avg reward `1.0`
      - repaired seeds: `one_comma`, `exact_10w_bullets`
    - implication: `if_summarize_judge` is now a usable MeTTa benchmark surface, and the current reliable gain comes from the repair-aware lane more than from prompt-only runtime memory
