# Synapse — quickstart

Five minutes from a fresh install to a queryable second brain you drive
from the terminal — and, when you want it, from your AI. Assumes `syn`
is already installed ([README](./README.md)).

---

## 1. Make a workspace

A workspace is just a folder of Markdown.

```bash
syn init ~/brain
cd ~/brain
```

You get `projects/`, `people/`, `entities/`, `apis/`, `tasks/`, `notes/`
and a disposable `.synapse/` index (delete it, run `syn reindex`, you're
back).

On a fresh, interactive run, `syn init` asks one question — whether to
download the semantic-search models (~920 MB, one-time):

```
Download the models now? [Y/n]
```

Say **yes** for meaning-search ([§4](#4-search-by-meaning-optional)), or
skip it — everything else works either way, and you can enable it later
with `syn embed --all`.

## 2. Capture what's in your head

Synapse models six entity types. A person exists **once** and is
referenced everywhere they appear.

```bash
syn project add "Cliente Alfa" --status active
syn person  add "Maria Silva" --email maria@empresa.com --job-title "Tech Lead"
syn person  link maria-silva --project cliente-alfa --role focal
syn note    add "Why we picked PKCE" --kind decision --project cliente-alfa --tag auth
```

Slugs are derived automatically; the YAML on disk is plain and
human-editable.

## 3. Ask the graph

```bash
syn project list
syn person  show maria-silva
syn search  PKCE                  # full-text (FTS5): fast, exact-term
syn graph   project cliente-alfa  # who/what links to this project
syn doctor                        # health check: dangling links, orphans
```

## 4. Search by meaning (optional)

The default binary ships an on-device **semantic layer** (embeddings +
NER + hybrid search). It is **opt-out** and pulls no data anywhere — but
its models are **downloaded only with your consent**. Turn it on once:

```bash
syn embed --all     # first run downloads ~920 MB of models, then embeds everything
syn embed --check   # … models_ready: true
```

Now search matches *meaning*, not just words:

```bash
syn search "the payments decision"   # finds the note even if it says "pagamentos", never "payments"
syn search --semantic "auth flow"    # vector-only: conceptually nearest
syn search --no-vector cliente-alfa  # FTS + graph only, skips the model (fast)
```

Until you run `syn embed --all`, writes still save (without embeddings)
and search falls back to keyword + graph — nothing blocks, nothing
downloads silently. Everything stays **on your machine**: the models are
fetched once from Hugging Face, then it runs fully offline.

> **Linux:** the semantic binary needs **glibc ≥ 2.38** (Ubuntu 24.04+,
> Debian 13+, Fedora 39+). On older distros the install still works for
> the keyword + graph + MCP features; meaning-search needs a newer base.

Full detail on the models, footprint, offline use and privacy: **[MODELS.md](./MODELS.md)**.

## 5. Hand it to your AI (MCP)

```bash
syn mcp     # the MCP server on stdio
```

Point Claude Code at the workspace:

```jsonc
// ~/.claude.json
{
  "mcpServers": {
    "synapse": { "command": "syn", "args": ["mcp"], "cwd": "/Users/you/brain" }
  }
}
```

Restart Claude Code and ask *"Who's the focal contact for cliente-alfa?"* —
it answers from **your facts**, never a hallucination.

**The AI proposes; you sanction.** MCP never writes directly. When the AI
wants to capture a fact it queues a proposal; you review and apply it:

```bash
syn pending list        # what the AI wants to write
syn pending show 1      # inspect the payload + reasoning
syn pending accept 1    # apply it — or `reject 1 --prune`
```

Every accepted write is provenance-stamped and appended to an audit
trail — the decision is on the record.

## Next

```bash
syn --help              # every command
syn <command> --help    # flags for one command
syn completions <shell> # shell completions
syn manpages <dir>      # man pages
```
