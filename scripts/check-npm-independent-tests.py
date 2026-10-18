#!/usr/bin/env python3
"""Independent archive identity regressions using the real publisher CLI."""
import importlib.util
import json
from pathlib import Path
import stat
import sys
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


def load_tests(loader, tests, pattern):
    return unittest.TestSuite(IndependentArchiveIdentityTests(name) for name in IndependentArchiveIdentityTests.__dict__ if name.startswith('test_'))


if __name__ == '__main__':
    unittest.main()
