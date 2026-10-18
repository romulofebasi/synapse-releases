#!/usr/bin/env python3
"""Admit the explicit distribution suites through unittest's result API."""
import importlib.util
import io
from pathlib import Path
import sys
import unittest

REQUIRED_MODULES = ('check-npm-publish-tests.py', 'check-distribution-gate-tests.py')
MINIMUM_CASES = 16


def load_required(directory, names=REQUIRED_MODULES):
    """Missing declared modules or empty modules are admission failures."""
    suite = unittest.TestSuite()
    for index, name in enumerate(names):
        path = directory / name
        if not path.is_file() or path.is_symlink():
            raise ValueError('Missing required distribution test module')
        spec = importlib.util.spec_from_file_location(f'distribution_required_{index}', path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        selected = unittest.defaultTestLoader.loadTestsFromModule(module)
        if selected.countTestCases() == 0:
            raise ValueError('Required module selected no cases')
        suite.addTests(selected)
    return suite


def admit(suite, minimum=MINIMUM_CASES, stream=None):
    """Reject empty selection, failures, errors, skips and expected failures."""
    selected = suite.countTestCases()
    if selected < minimum or selected == 0:
        return False
    result = unittest.TextTestRunner(verbosity=2, stream=stream or sys.stderr).run(suite)
    return (result.wasSuccessful() and result.testsRun == selected
            and not result.skipped and not result.expectedFailures)


def main():
    try:
        return 0 if admit(load_required(Path(__file__).resolve().parent)) else 1
    except (OSError, ValueError, ImportError):
        print('Required distribution evidence is missing or invalid.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
