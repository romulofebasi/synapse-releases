#!/usr/bin/env python3
"""Exercise actual npm workflow shell steps with private files and recording external tools."""
import json
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tarfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class NpmWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="syn341-npm-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "scripts").mkdir()
        helper = ROOT / "scripts/publish-npm.py"
        if helper.exists():
            shutil.copyfile(helper, self.root / "scripts/publish-npm.py")
        shutil.copytree(ROOT / "npm", self.root / "npm")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        gh = self.bin / "gh"
        gh.write_text("#!" + sys.executable + "\nimport json,os,pathlib,sys\n" +
                      "with pathlib.Path(os.environ['OWNED_CALLS']).open('a') as log:log.write(json.dumps(sys.argv[1:])+'\\n')\n")
        gh.chmod(0o700)
        self.tag = "v1.5.0"
        self.environment = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ["PATH"],
            GITHUB_OUTPUT=str(self.root / "outputs"), GITHUB_REPOSITORY="romulofebasi/synapse-releases",
            TAG=self.tag, RELEASE_TAG=self.tag, OWNED_CALLS=str(self.root / "calls"), GH_TOKEN="synthetic-only")
        self.tool('gh', """
if os.environ.get('OWNED_SOURCE'):
 destination=pathlib.Path(sys.argv[sys.argv.index('--dir')+1]);destination.mkdir()
 for source in pathlib.Path(os.environ['OWNED_SOURCE']).iterdir():shutil.copyfile(source,destination/source.name)
""")
        self.tool('cosign', """
if os.environ.get('REPLACE_MANIFEST'):
 p=pathlib.Path('dl/SHA256SUMS');q=p.with_suffix('.new');q.write_bytes(p.read_bytes());q.replace(p)
sys.exit(int(os.environ.get('COSIGN_EXIT','0')))
""")
        self.tool('npm', """
if sys.argv[1:] == ['--version']: print(os.environ.get('NPM_VERSION','11.5.1'))
elif sys.argv[1]=='view':
 name=sys.argv[2].rsplit('@',1)[0];state=json.loads(os.environ.get('REGISTRY_RESULTS','{}')).get(name,'E404')
 if state=='exists':print(json.dumps('1.5.0'))
 elif state=='malformed':print('not JSON');sys.exit(1)
 else:print(json.dumps({'error':{'code':state}}));sys.exit(1)
elif sys.argv[1]=='publish':sys.exit(0)
else:sys.exit(2)
""")

    def tool(self, name, body):
        path = self.bin / name
        path.write_text('#!' + sys.executable + '\nimport json,os,pathlib,shutil,sys\n' +
            "with pathlib.Path(os.environ['OWNED_CALLS']).open('a') as f:f.write(json.dumps({'tool':pathlib.Path(sys.argv[0]).name,'args':sys.argv[1:],'cwd':os.getcwd()})+'\\n')\n" + body)
        path.chmod(0o700)

    def calls(self, tool=None):
        path = self.root / 'calls'
        rows = [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []
        return [row for row in rows if tool is None or row['tool'] == tool]

    def invoke(self, operation):
        return subprocess.run([sys.executable, str(self.root / 'scripts/publish-npm.py'), operation,
                               '--tag', self.tag], cwd=self.root, env=self.environment,
                              capture_output=True, text=True, timeout=15)

    def rejected(self, result, reason):
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout), {'status': 'rejected', 'reason': reason})
        self.assertFalse(self.calls('npm'), 'Rejected inputs must not reach any registry or publication call')

    def fixture(self):
        directory = self.root / 'dl'
        directory.mkdir()
        self.targets = [('aarch64-apple-darwin', 'tar.gz', 'syn'),
                        ('x86_64-unknown-linux-gnu', 'tar.gz', 'syn'),
                        ('aarch64-unknown-linux-gnu', 'tar.gz', 'syn'),
                        ('x86_64-pc-windows-msvc', 'zip', 'syn.exe')]
        self.changelog = b'## [1.5.0]\n- reviewed fixture\n'
        for target, suffix, binary in self.targets:
            self.archive(target, suffix, binary)
        self.metadata = {'schemaVersion': 1, 'tag': self.tag, 'version': '1.5.0', 'commit': 'a' * 40,
            'inputs': {'Cargo.toml': 'b' * 64, 'Cargo.lock': 'c' * 64,
                       'CHANGELOG.md': hashlib.sha256(self.changelog).hexdigest()}, 'notesSHA256': 'd' * 64}
        self.manifest()
        (directory / 'SHA256SUMS.cosign.bundle').write_bytes(b'synthetic verification boundary')

    def archive(self, target, suffix, binary, special=None):
        prefix = f'synapse-1.5.0-{target}'
        files = {binary: b'owned fixture bytes: ' + target.encode(), 'README.md': b'readme',
                 'LICENSE': b'MIT', 'CHANGELOG.md': self.changelog}
        path = self.root / 'dl' / f'{prefix}.{suffix}'
        if suffix == 'zip':
            with zipfile.ZipFile(path, 'w') as archive:
                for name, data in files.items():
                    archive.writestr(prefix + '/' + name, data)
        else:
            with tarfile.open(path, 'w:gz') as archive:
                for name, data in files.items():
                    entry = tarfile.TarInfo(prefix + '/' + name)
                    entry.size = len(data)
                    if special and name == binary:
                        entry.name = special if special != 'link' else prefix + '/' + name
                        if special == 'link':
                            entry.type = tarfile.SYMTYPE
                            entry.linkname = '../../outside'
                            entry.size = 0
                    archive.addfile(entry, io.BytesIO(data))

    def manifest(self):
        directory = self.root / 'dl'
        (directory / 'release-metadata.json').write_text(json.dumps(self.metadata))
        names = [p for p in directory.iterdir() if p.name not in ('SHA256SUMS', 'SHA256SUMS.cosign.bundle')]
        (directory / 'SHA256SUMS').write_text(''.join(
            f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in sorted(names)))

    def step(self, name):
        lines = (ROOT / ".github/workflows/npm-publish.yml").read_text().splitlines()
        start = lines.index("      - name: " + name)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("      - ")), len(lines))
        block = lines[start:end]
        run = next(i for i, line in enumerate(block) if line.strip() == "run: |")
        body = "\n".join(line[10:] if line.startswith("          ") else line for line in block[run + 1:])
        body = body.replace("${{ steps.v.outputs.tag }}", self.tag).replace("${{ github.repository }}", "romulofebasi/synapse-releases")
        self.assertNotIn("${{", body, "Unknown workflow expression is an invalid local fixture")
        return subprocess.run(["/bin/bash", "-e", "-o", "pipefail", "-c", body], cwd=self.root,
                              env=self.environment, capture_output=True, text=True, timeout=15)

    def test_hostile_tag_is_rejected_before_download_or_shell_side_effect(self):
        self.tag = "v1.5.0$(touch${IFS}owned-tag-executed)"
        self.environment.update(TAG=self.tag, RELEASE_TAG=self.tag)
        result = self.step("resolve tag")
        if result.returncode == 0:
            result = self.step("download release archives")
        self.assertNotEqual(result.returncode, 0, "Hostile tag bytes must stop before any download")
        self.assertFalse((self.root / "owned-tag-executed").exists(), "Tag bytes must never become shell code")
        self.assertFalse((self.root / "calls").exists(), "Invalid tag must not invoke gh or npm")

    def test_valid_tag_outputs_and_exact_download_inventory_remain_literal(self):
        self.fixture()
        source = self.root / 'upstream'
        (self.root / 'dl').rename(source)
        self.environment['OWNED_SOURCE'] = str(source)
        result = self.step('resolve tag')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.root / 'outputs').read_text(), 'tag=v1.5.0\nversion=1.5.0\n')
        result = self.step('download release archives')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        call, = self.calls('gh')
        self.assertEqual(call['args'][:5], ['release', 'download', self.tag, '--repo', 'romulofebasi/synapse-releases'])
        expected = {p.name for p in source.iterdir()}
        patterns = {call['args'][i + 1] for i, x in enumerate(call['args']) if x == '--pattern'}
        self.assertEqual(patterns, expected)
        self.assertEqual({p.name for p in (self.root / 'dl').iterdir()}, expected)
        self.assertNotIn('--clobber', call['args'])

    def test_authenticated_four_platform_bytes_and_launcher_are_prepared_without_execution(self):
        self.fixture()
        result = self.invoke('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        call, = self.calls('cosign')
        self.assertEqual(call['args'][call['args'].index('--certificate-identity') + 1],
                         'https://github.com/romulofebasi/synapse/.github/workflows/release.yml@refs/tags/v1.5.0')
        self.assertEqual(call['args'][call['args'].index('--certificate-oidc-issuer') + 1],
                         'https://token.actions.githubusercontent.com')
        mapping = [('darwin-arm64', self.targets[0]), ('linux-x64', self.targets[1]),
                   ('linux-arm64', self.targets[2]), ('win32-x64', self.targets[3])]
        for name, (target, _, binary) in mapping:
            self.assertEqual((self.root / 'prepared' / name / binary).read_bytes(), b'owned fixture bytes: ' + target.encode())
        launcher = json.loads((self.root / 'prepared/launcher/package.json').read_text())
        self.assertEqual(set(launcher['optionalDependencies'].values()), {'1.5.0'})
        self.assertEqual(len(launcher['optionalDependencies']), 4)
        self.assertEqual(json.loads((self.root / 'npm/synapse/package.json').read_text())['version'], '0.0.0')
        self.assertFalse(self.calls('npm'))

    def test_signature_failure_prevents_packages_registry_and_publication(self):
        self.fixture()
        self.environment['COSIGN_EXIT'] = '1'
        self.rejected(self.invoke('publish'), 'signature-verification-failed')
        self.assertFalse((self.root / 'prepared').exists())

    def test_fourth_archive_tamper_is_detected_before_any_registry_call(self):
        self.fixture()
        archive = next((self.root / 'dl').glob('*.zip'))
        archive.write_bytes(archive.read_bytes() + b'changed')
        self.rejected(self.invoke('publish'), 'signed-checksum-mismatch')

    def test_signed_source_receipt_cannot_select_another_tag(self):
        self.fixture()
        self.metadata.update(tag='v1.5.1', version='1.5.1')
        self.manifest()
        self.rejected(self.invoke('publish'), 'source-receipt-tag-mismatch')

    def test_receipt_requires_exact_commit_and_complete_input_digests(self):
        for change, reason in [({'commit': 'branch'}, 'invalid-source-commit'),
                               ({'inputs': {}}, 'invalid-source-inputs')]:
            with self.subTest(change=change):
                self.fixture()
                self.metadata.update(change)
                self.manifest()
                self.rejected(self.invoke('publish'), reason)
                shutil.rmtree(self.root / 'dl')
                (self.root / 'calls').unlink()

    def test_missing_extra_and_symlink_assets_are_not_authenticated(self):
        for kind in ('missing', 'extra', 'symlink'):
            with self.subTest(kind=kind):
                self.fixture()
                path = next((self.root / 'dl').glob('*.zip'))
                if kind == 'missing':
                    path.unlink()
                elif kind == 'extra':
                    (self.root / 'dl/extra').write_bytes(b'unknown')
                else:
                    path.unlink()
                    path.symlink_to(self.root / 'npm/synapse/README.md')
                self.rejected(self.invoke('publish'), 'missing-or-unsafe-file' if kind == 'symlink' else 'incomplete-release-inventory')
                self.assertFalse(self.calls('cosign'))
                shutil.rmtree(self.root / 'dl')

    def test_traversal_and_link_members_are_never_extracted(self):
        for special, reason in [('../../outside', 'unexpected-archive-member'), ('link', 'unsafe-archive-member')]:
            with self.subTest(special=special):
                self.fixture()
                self.archive(*self.targets[0], special=special)
                self.manifest()
                self.rejected(self.invoke('publish'), reason)
                self.assertFalse((self.root / 'outside').exists())
                shutil.rmtree(self.root / 'dl')
                (self.root / 'calls').unlink()

    def test_signed_archive_changelog_matches_committed_source_receipt(self):
        self.fixture()
        self.metadata['inputs']['CHANGELOG.md'] = 'e' * 64
        self.manifest()
        self.rejected(self.invoke('publish'), 'archive-changelog-mismatch')

    def test_replaced_manifest_during_signature_check_is_not_the_selected_file(self):
        self.fixture()
        self.environment['REPLACE_MANIFEST'] = '1'
        self.rejected(self.invoke('publish'), 'release-input-changed')

    def test_existing_versions_are_preserved_and_all_registry_queries_precede_publication(self):
        self.fixture()
        names = ['@febasi/synapse-' + name for name in ('darwin-arm64', 'linux-x64', 'linux-arm64', 'win32-x64')] + ['@febasi/synapse']
        self.environment['REGISTRY_RESULTS'] = json.dumps({name: 'exists' for name in names})
        result = self.step('assemble + publish (OIDC)')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len([r for r in self.calls('npm') if r['args'][0] == 'view']), 5)
        self.assertFalse([r for r in self.calls('npm') if r['args'][0] == 'publish'])

    def test_confirmed_absence_publishes_exact_packages_then_launcher_with_provenance(self):
        self.fixture()
        result = self.step('assemble + publish (OIDC)')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        calls = self.calls('npm')
        publications = [r for r in calls if r['args'][0] == 'publish']
        self.assertEqual(len(publications), 5)
        self.assertEqual(Path(publications[-1]['cwd']).name, 'launcher')
        self.assertTrue(all(r['args'] == ['publish', '--provenance', '--access', 'public', '--ignore-scripts'] for r in publications))
        self.assertTrue(all(r['args'][0] != 'publish' for r in calls[:6]))

    def test_registry_errors_cannot_mean_absent_or_cause_partial_publication(self):
        for error in ('E401', 'E403', 'E500', 'malformed'):
            with self.subTest(error=error):
                self.fixture()
                self.environment['REGISTRY_RESULTS'] = json.dumps({'@febasi/synapse-linux-arm64': error})
                result = self.invoke('publish')
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertEqual(json.loads(result.stdout)['reason'], 'invalid-json' if error == 'malformed' else 'registry-query-failed')
                self.assertFalse([r for r in self.calls('npm') if r['args'][0] == 'publish'])
                shutil.rmtree(self.root / 'dl')
                shutil.rmtree(self.root / 'prepared')
                (self.root / 'calls').unlink()

    def test_unsupported_npm_version_stops_before_registry_or_publish(self):
        self.fixture()
        self.environment['NPM_VERSION'] = '11.5.0'
        result = self.invoke('publish')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['reason'], 'unsupported-npm-version')
        self.assertEqual([r['args'] for r in self.calls('npm')], [['--version']])

    def test_workflow_never_embeds_event_expressions_in_shell_source(self):
        for name in ('resolve tag', 'download release archives', 'assemble + publish (OIDC)'):
            self.assertNotIn('${{', self.step_source(name))

    def step_source(self, name):
        lines = (ROOT / '.github/workflows/npm-publish.yml').read_text().splitlines()
        start = lines.index('      - name: ' + name)
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith('      - ')), len(lines))
        block = lines[start:end]
        run = next(i for i, line in enumerate(block) if line.strip() == 'run: |')
        return '\n'.join(block[run + 1:])


if __name__ == "__main__":
    unittest.main()
