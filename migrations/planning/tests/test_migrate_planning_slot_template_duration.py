from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~17.3")
class TestMigratePlanningSlotTemplateDuration(UpgradeCase):
    def prepare(self):
        slot_templates = self.env["planning.slot.template"].create(
            [
                {
                    "start_time": 8.0,
                    "duration": 8.0,
                },
                {
                    "start_time": 8.0,
                    "duration": 9.0,
                },
                {
                    "start_time": 8.0,
                    "duration": 24,
                },
                {
                    "start_time": 8.0,
                    "duration": 25,
                },
                {
                    "start_time": 8.0,
                    "duration": 4,
                },
                {
                    "start_time": 8.0,
                    "duration": 23,
                },
                {
                    "start_time": 8.0,
                    "duration": 16,
                },
            ]
        )
        return slot_templates.ids

    def check(self, init):
        slot_template_ids = init
        (
            slot_template1,
            slot_template2,
            slot_template3,
            slot_template4,
            slot_template5,
            slot_template6,
            slot_template7,
        ) = self.env["planning.slot.template"].browse(slot_template_ids)
        self.assertEqual(slot_template1.duration_days, 1)
        self.assertEqual(slot_template1.end_time, 16.0)

        self.assertEqual(slot_template2.duration_days, 1)
        self.assertEqual(slot_template2.end_time, 17.0)

        self.assertEqual(slot_template3.duration_days, 2)
        self.assertEqual(slot_template3.end_time, 8.0)

        self.assertEqual(slot_template4.duration_days, 2)
        self.assertEqual(slot_template4.end_time, 9.0)

        self.assertEqual(slot_template5.duration_days, 1)
        self.assertEqual(slot_template5.end_time, 12.0)

        self.assertEqual(slot_template6.duration_days, 2)
        self.assertEqual(slot_template6.end_time, 7.0)

        self.assertEqual(slot_template7.duration_days, 2)
        self.assertEqual(slot_template7.end_time, 0.0)
