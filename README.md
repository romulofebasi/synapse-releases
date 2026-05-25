<div align="center">

<img src="https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/assets/wordmark-horizontal.png" width="800" alt="Synapse — second brain · cli + mcp" />

<br/>

*Install Synapse — the queryable second brain for AI-augmented developers.*

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

The installer detects your OS and CPU, downloads the right binary, drops `syn` into `/usr/local/bin/` (override with `INSTALL_DIR=~/.local/bin`), and clears the macOS Gatekeeper attribute for you.

### Windows (PowerShell)

```powershell
$ver = "v0.1.0"
$url = "https://github.com/romulofebasi/synapse-releases/releases/download/$ver/synapse-$($ver.Substring(1))-x86_64-pc-windows-msvc.zip"
$tmp = "$env:TEMP\synapse.zip"
Invoke-WebRequest $url -OutFile $tmp
Expand-Archive $tmp -DestinationPath $env:TEMP -Force
Move-Item "$env:TEMP\synapse-$($ver.Substring(1))-x86_64-pc-windows-msvc\syn.exe" "$HOME\bin\syn.exe" -Force
```

### Pin a specific version

```bash
curl -fsSL https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/install.sh | SYNAPSE_VERSION=v0.1.0 sh
```

### Manual download

Pick your platform from the [latest release](https://github.com/romulofebasi/synapse-releases/releases/latest), extract, and put `syn` (or `syn.exe`) on your `PATH`.

| OS | Architecture | Asset |
|---|---|---|
| macOS | Apple Silicon (M1+) | `synapse-<version>-aarch64-apple-darwin.tar.gz` |
| macOS | Intel | `synapse-<version>-x86_64-apple-darwin.tar.gz` |
| Linux | x86_64 | `synapse-<version>-x86_64-unknown-linux-gnu.tar.gz` |
| Linux | ARM64 | `synapse-<version>-aarch64-unknown-linux-gnu.tar.gz` |
| Windows | x86_64 | `synapse-<version>-x86_64-pc-windows-msvc.zip` |

---

## First steps

```bash
syn init ~/brain
cd ~/brain
syn project add "Projeto Alfa"
syn person  add "Maria Silva" --email maria@empresa.com
syn search  alfa
syn mcp     # plug into Claude Code for AI access
```

Full documentation, tutorial, MCP wiring and command reference live in the [Synapse docs](https://github.com/romulofebasi/synapse#documentation).

---

## A note on Gatekeeper / SmartScreen

The binaries are not yet code-signed (signing arrives with v1.0). The one-line installer handles macOS for you. If you went the manual route:

- **macOS**: `xattr -dr com.apple.quarantine /usr/local/bin/syn`
- **Windows**: SmartScreen prompts once on first run → *More info → Run anyway*.
- **Linux**: nothing special.

Optional sanity check before you trust the bytes:

```bash
shasum -a 256 ~/Downloads/synapse-0.1.0-*.tar.gz
```

Compare against the value on the release page.

---

## License

MIT — see [LICENSE](./LICENSE).

---

<div align="center">

<img src="https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/assets/lil-syn-firing.svg" width="100" alt="Lil Syn celebrating" />

<sub>Built with care · <a href="https://github.com/romulofebasi/synapse">Synapse on GitHub</a></sub>

</div>
