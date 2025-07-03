import unittest
from pathlib import Path

from odoo.modules import migration

from odoo.addons.base.maintenance.migrations.testing import UnitTestCase
from odoo.addons.base.maintenance.migrations.util.misc import version_gte

ROOT = Path(__file__).parent.parent.parent


@unittest.skipUnless(version_gte("saas~16.3"), "Only works from version saas~16.3")
class TestEnsureVersion(UnitTestCase):
    def test_fs(self):
        for path in ROOT.glob("*/*"):
            if not path.is_dir() or path.is_relative_to(ROOT / "util"):
                continue
            version = path.name

            if version in {"tests", "__pycache__"}:
                continue

            with self.subTest():
                self.assertIsNotNone(migration.VERSION_RE.match(version), f"Invalid version {path.relative_to(ROOT)}")
