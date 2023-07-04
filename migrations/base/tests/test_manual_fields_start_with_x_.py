from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~16.4")
class ManualFieldsStartsWithX(UpgradeCase):
    def prepare(self):
        custom_field = self.env["ir.model.fields"].create(
            {
                "name": "x_foo",
                "model_id": self.env.ref("base.model_res_partner").id,
                "ttype": "char",
                "state": "manual",
            },
        )
        self.env.cr.execute("UPDATE ir_model_fields SET name = 'foo' WHERE id = %s", [custom_field.id])
        custom_field.invalidate_recordset(["name"])
        self.assertEqual(custom_field.name, "foo")
        return custom_field.id

    def check(self, field_id):
        custom_field = self.env["ir.model.fields"].browse(field_id)
        self.assertEqual(custom_field.name, "x_foo")
