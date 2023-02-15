# -*- coding: utf-8 -*-
from .test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("16.0")
class TestAnalyticApocalypse(TestAccountingSetupCommon):
    def _prepare_analytic_tests(self):
        self.env.user.write(
            {
                "groups_id": [
                    (4, self.env.ref("analytic.group_analytic_accounting").id),
                    (4, self.env.ref("analytic.group_analytic_tags").id),
                ],
            }
        )
        self.analytic_account = self.env["account.analytic.account"].create(
            {
                "name": "Account A",
            }
        )
        self.analytic_tag = self.env["account.analytic.tag"].create(
            {
                "name": "Tag 1",
                "active_analytic_distribution": True,
            }
        )
        self.analytic_tag_without_distribution = self.env["account.analytic.tag"].create(
            {
                "name": "Tag Without Distribution",
                "active_analytic_distribution": False,
            }
        )
        self.env["account.analytic.distribution"].create(
            {
                "account_id": self.analytic_account.id,
                "percentage": 50,
                "tag_id": self.analytic_tag.id,
            }
        )

    def _prepare_analytic_distribution_move_test(self):
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
                            "analytic_account_id": self.analytic_account.id,
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
                            "analytic_account_id": self.analytic_account.id,
                            "analytic_tag_ids": [(6, 0, self.analytic_tag.ids)],
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
                            "analytic_tag_ids": [(6, 0, self.analytic_tag.ids)],
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
                    (
                        0,
                        0,
                        {
                            "name": "line5",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "analytic_tag_ids": [(6, 0, self.analytic_tag_without_distribution.ids)],
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "line6",
                            "quantity": 1.0,
                            "price_unit": 100.0,
                            "analytic_account_id": self.analytic_account.id,
                            "analytic_tag_ids": [(6, 0, self.analytic_tag_without_distribution.ids)],
                        },
                    ),
                ],
            }
        )

        return [invoice.id, self.analytic_account.id]

    def _prepare_analytic_default_model_test(self):
        product = self.env["product.product"].create(
            {
                "name": "Product",
                "list_price": 15.00,
                "standard_price": 15.00,
            }
        )
        analytic_account_company = self.env["account.analytic.account"].create(
            {
                "name": "Account Company",
                "company_id": self.company.id,
            }
        )
        second_company = self.env["res.company"].create(
            {
                "name": "Second Company",
            }
        )
        self.env["account.analytic.default"].create(
            [
                {
                    "analytic_id": self.analytic_account.id,
                    "analytic_tag_ids": [(6, 0, self.analytic_tag.ids)],
                    "product_id": product.id,
                    "account_id": self.account_receivable.id,
                    "partner_id": self.partner.id,
                },
                {
                    "analytic_id": analytic_account_company.id,
                    "account_id": self.account_receivable.id,
                    "partner_id": self.partner.id,
                },
                # Should not be transmitted
                {
                    "analytic_id": analytic_account_company.id,
                    "product_id": product.id,
                    "partner_id": self.partner.id,
                    "company_id": second_company.id,
                },
            ]
        )

        return [
            {
                "analytic_account_id": self.analytic_account.id,
                "product_id": product.id,
                "analytic_account_company_id": analytic_account_company.id,
                "partner_id": self.partner.id,
                "account_receivable_code": self.account_receivable.code,
            }
        ]

    def _check_analytic_distribution_move_test(self, config, invoice_id, analytic_account_id):
        invoice = self.env["account.move"].browse(invoice_id)
        analytic_account_from_tag = self.env["account.analytic.account"].search(
            [("name", "=", "Tag Without Distribution")]
        )

        self.assertEqual(invoice.invoice_line_ids[0].analytic_distribution, {str(analytic_account_id): 100.0})
        self.assertEqual(invoice.invoice_line_ids[1].analytic_distribution, {str(analytic_account_id): 150.0})
        self.assertEqual(invoice.invoice_line_ids[2].analytic_distribution, {str(analytic_account_id): 50.0})
        self.assertEqual(invoice.invoice_line_ids[3].analytic_distribution, False)
        self.assertEqual(invoice.invoice_line_ids[4].analytic_distribution, {str(analytic_account_from_tag.id): 100.0})
        self.assertEqual(
            invoice.invoice_line_ids[5].analytic_distribution,
            {str(analytic_account_id): 100.0, str(analytic_account_from_tag.id): 100.0},
        )

    def _check_analytic_default_model_test(self, config, values):
        distribution_model = self.env["account.analytic.distribution.model"].search([], order="id asc")
        self.assertRecordValues(
            distribution_model,
            [
                {
                    "analytic_distribution": {str(values["analytic_account_id"]): 150.0},
                    "product_id": values["product_id"],
                    "partner_id": values["partner_id"],
                    "account_prefix": values["account_receivable_code"],
                },
                {
                    "analytic_distribution": {str(values["analytic_account_company_id"]): 100.0},
                    "product_id": False,
                    "partner_id": values["partner_id"],
                    "account_prefix": values["account_receivable_code"],
                },
            ],
        )

    def prepare(self):
        res = super().prepare()
        self._prepare_analytic_tests()
        res["tests"].append(("_check_analytic_distribution_move_test", self._prepare_analytic_distribution_move_test()))
        res["tests"].append(("_check_analytic_default_model_test", self._prepare_analytic_default_model_test()))
        return res
