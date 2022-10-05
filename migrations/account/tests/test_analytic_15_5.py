# -*- coding: utf-8 -*-
from .common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("16.0")
class TestAnalyticApocalypse(TestAccountingSetupCommon):
    def _prepare_analytic_test(self):
        self.env.user.write(
            {
                "groups_id": [
                    (4, self.env.ref("analytic.group_analytic_accounting").id),
                    (4, self.env.ref("analytic.group_analytic_tags").id),
                ],
            }
        )
        analytic_account = self.env["account.analytic.account"].create(
            {
                "name": "Account A",
            }
        )
        analytic_tag = self.env["account.analytic.tag"].create(
            {
                "name": "Tag 1",
                "active_analytic_distribution": True,
            }
        )
        self.env["account.analytic.distribution"].create(
            {
                "account_id": analytic_account.id,
                "percentage": 50,
                "tag_id": analytic_tag.id,
            }
        )

        move_type_field = "move_type" if util.version_gte("saas~13.3") else "type"
        invoice = self.env["account.move"].create(
            {
                move_type_field: "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2016-01-01",
                "date": "2016-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line1",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "analytic_account_id": analytic_account.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "line2",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "analytic_account_id": analytic_account.id,
                            "analytic_tag_ids": [(6, 0, analytic_tag.ids)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "line3",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "analytic_tag_ids": [(6, 0, analytic_tag.ids)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "line4",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                        },
                    ),
                ],
            }
        )
        return [invoice.id, analytic_account.id]

    def _check_analytic_test(self, config, invoice_id, analytic_account_id):
        invoice = self.env["account.move"].browse(invoice_id)

        self.assertEqual(invoice.invoice_line_ids[0].analytic_distribution, {str(analytic_account_id): 100.0})
        self.assertEqual(invoice.invoice_line_ids[1].analytic_distribution, {str(analytic_account_id): 150.0})
        self.assertEqual(invoice.invoice_line_ids[2].analytic_distribution, {str(analytic_account_id): 50.0})
        self.assertEqual(invoice.invoice_line_ids[3].analytic_distribution, False)

    def prepare(self):
        res = super().prepare()
        res["tests"].append(("_check_analytic_test", self._prepare_analytic_test()))
        return res
