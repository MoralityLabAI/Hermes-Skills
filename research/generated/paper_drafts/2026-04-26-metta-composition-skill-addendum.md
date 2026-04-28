# Addendum: TRM-Aware MeTTa Skill Composition

Status: draft addendum  
Date: April 26, 2026

## Thesis

Hermes now needs a composition layer above individual TRM-infused skills. The role of this layer is to wire existing skills into MeTTa gate circuits while respecting the TRM role taxonomy: formatters should not become solvers, critics should not become action generators, and hard-reasoning roles should remain verifier or auditor roles until their exact-positive banks justify stronger routing.

The new composition skill is [metta-composition-hermes/SKILL.md](<C:\projects\Hermes-Skills\Hermes Skills\metta-composition-hermes\SKILL.md>). Its contract is [composition_contract.md](<C:\projects\Hermes-Skills\Hermes Skills\metta-composition-hermes\references\composition_contract.md>).

## Generated Composition Plan

The generated plan is [metta_composition_plan.md](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_composition_plan.md>) with machine-readable JSON at [metta_composition_plan.json](<C:\projects\Hermes-Skills\Hermes Skills\research\generated\metta_composition_plan.json>).

It defines six ready circuits:

- `contract_compactification_circuit`: choice, structure, and constraint repair.
- `tool_schema_composition_circuit`: MCP/tool routing with schema validation.
- `intellect3_logic_signature_circuit`: hard logic projection through signatures and grid constraints.
- `intellect3_math_teacher_auditor_circuit`: math as teacher-candidate auditing, not small-model solving.
- `safety_abstain_veto_circuit`: early safety/risk veto before final commit.
- `psycho_item_vector_composition_circuit`: item-vector and profile-stability interpretation.

## Methodological Use

This separates three layers that were previously easy to conflate:

- `metta-composition-hermes`: chooses valid skill circuits and role-compatible gates.
- `metta-eval-optimizer-hermes`: decides how forks should be evaluated and curated.
- Pure-TRM-Trainer / PrimeLab: train controller rows or run environment and QLoRA workflows.

The paper claim should be that MeTTa supplies a typed composition grammar for TRM-infused Hermes skills. The benchmark claim still depends on the downstream evidence class: live run, deterministic replay, post-hoc projection, or control-plane threshold eval.
