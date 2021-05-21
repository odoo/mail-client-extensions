# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.tests import tagged

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util.accounting import no_fiscal_lock


@tagged("amount_signed")
@change_version("12.4")
class CheckTotalSigned(UpgradeCase):
    def prepare(self):
        with no_fiscal_lock(self.env.cr):
            move_ids = []
            currency_eur = self.env.ref("base.EUR")
            currency_usd = self.env.ref("base.USD")
            company = self.env["res.company"].create({"name": "company 1", "currency_id": currency_usd.id})
            account_user = (
                self.env["res.users"]
                .with_context({"no_reset_password": True})
                .create(
                    {
                        "name": "Accountant for tests",
                        "company_id": company.id,
                        "company_ids": [(4, company.id)],
                        "login": "at",
                        "email": "at@test.com",
                    }
                )
            )
            self_sudo = account_user.sudo(account_user)
            self_sudo.env["res.currency.rate"].create(
                {"currency_id": currency_usd.id, "rate": 1.0, "name": "2020-05-25"}
            )
            self_sudo.env["res.currency.rate"].create(
                {"currency_id": currency_eur.id, "name": "2020-05-25", "rate": 2.0}
            )
            user_type_receivable = self.env.ref("account.data_account_type_receivable")
            user_type_payable = self.env.ref("account.data_account_type_payable")
            receivable_account_id = self_sudo.env["account.account"].create(
                {
                    "code": "TR1",
                    "name": "Test Receivable Account",
                    "user_type_id": user_type_receivable.id,
                    "reconcile": True,
                }
            )
            payable_account_id = self_sudo.env["account.account"].create(
                {
                    "code": "TP1",
                    "name": "Test Payable Account",
                    "user_type_id": user_type_payable.id,
                    "reconcile": True,
                }
            )
            partner_id = self_sudo.env["res.partner"].create(
                {
                    "name": "Test upgrade partner",
                    "email": "t@test.com",
                    "property_account_receivable_id": receivable_account_id.id,
                    "property_account_payable_id": payable_account_id.id,
                }
            )
            user_type_income = self.env.ref("account.data_account_type_revenue")
            user_type_expense = self.env.ref("account.data_account_type_expenses")
            account_income_id = self_sudo.env["account.account"].create(
                {"code": "PC200", "name": "Product Sale", "user_type_id": user_type_income.id}
            )
            account_expense_id = self_sudo.env["account.account"].create(
                {"code": "PC220", "name": "Product Purchase", "user_type_id": user_type_expense.id}
            )

            journal_sale = self_sudo.env["account.journal"].create(
                {"name": "Sale Journal Test", "code": "SALE-JT", "type": "sale"}
            )
            journal_purchase = self_sudo.env["account.journal"].create(
                {"name": "Purchase Journal Test", "code": "PURC-JT", "type": "purchase"}
            )
            journal_general = self_sudo.env["account.journal"].create(
                {"name": "General Test", "code": "GENERAL-JT", "type": "general"}
            )
            tax_15 = self_sudo.env["account.tax"].create(
                {"name": "Tax 15%", "amount": 15, "amount_type": "percent", "type_tax_use": "sale", "sequence": 10}
            )
            tax_15_P = self_sudo.env["account.tax"].create(
                {"name": "Tax 15%", "amount": 15, "amount_type": "percent", "type_tax_use": "purchase", "sequence": 10}
            )

            for _type, journal, account, tax in [
                ("out", journal_sale, account_income_id, tax_15),
                ("in", journal_purchase, account_expense_id, tax_15_P),
            ]:
                for subtype in ("invoice", "refund"):
                    invoice_type = "%s_%s" % (_type, subtype)
                    invoice = self_sudo.env["account.invoice"].create(
                        {
                            "name": "Test Upgrades",
                            "type": invoice_type,
                            "journal_id": journal.id,
                            "partner_id": partner_id.id,
                            "currency_id": currency_eur.id,
                            "invoice_line_ids": [
                                (
                                    0,
                                    0,
                                    {
                                        "quantity": 1,
                                        "account_id": account.id,
                                        "name": "update test",
                                        "price_unit": 100,
                                        "invoice_line_tax_ids": [(6, 0, [tax.id])],
                                    },
                                )
                            ],
                        }
                    )
                    invoice.action_invoice_open()
                    move_ids.append(invoice.move_id.id)

            # Create a miscellaneous move (type 'entry') to check its totals are correctly computed by the upgrade
            # See previous comment
            account_asset_id = self_sudo.env["account.account"].create(
                {
                    "code": "PC241",
                    "name": "Assets",
                    "user_type_id": self.env.ref("account.data_account_type_non_current_assets").id,
                }
            )
            account_depreciation_id = self_sudo.env["account.account"].create(
                {
                    "code": "PC630",
                    "name": "Depreciation",
                    "user_type_id": self.env.ref("account.data_account_type_depreciation").id,
                }
            )
            misc_move = self_sudo.env["account.move"].create(
                {
                    "journal_id": journal_general.id,
                    "currency_id": currency_eur.id,
                    "line_ids": [
                        (0, 0, {"account_id": account_asset_id.id, "credit": 200}),
                        (0, 0, {"account_id": account_depreciation_id.id, "debit": 200}),
                    ],
                }
            )
            misc_move.action_post()
            move_ids.append(misc_move.id)

        return {"move_ids": move_ids}

    def check(self, init):
        result = init
        check_fields = [
            "amount_untaxed",
            "amount_untaxed_signed",
            "amount_tax",
            "amount_tax_signed",
            "amount_total",
            "amount_total_signed",
            "amount_residual",
            "amount_residual_signed",
        ]

        for move in self.env["account.move"].browse(result["move_ids"]):
            origin = {}

            # 1. Recover the value computed by the upgrade
            for field in check_fields:
                origin[field] = move[field]

            # 2. Force the recomputation by the ORM
            move._compute_amount()

            # 3. Assert the value computed by the upgrade and the ORM are the same
            for field in check_fields:
                self.assertEqual(
                    move[field],
                    origin[field],
                    "The move field '%s' value computed by the upgrade is different than the value computed by the ORM"
                    % field,
                )
