# Synapse

> Local-first Markdown "second brain". One `syn` binary is both a CLI (humans)
> and an MCP server (`syn mcp`, agents), bound to the same core. Six linked
> entity types — project, person, entity/org, api, task, note — stored as
> Markdown + YAML frontmatter (source of truth) with a disposable SQLite index
> and on-device semantic search.

## The load-bearing rule

Over MCP the assistant **never writes directly**. Write tools enqueue a
*proposal*; the human applies it with `syn pending accept <id>`. Never claim a
write succeeded — surface the pending id and the accept command. Never edit
Markdown or `.synapse/` by hand; that bypasses provenance and the audit trail.

## MCP tools (20)

Every read returns `{ "result": …, "freshness"? }` as `structuredContent`
(read that field; the text mirror is compact JSON). Search hits and
`get_entity` attach `resource_link`s — `resources/read` a hit directly.

Read (local): `workspace_overview {recent?}` (counts + recent — orient here) ·
`search_knowledge {query,type?,tag?,owner?,limit?,mode?}` → `{type,id,title,snippet}[]`
(mode = hybrid|semantic|no-vector) · `get_entity {type,id}` → `{markdown}` ·
`get_entities {items:[{type,id,fields?}]}` (batch + field projection) ·
`list_by_type {type,status?,limit?,cursor?}` (paginated) ·
`project_graph {type,id,rel?}` (neighbours) ·
`recent_changes {since,limit?}` (audit delta, newest first) ·
`query {group_by,filter?,limit?}` (read-only aggregation — counts by
type|status|owner|priority|due|tag without paging; no SQL, ADR-023).
Federation (opt-in): `list_workspaces` · `federated_search {query,workspaces?}`
(keyword, not semantic) · `get_entity_from` · `get_workspace_manifest`.
Maintenance: `reindex`. Audit: `replay_proposal`.
Write proposals (enqueue, never apply): `capture_fact`, `link_entity`,
`update_status`, `add_workspace_topic`, `add_workspace_tag`, and
`propose_batch {proposals:[{kind,payload}]}` — bundle many into one accept.

## Token-efficient usage

- Orient with `workspace_overview`; pick the cheapest read: `get_entity` for a
  known id, `list_by_type` for an inventory, `project_graph` for relationships,
  `search_knowledge` to discover. Don't dump the workspace.
- `search_knowledge` returns snippets, not bodies — triage, then `get_entity`/
  `get_entities` only what you must read fully.
- Choose a search `mode` on purpose: `no-vector` (cheapest, exact-term),
  `semantic` (meaning-only), `hybrid` (default).
- Batch related writes with `propose_batch`; hand the user one accept.

## Skill

The full operating procedure is the Agent Skill — install it with
`syn skill install` (drops `SKILL.md` into `~/.claude/skills/synapse-second-brain/`).
