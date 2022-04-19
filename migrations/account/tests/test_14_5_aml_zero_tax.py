# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.5")
class TestAmlZeroTax(UpgradeCase):

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------
    def _prepare_test_1_simple_line(self):
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
                            "name": "line",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "tax_ids": [(6, 0, self.zero_percent_tax_sale.ids)],
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        return {"invoice": invoice.id, "zero_percent_tax": self.zero_percent_tax_sale.id}

    def _prepare_test_2_group_of_taxes(self):
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
                            "name": "line",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "tax_ids": [(6, 0, self.zero_percent_tax_group.ids)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "other line",
                            "quantity": 1.0,
                            "price_unit": 50.0,
                            "account_id": self.account_income.id,
                            "tax_ids": [(6, 0, self.zero_percent_tax_sale.ids)],
                        },
                    ),
                ],
            }
        )
        invoice.action_post()
        return {
            "invoice": invoice.id,
            "zero_percent_tax": self.zero_percent_tax.id,
            "zero_percent_tax_type_tax_use": self.zero_percent_tax_sale.id,
            "ten_percent_tax": self.ten_percent_tax.id,
            "tax_group": self.zero_percent_tax_group.id,
        }

    def _prepare_test_3_existing_line(self):
        move_type_field = "move_type" if util.version_gte("saas~13.3") else "type"
        invoice = self.env["account.move"].create(
            {
                move_type_field: "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": "2016-01-01",
                "date": "2016-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_income.id,
                            "debit": 100.0,
                            "name": "line",
                            "quantity": 1,
                            "tax_ids": [(6, 0, self.zero_percent_tax_sale.ids)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "account_id": self.account_receivable.id,
                            "credit": 100.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": self.zero_percent_tax_sale.name,
                            "partner_id": self.partner.id,
                            "tax_base_amount": 100.0,
                            "date": "2016-01-01",
                            "account_id": self.account_income.id,
                            "tax_repartition_line_id": self.zero_percent_tax_sale.invoice_repartition_line_ids.filtered(
                                lambda l: l.repartition_type == "tax"
                            ).id,
                            "tax_line_id": self.zero_percent_tax_sale.id,
                            "exclude_from_invoice_tab": True,
                        },
                    ),
                ],
            }
        )
        return {"invoice": invoice.id, "zero_percent_tax": self.zero_percent_tax_sale.id}

    def _prepare_test_4_CABA(self):
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
                            "name": "line",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "account_id": self.account_income.id,
                            "tax_ids": [(6, 0, self.zero_percent_tax_caba.ids)],
                        },
                    )
                ],
            }
        )
        invoice.action_post()
        # To create the CABA entry, we have to register a payment
        self.env["account.payment.register"].with_context(active_ids=invoice.ids, active_model="account.move").create(
            {
                "payment_date": invoice.date,
            }
        )._create_payments()
        return {
            "invoice": invoice.id,
            "zero_percent_tax_caba": self.zero_percent_tax_caba.id,
            "income_account_id": self.account_income.id,
            "caba_account_id": self.account_caba.id,
        }

    def _check_test_1_simple_line(self, data):
        invoice = self.env["account.move"].browse(data["invoice"])
        tax_lines = invoice.line_ids.filtered("tax_line_id")
        self.assertRecordValues(
            tax_lines,
            [
                {
                    "tax_line_id": data["zero_percent_tax"],
                    "tax_base_amount": 100,
                    "group_tax_id": False,
                    "balance": 0,
                }
            ],
        )

    def _check_test_2_group_of_taxes(self, data):
        invoice = self.env["account.move"].browse(data["invoice"])
        tax_lines = invoice.line_ids.filtered("tax_line_id")
        self.assertRecordValues(
            tax_lines,
            [
                {
                    "tax_line_id": data["ten_percent_tax"],
                    "tax_base_amount": 100,
                    "group_tax_id": data["tax_group"],
                    "balance": -10,
                },
                {
                    "tax_line_id": data["zero_percent_tax_type_tax_use"],
                    "tax_base_amount": 50,
                    "group_tax_id": False,
                    "balance": 0,
                },
                {
                    "tax_line_id": data["zero_percent_tax"],
                    "tax_base_amount": 100,
                    "group_tax_id": data["tax_group"],
                    "balance": 0,
                },
                {
                    "tax_line_id": data["zero_percent_tax_type_tax_use"],
                    "tax_base_amount": 100.0,
                    "group_tax_id": data["tax_group"],
                    "balance": 0,
                },
            ],
        )

    def _check_test_3_existing_line(self, data):
        invoice = self.env["account.move"].browse(data["invoice"])
        tax_lines = invoice.line_ids.filtered("tax_line_id")
        self.assertRecordValues(
            tax_lines,
            [
                {
                    "tax_line_id": data["zero_percent_tax"],
                    "tax_base_amount": 100,
                    "group_tax_id": False,
                    "balance": 0,
                }
            ],
        )

    def _check_test_4_caba(self, data):
        invoice = self.env["account.move"].browse(data["invoice"])
        if util.version_gte("saas~14.5"):
            caba_origin_field = "tax_cash_basis_origin_move_id"
        else:
            caba_origin_field = "tax_cash_basis_move_id"
        caba_move = self.env["account.move"].search([(caba_origin_field, "=", invoice.id)])
        tax_lines = invoice.line_ids.filtered("tax_line_id")
        self.assertRecordValues(
            tax_lines,
            [
                {
                    "tax_line_id": data["zero_percent_tax_caba"],
                    "tax_base_amount": 100,
                    "group_tax_id": False,
                    "balance": 0,
                    "account_id": data["caba_account_id"],
                }
            ],
        )
        self.assertRecordValues(
            caba_move.line_ids,
            [
                # Regular lines
                {
                    "tax_line_id": False,
                    "credit": 0,
                    "debit": 100,
                    "account_id": data["income_account_id"],
                },
                {
                    "tax_line_id": False,
                    "credit": 100,
                    "debit": 0,
                    "account_id": data["income_account_id"],
                },
                # CABA line to final account
                {
                    "tax_line_id": data["zero_percent_tax_caba"],
                    "credit": 0,
                    "debit": 0,
                    "account_id": data["income_account_id"],
                },
                # CABA line from caba account
                {
                    "tax_line_id": False,
                    "credit": 0,
                    "debit": 0,
                    "account_id": data["caba_account_id"],
                },
            ],
        )

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        test_name = "TestAmlZeroTax"
        self.company = self.env["res.company"].create(
            {
                "name": f"company for {test_name}",
                "user_ids": [(4, self.env.ref("base.user_admin").id)],
                "tax_exigibility": True,
            }
        )

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
                    "company_ids": [(6, 0, self.company.ids)],
                    "company_id": self.company.id,
                }
            )
        )
        user.partner_id.email = "%s@test.com" % test_name

        self.env = self.env(user=user)
        self.cr = self.env.cr

        chart_template = self.env.ref("l10n_generic_coa.configurable_chart_template", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading(company=self.company)

        revenue = self.env.ref("account.data_account_type_revenue").id
        self.account_income = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id", "=", revenue)],
            limit=1,
        )
        self.account_receivable = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id.type", "=", "receivable")],
            limit=1,
        )
        self.account_caba = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id", "=", revenue)],
            order="id desc",
            limit=1,
        )

        # Setup partner.
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner %s" % test_name,
                "property_account_receivable_id": self.account_receivable.id,
                "company_id": self.company.id,
            }
        )

        self.zero_percent_tax_caba = self.env["account.tax"].create(
            {
                "name": "zero_percent_tax_caba",
                "amount_type": "percent",
                "amount": 0.0,
                "type_tax_use": "sale",
                "tax_exigibility": "on_payment",
                "cash_basis_transition_account_id": self.account_caba.id,
            }
        )
        # Just need to have two different ones
        self.zero_percent_tax_caba.invoice_repartition_line_ids[1].account_id = self.account_income.id

        self.zero_percent_tax = self.env["account.tax"].create(
            {
                "name": "zero_percent_tax",
                "amount_type": "percent",
                "amount": 0.0,
                "type_tax_use": "none",
            }
        )

        self.ten_percent_tax = self.env["account.tax"].create(
            {
                "name": "ten_percent_tax",
                "amount_type": "percent",
                "amount": 10.0,
                "type_tax_use": "none",
            }
        )

        self.zero_percent_tax_sale = self.env["account.tax"].create(
            {
                "name": "zero_percent_tax_sale",
                "amount_type": "percent",
                "amount": 0.0,
                "type_tax_use": "sale",
            }
        )

        self.zero_percent_tax_group = self.env["account.tax"].create(
            {
                "name": "tax_group",
                "amount_type": "group",
                "type_tax_use": "sale",
                "children_tax_ids": [
                    (6, 0, (self.zero_percent_tax | self.ten_percent_tax | self.zero_percent_tax_sale).ids)
                ],
            }
        )

        return {
            "14.5-test-zero-tax-line": [
                self._prepare_test_1_simple_line(),
                self._prepare_test_2_group_of_taxes(),
                self._prepare_test_3_existing_line(),
                self._prepare_test_4_CABA(),
            ],
        }

    def check(self, init):
        self._check_test_1_simple_line(init["14.5-test-zero-tax-line"][0])
        self._check_test_2_group_of_taxes(init["14.5-test-zero-tax-line"][1])
        self._check_test_3_existing_line(init["14.5-test-zero-tax-line"][2])
        self._check_test_4_caba(init["14.5-test-zero-tax-line"][3])
