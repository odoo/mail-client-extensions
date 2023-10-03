# -*- coding: utf-8 -*-
from odoo import fields

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


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

        self.assertEqual(move.ref, "name_receivable_line")
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

    def _prepare_test_invoice_grouped(self, env_user):
        journal_grouped = env_user["account.journal"].create(
            {
                "name": "Sale grouped journal",
                "type": "sale",
                "code": "SJGRP",
                "group_invoice_lines": True,
            }
        )
        invoice = env_user["account.invoice"].create(
            {
                "journal_id": journal_grouped.id,
                "partner_id": self.partner.id,
                "type": "out_invoice",
                "date_invoice": "2016-01-01",
                "date": False,
                "account_id": self.account_receivable.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product.name,
                            "product_id": product.id,
                            "account_id": self.account_income.id,
                            "price_unit": price_unit,
                            "quantity": quantity,
                        },
                    )
                    for product, price_unit, quantity in [
                        (self.product1, 10.0, 1),
                        (self.product2, 20.0, 2),
                        (self.product2, 20.0, 2),  # Two lines with the same product and same subtotal
                        (self.product3, 30.0, 3),
                        (self.product3, 30.0, 4),  # Two lines with the same product but different subtotals
                    ]
                ],
            }
        )
        invoice.action_invoice_open()
        result = [
            (line["product_id"][0], line["quantity"], line["price_subtotal"])
            for line in env_user["account.invoice.line"].read_group(
                [("invoice_id", "=", invoice.id)], ["product_id", "quantity", "price_subtotal"], ["product_id"]
            )
        ]
        return invoice.id, result

    def _check_test_invoice_grouped(self, config, args):
        invoice_id, expected = args
        move = self.env["account.move"].browse(self._get_move_id_from_invoice_id(invoice_id))
        result = self.env["account.invoice.report"].read_group(
            [("move_id", "=", move.id)],
            ["product_id", "quantity", "price_subtotal"],
            ["product_id"],
            lazy=False,
        )
        for product_id, quantity, price_subtotal in expected:
            line = next(r for r in result if r["product_id"][0] == product_id)
            self.assertEqual(quantity, line["quantity"])
            self.assertEqual(price_subtotal, line["price_subtotal"])

    def _prepare_test_refund_with_creditors_at_debit_side(self, env_user):
        invoice = env_user["account.invoice"].create(
            {
                "partner_id": self.partner.id,
                "type": "out_refund",
                "account_id": self.account_receivable.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line",
                            "product_id": self.product.id,
                            "account_id": self.account_income.id,
                            "price_unit": 10.0,
                            "quantity": 1.0,
                        },
                    )
                ],
            }
        )
        invoice.action_invoice_open()
        move = invoice.move_id
        creditor_line = move.line_ids.filtered(lambda ln: ln.account_id == self.account_receivable)
        self.cr.execute("UPDATE account_move SET state='draft' WHERE id IN %s", (tuple(move.ids),))
        move.write(
            {
                "line_ids": [
                    (1, creditor_line.id, {"credit": 11.0}),
                    (0, 0, {"name": "/", "account_id": self.account_receivable.id, "credit": 0.0, "debit": 1.0}),
                ]
            }
        )
        move.post()
        return invoice.id

    def _check_test_refund_with_creditors_at_debit_side(self, config, args):
        move = self.env["account.move"].browse(self._get_move_id_from_invoice_id(args))
        self.assertEqual(move.type, "out_refund")

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

        self.cr.execute(
            """
            SELECT module || '.' || name
              FROM ir_model_data
             WHERE model='account.chart.template'
             ORDER BY id DESC
             LIMIT 1
            """
        )
        coa_xmlid = (
            self.env.cr.fetchone()[0] if self.env.cr.rowcount else "l10n_generic_coa.configurable_chart_template"
        )
        chart_template = env_user.ref(coa_xmlid, raise_if_not_found=False)
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
        for i in range(1, 4):
            setattr(
                self,
                "product%s" % i,
                env_user["product.product"].create(
                    {
                        "name": "Test product %s %s" % (test_name, i),
                        "uom_id": self.uom_unit.id,
                        "uom_po_id": self.uom_unit.id,
                        "property_account_income_id": self.account_income.id,
                        "property_account_expense_id": self.account_expense.id,
                    }
                ),
            )
        self.product = self.product1

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
                self._prepare_test_invoice_grouped(env_user),
                self._prepare_test_refund_with_creditors_at_debit_side(env_user),
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
        self._check_test_invoice_grouped(config, init["tests"][5])
        self._check_test_refund_with_creditors_at_debit_side(config, init["tests"][6])
