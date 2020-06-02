# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.tests import tagged


@tagged("amount_signed")
@change_version("12.4")
class CheckTotalSigned(UpgradeCase):
    def prepare(self):
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
                    "email": "at@test.com"
                }
            )
        )
        self_sudo = account_user.sudo(account_user)
        self_sudo.env['res.currency.rate'].create({
            'currency_id': currency_usd.id,
            'rate': 1.0,
            'name': '2020-05-25',
        })
        self_sudo.env["res.currency.rate"].create(
            {
            'currency_id': currency_eur.id,
            'name': '2020-05-25',
             "rate": 2.0
            }
        )
        user_type_receivable = self.env.ref('account.data_account_type_receivable')
        receivable_account_id = self_sudo.env['account.account'].create({
            'code': 'TR1',
            'name': 'Test Receivable Account',
            'user_type_id': user_type_receivable.id,
            'reconcile': True,
        })
        partner_id = self_sudo.env["res.partner"].create({
            'name': 'Test upgrade partner',
            'email': 't@test.com',
            'property_account_receivable_id': receivable_account_id.id
        })
        user_type_income = self.env.ref('account.data_account_type_revenue')
        account_income_id = self_sudo.env['account.account'].create({
            'code': 'PC211',
            'name': 'Product Sale',
            'user_type_id': user_type_income.id
        })

        journal_sale = self_sudo.env['account.journal'].create({
            'name': 'Sale Journal Test',
            'code': 'SALE-JT',
            'type': 'sale'
        })
        journal_general = self_sudo.env['account.journal'].create({
            'name': 'General Test',
            'code': 'GENERAL-JT',
            'type': 'general'
        })
        tax_15 = self_sudo.env["account.tax"].create(
            {"name": "Tax 15%", "amount": 15, "amount_type": "percent", "type_tax_use": "sale", "sequence": 10}
        )
        invoice = self_sudo.env['account.invoice'].create(
            {
                "name": "Test Upgrades",
                "journal_id": journal_sale.id,
                "partner_id": partner_id.id,
                "currency_id": currency_eur.id,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "quantity": 1,
                            "account_id": account_income_id.id,
                            "name": "update test",
                            "price_unit": 100,
                            "invoice_line_tax_ids": [(6, 0, [tax_15.id])],

                        },
                    )
                ]
                ,
            }
        )
        invoice.action_invoice_open()
        return {"move": invoice.move_id.id}

    def check(self, init):
        result = init
        #company currency USD:
        #invoice in currrency EUR with rate 2.0
        move = self.env["account.move"].browse(result['move'])
        self.env.cr.execute(
            """
            SELECT sum(balance) as amount, sum(amount_currency) as amount_curr
              FROM account_move_line
             WHERE exclude_from_invoice_tab = false
               AND move_id= %s
          GROUP BY move_id
          """, [move.id]
        )
        move_amount_untaxed = self.cr.dictfetchone()
        self.cr.execute(
            """
            SELECT COALESCE(SUM(balance), 0.0) as amount, COALESCE(SUM(amount_currency), 0.0) as amount_curr
              FROM account_move_line
             WHERE tax_line_id IS NOT NULL
               AND move_id= %s
          GROUP BY move_id
        """, [move.id]
        )
        move_amount_taxed = self.cr.dictfetchone()
        self.env.cr.execute(
            """
            SELECT sum(balance) as amount, sum(amount_currency) as amount_curr
              FROM account_move_line
             WHERE account_internal_type NOT IN ('receivable', 'payable')
               AND move_id= %s
          GROUP BY move_id
          """, [move.id]
        )
        move_amount_total = self.cr.dictfetchone()
        self.env.cr.execute(
            """
            SELECT sum(amount_residual) as amount,
                   sum(amount_residual_currency) as amount_curr
              FROM account_move_line
             WHERE account_internal_type IN ('receivable', 'payable')
               AND move_id=%s
          GROUP BY move_id
          """, [move.id]
        )
        move_amount_residual = self.cr.dictfetchone()

        self.assertEqual(move.amount_untaxed, move_amount_untaxed['amount_curr'] * (-1))
        self.assertEqual(move.amount_untaxed_signed, move_amount_untaxed['amount'] * (-1))
        self.assertEqual(move.amount_tax, move_amount_taxed['amount_curr'] * (-1))
        self.assertEqual(move.amount_tax_signed, move_amount_taxed['amount'] * (-1))
        self.assertEqual(move.amount_total, move_amount_total['amount_curr'] * (-1))
        self.assertEqual(move.amount_total_signed, move_amount_total['amount'] * (-1))
        self.assertEqual(move.amount_residual, move_amount_residual['amount_curr'])
        self.assertEqual(move.amount_residual_signed, move_amount_residual['amount'])
