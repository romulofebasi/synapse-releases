# @febasi/synapse

Operational memory for agents, with governed changes, preserved history, and explicit integrity checks.

Synapse connects project knowledge in Markdown and Git. Its CLI and MCP server let people and agents retrieve context and submit supported changes through an explicit governed workflow. Verification reports documented integrity properties and coverage limits; it does not certify every fact or eliminate all natural-language contradictions.

## Install

```bash
npx @febasi/synapse --help
npm install -g @febasi/synapse
syn --version
```

For a reproducible installation, select an exact published package version and retain the lockfile or installation record. Discover the installed commands with `syn --help`; development documentation can describe a newer contract.

## How the binary is delivered

The npm package requires Node.js 18 or later for its launcher. The actual `syn` program is a compiled Rust executable supplied by a matching optional companion package. The launcher resolves the installed binary and forwards arguments; it does not download a binary at launch.

Supported companion targets are `darwin-arm64`, `linux-x64`, `linux-arm64` and `win32-x64`. Keep npm optional dependencies enabled. If the platform is unsupported, check whether the [selected release assets](https://github.com/romulofebasi/synapse-releases/releases) provide a compatible target before downloading anything.

The executable can separately download consented models or contact explicitly configured integrations. A launcher without a binary download is not a claim that all commands are network-free. See [models and privacy](https://github.com/romulofebasi/synapse-releases/blob/main/MODELS.md).

## Trust

Published npm provenance, when present for the selected package, links the artifact to its stated build. GitHub release archives have a separate signed checksum-manifest workflow. Inspect the actual published evidence and expected identity; the launcher itself does not run cosign or authenticate a GitHub archive.

For manual archives, [verify both the manifest signature and the archive checksum](https://github.com/romulofebasi/synapse-releases/blob/main/VERIFYING-RELEASES.md) before use. Artifact provenance does not establish freedom from defects, notarization or factual truth in a knowledge store.

## Learn more

[Public documentation and onboarding](https://github.com/romulofebasi/synapse-releases). Local Synapse does not require a Synapse account; connected services keep their own access requirements.

License: MIT. See the notices distributed with the selected artifact.
