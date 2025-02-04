import contextlib

with contextlib.suppress(ImportError):
    from odoo import Command

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.account_reports.tests.test_common import TestReportValuesCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~18.5")
class TestAtTaxTags(TestReportValuesCommon):
    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_tags_in_repartition_lines_and_amls(self):
        """Prepare three cases:
        - when the right tag is applied to a tax's repartition line and the tax is used in a move (replicates the behavior
        in which a user manually changed the tag in a tax)
        - when the wrong tag is applied to a tax's repartition line and the tax is used in a move (replicates the behavior
        in which the user did not change the tag)
        - when a negative tag is used in an invoice line and this line is not associated to one of the taxes with incorrect
        tags (replicates the behavior of a manually added tag in the invoice line)
        """

        def create_tax(name, invoice_base_tag, refund_base_tag):
            return self.env["account.tax"].create(
                {
                    "name": name,
                    "amount_type": "percent",
                    "amount": 25.0,
                    "type_tax_use": "purchase",
                    "company_id": self.company.id,
                    "invoice_repartition_line_ids": [
                        Command.create(
                            {
                                "factor_percent": 100,
                                "repartition_type": "base",
                                "tag_ids": [Command.set(invoice_base_tag.ids)],
                            }
                        ),
                        Command.create(
                            {
                                "factor_percent": 100,
                                "account_id": tax_recover_account.id,
                                "tag_ids": [Command.set(tax_tag_positive.ids)],
                            }
                        ),
                    ],
                    "refund_repartition_line_ids": [
                        Command.create(
                            {
                                "factor_percent": 100,
                                "repartition_type": "base",
                                "tag_ids": [Command.set(refund_base_tag.ids)],
                            }
                        ),
                        Command.create(
                            {
                                "factor_percent": 100,
                                "account_id": tax_recover_account.id,
                                "tag_ids": [Command.set(tax_tag_negative.ids)],
                            }
                        ),
                    ],
                }
            )

        def create_bill(**kwargs):
            bill = self.env["account.move"].create(
                {
                    "move_type": "in_invoice",
                    "partner_id": self.partner.id,
                    "invoice_date": "2025-01-01",
                    "date": "2025-01-01",
                    "invoice_line_ids": [
                        Command.create(
                            {
                                "name": "line",
                                "quantity": 1.0,
                                "price_unit": 100.0,
                                **kwargs,
                            }
                        )
                    ],
                }
            )
            bill.action_post()
            return bill

        country = self.env["res.country"].search([("code", "=", "AT")])
        domain = [
            ("applicability", "=", "taxes"),
            ("country_id", "=", country.id),
        ]
        base_tag_positive = self.env["account.account.tag"].search(
            [*domain, ("name", "=", "+KZ 008 Bemessungsgrundlage")]
        )
        base_tag_negative = self.env["account.account.tag"].search(
            [*domain, ("name", "=", "-KZ 008 Bemessungsgrundlage")]
        )

        tax_recover_account = self._get_account([("account_type", "=", "liability_current")])
        tax_tag_positive = self.env["account.account.tag"].search([*domain, ("name", "=", "+KZ 077")])
        tax_tag_negative = self.env["account.account.tag"].search([*domain, ("name", "=", "-KZ 077")])

        tax_correct = create_tax("tax_test_correct", base_tag_positive, base_tag_negative)
        tax_incorrect = create_tax("tax_test_incorrect", base_tag_negative, base_tag_positive)

        bill_tax_correct = create_bill(tax_ids=[Command.set(tax_correct.ids)])
        bill_tax_incorrect = create_bill(tax_ids=[Command.set(tax_incorrect.ids)])
        bill_tax_no_tax_with_tag = create_bill()  # No tax, but still has an "incorrect" tag added manually
        bill_tax_no_tax_with_tag.invoice_line_ids.tax_tag_ids = base_tag_negative.ids

        return [
            (tax_correct + tax_incorrect).ids,
            (bill_tax_correct + bill_tax_incorrect + bill_tax_no_tax_with_tag).ids,
        ]

    def _check_tags_in_repartition_lines_and_amls(self, config, tax_ids, invoice_ids):
        """
        Both cases outlined in `_prepare_tags_in_repartition_lines_and_amls` should have the correct tags in repartition
        lines as well as in account move lines.
        """
        for tax_id in tax_ids:
            tax = self.env["account.tax"].browse(tax_id)
            # Check tag exists in repartition line to avoid false positive in the tax_negate assertion
            self.assertTrue(tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == "base").tag_ids)
            self.assertFalse(
                tax.invoice_repartition_line_ids.filtered(lambda x: x.repartition_type == "base").tag_ids.tax_negate
            )
            self.assertTrue(
                tax.refund_repartition_line_ids.filtered(lambda x: x.repartition_type == "base").tag_ids.tax_negate
            )
        for invoice_id in invoice_ids:
            invoice = self.env["account.move"].browse(invoice_id)
            # Check tag exists in invoice line to avoid false positive in the tax_negate assertion
            self.assertTrue(invoice.invoice_line_ids.tax_tag_ids)
            if invoice.invoice_line_ids.tax_ids:
                self.assertFalse(invoice.invoice_line_ids.tax_tag_ids.tax_negate)
            else:
                # Checks the case where the "incorrect" negative tag was added manually (not coming from one of the updated taxes)
                self.assertTrue(invoice.invoice_line_ids.tax_tag_ids.tax_negate)

    def _prepare_vat_report(self):
        line_report_that_should_be_inverted = (
            "l10n_at.tax_report_line_l10n_at_tva_sale_03_report_title",
            "l10n_at.tax_report_line_l10n_at_tva_line_4_25",
            "l10n_at.tax_report_line_l10n_at_tva_line_4_26",
            "l10n_at.tax_report_line_l10n_at_tva_line_4_27",
            "l10n_at.tax_report_line_l10n_at_tva_sale_04_report_title",
            "l10n_at.tax_report_line_at_base_title_umsatz_base_4_28_31",
            "l10n_at.tax_report_line_l10n_at_tva_line_4_28_base",
            "l10n_at.tax_report_line_l10n_at_tva_line_4_29_base",
            "l10n_at.tax_report_line_l10n_at_tva_line_4_30_base",
            "l10n_at.tax_report_line_l10n_at_tva_line_4_31_base",
            "l10n_at.tax_report_line_l10n_at_tva_line_4_32",
        )
        report_values = self._prepare_report_values(
            "l10n_at.tax_report",
            {
                "date": {
                    "date_from": "2023-08-01",
                    "date_to": "2023-08-31",
                    "mode": "range",
                    "filter": "custom",
                },
            },
        )
        at_report_values = report_values[0]["old_values"]
        for report_line_xml_id in line_report_that_should_be_inverted:
            at_report_values[report_line_xml_id][0] = -at_report_values[report_line_xml_id][0]

        # Line tax_report_line_l10n_at_tva_line_4_33 and its parent are special cases: Tax 0% A contains repartition lines
        # with tag KZ 077, but with the correct sign. For this report line, we don't want the inverted value, but rather the
        # inverted value of move lines with the inverted tags + the current, correct value of lines with 0% A. Since all
        # base repartition lines with KZ 077 also include KZ 076, except 0% A, this test sets the desired value of
        # tax_report_line_l10n_at_tva_line_4_33 as tax_report_line_l10n_at_tva_line_4_32 + the sum of all balances with 0% A tax
        tax_0_at = (
            self.env["account.tax"]
            .with_context(active_test=False)
            .search(
                [
                    ("company_id", "=", self.company.id),
                    ("type_tax_use", "=", "purchase"),
                    ("name", "=", "0% A"),
                ]
            )
        )
        balances = self.env["account.move.line"].search([("tax_ids", "=", tax_0_at.id)]).mapped("balance")
        prefix = "l10n_at.tax_report_line_l10n_at_tva"
        at_report_values[f"{prefix}_line_4_33"][0] = at_report_values[f"{prefix}_line_4_32"][0] + sum(balances)
        # The parent report line is the sum of lines with tag KZ 076 and KZ 077
        at_report_values[f"{prefix}_sale_05_report_title"][0] = (
            at_report_values[f"{prefix}_line_4_32"][0] + at_report_values[f"{prefix}_line_4_33"][0]
        )

        return [{"l10n_at.tax_report": report_values}]

    def _check_vat_report(self, config, old_balances_by_report):
        for old_report_xmlid, old_balances in old_balances_by_report.items():
            self._check_report_values(config, old_balances[0], "l10n_at." + old_report_xmlid.split(".")[1])

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self, chart_template_ref="at"):
        res = super().prepare(chart_template_ref)
        self._generate_invoices_with_taxes()
        res["tests"].append(
            ("_check_tags_in_repartition_lines_and_amls", self._prepare_tags_in_repartition_lines_and_amls())
        )
        if util.module_installed(self.env.cr, "account_report"):
            res["tests"].append(("_check_vat_report", self._prepare_vat_report()))
        return res
