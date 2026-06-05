---
name: synapse-second-brain
description: Use when the user works with Synapse — the `syn` CLI and MCP server that stores people, projects, organisations, APIs, tasks and notes as a queryable, local Markdown graph (a "second brain"). Teaches the token-efficient, correct way to drive it: which read tool to reach for (search_knowledge / get_entity / list_by_type / project_graph), how to route across federated workspaces, the semantic-search modes, and the load-bearing rule that the assistant only *proposes* writes (capture_fact / link_entity / update_status) which the human accepts with `syn pending accept`. Trigger on mentions of Synapse, the `syn` command, a `.synapse/` workspace, or "second brain".
---

# Driving Synapse correctly

Synapse is a local-first knowledge graph. One `syn` binary is both a **CLI** (for the human) and an **MCP server** (`syn mcp`, for you). Source of truth is plain Markdown with YAML frontmatter under `projects/ people/ entities/ apis/ tasks/ notes/`; a disposable SQLite index makes it queryable. Six entity types: `project`, `person`, `entity` (org/vendor), `api`, `task`, `note`. A person/API/etc. exists **once** and is referenced by every project that touches it.

## The one rule that matters (BR-12.3)

**Over MCP you never write directly.** The write tools (`capture_fact`, `link_entity`, `update_status`, `add_workspace_topic`, `add_workspace_tag`) **enqueue a proposal** — they do *not* change anything. The tool returns a `pending_id` and the exact `syn pending accept <id>` command. The human reviews (`syn pending show <id>`) and accepts.

- **Never claim a write happened.** Say "I've queued a proposal (#N) — run `syn pending accept N` to apply it," and surface the id + command.
- **Never edit the Markdown or `.synapse/` directly** (no `sed`/`echo`/file writes). That bypasses provenance + audit. Use the tools.
- Batch related proposals, then give the user one list of ids to accept.

## Read: pick the cheapest tool that answers the question

Don't dump the workspace. Each tool returns JSON — parse it and reuse it; don't re-fetch.

| You want… | Use | Returns (verified against the code) |
|---|---|---|
| Find things by topic/keyword/meaning | `search_knowledge` | A JSON array of hits, each `{type, id, title, snippet}` — a short **snippet**, *not* the full body. Filter with `type`/`tag`/`owner`; cap with `limit`. |
| One known entity's full content | `get_entity {type, id}` | `{"markdown": "…"}` — the whole entity (frontmatter + body) as one text blob. The cheapest way to read a specific entity; don't search for something you can address by id. |
| A compact inventory of a type | `list_by_type {type, status?}` | A JSON array of `{type, id, title, status, owner, path}` — cheap; ideal before deciding what to read. |
| Relationships ("who owns X", "what depends on Y") | `project_graph {type, id, rel?}` | Inbound + outbound neighbours (`{direction, id, rel, …}`). Beats reading many entities to infer links. |

**Snippet → get_entity pattern (saves tokens):** `search_knowledge` gives you titles + snippets, not bodies. Triage on those, then call `get_entity` only on the handful you actually need to read in full. Don't pull every entity to find one.

### search_knowledge modes (token + latency aware)

`mode` mirrors the CLI. Pick deliberately:

- **`hybrid`** (default) — FTS + vector + graph, fused (RRF). Best recall for "find what I mean".
- **`semantic`** — vector-only. For "find things *like* this" with no shared words.
- **`no-vector`** — FTS + graph, **no model load**. Fastest; use when you know the term, or when models aren't downloaded.

If hits look empty and the user expected meaning-match, the models may not be downloaded — suggest `syn embed --all` (one-time ~920 MB, on their consent), or fall back to `no-vector`.

## Federation: route before you fan out

Workspaces are isolated unless the user opted them in (`syn ws include`). To answer across them **cheaply**:

1. `list_workspaces` — returns each opt-in workspace's identity card (name, description, topics, tags, language). **Route on this first** — it's small and tells you which workspace is relevant.
2. Only then `federated_search` (optionally `workspaces: [ids]` to restrict) or `get_entity_from {workspace, type, id}`. Don't blind-fan-out across everything. Returns `[{workspace, hits}]` grouped by workspace. **Cross-workspace search is keyword (FTS + graph), not semantic** — meaning-match (vectors) only works within the local workspace, so phrase federated queries with the actual terms.
3. `get_workspace_manifest {workspace}` to read a workspace's SYNAPSE.md before touching its content.

Workspaces the user didn't opt in are invisible — you cannot see or probe them.

## Write: propose well

All write tools take an optional `reason` (the user sees it on `syn pending show` — **always provide a concise one**) and an optional `context` JSON snapshot (a small JSON of your view at proposal time; it enables `syn audit replay` to detect model drift — include it for non-trivial proposals).

- **`capture_fact {type, title, body?, tags?, fields?, reason}`** — create an entity. `fields` is extra frontmatter, e.g. `{"status":"draft"}`. Slug is derived from `title`.
- **`link_entity {from_type, from_id, to_type, to_id, rel, reason}`** — labelled relation, e.g. `rel: "focal"`, `"uses-api"`, `"depends-on"`.
- **`update_status {type, id, status, reason}`** — e.g. a task to `done`, a project to `paused`. Validation happens at accept time.
- **`add_workspace_topic` / `add_workspace_tag`** — curate a workspace's identity card (improves future routing).

## A correct, token-lean session

```
User: "Who's the focal contact for cliente-alfa and what APIs do they own?"
You:  project_graph {type:"project", id:"cliente-alfa"}    # one call → people + links, incl. focal
      → focal = maria-silva; project_graph {type:"person", id:"maria-silva"}  # → the APIs she owns
      Answer from the JSON. No extra reads.

User: "We decided to use PKCE for OAuth on cliente-alfa. Note it."
You:  capture_fact {type:"note", title:"OAuth: PKCE chosen",
        body:"...", tags:["auth"], fields:{"kind":"decision"},
        reason:"user stated the OAuth decision for cliente-alfa"}
      → "Queued proposal #3. Run `syn pending accept 3` to save it."
      (Do NOT say the note was created.)
```

## Maintenance & misc

- `reindex` (MCP) / `syn reindex` — rebuild the index from Markdown if it drifts (user edited files by hand). `syn doctor` reports drift without mutating.
- Read tools are safe and read-only. When unsure what exists, `list_by_type` then `get_entity` beats guessing.

## CLI equivalents (when you have shell access)

If you're driving the terminal instead of MCP, the same model holds — **propose, the user accepts**:

```bash
syn search "<q>" --type project --format json   # always --format json for parsing
syn graph project cliente-alfa
syn pending list                                 # what's queued
# you do NOT run `syn pending accept` — that's the user's sign-off
```

Use `--format json` on any read command for compact, parseable output. Don't shell-edit Markdown; capture via the proposal flow.
