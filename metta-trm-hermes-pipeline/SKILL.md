---
name: metta-trm-hermes-pipeline
description: "Use for compiling MeTTa skill contracts into TRM retrieval packets, critic hints, and trace labels for Hermes skills."
---

# MeTTa TRM Hermes Pipeline

Use this surface when you want a symbolic source of truth for Hermes skill contracts and a concrete path from MeTTa rules into TRM artifacts.

## Local references

- Architecture: `README.md`
- Package contract: `package_contract.md`

## Local scripts

- `scripts/compile_metta_package.py`

## Working model

1. Author env and skill rules in `.metta` files.
2. Keep package metadata in `package.manifest.json`.
3. Compile the package into:
   - retrieval packets
   - critic hints
   - trace labels
   - bundle manifests
4. Feed those artifacts into Hermes skills and TRM studies.

## Operational rules

- Keep one top-level atom per line in example packages so the lightweight compiler can extract it deterministically.
- Use MeTTa for contracts, invariants, failure modes, and routing cues, not for long prose.
- Treat compiled packets as deployable runtime slices and the full MeTTa package as the research source.
