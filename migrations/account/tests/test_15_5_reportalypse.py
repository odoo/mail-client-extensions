# -*- coding: utf-8 -*-
from .common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("16.0")
class TestReportalypse(TestAccountingSetupCommon):

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_tax_tags_not_removed(self):
        tax_report = self.env["account.tax.report"].create(
            {
                "name": "Tax report 1",
                "country_id": self.env.company.country_id.id,
                "line_ids": [
                    (0, 0, {"name": "[01] Line 01", "tag_name": "01", "sequence": 2}),
                ],
            }
        )
        tags = tax_report.line_ids.tag_ids

        percent_tax = self.env["account.tax"].create(
            {
                "name": "percent_tax",
                "amount_type": "percent",
                "amount": 15.0,
                "type_tax_use": "sale",
                "invoice_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base", "tag_ids": [(6, 0, tags[0].ids)]}),
                    (0, 0, {"factor_percent": 100, "repartition_type": "tax", "tag_ids": [(6, 0, tags[1].ids)]}),
                ],
                "refund_repartition_line_ids": [
                    (0, 0, {"factor_percent": 100, "repartition_type": "base"}),
                    (0, 0, {"factor_percent": 100, "repartition_type": "tax"}),
                ],
            }
        )

        invoice = self.env["account.move"].create(
            {
                "move_type": "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2016-01-01",
                "date": "2016-01-01",
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "tax_ids": [(6, 0, percent_tax.ids)],
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        return [invoice.id, tags.ids]

    def _check_test_tax_tags_not_removed(self, config, invoice_id, tag_ids):
        invoice = self.env["account.move"].browse(invoice_id)
        tags = self.env["account.account.tag"].browse(tag_ids)
        self.assertEqual(invoice.line_ids.tax_tag_ids, tags)

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        res = super().prepare()
        res["tests"].append(("_check_test_tax_tags_not_removed", self._prepare_test_tax_tags_not_removed()))
        return res
