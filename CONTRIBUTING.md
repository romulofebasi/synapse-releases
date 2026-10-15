# Contributing to Synapse

Synapse is distributed through this public repository. The Rust product source
is maintained separately, so the contribution path depends on what you want
to change.

## Report a bug

Open a [bug report](https://github.com/romulofebasi/synapse-releases/issues/new?template=bug_report.yml).
Please include your `syn --version`, your OS and CPU, how you installed (npm,
the install script, or a manual archive), and the output of `syn doctor`. When
the issue is about memory integrity, a `syn verify` report helps a lot.

## Request a feature or share an idea

Open a [feature request](https://github.com/romulofebasi/synapse-releases/issues/new?template=feature_request.yml).
Describe the problem you are trying to solve, not only the solution you have in
mind. Real workflows are the most useful thing you can give us.

## Fix the docs or the install script

The product source is private, but *this* repository is public. The docs
(`ONBOARDING.md`, `MODELS.md`, `BENCHMARKS_EXPLAINED.md`, `LLM.md`), the
`install.sh` script, the npm launcher under `npm/`, and the agent skill under
`skills/` all live here and accept pull requests. Write all maintained documentation, captions and agent instructions in English.
Do not use em dashes. Use sentences, commas, colons or parentheses while preserving
the original meaning. Follow the [Febasi writing rule](https://github.com/romulofebasi/febasi-standards/blob/main/CONVENTIONS.md#0-writing-rule-applies-everywhere).
Keep each change focused.

## Evidence and visual review

Distinguish the selected published release from current development contracts. Discover actual installed commands and MCP schemas instead of hardcoding a tool count. Describe verification through named checks and limitations; do not promise universal non-corruption, semantic truth or automatic organizational authority.

For documentation visuals, follow [VISUAL_GUIDE.md](VISUAL_GUIDE.md). Keep SVG editable, self-contained and accompanied by alt text and a prose equivalent. Inspect desktop and narrow layouts. Preserve historical anchors when rewriting headings or replacing translated sections. Label synthetic or historical measurements and retain their denominator.

Installer and launcher changes require separate runtime review. The current installer can skip or warn through missing/failed verification; documentation must not describe it as a strict fail-closed verifier. Do not change binaries, release tags or historical artifacts as part of a documentation cleanup.

Public reports must exclude credentials, raw private knowledge, filesystem paths and sensitive verification details. Include a sanitized reproduction, installed version, selected model/profile and clearly bounded evidence instead.

## What cannot be a pull request here

The Rust source of the `syn` binary lives in a separate private repository, so
code changes to the CLI, the MCP server, or the semantic layer cannot be sent
as pull requests. File a bug or a feature request instead and we will pick it
up.

## Security

Please do not open a public issue for a security vulnerability. See
[SECURITY.md](./.github/SECURITY.md) for private disclosure.

## Code of conduct

Be respectful and assume good faith. Harassment or abuse is not tolerated.
