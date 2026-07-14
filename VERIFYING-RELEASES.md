# Verifying a Synapse release

Synapse's promise is *provable non-corruption*, so the binaries you download are
**signed**. You can prove they came from this project's release workflow and were
not tampered with in transit.

Signing is **keyless [Sigstore](https://www.sigstore.dev/) / cosign**: there is no
long-lived private key to steal or rotate. The signing identity **is** the GitHub
Actions release workflow on the pushed tag, and every signature is recorded in the
public [Rekor](https://docs.sigstore.dev/logging/overview/) transparency log. npm
builds additionally carry [provenance](https://docs.npmjs.com/generating-provenance-statements),
tying each package back to the exact CI run that built it. Each GitHub release
attaches:

- the platform archives (`synapse-<version>-<target>.tar.gz` or `.zip`),
- `SHA256SUMS`, a checksum manifest over every archive,
- `SHA256SUMS.cosign.bundle`, the cosign signature, certificate, and Rekor entry
  for `SHA256SUMS`.

> The one-line installer (`install.sh`) verifies the checksum automatically, and
> the cosign signature too when `cosign` is on your PATH. The steps below are the
> manual equivalent.

## Verify (one time: install cosign)

Install [cosign](https://docs.sigstore.dev/cosign/system_config/installation/)
(`brew install cosign`, or the release binary from sigstore/cosign).

## Verify a download

From a directory holding the release assets (`SHA256SUMS`,
`SHA256SUMS.cosign.bundle`, and the archive you downloaded):

```bash
# 1. Prove the checksum manifest was signed by the release workflow.
cosign verify-blob \
  --bundle SHA256SUMS.cosign.bundle \
  --certificate-identity-regexp '^https://github.com/romulofebasi/synapse/\.github/workflows/release\.yml@refs/tags/v' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  SHA256SUMS
# => "Verified OK"

# 2. Prove your archive matches the (now trusted) manifest.
sha256sum --check --ignore-missing SHA256SUMS
# => synapse-<version>-<target>.tar.gz: OK
```

Both steps must pass. Step 1 fails if the manifest was not signed by this
project's release workflow (a forged or re-hosted artifact set); step 2 fails if
the archive was altered after signing.

## What this proves (and does not)

- **Proves:** the `SHA256SUMS` was produced by the Synapse release workflow on a
  `v*` tag, is logged in Rekor, and your archive hashes to an entry in it.
  Provenance and integrity, offline-checkable.
- **Does not prove:** that the source is bug-free, only that the binary is the one
  this project's CI built and published.

Companion to `syn verify` (which proves your *memory* was not silently corrupted):
this proves the *tool itself* was not.
