# -*- coding: utf-8 -*-

from odoo import fields
from odoo.tests.common import Form

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import module_installed, version_gte
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock


@change_version("14.1")
class TestTagNoInvert(UpgradeCase):
    def prepare(self):
        def register_payment(invoice):
            self.env["account.payment.register"].with_context(
                active_ids=invoice.ids, active_model="account.move"
            ).create(
                {
                    "payment_date": invoice.date,
                }
            )._create_payments()

        def match_opposite(invoices):
            invoices.mapped("line_ids").filtered(
                lambda x: x.account_internal_type in ("receivable", "payable")
            ).reconcile()

        def neg_line_invoice_generator(inv_type, partner, account, date, tax):
            return self.env["account.move"].create(
                {
                    "move_type": inv_type,
                    "partner_id": partner.id,
                    "invoice_date": date,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "test",
                                "quantity": -1,
                                "account_id": account.id,
                                "price_unit": 100,
                                "tax_ids": [(6, 0, tax.ids)],
                            },
                        ),
                        # Second line, so that the invoice doesn't have a negative total
                        (
                            0,
                            0,
                            {
                                "name": "test",
                                "quantity": 1,
                                "account_id": account.id,
                                "price_unit": 200,
                            },
                        ),
                    ],
                }
            )

        def invoice_like_misc_generator(inv_type, partner, account, date, tax):
            account_type = tax.type_tax_use == "sale" and "receivable" or "payable"
            reconcilable_account = self.env["account.account"].search(
                [("company_id", "=", self.env.company.id), ("internal_type", "=", account_type)], limit=1
            )

            # We create the move in a form so that the onchanges creating the tax lines are called
            debit_positive = inv_type in ("in_invoice", "out_refund")
            with Form(self.env["account.move"].with_context(default_move_type="entry")) as move_form:
                move_form.partner_id = partner
                move_form.date = date

                with move_form.line_ids.new() as base_line:
                    base_line.name = "test"
                    base_line.account_id = account
                    base_line.tax_ids.add(tax)
                    base_line.debit = 100 if debit_positive else 0
                    base_line.credit = 0 if debit_positive else 100

                with move_form.line_ids.new() as counterpart_line:
                    counterpart_line.name = "test"
                    counterpart_line.account_id = reconcilable_account
                    counterpart_line.debit = 0 if debit_positive else 138.25
                    counterpart_line.credit = 138.25 if debit_positive else 0

            return move_form.save()

        def invoice_only_tags_generator(inv_type, partner, account, date, tax):
            rep_lines = getattr(tax, "%s_repartition_line_ids" % inv_type.split("_")[1])

            tax_rep_ln = rep_lines.filtered(lambda x: x.repartition_type == "tax")[0]
            base_rep_ln = rep_lines.filtered(lambda x: x.repartition_type == "base")

            rslt = self.env["account.move"].create(
                {
                    "move_type": inv_type,
                    "partner_id": partner.id,
                    "invoice_date": date,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "test_base",
                                "quantity": 1,
                                "account_id": account.id,
                                "price_unit": 100,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "test_tax",
                                "quantity": 1,
                                "account_id": tax_rep_ln.account_id,
                                "price_unit": 45,
                                "tax_ids": [(5, 0, 0)],
                            },
                        ),
                    ],
                }
            )

            rslt.line_ids.filtered(lambda x: x.name == "test_base").tax_tag_ids = [(6, 0, base_rep_ln.tag_ids.ids)]
            rslt.line_ids.filtered(lambda x: x.name == "test_tax").tax_tag_ids = [(6, 0, tax_rep_ln.tag_ids.ids)]

            return rslt

        with no_fiscal_lock(self.env.cr):
            # Ensure the lock dates allow what we are doing
            self.env.company.fiscalyear_lock_date = None
            self.env.company.tax_lock_date = None
            self.env.company.period_lock_date = None

            # Create a tax report for a brand new country
            country = self.env["res.country"].create(
                {
                    "name": "Wakanda",
                    "code": "WA",
                }
            )
            tax_report = self.env["account.tax.report"].create(
                {
                    "name": "Test",
                    "country_id": country.id,
                }
            )
            self.env.company.account_tax_fiscal_country_id = country
            self.env.company.country_id = country

            if module_installed(self.env.cr, "l10n_latam_invoice_document"):
                domain = [("company_id", "=", self.env.company.id), ("l10n_latam_use_documents", "=", True)]
                self.env["account.journal"].search(domain).write({"l10n_latam_use_documents": False})

            # Populate the tax report
            today = fields.Date.today()

            # Case 1: Invoice with a single, positive line and a payment
            self._instantiate_test_data(tax_report, "case1", today, on_invoice_created=register_payment)
            # Case 2: Invoice containing a line with a negative quantity (and some tax on it), paid with a payment
            self._instantiate_test_data(
                tax_report,
                "case2",
                today,
                invoice_generator=neg_line_invoice_generator,
                on_invoice_created=register_payment,
            )
            # Case 3: Invoice reconciled with a credit note
            self._instantiate_test_data(tax_report, "case3", today, on_all_invoices_created=match_opposite)
            # Case 4: Invoice and credit note with a negative line, reconciled together
            self._instantiate_test_data(tax_report, "case4", today, on_all_invoices_created=match_opposite)
            # Case 5: Misc operations with taxes, reconciled together
            self._instantiate_test_data(
                tax_report,
                "case5",
                today,
                on_all_invoices_created=match_opposite,
                invoice_generator=invoice_like_misc_generator,
            )
            # Case 6: Invoice with tags, but without taxes (could happen with stuff imported from other softwares)
            self._instantiate_test_data(
                tax_report,
                "case6",
                today,
                on_invoice_created=register_payment,
                invoice_generator=invoice_only_tags_generator,
            )

            # Generate the report
            report_lines = self._get_report_lines(today)

            report_balances = {}
            for report_line in report_lines:
                if version_gte("saas~14.5"):
                    line_id = self.env["account.generic.tax.report"]._parse_line_id(report_line["id"])[-1][2]
                else:
                    line_id = report_line["id"]
                report_balances[str(line_id)] = report_line["columns"][0]["balance"]

            return str(today), report_balances

    def _instantiate_test_data(
        self, tax_report, label, today, invoice_generator=None, on_invoice_created=None, on_all_invoices_created=None
    ):
        def default_invoice_generator(inv_type, partner, account, date, tax):
            return self.env["account.move"].create(
                {
                    "move_type": inv_type,
                    "partner_id": partner.id,
                    "invoice_date": date,
                    "invoice_line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "test",
                                "quantity": 1,
                                "account_id": account.id,
                                "price_unit": 100,
                                "tax_ids": [(6, 0, tax.ids)],
                            },
                        )
                    ],
                }
            )

        partner = self.env["res.partner"].create({"name": label})

        # Create invoice and refund using the tax we just made
        invoice_types = {"sale": ("out_invoice", "out_refund"), "purchase": ("in_invoice", "in_refund")}

        account_types = {
            "sale": self.env.ref("account.data_account_type_revenue").id,
            "purchase": self.env.ref("account.data_account_type_expenses").id,
        }
        for tax_exigibility in ("on_invoice", "on_payment"):
            for type_tax_use in ("sale", "purchase"):

                tax = self._instantiate_test_tax(
                    tax_report, "%s-%s-%s" % (label, type_tax_use, tax_exigibility), type_tax_use, tax_exigibility
                )

                invoices = self.env["account.move"]
                domain = [
                    ("company_id", "=", self.env.company.id),
                    ("user_type_id", "=", account_types[tax.type_tax_use]),
                ]
                account = self.env["account.account"].search(domain, limit=1)
                for inv_type in invoice_types[tax.type_tax_use]:
                    invoice = (invoice_generator or default_invoice_generator)(inv_type, partner, account, today, tax)
                    invoice.action_post()
                    invoices += invoice

                    if on_invoice_created:
                        on_invoice_created(invoice)

                if on_all_invoices_created:
                    on_all_invoices_created(invoices)

    def _instantiate_test_tax(self, tax_report, label, type_tax_use, tax_exigibility):
        tax_report_line = self.env["account.tax.report.line"].create(
            {
                "name": label,
                "report_id": tax_report.id,
                "tag_name": label,
                "sequence": len(tax_report.line_ids),
            }
        )

        tax_template = self.env["account.tax.template"].create(
            {
                "name": label,
                "amount": 45,
                "amount_type": "percent",
                "type_tax_use": type_tax_use,
                "chart_template_id": self.env.company.chart_template_id.id,
                "tax_exigibility": tax_exigibility,
                "invoice_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "base",
                            "plus_report_line_ids": tax_report_line.ids,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 25,
                            "repartition_type": "tax",
                            "plus_report_line_ids": tax_report_line.ids,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 75,
                            "repartition_type": "tax",
                            "plus_report_line_ids": tax_report_line.ids,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": -10,
                            "repartition_type": "tax",
                            "plus_report_line_ids": tax_report_line.ids,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": -5,
                            "repartition_type": "tax",
                            "minus_report_line_ids": tax_report_line.ids,
                        },
                    ),
                ],
                "refund_repartition_line_ids": [
                    (
                        0,
                        0,
                        {
                            "factor_percent": 100,
                            "repartition_type": "base",
                            "minus_report_line_ids": tax_report_line.ids,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 25,
                            "repartition_type": "tax",
                            "minus_report_line_ids": tax_report_line.ids,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": 75,
                            "repartition_type": "tax",
                            # No tags on this repartition line, on purpose: this way we have an asymmetric
                            # repartition between invoice and refund and avoid shadowing effects if something is wrong
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": -10,
                            "repartition_type": "tax",
                            "minus_report_line_ids": tax_report_line.ids,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "factor_percent": -5,
                            "repartition_type": "tax",
                            # Same as for the 75 repartition line: we force asymmetry
                        },
                    ),
                ],
            }
        )

        # The template needs an xmlid in order so that we can call _generate_tax
        self.env["ir.model.data"].create(
            {
                "name": "account_reports.14_1_migration_test_tax_report_tax_" + label,
                "module": "account_reports",
                "res_id": tax_template.id,
                "model": "account.tax.template",
            }
        )
        tax_id = tax_template._generate_tax(self.env.user.company_id)["tax_template_to_tax"][tax_template.id]
        return self.env["account.tax"].browse(tax_id)

    def _get_report_lines(self, today):
        report = self.env["account.generic.tax.report"]
        report_opt = report._get_options(
            {
                "date": {
                    "period_type": "custom",
                    "filter": "custom",
                    "date_to": today,
                    "mode": "range",
                    "date_from": today,
                }
            }
        )
        new_context = report._set_context(report_opt)
        return report.with_context(new_context)._get_lines(report_opt)

    def check(self, init):
        today, report_balances = init

        # Check the tax report is unchanged
        for report_line in self._get_report_lines(today):
            if version_gte("saas~14.5"):
                line_id = self.env["account.generic.tax.report"]._parse_line_id(report_line["id"])[-1][2]
            else:
                line_id = report_line["id"]
            self.assertEqual(
                report_line["columns"][0]["balance"],
                report_balances[str(line_id)],
                "Tags reinversion modified the tax report!",
            )

        # Check we don't have inconsistent tax_tag_invert values
        # This is necessary to ensure we haven't inverted too many tags (it happened ...),
        # totally inverting the tags, but keeping the tax report correct, hence shadowing the error.

        # Cash basis entries from invoices with negative lines shouldn't be inverted
        neg_amount_lines = self.env["account.move.line"].search(
            [("move_id.move_type", "!=", "entry"), ("quantity", "<", 0)]
        )
        all_neg_invoice_ids = neg_amount_lines.mapped("move_id.id")

        if version_gte("saas~14.5"):
            caba_origin_field = "tax_cash_basis_origin_move_id"
        else:
            caba_origin_field = "tax_cash_basis_move_id"

        neg_inv_caba_moves = self.env["account.move"].search([(caba_origin_field, "in", all_neg_invoice_ids)])

        for neg_caba_move in neg_inv_caba_moves:
            check_value = any(neg_caba_move.mapped("line_ids.tax_tag_invert"))
            self.assertFalse(
                check_value,
                f"Cash basis entries from invoices with negative lines shouldn't have been inverted (move {neg_caba_move.name})",
            )

        # Check base lines for all other entries
        wrong_base_lines = self.env["account.move.line"].search(
            [
                ("tax_ids", "!=", False),
                ("tax_repartition_line_id", "=", False),
                ("move_id", "not in", neg_inv_caba_moves.ids),
                "|",
                "&",
                ("tax_tag_invert", "=", True),
                "|",
                ("move_id.move_type", "in", ["in_invoice", "out_refund", "in_receipt"]),
                "&",
                "&",
                ("move_id.move_type", "=", "entry"),
                ("tax_ids.type_tax_use", "in", ["sale"]),
                ("debit", ">", 0),
                "&",
                ("tax_tag_invert", "=", False),
                "|",
                ("move_id.move_type", "in", ["out_invoice", "in_refund", "out_receipt"]),
                "&",
                "&",
                ("move_id.move_type", "=", "entry"),
                ("tax_ids.type_tax_use", "in", ["purchase"]),
                ("credit", ">", 0),
            ]
        )

        wrong_base_move_names = set(wrong_base_lines.mapped("move_id.name"))
        self.assertFalse(
            wrong_base_lines,
            "The following moves contain incorrect tax_tag_invert on base lines: %s" % wrong_base_move_names,
        )

        # Check tax lines for all other entries
        wrong_tax_lines = self.env["account.move.line"].search(
            [
                ("move_id", "not in", neg_inv_caba_moves.ids),
                ("tax_repartition_line_id", "!=", False),
                "|",
                "&",
                "&",
                ("tax_tag_invert", "=", True),
                ("tax_line_id.type_tax_use", "=", "sale"),
                ("tax_repartition_line_id.refund_tax_id", "!=", False),
                "&",
                "&",
                ("tax_tag_invert", "=", False),
                ("tax_line_id.type_tax_use", "=", "purchase"),
                ("tax_repartition_line_id.refund_tax_id", "!=", False),
            ]
        )

        wrong_tax_move_names = set(wrong_tax_lines.mapped("move_id.name"))
        self.assertFalse(
            wrong_tax_lines,
            "The following moves contain incorrect tax_tag_invert on tax lines: %s" % wrong_tax_move_names,
        )
