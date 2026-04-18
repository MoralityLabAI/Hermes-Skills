# Postgres MCP Example

Use this as the third worked example for `TRM-MCP`.

Why `postgres` next:

- it is a common structured-query MCP surface
- routing between exact relation reads and query templates is high leverage
- verifier negatives are easy to generate from wrong-table and wrong-schema near misses
- efficiency gains matter because broad schema scans are expensive

## Example flow

`TRM_MCP_ROUTE -> TRM_MCP_RETRIEVE -> TRM_MCP_VERIFY`

### Typical successful cases

1. Query: "Open the schema for `public.users`"
   - route: `resource_read`
   - retrieve: `mcp://postgres/db/app/schema/public.tables/users`
   - verify: `accept`

2. Query: "Find the top customers by revenue in the last 30 days"
   - route: `resource_template_list`
   - retrieve: `mcp://postgres/templates/top_customers_last_30d`
   - verify: `accept`

### Typical failure cases

1. Right route, wrong table
   - query asks for `public.users`
   - retriever picks `public.user_sessions`
   - verifier should `reject`

2. Wrong route
   - query asks for one exact table schema
   - router picks a broad table-list workflow instead of direct relation read
   - verifier should `reject`

## What the TRMs should learn

- `TRM_MCP_ROUTE`
  - when one stable relation handle is enough
  - when a reusable query template is the correct first move

- `TRM_MCP_RETRIEVE`
  - exact schema/table/view handle selection
  - exact query-template selection by task shape

- `TRM_MCP_VERIFY`
  - reject semantically related but wrong tables
  - reject wrong schema scope
  - reject broad listing workflows when the task required one exact object

## Metrics

- exact relation or template hit rate
- wrong-table rejection precision
- template-vs-direct-read routing accuracy
- average lookup calls before first useful hit
