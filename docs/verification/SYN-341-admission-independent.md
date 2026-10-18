# SYN-341: Independent distribution admission review

The strict Python CI admission boundary is accepted within the reviewed scope at
`b57f5f192567d6ec85db5e5e0322cfb485d10e55`. Independent review found two actual
false successes, preserved assertion regressions before the corrections, and
verified the corrections through the actual gate CLI. This review concerns test
admission only. Archive authentication and publication review are separate.

## Required evidence

[check-distribution.py](../../scripts/check-distribution.py) explicitly loads the
author, independent and admission-control modules, requiring at least 16, 14 and
9 cases respectively. Missing, empty or undersized modules cannot pass. Admission
uses unittest's result API and requires every selected case to run successfully,
with no skips or expected failures. Success-like console text does not grant
admission. The [CI workflow](../../.github/workflows/ci.yml) invokes this gate
directly, rather than interpreting test output text.

## Frozen rounds

| Round | Source | Observed evidence |
| :-- | :-- | :-- |
| Original admission | `6020430` | Seven original public controls passed. A private complete 36-case fixture passed, while missing, empty, undersized, skipped, expected-failure, assertion, runner-error, import-error and misleading-success-text controls were rejected. A separate required-module termination case produced a genuine false success and one independent assertion RED. |
| Import correction | `5addc49` | The original import assertion passed unchanged. Eight public controls and a separate 38-case fixture passed. Removing the import guard produced one relevant assertion failure against the unchanged eight controls. A separate selection-termination regression still failed on pristine source, exposing the second false success. |
| Selection correction | `b57f5f1` | The original selection assertion passed unchanged. Nine public controls passed. The actual complete 39-case distribution suite passed. Removing only the main termination guard, while retaining the import guard, produced one relevant assertion failure against the unchanged nine controls. Restoring the gate returned all nine controls to GREEN. |

The first correction rejects successful premature termination during required
module import. The second also rejects termination during unittest selection at
the authoritative main boundary. Neither is accepted merely because another
exception or a nonzero runner exit occurred: the retained independent regressions
observed erroneous CLI success and failed an explicit assertion before correction.

The original 36-case fixture uses synthetic 16-case and 13-case modules plus the
actual seven admission controls. The later 38-case fixture uses synthetic 16-case
and 14-case modules plus eight actual controls. The final 39-case fixture uses
synthetic 16-case and 14-case modules plus nine actual controls. These are separate
admission fixtures, never substitutes for the genuine publication suites.

## Final verification

In a private copy pinned to `b57f5f1`, independent execution of:

```sh
python3 scripts/check-distribution.py
```

passed all 39 actual methods in 22.105 seconds, exit0, with no errors, failures,
skips or expected failures. This includes the actual 16 author methods, 14
independent methods and nine admission controls. A separate synthetic 39-case
fixture passed with the current module thresholds.

The two targeted mutation rounds are distinct. Each produced exactly one
assertion kill, with no runner errors, survivors or invalid mutation attempts.
The tests were unchanged during each round. Final test SHA-256 before and after
the main-guard mutation was
`3b05ad5564b458154edab3955898c9490f0b224c33af3b9df7b942aa8ba95852`.
The [allowlisted receipt](SYN-341-admission-independent.json) retains the source,
test and private evidence digests. Raw logs and temporary fixture paths remain
private. The original rounds are retained without relabeling their counts or
source revisions.

## Limits

This is an independent local unittest review, not a claim that a separate
structured evidence adapter ran. It does not sandbox arbitrary test code. The
publication suites use recording `gh`, `cosign` and `npm` fakes; no genuine
signature verification, platform build, registry authentication or npm publish
is established here. Exact final-head hosted CI and any actual publication remain
separate gates. The convenience installer remains unchanged and best-effort.

Follow the [Febasi test-first standard](https://github.com/romulofebasi/febasi-standards/blob/main/skills/test-first/SKILL.md)
for further corrections: preserve observable assertion RED and original mutation
results, restore the full relevant GREEN, and retain independent challenge scope.
