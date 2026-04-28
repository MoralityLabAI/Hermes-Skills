# Intellect3 Logic Public-Trace Study

## Goal

Evaluate whether `trm-public-rationale-chain` improves held `Intellect-3-Logic` performance when the benchmark explicitly allows a visible rationale channel.

## Pairing

- Base skill: [intellect3-logic-hermes](C:/projects/Hermes-Skills/Hermes Skills/intellect3-logic-hermes/SKILL.md)
- Overlay: [trm-public-rationale-chain](C:/projects/Hermes-Skills/Hermes Skills/trm-public-rationale-chain/SKILL.md)
- Workflow support: [trm-observability-workflow](C:/projects/Hermes-Skills/Hermes Skills/trm-observability-workflow/SKILL.md)

## Current Evidence Inputs

- [contract.md](C:/projects/Hermes-Skills/Hermes Skills/intellect3-logic-hermes/references/contract.md)
- [logic_hybrid_200.summary.json](C:/projects/Hermes-Skills/Hermes Skills/intellect3-logic-hermes/references/logic_hybrid_200.summary.json)
- [logic_router_200.summary.json](C:/projects/Hermes-Skills/Hermes Skills/intellect3-logic-hermes/references/logic_router_200.summary.json)
- [public_trace_contract.md](C:/projects/Hermes-Skills/Hermes Skills/trm-public-rationale-chain/references/public_trace_contract.md)

## Planned Commands

```powershell
python "C:\projects\Hermes-Skills\Hermes Skills\intellect3-logic-hermes\scripts\build_skill_prompt.py"
python "C:\projects\Hermes-Skills\Hermes Skills\trm-public-rationale-chain\scripts\build_skill_prompt.py" --task-family logic --trace-format tagged --max-step-chars 96
python "C:\projects\Hermes-Skills\Hermes Skills\trm-observability-workflow\scripts\show_workflow.py"
```

## Artifact Contract

Store new outputs under:

- `research/studies/2026-04-22-intellect3-logic-public-trace/artifacts/`
- expected first artifacts:
  - `logic_public_trace_prompt.txt`
  - `logic_public_trace_eval_notes.md`
  - `logic_public_trace_decision.md`

## Decision Boundary

Do not promote this overlay if it lowers held exact-grid accuracy or causes contract breaks such as prose leakage, malformed lists, or extra non-final lines in settings that still require a strict final grid.
