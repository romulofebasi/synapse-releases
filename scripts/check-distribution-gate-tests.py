#!/usr/bin/env python3
"""Negative controls for required distribution suite admission."""
import importlib.util
import io
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('distribution_gate_controlled', Path(__file__).with_name('check-distribution.py'))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class DistributionAdmissionTests(unittest.TestCase):
    def fixture(self, kind):
        class Case(unittest.TestCase):
            def runTest(self):
                if kind == 'assertion':
                    self.fail('Owned admission control')
                elif kind == 'error':
                    raise RuntimeError('Owned invalid runner control')
        if kind == 'skip':
            Case = unittest.skip('Owned required skip')(Case)
        elif kind == 'expected':
            Case.runTest = unittest.expectedFailure(lambda self: self.fail('Owned expected failure'))
        return unittest.TestSuite([Case()])

    def test_complete_selection_is_admitted(self):
        self.assertTrue(gate.admit(self.fixture('pass'), minimum=1, stream=io.StringIO()))

    def test_zero_selected_cases_cannot_pass(self):
        self.assertFalse(gate.admit(unittest.TestSuite(), minimum=0, stream=io.StringIO()))

    def test_below_required_count_cannot_pass(self):
        self.assertFalse(gate.admit(self.fixture('pass'), minimum=2, stream=io.StringIO()))

    def test_required_skip_and_expected_failure_cannot_pass(self):
        for kind in ('skip', 'expected'):
            with self.subTest(kind=kind):
                self.assertFalse(gate.admit(self.fixture(kind), minimum=1, stream=io.StringIO()))

    def test_assertion_and_runner_error_cannot_pass(self):
        for kind in ('assertion', 'error'):
            with self.subTest(kind=kind):
                self.assertFalse(gate.admit(self.fixture(kind), minimum=1, stream=io.StringIO()))

    def test_missing_and_empty_required_module_cannot_pass(self):
        with tempfile.TemporaryDirectory(prefix='distribution-admission-') as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, 'Missing required'):
                gate.load_required(root, names=('required.py',))
            (root / 'required.py').write_text('# Owned empty control\n')
            with self.assertRaisesRegex(ValueError, 'selected no cases'):
                gate.load_required(root, names=('required.py',))

    def test_undersized_declared_publication_module_cannot_pass(self):
        with tempfile.TemporaryDirectory(prefix='distribution-admission-') as temporary:
            root = Path(temporary)
            name = 'check-npm-publish-tests.py'
            (root / name).write_text('import unittest\nclass Case(unittest.TestCase):\n def test_one(self): pass\n')
            with self.assertRaisesRegex(ValueError, 'fewer than its admitted cases'):
                gate.load_required(root, names=(name,))

    def run_fixture(self, kind):
        self.assertEqual(kind, 'imported-unittest-runner')
        with tempfile.TemporaryDirectory(prefix='distribution-import-boundary-') as temporary:
            root = Path(temporary)
            shutil.copyfile(Path(__file__).with_name('check-distribution.py'), root / 'check-distribution.py')
            methods = ''.join(f' def test_{index:02d}(self): pass\n' for index in range(16))
            (root / 'check-npm-publish-tests.py').write_text(
                'import unittest\nclass Evidence(unittest.TestCase):\n' + methods + '\nunittest.main(module=__name__)\n')
            return subprocess.run([sys.executable, str(root / 'check-distribution.py')],
                                  capture_output=True, text=True, timeout=15)

    def test_imported_unittest_runner_cannot_bypass_missing_later_required_module(self):
        self.assertNotEqual(self.run_fixture('imported-unittest-runner').returncode, 0,
                            'A required module exiting successfully during import must not admit missing independent evidence')


if __name__ == '__main__':
    unittest.main()
