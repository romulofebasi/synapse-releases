# Synapse quickstart

Create a local knowledge workspace, connect an agent and review a concrete change. Start with an installed `syn`; see the [installation guide](README.md#install).

Public releases may predate development documentation. Run `syn --version` and inspect `syn --help` and each command's help before using an example with your selected release. The walkthrough does not require development-only shared authority.

## 1. Make a workspace

```bash
syn init ~/brain
cd ~/brain
```

A workspace stores Markdown knowledge content and local operational metadata. Common folders include `projects/`, `people/`, `entities/`, `apis/`, `tasks/` and `notes/`. The search index is a derived projection; use `syn reindex` to rebuild supported index state.

**Do not delete `.synapse/` as an index repair shortcut.** It can also hold configuration, governance state, keys, pending proposals and other release-specific operational records. Back up the workspace and inspect the supported recovery procedure first.

An interactive first setup can ask for locale, output format and a personal profile. Provide only information appropriate for the workspace's access policy. Noninteractive behavior and prompts depend on the installed version.

Semantic model download is optional and requires consent. The default multilingual profile is about 2.5 GB; a lighter supported profile may suit a smaller machine. Check [models and privacy](MODELS.md) before downloading. Keyword retrieval remains an option with a compatible executable.

## 2. Capture what's in your head

Use supported CLI commands to create records and relationships:

```bash
syn project add "Payments Platform" --status active
syn person add "Maria Silva" --email maria@example.com --job-title "Tech Lead"
syn person link maria-silva --project payments-platform --role focal
syn note add "Why we picked PKCE" --kind decision --project payments-platform --tag auth
```

Inspect actual returned IDs and slugs. Markdown remains readable; direct file editing is not equivalent to a governed change. Prefer the supported commands/proposal path when attribution and integrity history matter.

## 3. Ask the graph

```bash
syn project list
syn person show maria-silva
syn search PKCE
syn graph project payments-platform
syn doctor
```

Inspect source context, freshness and scope. A retrieval hit can help an agent answer; it does not guarantee that the agent's resulting answer is correct.

## 4. Search by meaning (optional)

For a release supporting these commands:

```bash
syn embed --check
syn embed --all
syn search --semantic "authentication decision"
syn search --no-vector payments
```

`--check` inspects readiness. Run the download/embed operation only after reviewing the selected model, footprint and consent. Local models process locally; an explicitly configured hosted provider can send configured content to that provider. Meaning matching is model-dependent and can miss or misrank a result.

A model profile change needs compatible re-embedding; equal vector dimensions alone do not establish compatible embeddings. Linux executable/runtime compatibility must be checked independently of whether a query uses vectors. See [MODELS.md](MODELS.md).

## 5. Hand it to your AI (MCP)

Inspect the installed registration command and your client's configuration:

```bash
syn mcp install --workspace ~/brain
```

Restart or reload the client as required. Discover its actual Synapse tool list and schemas. Ask for the focal contact for `payments-platform` and inspect the source-backed response.

<details>
<summary>Prefer to wire it by hand?</summary>

Where supported, `syn mcp` serves stdio. Point a compatible MCP client at the selected workspace:

```json
{
  "mcpServers": {
    "synapse": {
      "command": "syn",
      "args": ["mcp", "--workspace", "/Users/you/brain"]
    }
  }
}
```

Review your client's merge and reload behavior before changing its configuration.

</details>

The governed workflow has the agent propose a change, then the operator inspect its exact payload and applicable policy:

```bash
syn pending list
syn pending show 1
syn pending accept 1
syn verify
```

Use the actual pending ID. A queued proposal is not an accepted fact. Respect the installed release's explicit approval and authority requirements, and inspect failures, skipped verification checks and coverage limits. Undo is operation-specific; inspect `syn undo --help` before promising reversal.

## Next

Use `syn <command> --help` to discover supported flags. Read [agent orientation](LLM.md), [the portable skill](skills/synapse/SKILL.md), [release verification](VERIFYING-RELEASES.md) and the [visual guide](VISUAL_GUIDE.md). Preserve both knowledge source and necessary operational state in your backup plan.
