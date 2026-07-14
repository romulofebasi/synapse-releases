# Synapse

> Governed, local-first memory for AI agents. One `syn` binary is both a CLI (humans)
> and an MCP server (`syn mcp`, agents), bound to the same core. Six built-in
> linked entity types (project, person, entity/org, api, task, note), **plus
> any registered custom types** (`.synapse/types.toml`; discover them with
> `search_everything` / `list_by_type`). Stored as Markdown + YAML frontmatter
> (source of truth) with a disposable SQLite index and on-device semantic search.

## The load-bearing rule

Over MCP the assistant **never writes directly**. Write tools enqueue a
*proposal*; the human applies it with `syn pending accept <id>`. Never claim a
write succeeded. Surface the pending id and the accept command. Never edit
Markdown or `.synapse/` by hand; that bypasses provenance and the audit trail.

## MCP tools (25)

Every read returns `{ "result": …, "freshness"? }` as `structuredContent`
(read that field; the text mirror is compact JSON). Search hits and
`get_entity` attach `resource_link`s; `resources/read` a hit directly. Every
tool carries MCP annotations (reads are `readOnlyHint`; writes are additive, not
destructive); a client can auto-allow reads and gate writes. High-value reads
also attach a deterministic `_meta` sidecar (SYN-308): `workspace`, a `precision`
band count for searches, and a `next_step`, read it to judge if results are
on-topic before spending tokens. Recoverable errors come back as `invalid_params`
with a `data.remediation` naming the exact fix (SYN-309); retry on that, don't give up.

Read (local): `workspace_overview {recent?}` (counts + recent, orient here) ·
`workspace_health {days?}` (activity + hygiene + a `next_steps` list with the exact `syn` command to hand the human, surface what needs attention) ·
`search_knowledge {query,type?,tag?,owner?,limit?,mode?}` → `{type,id,title,snippet,matched_by?,relevance?,compatibility?}[]`
(mode = hybrid|semantic|no-vector; `matched_by` = which legs surfaced it (fts/vector/graph); `relevance` = strong|good|partial band; `compatibility` = bounded [0,1] score from leg agreement + rank position. Legs run in parallel; fused order deterministic) ·
`search_everything {query,...}` (same hybrid retrieval across **every** kind, built-in and custom, no type filter) ·
`get_entity {type,id}` → `{markdown}` ·
`get_entities {items:[{type,id,fields?}]}` (batch + field projection) ·
`list_by_type {type,status?,limit?,cursor?}` (paginated) ·
`project_graph {type,id,rel?}` (neighbours) ·
`recent_changes {since,limit?}` (audit delta, newest first) ·
`blame {type,id}` (provenance lineage + trust band) · `diff {ref?}` (git-over-time changes) ·
`verify` (proves the memory was not silently corrupted, the headline; offer it after a write) ·
`query {group_by,filter?,limit?}` (read-only aggregation, counts by
type|status|owner|priority|due|tag without paging; no SQL, ADR-023).
Federation (opt-in): `list_workspaces` · `federated_search {query,workspaces?}`
(keyword, not semantic) · `get_entity_from` · `get_workspace_manifest`.
Maintenance: `reindex {full?,relink?}`. Audit: `replay_proposal` (client-driven).
Resource: read `synapse://capabilities` (or run `syn context`) for the workspace
vocabulary (entity types + fields, link relations, reserved `x-*` keys, proposal
payload shapes, enrichment sources) to avoid proposing an invalid kind/rel/key.
Write proposals (enqueue, never apply): `capture_fact`, `link_entity`,
`update_status`, `add_workspace_topic`, `add_workspace_tag`, and
`propose_batch {proposals:[{kind,payload}]}`, bundle many into one accept.
If you used context from another connected MCP source (a calendar, tickets)
to fill people/project/tags/title, set the write's `enriched_from` to that
source class, the write is then always human-gated (SYN-303). A `capture_fact`
create is reversible after accept with `syn undo <id>`.

## Token-efficient usage

- Orient with `workspace_overview`; pick the cheapest read: `get_entity` for a
  known id, `list_by_type` for an inventory, `project_graph` for relationships,
  `search_knowledge` to discover. Don't dump the workspace.
- `search_knowledge` returns snippets, not bodies. Triage, then `get_entity`/
  `get_entities` only what you must read fully.
- Choose a search `mode` on purpose: `no-vector` (cheapest, exact-term),
  `semantic` (meaning-only), `hybrid` (default).
- Batch related writes with `propose_batch`; hand the user one accept.

## Skill

The full operating procedure is the Agent Skill. Install it with
`syn skill install` (drops `SKILL.md` into `~/.claude/skills/synapse-second-brain/`).
