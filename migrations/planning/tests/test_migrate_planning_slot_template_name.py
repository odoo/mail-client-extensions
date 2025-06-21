from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~18.4")
class TestMigratePlanningSlotTemplateName(UpgradeCase):
    def prepare(self):
        slot_templates = self.env["planning.slot.template"].create(
            [
                {
                    "start_time": 8.0,
                    "end_time": 12.0,
                },
                {
                    "start_time": 10.5,
                    "end_time": 12.5,
                },
                {
                    "start_time": 10.5,
                    "end_time": 8.0,
                    "duration_days": 2,
                },
            ]
        )
        return slot_templates.ids

    def check(self, init):
        slot_template_ids = init
        template1, template2, template3 = self.env["planning.slot.template"].browse(slot_template_ids)
        self.assertEqual(template1.name, "08:00 - 12:00")
        self.assertEqual(template2.name, "10:30 - 12:30")
        self.assertEqual(template3.name, "10:30 - 08:00")
