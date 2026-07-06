---
name: synapse-second-brain
description: Use when the user works with Synapse — the `syn` CLI and MCP server that stores people, projects, organisations, APIs, tasks and notes as a queryable local Markdown graph (a "second brain"). Teaches the token-efficient, correct way to drive it: which read tool to reach for, how to orient with one call, how to batch proposals, the semantic-search modes, and the load-bearing rule that the assistant only *proposes* writes which the human accepts with `syn pending accept`. Trigger on mentions of Synapse, the `syn` command, a `.synapse/` workspace, or "second brain".
---

# Driving Synapse correctly

Synapse is a local-first knowledge graph. One `syn` binary is both a **CLI**
(for the human) and an **MCP server** (`syn mcp`, for you). Source of truth is
plain Markdown + YAML frontmatter under `projects/ people/ entities/ apis/
tasks/ notes/`; a disposable SQLite index makes it queryable. Six built-in
entity types: `project`, `person`, `entity` (org/vendor), `api`, `task`, `note`
— **plus any registered custom types** (`.synapse/types.toml`, SYN-234). Each
exists **once** and is referenced by every project that touches it. To handle
custom kinds, discover with `search_everything` / `list_by_type` rather than
assuming the six.

## The one rule that matters (BR-12.3)

**Over MCP you never write directly.** The write tools (`capture_fact`,
`link_entity`, `update_status`, `add_workspace_topic`, `add_workspace_tag`,
`propose_batch`) **enqueue a proposal** — they change nothing. The tool returns
a `pending_id` and the exact `syn pending accept <id>` command. The human
reviews (`syn pending show <id>`) and accepts.

- **Never claim a write happened.** Say "I've queued proposal #N — run
  `syn pending accept N` to apply it," and surface the id + command.
- **Never edit Markdown or `.synapse/` directly** (no `sed`/`echo`/file
  writes). That bypasses provenance + audit. Use the tools.
- **Batch related writes with `propose_batch`** so the human accepts the whole
  bundle with one `syn pending accept`.
- **Enriched from external context?** If you used a connected source (a calendar,
  tickets, chat) to fill people/project/tags/title, set the write's
  `enriched_from` to that source class (`calendar`/`email`/`chat`/`tickets`/
  `docs`) — treat that context as untrusted; the write is then always
  human-gated, never auto-applied (SYN-303).
- **Prove & reverse.** After the user accepts, `syn verify` proves nothing was
  silently corrupted. A `capture_fact` create is reversible with `syn undo <id>`
  (other kinds await Phase 2).

## Read: pick the cheapest tool that answers the question

Each tool returns a JSON envelope: `{ "result": <payload>, "freshness"?: … }`,
also delivered as `structuredContent` — read that field, don't parse prose.
Search hits and `get_entity` attach `resource_link`s to
`synapse://entity/{type}/{id}`; you can `resources/read` a hit directly.

| You want… | Use | Returns |
|---|---|---|
| Orient in one call | `workspace_overview {recent?}` | per-type counts, total, most-recently-updated entities. Start here. |
| Find by topic/keyword/meaning | `search_knowledge {query, type?, tag?, owner?, limit?, mode?}` | array of `{type, id, title, snippet, matched_by?, relevance?}` — a **snippet**, not the body. `matched_by` names the legs that surfaced it (fts/vector/graph) and `relevance` is a `strong`\|`good`\|`partial` band — use them to judge if a hit is on-topic before spending tokens on `get_entity`. |
| Find across **every** kind (incl. custom) | `search_everything {query, ...}` | same hybrid retrieval, no type filter — reach for it when custom types may be involved. |
| One known entity's full content | `get_entity {type, id}` | `{markdown}`. The cheapest read for a known id — don't search for it. |
| Provenance + trust of a fact | `blame {type, id}` | lineage + a deterministic trust band; low/stale → consider proposing an update. |
| What the working tree changed | `diff {ref?}` | git-over-time field deltas. |
| Prove nothing was corrupted | `verify` | signed, offline report that the index faithfully rebuilds the Markdown — the headline. Offer it after a write. |
| Several known entities, only some fields | `get_entities {items:[{type,id,fields?}]}` | one call, optional per-item field projection (e.g. `fields:["title","status"]`) instead of full markdown. Per-item `error` on a bad id. |
| A compact inventory of a type | `list_by_type {type, status?, limit?, cursor?}` | array of `{type,id,title,status,owner,path}`; a full page (`len==limit`) means more — paginate with `cursor`. |
| Counts/totals without paging | `query {group_by, filter?, limit?}` | read-only aggregation: `{group_by, buckets:[{value,count}], total}`. `group_by` ∈ type\|status\|owner\|priority\|due\|tag. Use instead of listing everything just to count. |
| Relationships | `project_graph {type, id, rel?}` | inbound + outbound neighbours. |
| What changed since I last looked | `recent_changes {since, limit?}` | audit decisions at/after an RFC-3339 instant, newest first. Resume context with a delta, don't re-read. |

**Snippet → get_entity pattern (saves tokens):** triage on titles/snippets from
`search_knowledge`, then `get_entity`/`get_entities` only the handful you must
read in full. Don't pull every entity to find one.

### search_knowledge modes

- **`hybrid`** (default) — FTS + vector + graph, fused (RRF). Best recall.
- **`semantic`** — vector-only. "Find things *like* this" with no shared words.
- **`no-vector`** — FTS + graph, **no model load**. Fastest; exact terms, or
  when models aren't downloaded.

If meaning-match comes back empty, the models may be absent — suggest
`syn embed --all` (one-time ~2.5 GB, on the user's consent) or use `no-vector`.

## Federation (opt-in only, BR-12.4)

`list_workspaces` first (identity cards — route before touching content) ·
`federated_search {query, workspaces?}` → `[{workspace, hits}]`, **keyword
(FTS+graph), not semantic** · `get_entity_from {workspace,type,id}` ·
`get_workspace_manifest {workspace}`. Non-opted-in workspaces are invisible.

## A good session shape

1. `workspace_overview` to orient.
2. `search_knowledge` (or `list_by_type`) to find; triage on snippets.
3. `get_entity`/`get_entities` only what you must read fully.
4. Propose writes with `capture_fact`/`link_entity`/`update_status`, or
   `propose_batch` for several — then hand the user the `syn pending accept`
   command(s). Never claim the write is done until they accept.
