#!/usr/bin/env python3
"""Exercise actual npm workflow shell steps with private files and recording external tools."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

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


if __name__ == "__main__":
    unittest.main()
