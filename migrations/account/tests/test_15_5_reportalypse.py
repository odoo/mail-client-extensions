from .test_common import TestAccountingSetupCommon
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

    def _prepare_test_custom_tax_report_migrated(self):
        atr = self.env["account.tax.report"]
        atrl = self.env["account.tax.report.line"]

        report = atr.create(
            {
                "name": "Custom Tax Report Test 1",
                "country_id": self.env["res.country"].search([("name", "=", "Belgium")]).id,
            }
        )
        report_vals = {
            "name": report.name,
            "country_id": report.country_id.id,
        }

        line1 = atrl.create(
            {
                "code": "tax_line_custom_code_1",
                "name": "Custom Tax Report Line Test 1",
                "report_id": report.id,
                "sequence": 10,
                "tag_name": "543",
            }
        )
        line1_vals = {
            "code": line1.code,
            "name": line1.name,
            "sequence": line1.sequence,
            "tag_name": line1.tag_name,
        }

        return report_vals, line1_vals

    def _check_test_custom_tax_report_migrated(self, config, rep_vals, l1_vals):
        ar = self.env["account.report"]
        arc = self.env["account.report.column"]
        arl = self.env["account.report.line"]
        are = self.env["account.report.expression"]

        report = ar.search(
            [
                ("name", "=", rep_vals["name"]),
                ("country_id", "=", rep_vals["country_id"]),
                ("availability_condition", "=", "country"),
                ("root_report_id", "=", self.env.ref("account.generic_tax_report").id),
            ]
        )
        self.assertTrue(report)

        column = arc.search([("report_id", "=", report.id)])
        self.assertTrue(column)

        l1 = arl.search(
            [
                ("report_id", "=", report.id),
                ("name", "=", l1_vals["name"]),
                ("code", "=", l1_vals["code"]),
                ("parent_id", "=", False),
            ]
        )
        self.assertTrue(l1)

        e1 = are.search(
            [
                ("report_line_id", "=", l1.id),
                ("label", "=", "balance"),
                ("engine", "=", "tax_tags"),
                ("formula", "=", l1_vals["tag_name"]),
                ("subformula", "=", False),
            ]
        )
        self.assertTrue(e1)

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        res = super().prepare()
        res["tests"].append(("_check_test_tax_tags_not_removed", self._prepare_test_tax_tags_not_removed()))
        res["tests"].append(("_check_test_custom_tax_report_migrated", self._prepare_test_custom_tax_report_migrated()))
        return res
