from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class TestDomainRemovalForOnChangeAutomations(UpgradeCase):
    def prepare(self):
        automation = self.env["base.automation"].create(
            {
                "active": True,
                "name": "Test",
                "trigger": "on_change",
                "model_id": self.env.ref("base.model_res_partner").id,
                "on_change_field_ids": [self.env["ir.model.fields"]._get("res.partner", "comment").id],
                "filter_domain": "[('comment', 'like', 'geez')]",
            }
        )
        return automation.id

    def check(self, automation_id):
        automation = self.env["base.automation"].browse(automation_id)
        self.assertRecordValues(
            automation,
            [
                {
                    "active": True,
                    "name": "Test",
                    "trigger": "on_change",
                    "model_id": self.env.ref("base.model_res_partner").id,
                    "on_change_field_ids": [self.env["ir.model.fields"]._get("res.partner", "comment").id],
                    "filter_domain": None,
                },
            ],
        )
