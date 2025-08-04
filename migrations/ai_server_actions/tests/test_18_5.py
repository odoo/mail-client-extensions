from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.5")
class TestAiServerActionMigration(UpgradeCase):
    def prepare(self):
        if not util.version_gte("saas~18.4"):
            self.skipTest("This test is only valid from saas~18.4+")

        actions = self.env["ir.actions.server"].create(
            [
                {
                    "name": "Action 1",
                    "ai_prompt": """<span data-oe-protected="true" class="o_ai_field" contenteditable="false"><span class="d-none">{"name":</span><t t-out="object.name" data-oe-t-inline="true" data-oe-protected="true" contenteditable="false">Name</t><span class="d-none">}</span></span>""",
                    "model_id": self.env["ir.model"]._get_id("res.partner"),
                    "state": "code",
                },
                {
                    "name": "Action 2",
                    "ai_prompt": """<span class="o_ai_record"/>{12: Name}</span>""",
                    "model_id": self.env["ir.model"]._get_id("res.partner"),
                    "state": "code",
                },
            ],
        )

        return {"actions": actions.ids}

    def check(self, init):
        if not init:
            return

        actions = self.env["ir.actions.server"].browse(init["actions"]).exists()
        self.assertEqual(len(actions), 2)
        self.assertEqual(
            actions[0].ai_update_prompt,
            '<span data-oe-protected="true" class="o_ai_field" contenteditable="false"><span data-oe-t-inline="true" data-oe-protected="true" contenteditable="false" data-ai-field="name">Name</span></span>',
        )
        self.assertEqual(
            actions[1].ai_update_prompt,
            '<span><span data-ai-record-id="12"/>{12: Name}</span>',
        )
