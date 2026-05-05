# TRM-MCP Paper Seed

Working title: **TRM-MCP: Tiny Recursive Controllers for Structured Tool Memory**

This folder rounds up the MCP-based work into a second paper package. The thesis is that MCP surfaces can be treated as structured external memory, and TRMs can learn low-token routing, retrieval, verification, and stop/escalate policies over those surfaces.

## Contents

- `paper.md`: first-pass manuscript scaffold.
- `claim_ledger.md`: what can and cannot be claimed from current artifacts.
- `evidence_manifest.json`: local source artifacts and scripts.
- `tables/trm_mcp_example_matrix.csv`: filesystem/GitHub/Postgres trace-row summary.
- `tables/storyworld_diary_mcp_lift.csv`: play-diary MCP benchmark lift summary.
- `tables/db_lookup_efficiency_model.csv`: bounded model of naive broad DB lookup vs direct TRM-MCP schema handles.
- `tables/metta_db_schema_enrichment.csv`: schema-surface enrichment counts from the MeTTa/Primehub MCP schema pack.
- `figures/trm_mcp_architecture.mmd`: Mermaid source for the architecture figure.
- `figures/db_lookup_efficiency.svg`: bar chart for modelled DB lookup efficiency.
- `figures/metta_db_schema_enrichment.svg`: bar chart for MeTTa schema-surface enrichment.

## Current Bounded Result

There are two evidence layers:

1. A generic TRM-MCP example matrix across filesystem, GitHub, and Postgres surfaces: `15` traces and `42` TRM rows, split into route/retrieve/verify tasks with exact positives and hard negatives.
2. A storyworld play-diary MCP environment study: `15` scenarios, `20` plays, average diary lift `+0.619333`, and diary recovery of four negative-NAV cases.

The current matrix is a training-data and methodology artifact. It is not yet a trained neural TRM benchmark.

## Added Graph Caveat

The DB lookup efficiency graph is an analytical model derived from the Postgres trace design, not a measured latency or token benchmark. The MeTTa schema-enrichment graph is based on the generated Primehub schema MCP surface; it shows how MeTTa/MCP makes schema constraints addressable for routing and verification, not a live SQL database migration.
