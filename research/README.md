# Hermes Research Structure

This folder is the coordination layer for Hermes Skills research with TRM infusion.

The goal is to keep three things separate:

1. the base skill contract
2. the TRM layer being tested
3. the evidence path used to justify a promotion or rejection

## Tracks

### Task Skill

A task skill defines the core answer contract and reasoning flow.

Examples:
- `intellect3-logic-hermes`
- `intellect3-math-hermes`
- `primehub-hard-reasoning-logic-hermes`
- `primehub-hard-reasoning-numeric-hermes`

### TRM Overlay

A TRM overlay changes how the task is routed, observed, or externally expressed without replacing the base task contract.

Examples:
- `trm-mcp`
- `trm-public-rationale-chain`

### TRM Operations

TRM operations are the collection and promotion loop.

Examples:
- `trm-observability-workflow`

### Domain Research

Domain research surfaces test Hermes contracts in a specialized area and may later split into task skills plus TRM overlays.

Examples:
- `hermes-bluebeam-research`
- `pixie-mechinterp`
- `metta-trm-hermes-pipeline`

## TRM Infusion Types

Use one label per study:

- `none`
  - baseline contract only
- `route`
  - TRM selects where or when the skill path is used
- `retrieve`
  - TRM improves lookup or MCP access before the skill runs
- `public-trace`
  - a bounded visible rationale channel is added
- `observability`
  - teacher traces, rows, and evaluation artifacts are the main intervention
- `compound`
  - more than one TRM layer is intentionally combined

## Minimum Study Packet

Every serious Hermes + TRM study should have:

1. a skill research brief
2. an experiment log
3. a fixed benchmark or environment family
4. a metric bundle
5. a promotion decision

Use:
- [templates/skill_research_brief.md](C:/projects/Hermes Skills/research/templates/skill_research_brief.md)
- [templates/experiment_log.md](C:/projects/Hermes Skills/research/templates/experiment_log.md)
- [studies/README.md](C:/projects/Hermes Skills/research/studies/README.md)

## Promotion Gates

Do not call a TRM infusion a win unless it clears all applicable gates:

- the base answer contract is preserved
- the improvement target is explicit
- the benchmark slice is named
- the evidence path is reproducible
- the failure mode is written down

## Practical Pairing Rules

- Pair base task skills with `trm-observability-workflow` when the main question is collection, row quality, training, or benchmarking.
- Pair logic or math task skills with `trm-public-rationale-chain` only when the evaluation explicitly permits a visible trace channel.
- Pair MCP- or lookup-heavy work with `trm-mcp` when the main bottleneck is retrieval efficiency rather than final-answer synthesis.
- Avoid stacking multiple TRM layers until the single-layer intervention is stable on held evidence.

## Generated Inventory

The generated registry lives in:

- [generated/skill_registry.md](C:/projects/Hermes Skills/research/generated/skill_registry.md)
- [generated/skill_registry.json](C:/projects/Hermes Skills/research/generated/skill_registry.json)
- [generated/study_queue.md](C:/projects/Hermes Skills/research/generated/study_queue.md)

## Legacy Notes

- [../hermes-trading.md](C:/projects/Hermes Skills/hermes-trading.md)
  - Keep one-off markdown notes here only as temporary references.
  - Promote them into a foldered skill package if they gain their own contract, references, and scripts.
  - Otherwise treat them as archival context, not as active research surfaces.

Rebuild it with:

```powershell
python "C:\projects\Hermes Skills\scripts\build_hermes_skill_registry.py"
```

## Study Packets

Use [studies/README.md](C:/projects/Hermes Skills/research/studies/README.md) to move from the generated queue into concrete, dated study folders with a brief and experiment log.
