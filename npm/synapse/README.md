# @febasi/synapse

Governed, local-first memory for AI agents.

Synapse gives your AI agents a Markdown knowledge graph they can read and propose
changes to, but never silently corrupt. Every write goes through a review gate,
carries provenance, and stays reversible, and `syn verify` proves the memory was
not tampered with. This package ships the `syn` command line tool and its MCP
server as a prebuilt binary.

## Install

```bash
# Run it once, without installing:
npx @febasi/synapse --help

# Or install the syn command globally:
npm install -g @febasi/synapse
syn --version
```

## How the binary is delivered

`syn` is a compiled Rust program, not JavaScript. This package is a small
launcher; the real binary ships in a per-platform companion package, and npm
installs only the one that matches your operating system and CPU. There is no
download at runtime and nothing is fetched from the network when you run `syn`.

Supported targets are `darwin-arm64` (Apple Silicon), `linux-x64`, `linux-arm64`,
and `win32-x64`. On any other platform, download a signed archive from the
[releases page](https://github.com/romulofebasi/synapse-releases/releases).

## Trust

Release builds are published with npm provenance, which ties each package back to
the exact GitHub Actions run that built it. The downloadable archives are also
signed with keyless Sigstore cosign. In short, you can prove that the tool you
installed is the one this project built and published.

## Learn more

Documentation, onboarding, and the model notes live in the public mirror:
<https://github.com/romulofebasi/synapse-releases>.

License: MIT.
