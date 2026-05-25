<div align="center">

<img src="https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/assets/wordmark-horizontal.png" width="800" alt="Synapse — second brain · cli + mcp" />

<br/>

**Public binaries for [Synapse](https://github.com/romulofebasi/synapse), the second-brain CLI + MCP server.**

[![Latest release](https://img.shields.io/github/v/release/romulofebasi/synapse-releases?label=latest&color=5B3EE0)](https://github.com/romulofebasi/synapse-releases/releases/latest)
[![Install](https://img.shields.io/badge/install-curl%20%7C%20sh-FFB454.svg)](#install)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

</div>

---

This repository is the **public mirror** of the Synapse releases.

- The **source code** lives in the private repository [`romulofebasi/synapse`](https://github.com/romulofebasi/synapse).
- Every tag pushed there triggers a workflow that **copies the cross-compiled binaries here**, so they can be downloaded without GitHub authentication.
- This split keeps the source private (for now) while letting anyone install the CLI in one command.

There is **no source code in this repository**. Issues and feature requests belong on the source repo (which is currently invite-only — open a discussion if you need access).

---

## Install

### One-liner (macOS, Linux)

```bash
curl -fsSL https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/install.sh | sh
```

The installer detects your OS and architecture, downloads the right binary, and drops `syn` into `/usr/local/bin/` (override with `INSTALL_DIR=~/.local/bin`).

### Pin a specific version

```bash
curl -fsSL https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/install.sh | SYNAPSE_VERSION=v0.1.0 sh
```

### Manual download

Grab the archive for your target from the [latest release](https://github.com/romulofebasi/synapse-releases/releases/latest), extract, and put `syn` (or `syn.exe`) on your `PATH`.

Available targets:

| OS | Architecture | Asset |
|---|---|---|
| macOS | Apple Silicon (M1+) | `synapse-<version>-aarch64-apple-darwin.tar.gz` |
| macOS | Intel | `synapse-<version>-x86_64-apple-darwin.tar.gz` |
| Linux | x86_64 | `synapse-<version>-x86_64-unknown-linux-gnu.tar.gz` |
| Linux | ARM64 | `synapse-<version>-aarch64-unknown-linux-gnu.tar.gz` |
| Windows | x86_64 | `synapse-<version>-x86_64-pc-windows-msvc.zip` |

### Windows (PowerShell)

```powershell
$ver = "v0.1.0"
$url = "https://github.com/romulofebasi/synapse-releases/releases/download/$ver/synapse-$($ver.Substring(1))-x86_64-pc-windows-msvc.zip"
$tmp = "$env:TEMP\synapse.zip"
Invoke-WebRequest $url -OutFile $tmp
Expand-Archive $tmp -DestinationPath $env:TEMP -Force
Move-Item "$env:TEMP\synapse-$($ver.Substring(1))-x86_64-pc-windows-msvc\syn.exe" "$HOME\bin\syn.exe" -Force
```

---

## Verify

The binaries are **not yet code-signed** (Apple Developer ID / Microsoft Authenticode arrive in v1.0). Until then:

- **macOS**: after install, `xattr -dr com.apple.quarantine $(which syn)` to clear the Gatekeeper attribute.
- **Windows**: SmartScreen prompts once; choose "More info → Run anyway".
- **Linux**: nothing special.

You can confirm the build by comparing the SHA-256 against the GitHub release page:

```bash
shasum -a 256 ~/Downloads/synapse-0.1.0-*.tar.gz
```

---

## Where do the binaries come from?

A GitHub Actions workflow in the source repo (`.github/workflows/release.yml`) builds five targets on every `v*.*.*` tag, then a second workflow (`mirror-release.yml`) reuploads them here. No human hands touch the binaries between `cargo build --release` and the asset you download.

---

## License

The build assets are MIT-licensed (mirroring the source). See [LICENSE](./LICENSE).

---

<div align="center">

<img src="https://raw.githubusercontent.com/romulofebasi/synapse-releases/main/assets/lil-syn-firing.svg" width="100" alt="Lil Syn celebrating with gold sparks" />

<sub>Built with care · Lil Syn approves · <a href="https://github.com/romulofebasi/synapse">source</a></sub>

</div>
