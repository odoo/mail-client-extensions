# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo import fields


@change_version("12.4")
class TestAccountPocalypse(UpgradeCase):

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def _get_move_id_from_invoice_id(self, invoice_id):
        self.cr.execute("SELECT move_id FROM account_invoice WHERE id = %s", [invoice_id])
        return self.cr.fetchone()[0]

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_out_invoice_payment_reference_draft(self, env_user):
        invoice = env_user["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "type": "out_invoice",
                "date_invoice": "2016-01-01",
                "account_id": self.account_receivable.id,
                "reference": "CUST123456789",  # Payment Ref.
                "name": "name_receivable_line",  # Reference/Description
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line",
                            "product_id": self.product.id,
                            "account_id": self.account_income.id,
                            "price_unit": 1.0,
                            "quantity": 1.0,
                        },
                    ),
                ],
            }
        )
        return invoice.id

    def _check_test_out_invoice_payment_reference_draft(self, config, invoice_id):
        move = self.env["account.move"].browse(self._get_move_id_from_invoice_id(invoice_id))
        receivable_line = move.line_ids.filtered(lambda line: line.account_id.id == config["account_receivable_id"])

        self.assertFalse(move.ref)
        self.assertEqual(move.invoice_payment_ref, "CUST123456789")
        self.assertEqual(receivable_line.name, "CUST123456789")

    def _prepare_test_out_invoice_payment_reference_posted(self, env_user):
        invoice = env_user["account.invoice"].browse(self._prepare_test_out_invoice_payment_reference_draft(env_user))
        invoice.action_invoice_open()

        move = invoice.move_id
        receivable_line = move.line_ids.filtered(lambda line: line.account_id == self.account_receivable)

        self.assertEqual(move.ref, invoice.reference)
        self.assertEqual(receivable_line.name, invoice.name)

        return invoice.move_id.id

    def _check_test_out_invoice_payment_reference_posted(self, config, move_id):
        move = self.env["account.move"].browse(move_id)
        receivable_line = move.line_ids.filtered(lambda line: line.account_id.id == config["account_receivable_id"])

        self.assertEqual(move.ref, "name_receivable_line")
        self.assertEqual(move.invoice_payment_ref, "CUST123456789")
        self.assertEqual(receivable_line.name, "CUST123456789")

    def _prepare_test_in_invoice_payment_reference_draft(self, env_user):
        invoice = env_user["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "type": "in_invoice",
                "date_invoice": "2016-01-01",
                "account_id": self.account_payable.id,
                "reference": "VENDOR11111",  # Vendor Reference.
                "name": "name_payable_line",  # Reference/Description
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line",
                            "product_id": self.product.id,
                            "account_id": self.account_expense.id,
                            "price_unit": 1.0,
                            "quantity": 1.0,
                        },
                    )
                ],
            }
        )
        return invoice.id

    def _check_test_in_invoice_payment_reference_draft(self, config, invoice_id):
        move = self.env["account.move"].browse(self._get_move_id_from_invoice_id(invoice_id))
        payable_line = move.line_ids.filtered(lambda line: line.account_id.id == config["account_payable_id"])

        self.assertEqual(move.ref, "VENDOR11111")
        self.assertEqual(move.invoice_payment_ref, "name_payable_line")
        self.assertEqual(payable_line.name, "name_payable_line")

    def _prepare_test_in_invoice_payment_reference_posted(self, env_user):
        invoice = env_user["account.invoice"].browse(self._prepare_test_in_invoice_payment_reference_draft(env_user))
        invoice.reference = "VENDOR22222"
        invoice.action_invoice_open()

        move = invoice.move_id
        payable_line = move.line_ids.filtered(lambda line: line.account_id == self.account_payable)

        self.assertEqual(move.ref, invoice.reference)
        self.assertEqual(payable_line.name, invoice.name)

        return invoice.move_id.id

    def _check_test_in_invoice_payment_reference_posted(self, config, move_id):
        move = self.env["account.move"].browse(move_id)
        payable_line = move.line_ids.filtered(lambda line: line.account_id.id == config["account_payable_id"])

        self.assertEqual(move.ref, "VENDOR22222")
        self.assertEqual(move.invoice_payment_ref, "name_payable_line")
        self.assertEqual(payable_line.name, "name_payable_line")  # line remains untouched.

    def _prepare_test_invoice_no_accounting_date(self, env_user):
        invoice = env_user["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "type": "out_invoice",
                "date_invoice": "2016-01-01",
                "date": False,
                "account_id": self.account_receivable.id,
                "reference": "CUST123456789",  # Payment Ref.
                "name": "name_receivable_line",  # Reference/Description
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line",
                            "product_id": self.product.id,
                            "account_id": self.account_income.id,
                            "price_unit": 1.0,
                            "quantity": 1.0,
                        },
                    )
                ],
            }
        )
        return invoice.id

    def _check_test_invoice_no_accounting_date(self, config, invoice_id):
        move = self.env["account.move"].browse(self._get_move_id_from_invoice_id(invoice_id))

        self.assertEqual(move.date, fields.Date.from_string("2016-01-01"))

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        test_name = "TestAccountPocalypse"
        company = self.env["res.company"].create({"name": "company for %s" % test_name})

        # Create user.
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "user %s" % test_name,
                    "login": test_name,
                    "groups_id": [
                        (6, 0, self.env.user.groups_id.ids),
                        (4, self.env.ref("account.group_account_user").id),
                    ],
                    "company_ids": [(6, 0, company.ids)],
                    "company_id": company.id,
                }
            )
        )
        user.partner_id.email = "%s@test.com" % test_name

        env_user = user.sudo(user).env

        chart_template = env_user.ref("l10n_generic_coa.configurable_chart_template", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading_for_current_company()

        # Setup accounts.
        self.account_income = env_user["account.account"].search(
            [
                ("company_id", "=", company.id),
                ("user_type_id", "=", env_user.ref("account.data_account_type_revenue").id),
            ],
            limit=1,
        )
        self.account_expense = env_user["account.account"].search(
            [
                ("company_id", "=", company.id),
                ("user_type_id", "=", env_user.ref("account.data_account_type_expenses").id),
            ],
            limit=1,
        )
        self.account_receivable = env_user["account.account"].search(
            [("company_id", "=", company.id), ("user_type_id.type", "=", "receivable")], limit=1
        )
        self.account_payable = env_user["account.account"].search(
            [("company_id", "=", company.id), ("user_type_id.type", "=", "payable")], limit=1
        )

        # Setup product.
        self.uom_unit = env_user.ref("uom.product_uom_unit")
        self.product = env_user["product.product"].create(
            {
                "name": "Test product %s" % test_name,
                "uom_id": self.uom_unit.id,
                "uom_po_id": self.uom_unit.id,
                "property_account_income_id": self.account_income.id,
                "property_account_expense_id": self.account_expense.id,
            }
        )

        # Setup partner.
        self.partner = env_user["res.partner"].create(
            {
                "name": "Test partner %s" % test_name,
                "property_account_receivable_id": self.account_receivable.id,
                "property_account_payable_id": self.account_payable.id,
                "company_id": company.id,
            }
        )

        return {
            "tests": [
                self._prepare_test_out_invoice_payment_reference_draft(env_user),
                self._prepare_test_out_invoice_payment_reference_posted(env_user),
                self._prepare_test_in_invoice_payment_reference_draft(env_user),
                self._prepare_test_in_invoice_payment_reference_posted(env_user),
                self._prepare_test_invoice_no_accounting_date(env_user),
            ],
            "config": {
                "account_income_id": self.account_income.id,
                "account_expense_id": self.account_expense.id,
                "account_receivable_id": self.account_receivable.id,
                "account_payable_id": self.account_payable.id,
            },
        }

    def check(self, init):
        config = init["config"]
        self._check_test_out_invoice_payment_reference_draft(config, init["tests"][0])
        self._check_test_out_invoice_payment_reference_posted(config, init["tests"][1])
        self._check_test_in_invoice_payment_reference_draft(config, init["tests"][2])
        self._check_test_in_invoice_payment_reference_posted(config, init["tests"][3])
        self._check_test_invoice_no_accounting_date(config, init["tests"][4])
