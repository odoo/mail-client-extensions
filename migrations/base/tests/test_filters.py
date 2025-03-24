from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("18.3")
class TestSharedWithField(UpgradeCase):
    def prepare(self):
        filter_1 = self.env["ir.filters"].create({"name": "Filter 1", "model_id": "ir.filters", "user_id": False})
        filter_2 = self.env["ir.filters"].create(
            {"name": "Filter 2", "model_id": "ir.filters", "user_id": self.env.ref("base.user_admin").id}
        )
        return {
            "filter_1": filter_1.id,
            "filter_2": filter_2.id,
        }

    def check(self, check):
        filter_1 = self.env["ir.filters"].browse(check["filter_1"])
        filter_2 = self.env["ir.filters"].browse(check["filter_2"])
        self.assertListEqual(filter_1.user_ids.ids, [])
        self.assertListEqual(filter_2.user_ids.ids, self.env.ref("base.user_admin").ids)
