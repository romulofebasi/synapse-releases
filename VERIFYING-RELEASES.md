# Verifying a Synapse release

A release signature and checksum help authenticate the bytes you downloaded. Workspace integrity checks answer a different question. Neither establishes general factual truth or freedom from defects.

## Release evidence

The published archive workflow supplies platform archives, a `SHA256SUMS` manifest and a `SHA256SUMS.cosign.bundle`. The bundle contains signature/certificate evidence for the manifest. Verify the expected GitHub workflow identity and issuer, not merely the existence of a signature.

The expected identity is the tagged release workflow in `romulofebasi/synapse`, even though these assets are distributed through `synapse-releases`. npm provenance, when present for a selected package, is separate evidence; the npm launcher does not perform the archive workflow below.

<picture>
  <source media="(max-width: 600px)" srcset="assets/diagrams/release-trust-mobile.svg">
  <img src="assets/diagrams/release-trust.svg" alt="Manual verification: pin a release, authenticate its checksum manifest, compare the selected archive's SHA-256, then inspect the installed executable.">
</picture>

## Verify (one time: install cosign)

Install cosign from the [official project installation instructions](https://docs.sigstore.dev/cosign/system_config/installation/), then use the format supported by your installed version. Retain the exact release tag, archive, manifest and signature bundle together.

## Verify a download

Choose a tagged release and target. Download its archive, `SHA256SUMS` and `SHA256SUMS.cosign.bundle`. Before extraction, authenticate the manifest:

```bash
cosign verify-blob \
  --bundle SHA256SUMS.cosign.bundle \
  --certificate-identity-regexp '^https://github.com/romulofebasi/synapse/\.github/workflows/release\.yml@refs/tags/v' \
  --certificate-oidc-issuer 'https://token.actions.githubusercontent.com' \
  SHA256SUMS
```

Inspect the verified tag identity against your selected tag; the example expression accepts the project's `v` tag family. A compatible cosign version may support a stricter exact certificate identity for the chosen tag. An unexpected identity, missing bundle or verification failure stops this manual workflow.

Then compare the selected archive to its entry in the authenticated manifest. On systems providing GNU `sha256sum`:

```bash
sha256sum --check --ignore-missing SHA256SUMS
```

Confirm that the **specific archive you plan to extract** is present, appears in the authenticated manifest and reports `OK`. A successful check of some other file is insufficient. On macOS, `shasum -a 256 <archive>` prints the selected archive's digest for exact comparison with its manifest entry; replace the placeholder with the actual filename.

Require both signature verification and exact checksum agreement. Do not extract/run the archive when either check is absent, failed or applies to the wrong artifact. Archive provenance and subsequent binary adoption remain separate from source-code review and operating-system signing/notarization policy.

## What this proves (and does not)

The checks authenticate a manifest under the expected workflow identity and establish that your selected archive matches a listed digest. They do not prove bug-free source, Apple notarization, complete supply-chain safety, workspace integrity or the truth of a stored claim.

`syn verify` separately reports documented properties of a selected workspace and release. Inspect named checks, exclusions, prerequisites and skipped signing. It is not a universal proof that no silent alteration ever occurred.

## Convenience installer behavior

The current [installer](install.sh) is **best-effort**, rather than the strict manual policy above:

| Condition | Current behavior |
| :-- | :-- |
| Manifest, matching entry and local hash utility are available | Compare the archive digest; a detected mismatch stops installation. |
| Checksum manifest cannot be downloaded | Warn and continue without checksum verification. |
| Matching manifest entry or local hash utility is unavailable | The checksum comparison can be skipped. |
| cosign and signature bundle are available | Attempt signature verification. |
| Signature verification fails | Warn and continue on the checksum path. |
| cosign or bundle is unavailable | Signature verification can be skipped. |

Review the script before executing it. Setting `SYNAPSE_VERSION` pins the requested tag, but does not make these optional checks mandatory. Use the explicit manual workflow when both checks are required by your installation policy. This documentation update does not change the installer.
