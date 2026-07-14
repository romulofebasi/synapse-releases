# Synapse quickstart

Five minutes from a fresh install to a queryable memory you drive from the
terminal and, when you want it, from your AI. Assumes `syn` is already
installed (`npx @febasi/synapse`, or see the [README](./README.md)).

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

On a fresh, interactive machine `syn init` first runs a short **guided
setup**: locale, output format, then your profile (name, birthdate,
profession, employers). That profile is captured once and seeded into
this (and every) workspace as your `self` person, which powers
`syn cv export` and helps your AI route work to you. In CI or a pipe it
stays silent and skips the prompts.

Then `syn init` asks whether to download the semantic-search models
(one-time):

```
Download the models now? [Y/n]
```

If you say yes, it asks which **embedding profile** you want: **Quality**
(BGE-M3 fp32, ~2.5 GB total, maximum recall, the recommended default) or
**Speed** (BGE-M3 int8, ~900 MB total, lighter and faster, small recall cost).
Both are multilingual and the same vector space, so you can switch later.

Say **yes** for meaning-search ([§4](#4-search-by-meaning-optional)), or
skip it. Everything else works either way, and you can enable it later
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

Or drop a fact in without ceremony and let Synapse slot it into place:

```bash
syn capture "Maria now owns the Payments API"
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
NER + hybrid search). It is **opt-out** and pulls no data anywhere, but
its models are **downloaded only with your consent**. Turn it on once:

```bash
syn embed --all     # first run downloads ~2.5 GB of models, then embeds everything
syn embed --check   # … models_ready: true
```

Now search matches *meaning*, not just words:

```bash
syn search "the payments decision"   # finds the note even if it says "pagamentos", never "payments"
syn search --semantic "auth flow"    # vector-only: conceptually nearest
syn search --no-vector cliente-alfa  # FTS + graph only, skips the model (fast)
```

Until you run `syn embed --all`, writes still save (without embeddings)
and search falls back to keyword + graph. Nothing blocks, nothing
downloads silently. Everything stays **on your machine**: the models are
fetched once from Hugging Face, then it runs fully offline.

> **Linux:** the semantic binary needs **glibc ≥ 2.38** (Ubuntu 24.04+,
> Debian 13+, Fedora 39+). On older distros the install still works for
> the keyword + graph + MCP features; meaning-search needs a newer base.

Full detail on the models, footprint, offline use and privacy: **[MODELS.md](./MODELS.md)**.

## 5. Hand it to your AI (MCP)

Register Synapse with your MCP client in one step. It is a non-destructive
merge, so it leaves the rest of your config untouched:

```bash
syn mcp install                      # add Synapse to your MCP client
syn mcp install --workspace ~/brain  # or pin a specific workspace
```

Restart your client and ask *"Who's the focal contact for cliente-alfa?"* and
it answers from **your facts**, never a hallucination.

<details>
<summary>Prefer to wire it by hand?</summary>

`syn mcp` runs the server on stdio. Point Claude Code at the workspace:

```jsonc
// ~/.claude.json
{
  "mcpServers": {
    "synapse": { "command": "syn", "args": ["mcp", "--workspace", "/Users/you/brain"] }
  }
}
```

</details>

**The AI proposes; you sanction.** MCP never writes directly. When the AI
wants to capture a fact it queues a proposal; you review and apply it:

```bash
syn pending list        # what the AI wants to write
syn pending show 1      # inspect the payload + reasoning
syn pending accept 1    # apply it, or `reject 1 --prune`
```

Every accepted write is provenance-stamped and appended to an audit
trail, so the decision is on the record.

**Prove it, reverse it.** After you accept, prove nothing was silently
corrupted, and undo a create if you change your mind:

```bash
syn verify              # signed, offline report that the memory is intact
syn undo <id>           # reverse a capture_fact create, a Ctrl+Z for your memory
```

## Next

```bash
syn --help              # every command
syn <command> --help    # flags for one command
syn completions <shell> # shell completions
syn manpages <dir>      # man pages
```
