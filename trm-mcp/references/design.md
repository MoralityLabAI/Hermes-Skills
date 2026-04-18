# TRM-MCP Design

## Goal

Use TRMs to compress an MCP surface into a cheap control system for lookup.

The point is not to make the TRM "know everything" in the MCP. The point is to make it reliably choose:

- where to look
- what handle or template to use
- whether a retrieved resource is actually relevant
- when to stop searching

## Recommended decomposition

### 1. Index TRM

Input:
- resource label
- URI
- short descriptor
- parameter names
- example query cues

Target:
- normalized family label
- lookup tags
- answer-shape tags

Use this to create a compressed lookup catalog.

### 2. Router TRM

Input:
- user query
- optional prior failure notes

Target:
- best MCP family
- whether to use:
  - `list_mcp_resources`
  - `list_mcp_resource_templates`
  - `read_mcp_resource`
  - direct local fallback

Train hard negatives where the family is plausible but still wrong.

### 3. Retriever TRM

Input:
- query
- candidate resource descriptors

Target:
- best URI or template
- optional parameter hints

This is where exact-hit supervision matters most.

### 4. Verifier TRM

Input:
- query
- chosen resource descriptor
- chosen parameters or action

Target:
- exact match / near miss / wrong scope / wrong family

This is usually the highest leverage TRM after routing.

## Good row types

- successful first-hit lookup
- wrong-family first attempt, corrected second attempt
- correct URI but wrong template arguments
- semantically related near-miss that should have been rejected
- abstain cases where the MCP does not contain the answer

## Metrics that matter

- first useful hit rate
- MCP calls per task
- tokens loaded per task
- verifier rejection precision on near-misses
- solved-task latency

## Common failure pattern

A generic retrieval layer overfits semantic similarity and keeps selecting attractive but wrong resources.

Fix:
- add scope-sensitive negatives
- train verifier separately
- include answer-shape tags
- split the surface into smaller specialist families

## Use pattern

If a model keeps scanning the same MCP surface over and over, a TRM-MCP layer is justified.

If a human could solve the lookup task by saying "this query usually maps to this URI/template family," that is strong evidence the task is TRM-friendly.
