# GitHub MCP Example

Use this as the second worked example for `TRM-MCP`.

Why `github` next:

- it is a common MCP surface
- handles are structured and stable
- routing between direct read and search templates is realistic
- verifier negatives naturally arise from stale issues, wrong PRs, and wrong repo scope

## Example flow

`TRM_MCP_ROUTE -> TRM_MCP_RETRIEVE -> TRM_MCP_VERIFY`

### Typical successful cases

1. Query: "Open issue #142 in the repo"
   - route: `resource_read`
   - retrieve: `mcp://github/issues/142`
   - verify: `accept`

2. Query: "Find PRs mentioning benchmark regressions"
   - route: `resource_template_list`
   - retrieve: `mcp://github/templates/search_pull_requests?q=benchmark+regression`
   - verify: `accept`

### Typical failure cases

1. Right route, wrong issue
   - query asks for issue `#142`
   - retriever picks issue `#124`
   - verifier should `reject`

2. Wrong route
   - query asks for a specific PR
   - router picks a broad search template instead of direct read
   - verifier should `reject`

## What the TRMs should learn

- `TRM_MCP_ROUTE`
  - when a stable handle exists and direct read is cheaper
  - when semantic search templates are justified

- `TRM_MCP_RETRIEVE`
  - exact issue, PR, file, or search-template handle selection

- `TRM_MCP_VERIFY`
  - reject wrong repo scope
  - reject numerically similar but wrong issue or PR ids
  - reject broad search results when the task required one exact object

## Metrics

- exact handle hit rate
- wrong-issue and wrong-PR rejection precision
- search-template vs direct-read routing accuracy
- average API calls before first useful hit
