#!/usr/bin/env python3
"""Independent archive identity regressions using the real publisher CLI."""
import importlib.util
import copy
import io
import json
import os
from pathlib import Path
import shlex
import shutil
import stat
import subprocess
import sys
import tarfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('frozen_workflow_fixtures', ROOT / 'scripts/check-npm-publish-tests.py')
fixtures = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = fixtures
spec.loader.exec_module(fixtures)


class IndependentArchiveIdentityTests(fixtures.NpmWorkflowTests):
    def replace_zip(self, *, nul_name=False, directory_type=False):
        path = next((self.root / 'dl').glob('*.zip'))
        with zipfile.ZipFile(path) as archive:
            rows = [(member.filename, archive.read(member)) for member in archive.infolist()]
        expected = next(name for name, _ in rows if name.endswith('/syn.exe'))
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in rows:
                member = zipfile.ZipInfo(name + '~unexpected' if nul_name and name == expected else name)
                member.create_system = 3
                member.external_attr = ((stat.S_IFDIR if directory_type and name == expected else stat.S_IFREG) | 0o755) << 16
                archive.writestr(member, data)
        if nul_name:
            original = (expected + '~unexpected').encode()
            replacement = (expected + '\0unexpected').encode()
            data = path.read_bytes()
            self.assertEqual(data.count(original), 2, 'Both local and central ZIP names must carry the fixture suffix')
            path.write_bytes(data.replace(original, replacement))
            with zipfile.ZipFile(path) as archive:
                member = next(m for m in archive.infolist() if '\0' in m.orig_filename)
                self.assertEqual(member.filename, expected)
                self.assertNotEqual(member.orig_filename, member.filename)
        if directory_type:
            with zipfile.ZipFile(path) as archive:
                member = archive.getinfo(expected)
                self.assertFalse(member.is_dir())
                self.assertEqual(stat.S_IFMT(member.external_attr >> 16), stat.S_IFDIR)
        self.manifest()

    def assert_refused_before_publication(self):
        result = self.invoke('publish')
        self.assertEqual(result.returncode, 1, 'Noncanonical archive identity must be refused: ' + result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'rejected')
        self.assertFalse(self.calls('npm'), 'An invalid binary member must not reach npm')
        self.assertFalse((self.root / 'prepared').exists())

    def test_zip_original_member_name_cannot_be_hidden_by_nul_normalization(self):
        self.fixture()
        self.replace_zip(nul_name=True)
        self.assert_refused_before_publication()

    def test_zip_directory_type_cannot_be_selected_as_regular_binary(self):
        self.fixture()
        self.replace_zip(directory_type=True)
        self.assert_refused_before_publication()


