# Hermes Skills

This workspace is a research surface for Hermes-style skill contracts plus TRM infusion.

It now has a clearer split between:

- task skills: exact-answer or domain contracts such as `intellect3-*` and `primehub-*`
- TRM overlays: retrieval, public-rationale, or routing layers such as `trm-mcp` and `trm-public-rationale-chain`
- TRM operations: collection, row building, training, and benchmarking via `trm-observability-workflow`
- scripts: shared runners, rollups, audit tools, and batch orchestration
- data: generated artifacts, benchmark outputs, and run receipts
- research: the top-level map, templates, and generated registry for keeping the work coherent

## Where To Start

- Read [research/README.md](C:/projects/Hermes-Skills/Hermes Skills/research/README.md) for the research structure.
- Read [research/generated/skill_registry.md](C:/projects/Hermes-Skills/Hermes Skills/research/generated/skill_registry.md) for the current inventory.
- Read [research/generated/study_queue.md](C:/projects/Hermes-Skills/Hermes Skills/research/generated/study_queue.md) for the recommended next studies.
- Use [scripts/build_hermes_skill_registry.py](C:/projects/Hermes-Skills/Hermes Skills/scripts/build_hermes_skill_registry.py) after adding or changing skill folders.

## Suggested Research Loop

1. Pick a base skill contract.
2. State the TRM infusion hypothesis.
3. Decide whether the infusion is:
   - overlay only
   - observability and training only
   - both
4. Collect bounded evidence with a fixed artifact contract.
5. Promote only if the TRM layer improves the target metric without breaking the base task contract.

## Core Research Artifacts

- [research/templates/skill_research_brief.md](C:/projects/Hermes-Skills/Hermes Skills/research/templates/skill_research_brief.md)
- [research/templates/experiment_log.md](C:/projects/Hermes-Skills/Hermes Skills/research/templates/experiment_log.md)
- [research/generated/skill_registry.json](C:/projects/Hermes-Skills/Hermes Skills/research/generated/skill_registry.json)
- [research/generated/study_queue.md](C:/projects/Hermes-Skills/Hermes Skills/research/generated/study_queue.md)

## Current Top-Level Categories

- `intellect3-*`
  - benchmark- and receipt-oriented exact-answer Hermes skills
- `primehub-*`
  - Primehub environment-facing Hermes contracts and TRM experiments
- `trm-*`
  - reusable TRM layers and TRM workflow infrastructure
- `hermes-bluebeam-research`, `pixie-mechinterp`
  - domain-specific or exploratory research surfaces
- `data/`
  - generated outputs, audit trails, and benchmark artifacts
- `scripts/`
  - shared automation across the workspace
- `hermes-trading.md`
  - legacy note; keep as reference material until it is either promoted into a foldered skill package or retired
