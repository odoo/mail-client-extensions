# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("12.3")
class TestTaxChild(UpgradeCase):
    def prepare(self):
        child_tax = self.env["account.tax"].create(
            {
                "name": "Test Child",
                "amount_type": "percent",
                "amount": 10,
            }
        )
        wrong_parent_tax = self.env["account.tax"].create(
            {
                "name": "Test Parent For non group tax",
                "amount_type": "percent",
                "amount": 10,
                "children_tax_ids": [(6, 0, child_tax.ids)],
            }
        )
        return {"wrong_parent_tax_id": wrong_parent_tax.id}

    def check(self, init):
        child_tax_ids = self.env["account.tax"].browse(init["wrong_parent_tax_id"]).children_tax_ids.ids
        self.assertFalse(child_tax_ids, "A non-group tax with children should have lost them during migration")