class IndependentPublicationCoverageTests(fixtures.NpmWorkflowTests):
    def modify_tar(self, *, wrong_path=False, duplicate=False, replacement=None):
        path = next((self.root / 'dl').glob('*aarch64-apple-darwin.tar.gz'))
        with tarfile.open(path, 'r:gz') as archive:
            rows = [(copy.copy(member), archive.extractfile(member).read()) for member in archive.getmembers()]
        with tarfile.open(path, 'w:gz') as archive:
            for member, data in rows:
                if member.name.endswith('/syn'):
                    if wrong_path:
                        member.name = 'unrelated-directory/syn'
                    if replacement is not None:
                        data = replacement
                        member.size = len(data)
                    archive.addfile(member, io.BytesIO(data))
                    if duplicate:
                        duplicate_member = copy.copy(member)
                        duplicate_data = b'different duplicate binary'
                        duplicate_member.size = len(duplicate_data)
                        archive.addfile(duplicate_member, io.BytesIO(duplicate_data))
                else:
                    archive.addfile(member, io.BytesIO(data))
        self.manifest()

    def test_bounded_stable_tag_contract_before_outputs_or_external_tools(self):
        bad = ['v' + '9' * 64 + '.0.0', 'v01.5.0', 'v1.05.0', 'v1.5.00', 'v1.5.0-rc.1',
               'v1.5.0+build', 'v1.5.0\nversion=9.9.9', ' v1.5.0', 'v1.5.0 ', 'v١.5.0', '1.5.0', '']
        for tag in bad:
            with self.subTest(tag=tag):
                (self.root / 'outputs').unlink(missing_ok=True)
                self.tag = tag
                self.environment.update(TAG=tag, RELEASE_TAG=tag)
                result = self.step('resolve tag')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / 'outputs').exists())
                self.assertFalse(self.calls())
                (self.root / 'outputs').unlink(missing_ok=True)
        for tag in ('v0.0.0', 'v1.5.0', 'v123.45.6'):
            with self.subTest(valid=tag):
                self.tag = tag
                self.environment.update(TAG=tag, RELEASE_TAG=tag)
                result = self.step('resolve tag')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual((self.root / 'outputs').read_text(), f'tag={tag}\nversion={tag[1:]}\n')
                (self.root / 'outputs').unlink()

    def test_signed_receipt_bytes_are_hashed_not_only_archive_bytes(self):
        self.fixture()
        path = self.root / 'dl/release-metadata.json'
        receipt = json.loads(path.read_text())
        receipt['commit'] = 'f' * 40
        path.write_text(json.dumps(receipt))
        self.rejected(self.invoke('publish'), 'signed-checksum-mismatch')
        self.assertFalse((self.root / 'prepared').exists())

    def test_duplicate_signed_manifest_lines_are_not_complete_inventory(self):
        self.fixture()
        path = self.root / 'dl/SHA256SUMS'
        data = path.read_text()
        path.write_text(data + data.splitlines(keepends=True)[0])
        self.rejected(self.invoke('publish'), 'signed-checksum-mismatch')

    def test_source_receipt_digests_and_schema_are_strict(self):
        for field in ('Cargo.toml', 'Cargo.lock', 'notesSHA256', 'schemaVersion'):
            with self.subTest(field=field):
                self.fixture()
                if field in ('Cargo.toml', 'Cargo.lock'):
                    self.metadata['inputs'][field] = 'not-a-digest'
                else:
                    self.metadata[field] = True if field == 'schemaVersion' else 'not-a-digest'
                self.manifest()
                self.rejected(self.invoke('publish'), 'source-receipt-tag-mismatch' if field == 'schemaVersion' else 'invalid-source-digest')

    def test_zip_symlink_cannot_supply_the_selected_binary(self):
        self.fixture()
        path = next((self.root / 'dl').glob('*.zip'))
        with zipfile.ZipFile(path) as archive:
            rows = [(member.filename, archive.read(member)) for member in archive.infolist()]
        with zipfile.ZipFile(path, 'w') as archive:
            for name, data in rows:
                member = zipfile.ZipInfo(name)
                member.create_system = 3
                member.external_attr = ((stat.S_IFLNK if name.endswith('/syn.exe') else stat.S_IFREG) | 0o755) << 16
                archive.writestr(member, data)
        self.manifest()
        self.rejected(self.invoke('publish'), 'unsafe-archive-member')

    def test_duplicate_binary_members_are_ambiguous_even_without_a_directory_record(self):
        self.fixture()
        self.modify_tar(duplicate=True)
        self.rejected(self.invoke('publish'), 'duplicate-archive-member')

    def test_binary_basename_is_insufficient_without_the_expected_version_target_path(self):
        self.fixture()
        self.modify_tar(wrong_path=True)
        self.rejected(self.invoke('publish'), 'unexpected-archive-member')

    def test_every_platform_and_launcher_manifest_uses_the_selected_version(self):
        self.fixture()
        result = self.invoke('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        directories = sorted(path for path in (self.root / 'prepared').iterdir() if path.is_dir())
        self.assertEqual({path.name for path in directories}, {'darwin-arm64', 'linux-x64', 'linux-arm64', 'win32-x64', 'launcher'})
        for path in directories:
            with self.subTest(package=path.name):
                package = json.loads((path / 'package.json').read_text())
                self.assertEqual(package['version'], '1.5.0')
                self.assertEqual(package['name'], '@febasi/synapse' if path.name == 'launcher' else '@febasi/synapse-' + path.name)
        self.assertFalse(self.calls('npm'))

    def test_late_registry_failure_cannot_publish_an_earlier_package(self):
        self.fixture()
        self.environment['REGISTRY_RESULTS'] = json.dumps({'@febasi/synapse-linux-arm64': 'E403'})
        result = self.invoke('publish')
        self.assertEqual(result.returncode, 1)
        self.assertFalse([row for row in self.calls('npm') if row['args'][0] == 'publish'], 'All registry observations must finish before publication')
        self.assertEqual(json.loads(result.stdout), {'status': 'rejected', 'reason': 'registry-query-failed'})

    def test_explicitly_metadata_free_producer_root_entries_preserve_all_binary_bytes(self):
        for zip_attributes in ('unix', 'dos', 'unspecified'):
            with self.subTest(zip_attributes=zip_attributes):
                self.fixture()
                producer = self.root / 'producer'
                shutil.rmtree(producer, ignore_errors=True)
                producer.mkdir()
                for target, suffix, binary in self.targets:
                    prefix = f'synapse-1.5.0-{target}'
                    path = self.root / 'dl' / f'{prefix}.{suffix}'
                    if suffix == 'tar.gz':
                        directory = producer / prefix
                        directory.mkdir()
                        with tarfile.open(path, 'r:gz') as archive:
                            for member in archive.getmembers():
                                (directory / Path(member.name).name).write_bytes(archive.extractfile(member).read())
                        command = [shutil.which('tar'), 'czf', str(path), prefix]
                        # BSD tar otherwise emits host AppleDouble metadata outside the release inventory.
                        result = subprocess.run(command, cwd=producer, env=dict(os.environ, COPYFILE_DISABLE='1'), capture_output=True, timeout=10)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        with tarfile.open(path, 'r:gz') as archive:
                            members = archive.getmembers()
                            self.assertEqual(len(members), 5)
                            self.assertTrue(any(member.isdir() and member.name.rstrip('/') == prefix for member in members))
                    else:
                        with zipfile.ZipFile(path) as archive:
                            rows = [(member.filename, archive.read(member)) for member in archive.infolist()]
                        with zipfile.ZipFile(path, 'w') as archive:
                            directory = zipfile.ZipInfo(prefix + '/')
                            directory.create_system = 3 if zip_attributes == 'unix' else 0
                            directory.external_attr = ((stat.S_IFDIR | 0o755) << 16 | 0x10) if zip_attributes == 'unix' else (0x10 if zip_attributes == 'dos' else 0)
                            archive.writestr(directory, b'')
                            for name, data in rows:
                                member = zipfile.ZipInfo(name)
                                member.create_system = directory.create_system
                                member.external_attr = ((stat.S_IFREG | 0o644) << 16) if zip_attributes == 'unix' else 0x20
                                archive.writestr(member, data)
                self.manifest()
                result = self.invoke('prepare')
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                for (target, _, binary), platform in zip(self.targets, ('darwin-arm64', 'linux-x64', 'linux-arm64', 'win32-x64')):
                    self.assertEqual((self.root / 'prepared' / platform / binary).read_bytes(), b'owned fixture bytes: ' + target.encode())
                self.assertFalse(self.calls('npm'))

    def test_zip_directory_flags_and_types_agree_with_the_member_kind(self):
        for kind in ('dos-directory-bit-on-binary', 'regular-type-on-directory'):
            with self.subTest(kind=kind):
                self.fixture()
                path = next((self.root / 'dl').glob('*.zip'))
                with zipfile.ZipFile(path) as archive:
                    rows = [(member.filename, archive.read(member)) for member in archive.infolist()]
                with zipfile.ZipFile(path, 'w') as archive:
                    if kind == 'regular-type-on-directory':
                        member = zipfile.ZipInfo(rows[0][0].rsplit('/', 1)[0] + '/')
                        member.create_system = 3
                        member.external_attr = (stat.S_IFREG | 0o755) << 16
                        archive.writestr(member, b'')
                    for name, data in rows:
                        member = zipfile.ZipInfo(name)
                        member.create_system = 3
                        member.external_attr = (stat.S_IFREG | 0o755) << 16
                        if kind == 'dos-directory-bit-on-binary' and name.endswith('/syn.exe'):
                            member.external_attr |= 0x10
                        archive.writestr(member, data)
                self.manifest()
                self.rejected(self.invoke('publish'), 'unsafe-archive-member')

    def test_archived_binary_is_copied_without_execution(self):
        self.fixture()
        marker = self.root / 'binary-was-executed'
        payload = ('#!/bin/sh\nprintf executed > ' + shlex.quote(str(marker)) + '\n').encode()
        self.modify_tar(replacement=payload)
        result = self.invoke('prepare')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.root / 'prepared/darwin-arm64/syn').read_bytes(), payload)
        self.assertFalse(marker.exists())
        self.assertFalse(self.calls('npm'))


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(case(name) for case in (IndependentArchiveIdentityTests, IndependentPublicationCoverageTests)
                              for name in case.__dict__ if name.startswith('test_'))


if __name__ == '__main__':
    unittest.main()
