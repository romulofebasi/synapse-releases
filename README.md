<div align="center">

<img src="https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/assets/wordmark-horizontal.png" width="800" alt="Synapse — second brain · cli + mcp" />

<br/>

*A local-first, queryable second brain for AI-augmented developers — six entity types (projects, people, orgs, APIs, tasks, notes), one graph, two doors: your terminal and your AI over [MCP](https://modelcontextprotocol.io).*

[![Latest release](https://img.shields.io/github/v/release/romulofebasi/synapse-releases?label=latest&color=5B3EE0)](https://github.com/romulofebasi/synapse-releases/releases/latest)
[![Install](https://img.shields.io/badge/install-curl%20%7C%20sh-FFB454.svg)](#install)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

## What's new in v0.7.0 — Governed-autonomy foundation

- **Governed autonomy.** A new write policy (`[proposals] auto_apply`) evolves the propose/accept gate. By default (`manual`) every AI write still queues for `syn pending accept` — the invariant is intact. Opt into `safe` and **low-risk, reversible** writes (linking two entities that already exist) apply on their own, stamped on the audit trail as `auto-accepted`. Underneath: AI batches are now **atomic** (all-or-nothing) and a single accept is **crash-safe** (never "applied but still pending").
- **Faster on big vaults.** `syn reindex` is now **incremental** — it only re-parses files that changed (and reconciles deletions), instead of rescanning the whole workspace. `syn reindex --full` forces a clean rebuild.
- **Choose quality or speed.** Guided `syn init` lets you pick the embedding profile: **BGE-M3 fp32** (~2.5 GB, maximum recall — the recommended default) or **int8** (~900 MB total, lighter & faster, small recall cost). Same 1024-dim space, so switching is just a re-embed.
- **One more agent tool — 20 MCP tools.** New read-only **`query`** aggregates counts (by type/status/owner/priority/due/tag, optionally filtered) **out of context** — and takes **no SQL**, so it can never read internal tables. `replay_proposal` is now **client-driven**: the server returns replay material the agent re-runs (no server-side sampling).
- **Honest footprint.** The on-device models are **~2.5 GB** (fp32 default) — measured and corrected from the earlier ~920 MB figure; see [MODELS.md](./MODELS.md).

---

## Install

### One-liner (macOS, Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/install.sh | sh
```

Detects your OS and CPU, downloads the right binary, drops `syn` into `/usr/local/bin/` (override with `INSTALL_DIR=~/.local/bin`), and clears the macOS Gatekeeper attribute for you. Pin a version with `SYNAPSE_VERSION=v0.7.0`.

### Windows (PowerShell)

```powershell
$ver = "v0.7.0"   # latest tag from the releases page
$url = "https://github.com/romulofebasi/synapse-releases/releases/download/$ver/synapse-$($ver.Substring(1))-x86_64-pc-windows-msvc.zip"
$tmp = "$env:TEMP\synapse.zip"
Invoke-WebRequest $url -OutFile $tmp
Expand-Archive $tmp -DestinationPath $env:TEMP -Force
Move-Item "$env:TEMP\synapse-$($ver.Substring(1))-x86_64-pc-windows-msvc\syn.exe" "$HOME\bin\syn.exe" -Force
```

### Manual download

Pick your platform from the [latest release](https://github.com/romulofebasi/synapse-releases/releases/latest), extract, and put `syn` (or `syn.exe`) on your `PATH`.

| OS | Architecture | Asset |
|---|---|---|
| macOS | Apple Silicon (M1+) | `synapse-<version>-aarch64-apple-darwin.tar.gz` |
| Linux | x86_64 | `synapse-<version>-x86_64-unknown-linux-gnu.tar.gz` |
| Linux | ARM64 | `synapse-<version>-aarch64-unknown-linux-gnu.tar.gz` |
| Windows | x86_64 | `synapse-<version>-x86_64-pc-windows-msvc.zip` |

> **Intel Macs (`x86_64`) are not supported.** The ONNX Runtime behind
> Synapse's semantic search ships no Intel-macOS build, so there is no
> binary for that target. Apple Silicon (M1+) is the only supported Mac.

---

## Requirements

`syn` is a single self-contained binary — no runtime, no Python, no system SQLite. The semantic-search features add a one-time model download (on your consent), not a heavier install.

| | Detail |
|---|---|
| **Disk** | ~25 MB binary. Semantic search downloads **~2.5 GB** of models on first use (once, shared across workspaces) — see [MODELS.md](./MODELS.md). Without it you still get keyword + graph search and the full MCP server. |
| **Linux** | Semantic search needs **glibc ≥ 2.38** — Ubuntu 24.04+, Debian 13+, Fedora 39+. On older distros `syn` installs and runs (CLI + MCP + keyword/graph search); only meaning-search needs a newer base. |
| **Network** | Only the one-time model download (from Hugging Face) ever leaves your machine. Your notes, entities and queries stay local — Synapse ships **no telemetry**. |

---

## First steps

```bash
syn init ~/brain && cd ~/brain
syn project add "Cliente Alfa"
syn person  add "Maria Silva" --email maria@empresa.com
syn search  alfa
syn mcp     # expose it to Claude Code
```

The walkthrough — entities, the graph, semantic search, and wiring up your AI with the propose/accept loop — is in **[ONBOARDING.md](./ONBOARDING.md)**.

## Docs

- **[ONBOARDING.md](./ONBOARDING.md)** — from install to your first answer, step by step.
- **[MODELS.md](./MODELS.md)** — semantic search, the on-device models, footprint, offline use, privacy.

## For your AI assistant

Synapse is built to be driven by an AI over [MCP](https://modelcontextprotocol.io) (`syn mcp`). To teach Claude (or any agent) the **right, token-efficient** way to use it — which read tool to pick, how to route across workspaces, and the rule that the AI only *proposes* writes while you accept them — two machine-oriented files ship here:

- **[`skills/synapse/SKILL.md`](./skills/synapse/SKILL.md)** — a portable [Agent Skill](https://agentskills.io) (the open standard used by Claude Code, the Claude apps/API, and other agents). Install it once:

  ```bash
  # Claude Code / Claude — personal (all projects):
  mkdir -p ~/.claude/skills && cp -r skills/synapse ~/.claude/skills/synapse
  # …or per-project: cp -r skills/synapse .claude/skills/synapse
  ```

  Claude then loads it automatically when you work with Synapse (or invoke `/synapse-second-brain`).

- **[`LLM.md`](./LLM.md)** — an [`llms.txt`](https://llmstxt.org)-style orientation file. Point any agent at it (or paste it) to give it a concise, accurate picture of Synapse and its MCP tools.

> As of **v0.6**, the binary installs these for you — no copying needed:
>
> ```bash
> syn skill install     # → ~/.claude/skills/synapse-second-brain/SKILL.md
> syn agents init       # → ./llms.txt
> syn plugin install    # scaffold a full Claude Code plugin (skill + MCP + hooks)
> ```

---

## Gatekeeper / SmartScreen

The binaries are not yet code-signed (signing arrives with v1.0). The one-line installer handles macOS for you. Manual route:

- **macOS**: `xattr -dr com.apple.quarantine /usr/local/bin/syn`
- **Windows**: SmartScreen prompts once → *More info → Run anyway*.
- **Linux**: nothing special.

Verify the bytes against the checksum on the release page:

```bash
shasum -a 256 ~/Downloads/synapse-*-*.tar.gz
```

---

## License

MIT — see [LICENSE](./LICENSE).

---

<div align="center">

<img src="https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/assets/lil-syn-firing.svg" width="100" alt="Lil Syn celebrating" />

<sub>Built with care.</sub>

</div>
