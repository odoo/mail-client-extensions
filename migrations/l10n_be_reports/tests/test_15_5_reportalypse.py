# -*- coding: utf-8 -*-
from odoo import fields
from odoo.tools import date_utils

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import change_version

common = util.import_script("account/tests/common.py")


@change_version("saas~15.5")
class TestReportalypseL10nBeReports(common.TestAccountingSetupCommon):

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_carryover_lines(self):
        tax_21m = self._get_tax_by_xml_id("l10n_be", "attn_VAT-IN-V81-21")

        invoices = self.env["account.move"].create(
            [
                {
                    "move_type": "in_refund",
                    "partner_id": self.partner.id,
                    "invoice_date": invoice_date,
                    "date": invoice_date,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "line",
                                "quantity": 1.0,
                                "price_unit": 1000.0,
                                "account_id": self.account_income.id,
                                "tax_ids": [(6, 0, tax_21m.ids)],
                            },
                        )
                    ],
                }
                for invoice_date in ("2020-01-01", "2020-02-01", "2020-03-01")
            ]
        )
        invoices.action_post()

        for tax_report_date in ("2020-01-31", "2020-02-29"):
            report = self.env["account.generic.tax.report"]
            options = report._get_options()
            date_from, date_to = date_utils.get_month(fields.Date.from_string(tax_report_date))
            options["date"]["date_from"] = fields.Date.to_string(date_from)
            options["date"]["date_to"] = fields.Date.to_string(date_to)
            closing_move = report._generate_tax_closing_entries(options)
            closing_move.with_context(l10n_be_reports_generation_options=False).action_post()

        carryover_lines = self.env["account.tax.carryover.line"].search([("company_id", "=", self.env.company.id)])
        self.assertRecordValues(
            carryover_lines,
            [
                {"date": fields.Date.from_string(tax_report_date), "amount": -1000.0}
                for tax_report_date in ("2020-01-31", "2020-02-29")
            ],
        )

        return []

    def _check_test_carryover_lines(self, config):
        external_values = self.env["account.report.external.value"].search([])
        self.assertRecordValues(
            external_values,
            [
                {"date": fields.Date.from_string("2020-01-31"), "value": -1000.0},
                {"date": fields.Date.from_string("2020-02-29"), "value": -2000.0},
            ],
        )

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        res = super().prepare(chart_template_ref="l10n_be.l10nbe_chart_template")

        self.env.company.partner_id.write(
            {
                "vat": "BE246697724",
                "street": "1021 Sint-Bernardsesteenweg",
                "city": "Antwerpen",
                "zip": "2660",
                "phone": "+32 470 12 34 56",
                "email": "info@company.beexample.com",
            }
        )

        res["tests"].append(("_check_test_carryover_lines", self._prepare_test_carryover_lines()))
        return res
