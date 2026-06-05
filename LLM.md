# Synapse

> Synapse is a local-first, Markdown-based "second brain" for AI-augmented developers. One `syn` binary is both a CLI (for humans) and an MCP server (`syn mcp`, for AI agents) — both bind to the same core. It models a workspace as six linked entity types (project, person, entity/org, api, task, note) stored as plain Markdown + YAML frontmatter (the source of truth), with a disposable SQLite index for fast queries and v0.5 on-device semantic search. This file orients an AI assistant that is helping a user operate `syn`. For the full operating procedure, load the skill at `skills/synapse/SKILL.md` (Agent Skills format).

## The load-bearing rule (read first)

> Over MCP, the assistant **never writes directly**. The write tools enqueue a *proposal*; the human applies it with `syn pending accept <id>`. Never claim a write succeeded — surface the pending id and the accept command. Never edit Markdown or `.synapse/` by hand; that bypasses provenance and the audit trail.

## MCP tools (15)

Read (local): `search_knowledge` → array of `{type,id,title,snippet}` (hybrid FTS+vector+graph; filter by type/tag/owner/limit; `mode` = hybrid|semantic|no-vector) · `get_entity {type,id}` → `{markdown}` (full doc as text) · `list_by_type {type,status?}` → array of `{type,id,title,status,owner,path}` · `project_graph {type,id,rel?}` → inbound+outbound neighbours.
Federation (opt-in only): `list_workspaces` (route here first — identity cards) · `federated_search {query,workspaces?}` → `[{workspace,hits}]`, **keyword (FTS+graph) not semantic** · `get_entity_from {workspace,type,id}` · `get_workspace_manifest {workspace}`.
Maintenance: `reindex`. Audit: `replay_proposal`.
Write proposals (enqueue, never apply): `capture_fact {type,title,body?,tags?,fields?,reason}`, `link_entity {from_type,from_id,to_type,to_id,rel,reason}`, `update_status {type,id,status,reason}`, `add_workspace_topic`, `add_workspace_tag`.

## Token-efficient usage (how it's meant to be driven)

- Pick the cheapest read that answers the question: `get_entity` for a known id, `list_by_type` for an inventory, `project_graph` for relationships, `search_knowledge` (with `type`/`tag`/`owner`/`limit`) to discover. Don't dump the workspace; parse the JSON you get and reuse it.
- `search_knowledge` returns **snippets**, not bodies. Triage on titles/snippets, then `get_entity` only the few you must read in full.
- Choose a search `mode` on purpose: `no-vector` (cheapest, exact-term), `semantic` (meaning-only), `hybrid` (default, best recall).
- Federation: call `list_workspaces` to route, then touch only the relevant workspace — never blind-fan-out.
- Writes: include a concise `reason` (the user sees it) and a small `context` snapshot for non-trivial proposals; batch related proposals and give the user one list of `accept` commands.

## Core CLI surface (when driving the terminal)

`syn init` · `syn {project|person|entity|api|task|note} add|list|show|rm` · `syn person link <slug> --project <p> --role <r>` · `syn search <q> [--type|--tag|--semantic|--no-vector] [--format json]` · `syn graph <type> <slug>` · `syn embed --all|--check` (semantic models, downloaded on consent) · `syn pending list|show|accept|reject` (the human's sign-off queue) · `syn doctor` (health, never mutates). Add `--format json` to any read for compact, parseable output.

## Semantic search

On-device embeddings (BGE-M3) + NER (GLiNER) + hybrid ranking, opt-out (compiled into the default binary). Models (~920 MB) download only on the user's consent (`syn init` onboarding or `syn embed --all`). Until then, search degrades to keyword + graph — suggest `syn embed --all` if meaning-match is needed.

## Optional — learn more

- [skills/synapse/SKILL.md](./skills/synapse/SKILL.md): the full Agent Skill — load this to operate `syn` correctly.
- [ONBOARDING.md](./ONBOARDING.md): the human getting-started walkthrough.
- [MODELS.md](./MODELS.md): semantic search, the downloaded models, footprint, privacy, compatibility.
- [README.md](./README.md): install + requirements.
