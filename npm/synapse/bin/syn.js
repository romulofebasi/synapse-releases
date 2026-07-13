#!/usr/bin/env node
// npm launcher for the `syn` binary (SYN-103 / #83).
//
// `syn` is a Rust binary, not JS. This package ships the platform binary through
// per-platform optionalDependencies (the esbuild/swc model): npm installs only
// the sub-package whose `os`/`cpu` match, and this launcher resolves it and execs
// the real binary. No runtime download — the binary is in the installed tarball
// (immutable, npm-provenance-attested), the same trust story as the cosign-signed
// release archives.
'use strict';

const { spawnSync } = require('node:child_process');
const fs = require('node:fs');

// npm arch names → the release target's arch token; platform → token.
const PLATFORM = process.platform; // 'darwin' | 'linux' | 'win32' | ...
const ARCH = process.arch; // 'arm64' | 'x64' | ...

// The supported set mirrors the release build matrix: macOS is Apple-Silicon
// only (SYN-174 drops Intel), Linux is x64 + arm64, Windows is x64.
const SUPPORTED = new Set([
  'darwin-arm64',
  'linux-x64',
  'linux-arm64',
  'win32-x64',
]);

const key = `${PLATFORM}-${ARCH}`;
const pkg = `@febasi/synapse-${key}`;
const binName = PLATFORM === 'win32' ? 'syn.exe' : 'syn';

function fail(msg) {
  process.stderr.write(`synapse: ${msg}\n`);
  process.stderr.write(
    'Prebuilt targets are darwin-arm64, linux-x64, linux-arm64, and win32-x64.\n' +
      'On other platforms, download a signed archive from ' +
      'https://github.com/romulofebasi/synapse-releases/releases\n',
  );
  process.exit(1);
}

if (!SUPPORTED.has(key)) {
  fail(`no prebuilt binary for ${key}.`);
}

let binPath;
try {
  binPath = require.resolve(`${pkg}/${binName}`);
} catch {
  fail(
    `the platform package ${pkg} is not installed. If you used ` +
      '--no-optional or --ignore-optional, reinstall without it.',
  );
}

// npm preserves the executable bit from the packed tarball, but be defensive:
// a restrictive umask or a copy that dropped the mode would make exec fail.
if (PLATFORM !== 'win32') {
  try {
    fs.accessSync(binPath, fs.constants.X_OK);
  } catch {
    try {
      fs.chmodSync(binPath, 0o755);
    } catch {
      /* best-effort; spawn will report the real error below */
    }
  }
}

const res = spawnSync(binPath, process.argv.slice(2), { stdio: 'inherit' });
if (res.error) {
  fail(`failed to launch ${binPath}: ${res.error.message}`);
}
// Forward the child's exit code (or 1 if it was signalled/killed).
process.exit(res.status === null ? 1 : res.status);
