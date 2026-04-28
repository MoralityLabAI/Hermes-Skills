---
name: metta-composition-hermes
description: "Use when composing Hermes task skills into MeTTa gate circuits that are aware of TRM-infused skill roles, role-based TRM support tiers, and compatible PrimeHub/Intellect skill pairings."
---

# MeTTa Composition Hermes

Use this skill to compose Hermes skills into a MeTTa/TRM circuit. It is not an eval runner and not a trainer. It decides which skill roles can be safely wired together.

## Local References

- Contract: `references/composition_contract.md`

## Local Scripts

- `scripts/build_metta_composition_plan.py`

## Composition Flow

Follow the `Hermes-MeTTa-Composition-v1` flow:

1. `SKILL_INVENTORY`: read the available Hermes skills and their registry roles.
2. `TRM_ROLE_MAP`: map each skill to TRM roles such as formatter, router, critic, verifier, repairer, retriever, or latent-action emitter.
3. `SUPPORT_TIER_CHECK`: distinguish action-support roles from critic-first roles before composing.
4. `GATE_GRAPH_BUILD`: wire skills into `route -> retrieve -> propose -> validate -> repair -> commit -> log`.
5. `BOUNDARY_LABEL`: label whether the circuit is compactifiable, symbolically amplifiable, scale-sensitive, or interpretability-only.
6. `EXPORT_PLAN`: emit Pure-TRM rows, PrimeLab env artifacts, and paper claims separately.

## Hard Rules

- Do not treat critic-first TRM roles as action generators.
- Do not route `hard_reasoning_numeric` as a solver unless teacher candidates, invariants, or an external solver are present.
- Do not compose safety or abstain gates after a commit gate; safety gates must be early vetoes.
- Do not let formatter roles change semantics; they may only wrap, canonicalize, or repair observable contracts.
- Do not claim MeTTa benchmark gain from a composition plan alone. Label plans as methodology until live or replay evidence exists.

## Default Composition Patterns

- Contract lane: `choice_contract + structured_map + constraint_summarize`.
- Tool lane: `trm-mcp + structured_map + choice_contract`.
- Logic lane: `hard_reasoning_logic + intellect3_logic + public_rationale_chain`.
- Math lane: `hard_reasoning_numeric + intellect3_math + teacher_candidate_auditor`.
- Safety lane: `abstain_guard + structured_map`.
- Latent-action lane: `internal_action + contract verifier`.

## Outputs

For each composition, emit:

- source skills
- TRM role compatibility
- MeTTa gates
- unsupported assumptions
- Pure-TRM export rows
- PrimeLab export artifacts
- benchmark arms
- claim boundary

Use `scripts/build_metta_composition_plan.py` to regenerate the paper-facing plan.
