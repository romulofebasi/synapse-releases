# Synapse 1.5.1 publication verification

The actual `v1.5.1` release from reviewed commit `23ba013d9b57588a58faf6c7ba4b16a9ecd3085f` passed source, public mirror, npm byte comparison and host launcher verification. This is a separate read-only verification of published bytes, performed by the producer-repair author. It does not replace the separate independent source and mutation review or convert local fixture controls into publication proof. The [machine receipt](receipt.json) records exact hashes, workflow identities, limits and retained nonpassing attempts.

| Boundary | Actual result |
| --- | --- |
| Source release | [Run 39103431019](https://github.com/romulofebasi/synapse/actions/runs/39103431019) passed tagged inputs, four platform builds and publication. |
| Public mirror | [Run 39104711966](https://github.com/romulofebasi/synapse/actions/runs/39104711966) passed automatically. All seven names, sizes, API SHA256 digests and notes match the source release. |
| Asset admission | Seven complete nonzero assets and the exact five-entry manifest were checked before any archive parsing. |
| Signature | Real cosign verified `SHA256SUMS` against the exact source workflow identity for `refs/tags/v1.5.1` and issuer `https://token.actions.githubusercontent.com`. |
| Canonical documents | README, LICENSE and the full CHANGELOG in all four actual archives equal immutable Git blobs. This includes the actual hosted Windows ZIP. No line ending normalization was applied. |
| npm publication | [Run 39104728647](https://github.com/romulofebasi/synapse-releases/actions/runs/39104728647) passed automatically. A fresh complete acquisition checked five exact package names and versions, SHA512 SRI and advertised provenance. |
| Binary comparison | All four npm platform binaries equal their authenticated source archive binaries in size and SHA256. |
| Host launcher | A private HOME, cache and npm configuration install with `--ignore-scripts` passed. The installed launcher and host binary matched checked npm bytes before `node syn.js --version` exited zero with `syn 1.5.1`. |

The macOS arm64 binary SHA256 is `6d9bfddf188475767b94712d8971cff9fa66f9aa088a4b3805f9ac59b531f401`, size 37,689,216 bytes. It was exported from the authenticated public archive for a separate Soma compatibility check. This report does not incorporate that separate product test.

Two initial cosign wrapper invocations had incompatible relative asset paths and exited nonzero. Their stderr was not retained by the frozen wrapper. An actual absolute-path diagnostic and the unchanged wrapper with absolute paths then verified the same sealed bytes. Those setup failures remain recorded and are not signature failures or passing evidence.

The first npm acquisition stopped at a Windows `E404` after downloading three Unix packages. A fresh exact Windows query later succeeded, and a separate complete acquisition passed. The original incomplete fetch and 404 observations remain retained. One registry diagnostic initially mishandled a JSON string error response and was corrected before the typed response was recorded. No package was republished, and no cause for the temporary registry availability gap is asserted.

Only macOS arm64 executed locally, through the launcher version command. Other platform results establish byte agreement plus their hosted build outcomes. Source signature verification was actually performed; npm provenance signature verification, independent reproducible builds, safe-code, live inference, notarization and other platform execution are outside this proof. Raw logs, caches, bundles and downloads remain private. This audit did not republish v1.5.0 or overwrite existing protected binaries. Its historical evidence remains separate.
