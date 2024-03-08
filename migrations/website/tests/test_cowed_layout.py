from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase


# This test runs on every version.
class TestCowedLayout(UpgradeCase):
    def prepare(self):
        if not util.version_gte("14.0"):
            self.skipTest(
                "pre-cowed-layout only runs after saas-12.3 - but test uses website.navbar_toggler which appears in 14.0"
            )
        other_website = self.env["website"].create(
            {
                "name": "Another Website",
            }
        )
        # Using navbar_toggler for the test to avoid impacting major layouts.
        view = self.env.ref("website.navbar_toggler")
        new_content = view.arch_db.replace("</t>", "<!-- Some change 1 --></t>")
        view.with_context(website_id=1).arch = new_content
        new_content = view.arch_db.replace("</t>", f"<!-- Some change {other_website.id} --></t>")
        view.with_context(website_id=other_website.id).arch = new_content
        cowed_view_1 = self.env["website"].with_context(website_id=1).viewref("website.navbar_toggler")
        cowed_view_2 = self.env["website"].with_context(website_id=other_website.id).viewref("website.navbar_toggler")
        return {
            "generic_view_id": view.id,
            "specific_view_ids": {
                "1": cowed_view_1.id,
                str(other_website.id): cowed_view_2.id,
            },
        }

    def check(self, init):
        View = self.env["ir.ui.view"]
        layout = View.browse(init["generic_view_id"])
        self.assertTrue(layout, "General website.navbar_toggler must exist")
        for website_id_str, view_id in init["specific_view_ids"].items():
            website_id = int(website_id_str)
            cowed_layout = View.browse(view_id)
            self.assertNotEqual(layout.id, cowed_layout.id, "General and specific must be different records")
            self.assertTrue(cowed_layout, "Specific website.navbar_toggler must exist")
            self.assertEqual(layout.arch_db, cowed_layout.arch_db, "Layout should have been reset")
            backup_layout = View.with_context(active_test=False).search(
                [("website_id", "=", website_id), ("key", "like", r"website.navbar_toggler\_backup")]
            )
            self.assertTrue(backup_layout, "Backup of specific website.navbar_toggler must exist")
            self.assertNotEqual(layout.arch_db, backup_layout.arch_db, "Different arch should have been backed up")
            self.assertIn(f"<!-- Some change {website_id} -->", backup_layout.arch_db, "Backup value must be correct")
