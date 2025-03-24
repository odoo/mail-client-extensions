from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.3")
class TestConversionToAfterBeforeDelayMode(UpgradeCase):
    def prepare(self):
        automation1 = self.env["base.automation"].create(
            {
                "active": True,
                "model_id": self.env.ref("base.model_ir_cron").id,
                "name": "Test",
                "trigger": "on_time",
                "trg_date_range": -2,
                "trg_date_range_type": "hour",
                "trg_date_id": self.env["ir.model.fields"]._get("ir.cron", "nextcall").id,
            }
        )
        automation2 = self.env["base.automation"].create(
            {
                "active": True,
                "model_id": self.env.ref("base.model_ir_cron").id,
                "name": "Test",
                "trigger": "on_time_created",
                "trg_date_range": -2,
                "trg_date_range_type": "hour",
            }
        )
        return {
            "automation1_id": automation1.id,
            "automation2_id": automation2.id,
        }

    def check(self, check):
        automation1 = self.env["base.automation"].browse(check["automation1_id"])
        automation2 = self.env["base.automation"].browse(check["automation2_id"])
        self.assertRecordValues(
            automation1,
            [
                {
                    "active": True,
                    "name": "Test",
                    "trigger": "on_time",
                    "model_id": self.env.ref("base.model_ir_cron").id,
                    "trg_date_range": 2,
                    "trg_date_range_type": "hour",
                    "trg_date_range_mode": "before",
                    "trg_date_id": self.env["ir.model.fields"]._get("ir.cron", "nextcall").id,
                },
            ],
        )
        self.assertRecordValues(
            automation2,
            [
                {
                    "active": True,
                    "name": "Test",
                    "trigger": "on_time_created",
                    "model_id": self.env.ref("base.model_ir_cron").id,
                    "trg_date_range": 2,
                    "trg_date_range_type": "hour",
                    "trg_date_range_mode": "after",
                },
            ],
        )
