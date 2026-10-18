# Independent downstream publication review

The original implementation at `f142eb5a5f22442020a84fa5929eee2fe7954881` had two confirmed ZIP identity defects outside its original fixture coverage. A NUL suffix in the original member name was hidden by Python's filename normalization, and a directory Unix type on a file-style name could supply the selected binary. Two independent methods failed through `AssertionError: 0 != 1`; both invalid fixtures reached all five recording publication calls. No real registry operation occurred.

Test-only commit `6f50224` captured those regressions before author correction `43f716d4b5ea9081e6e9a9cdf5f358dd33d4021f`. The correction requires the original name to match the parsed name and ZIP type/directory metadata to agree. The original regression methods and their helpers remain unchanged. Test-only commit `2999ca3` adds the remaining coverage and makes failed subtests independent of earlier fixture leftovers.

| Campaign | Executed scope | Assertion kills | Survivors | Invalid |
| --- | --- | --- | --- | --- |
| Original frozen round | 25 variants, unchanged original 16-method suite | 13 | 9 | 3 |
| Strengthened original gaps | 12 variants, frozen 30-method suite | 12 | 0 | 0 |
| Corrective ZIP guard removals | 3 variants, same frozen 30-method suite | 3 | 0 | 0 |

The original survivors and invalid attempts are preserved. Eleven strengthened replays apply the exact original patches unchanged. The ZIP metadata variant was adapted to the corrected guard, so that replay is explicitly not described as a byte-identical patch. The first workflow-expression variant changes two downstream shell uses and is killed by the explicit source assertion; strict tag guards remain present. It is not a new command-execution exploit claim.

The original registry variants exposed `FileExistsError` after failed subtests; the interleaved-publication variant also exposed `JSONDecodeError` before the relevant assertion. These attempts are invalid, not kills. After the original round was frozen, fixture admission resets only owned temporary files, and the no-publication assertion runs before error-output parsing. The strengthened tests then kill the same registry and inventory patches through assertions.

| Boundary | Actual controlled evidence |
| --- | --- |
| Tags and workflow source | Hostile and malformed tags stop before outputs/downloads; bounded stable versions stay literal; generated shell contains no event expressions. |
| Signature | A nonzero verifier result stops preparation and npm; calls pin the exact upstream tagged workflow and GitHub issuer. |
| Signed inventory | Exactly seven assets and five signed entries; archive and source-receipt tampering, duplicate manifest lines and malformed source evidence are refused. |
| Archive selection | Expected version/target paths, unique members, regular binary metadata, original ZIP name, changelog hash and exact selected bytes are checked before npm. |
| Producer layout | Explicit metadata-free real local tar produces root directory plus four files. ZIP root-directory compatibility covers representative Unix, DOS and unspecified attributes. |
| Registry and publication | All five observations precede publication; only structured E404 admits absence; matching existing versions are preserved; package versions and provenance flags are checked. |

The final restored production passes all 30 methods, 16 original plus 14 independent, with no failures, errors or skips. Its typed result capture completed in 17.985 seconds. Source and test hashes before and after each experiment, exact patches, typed assertion identities, original invalid types and log digests are in `evidence.json`. Raw logs and capture tools remain outside Git in restricted local storage. No reviewer production fix is included.

The checked-in suites can be run directly:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-npm-publish-tests.py -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/check-npm-independent-tests.py -v
```

The campaign executed those unchanged test modules through the reviewed Python unittest typed result collector. It classified every runtime/setup error as invalid and restored each production source before the next experiment. The separately evolving required-module CI gate is reviewed by the root team; its larger suite count is not this reviewer's execution claim.

The producer followup found that unmodified local BSD tar includes AppleDouble metadata: ten members rather than five for owned inputs. The initial five-member test precondition failure was a compatibility observation, not a consumer assertion RED. The strict consumer correctly refused those extra members. Author source correction `76ea7e09d4191791a32195eafd972bc5a9fc0f76` supplies `COPYFILE_DISABLE=1` without weakening consumer policy. A separate actual source-shell regression and environment-removal negative control prove that setting reaches real tar. The restored source release suites pass 13 original and 10 independent methods. Those experiments are separate from the downstream mutation counts.

External gh, cosign and npm executables were controlled fixtures. This proves invocation and refusal behavior, not real Sigstore cryptography, GitHub dispatch, registry availability or npm OIDC configuration. Windows 7z was unavailable; its representative ZIP fixtures are not actual Windows execution. No archived binary, Rust build, install, tag, release or remote publication was executed. Remote publication is not atomic across packages; a later real publish failure can leave earlier packages published, and matching existing versions are preserved on a fresh retry. Required remote checks and release authorization remain separate.
