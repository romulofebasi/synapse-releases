# Security Policy

## Reporting a vulnerability

Please report security issues privately, never in a public issue or pull
request.

Use GitHub's private vulnerability reporting on this repository: the
**Report a vulnerability** button under the **Security** tab, or
[this link](https://github.com/romulofebasi/synapse-releases/security/advisories/new).

We aim to acknowledge a report within a few business days and will keep you
updated as we investigate. Once a fix ships we are glad to credit you, unless
you prefer to stay anonymous.

## Scope

Synapse is local-first and ships no telemetry; your notes and queries stay on
your machine. Relevant areas include the `syn` binary's handling of workspace
data, the MCP server surface, the install script, and the npm launcher.

Release archives are signed with keyless Sigstore/cosign and npm builds carry
provenance, so you can verify that a build came from this project before you run
it. See [VERIFYING-RELEASES.md](../VERIFYING-RELEASES.md).

## Supported versions

Security fixes target the latest released version. Please reproduce on the
latest release before reporting.
