# Filesystem MCP Example

Use this as the default worked example for `TRM-MCP`.

Why `filesystem` first:

- it is widely recognized
- lookup failures are easy to interpret
- direct-read vs template-search routing is concrete
- near-miss verifier negatives are common and realistic

## Example flow

`TRM_MCP_ROUTE -> TRM_MCP_RETRIEVE -> TRM_MCP_VERIFY`

### Typical successful cases

1. Query: "Open the root README"
   - route: `resource_read`
   - retrieve: `file:///workspace/README.md`
   - verify: `accept`

2. Query: "Find all `*.spec.ts` files"
   - route: `resource_template_list`
   - retrieve: `mcp://filesystem/templates/glob?pattern=**/*.spec.ts`
   - verify: `accept`

### Typical failure cases

1. Right route, wrong file
   - query asks for `README.md`
   - retriever picks `README.old.md`
   - verifier should `reject`

2. Wrong route
   - query asks for a specific file
   - router picks `resource_list` instead of `resource_read`
   - no useful hit
   - verifier should `reject`

## What the TRMs should learn

- `TRM_MCP_ROUTE`
  - when a direct path is likely enough
  - when a glob or template search is justified

- `TRM_MCP_RETRIEVE`
  - exact URI selection for direct reads
  - exact template handle selection for search workflows

- `TRM_MCP_VERIFY`
  - reject stale or scope-mismatched lookups
  - reject route choices that did not produce a useful hit

## Metrics

- exact URI or template hit rate
- wrong-read rejection precision
- template-vs-direct-read routing accuracy
- average lookup calls before first useful hit
