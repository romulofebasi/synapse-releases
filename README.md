<div align="center">

<img src="https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/assets/wordmark-horizontal.png" width="800" alt="Synapse — second brain · cli + mcp" />

<br/>

*A local-first, queryable second brain for AI-augmented developers — six entity types (projects, people, orgs, APIs, tasks, notes), one graph, two doors: your terminal and your AI over [MCP](https://modelcontextprotocol.io).*

[![Latest release](https://img.shields.io/github/v/release/romulofebasi/synapse-releases?label=latest&color=5B3EE0)](https://github.com/romulofebasi/synapse-releases/releases/latest)
[![Install](https://img.shields.io/badge/install-curl%20%7C%20sh-FFB454.svg)](#install)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

## Install

### One-liner (macOS, Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/install.sh | sh
```

Detects your OS and CPU, downloads the right binary, drops `syn` into `/usr/local/bin/` (override with `INSTALL_DIR=~/.local/bin`), and clears the macOS Gatekeeper attribute for you. Pin a version with `SYNAPSE_VERSION=v0.5.0`.

### Windows (PowerShell)

```powershell
$ver = "v0.5.0"   # latest tag from the releases page
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
| **Disk** | ~25 MB binary. Semantic search downloads **~920 MB** of models on first use (once, shared across workspaces) — see [QUICKSTART §4](./QUICKSTART.md#4-search-by-meaning-optional). Without it you still get keyword + graph search and the full MCP server. |
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

The five-minute walkthrough — entities, the graph, semantic search, and wiring up your AI with the propose/accept loop — is in **[QUICKSTART.md](./QUICKSTART.md)**.

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
