# Contributing to Synapse

Thanks for helping make Synapse better. Synapse is a closed-source product
distributed through this public mirror, so how you contribute depends on what
you want to change.

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
`skills/` all live here and accept pull requests. Keep prose free of em-dashes
(house style) and keep each change focused.

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
