# Synapse

Operational memory for agents, with governed changes, preserved history, and explicit integrity checks.

One `syn` executable exposes a CLI and MCP server over the same core. Knowledge content lives in Markdown with YAML frontmatter; a derived SQLite index supplies retrieval. Common types include projects, people, organizations, APIs, tasks and notes. A workspace may register custom types.

## Discover the installed contract

This public distribution repository can document releases older than the current development branch. Start with `syn --version` and `syn --help`; inspect command help and the connected MCP client's tool list. Do not assume a fixed tool count or development-only shared authority features.

When available, read `synapse://capabilities` or use `syn context` to discover workspace types, fields, relationships and proposal shapes. An unavailable tool or field needs a compatible installed version, not an invented fallback.

## The load-bearing rule

Use supported proposal tools for knowledge changes. Treat every proposal as pending until the returned state and an explicit supported review action establish otherwise. Show the exact pending identifier and review command. Never report an accepted change merely because you submitted a request.

The governed workflow uses `syn pending show <id>` before `syn pending accept <id>`. Respect the selected release's policy and authority requirements. Do not edit source Markdown or `.synapse/` behind the tool's governance boundary to manufacture success. Required review cannot be replaced by model confidence.

<a id="mcp-tools-25"></a>

## MCP tools

Discover actual tool schemas through the MCP client. Depending on the release, common tools include:

| Need | Candidate tools to discover | Practice |
| :-- | :-- | :-- |
| Orient | `workspace_overview`, `workspace_health` | Inspect counts, freshness and actionable omissions first. |
| Find relevant context | `search_knowledge`, `search_everything` | Use bounded snippets and supported filters. |
| Read known records | `get_entity`, `get_entities`, `list_by_type` | Fetch only needed records/fields; paginate inventories. |
| Follow relationships | `project_graph`, `recent_changes` | Prefer a scoped relationship or delta over a workspace dump. |
| Inspect history | `blame`, `diff` | Preserve attribution and distinguish current from historical facts. |
| Check integrity | `verify` | Report named checks, failures, exclusions and signing prerequisites. |
| Propose a change | `capture_fact`, `link_entity`, `update_status`, `propose_batch` | Submit supported payloads; inspect the returned state and review boundary. |

Prefer returned `structuredContent` when the installed server supplies it. Follow explicit remediation fields rather than guessing argument names. Resource links are references, not permissions. A ranking score is not a probability that a fact is true.

## Token-efficient usage

1. Orient once, then select the narrowest query.
2. Triage search titles and snippets before fetching full records.
3. Use known IDs, field projection and pagination where supported.
4. Group related supported proposals while keeping their exact review input visible.
5. Surface source revisions, stale context and unavailable coverage.

Search modes may include `hybrid`, `semantic` and `no-vector`; inspect the installed schema. Semantic search requires compatible selected models. Downloading models requires consent. A hosted embedding provider sends configured content to that provider; local processing does not make every optional integration offline.

## Federation

Opt in to specific workspaces before querying them. Discover available workspace cards and supported federation tools. Preserve each workspace's scope and access rules; a local connection does not establish organization-wide approval authority.

## Integrity and evidence

`syn verify` checks documented properties of the selected workspace and release. It does not establish general semantic truth, detect every contradiction in natural language, prove complete unknown history, or certify an agent's compliance. A skipped signing check is not a signed result. Undo support is operation-specific; discover the available command and affected proposal before promising reversibility.

## Skill

See the [portable Agent Skill](skills/synapse/SKILL.md). Where supported, `syn skill install` installs the skill for a compatible client. Inspect its reported destination and the client's discovery rules.
