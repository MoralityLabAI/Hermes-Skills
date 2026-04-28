# Intellect3 Math Public-Trace Study

## Goal

Evaluate whether `trm-public-rationale-chain` helps `Intellect-3-Math` on rationale-allowed arithmetic slices without weakening the strict final-integer answer contract.

## Pairing

- Base skill: [intellect3-math-hermes](C:/projects/Hermes-Skills/Hermes Skills/intellect3-math-hermes/SKILL.md)
- Overlay: [trm-public-rationale-chain](C:/projects/Hermes-Skills/Hermes Skills/trm-public-rationale-chain/SKILL.md)
- Workflow support: [trm-observability-workflow](C:/projects/Hermes-Skills/Hermes Skills/trm-observability-workflow/SKILL.md)

## Current Evidence Inputs

- [contract.md](C:/projects/Hermes-Skills/Hermes Skills/intellect3-math-hermes/references/contract.md)
- [math_hybrid_200.summary.json](C:/projects/Hermes-Skills/Hermes Skills/intellect3-math-hermes/references/math_hybrid_200.summary.json)
- [math_router_100.summary.json](C:/projects/Hermes-Skills/Hermes Skills/intellect3-math-hermes/references/math_router_100.summary.json)
- [public_trace_contract.md](C:/projects/Hermes-Skills/Hermes Skills/trm-public-rationale-chain/references/public_trace_contract.md)

## Planned Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\intellect3-math-hermes\scripts\build_skill_prompt.py"
python "C:\projects\Hermes-Skills\Hermes Skills\trm-public-rationale-chain\scripts\build_skill_prompt.py" --task-family math --trace-format tagged --max-step-chars 96
python "C:\projects\Hermes-Skills\Hermes Skills\trm-observability-workflow\scripts\show_workflow.py"
```

## Artifact Contract

Store new outputs under:

- `research/studies/2026-04-22-intellect3-math-public-trace/artifacts/`
- expected first artifacts:
  - `math_public_trace_prompt.txt`
  - `math_public_trace_eval_notes.md`
  - `math_public_trace_decision.md`

## Decision Boundary

Do not promote this overlay unless it improves a rationale-allowed held slice despite the current note that packaged math receipts do not yet show a net aggregate win over vanilla.
