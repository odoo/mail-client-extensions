from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("14.0")
class TestManualTransientModelAccessRights(UpgradeCase):
    """Default access rights should be created for manual transient models
    on upgrade to version 14 and above.
    """

    def prepare(self):
        # Create a manual transient model, as possible to do through the UI
        manual_transient_model = self.env["ir.model"].create(
            {
                "name": "A manual transient model",
                "model": "x_manual_transient",
                "state": "manual",
                "transient": True,
                "field_id": [
                    (
                        0,
                        0,
                        {
                            "name": "x_name",
                            "ttype": "char",
                            "state": "manual",
                        },
                    )
                ],
            },
        )
        self.assertFalse(manual_transient_model.access_ids)
        return manual_transient_model.id

    def check(self, manual_transient_model_id):
        manual_transient_model = self.env["ir.model"].browse(manual_transient_model_id)
        operations = ["perm_read", "perm_write", "perm_create", "perm_unlink"]
        # Check access right
        self.assertEqual(len(manual_transient_model.access_ids), 1)
        self.assertFalse(manual_transient_model.access_ids.group_id)
        self.assertTrue(all(manual_transient_model.access_ids[op] for op in operations))
        # Check record rule
        self.assertEqual(len(manual_transient_model.rule_ids), 1)
        self.assertTrue(all(manual_transient_model.rule_ids[op] for op in operations))
        self.assertEqual(manual_transient_model.rule_ids.domain_force, '[("create_uid", "=", user.id)]')
