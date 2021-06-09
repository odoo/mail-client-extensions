# -*- coding: utf-8 -*-
from odoo import fields

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("13.1")
class TestBankStatementLine(UpgradeCase):
    def _update_lines(self, currency2, statement):
        query = """UPDATE account_bank_statement_line
                      SET currency_id = %s
                    WHERE name ilike %s
                      AND statement_id = %s"""
        self.env.cr.execute(query, [None, "line_3", statement.id])
        self.env.cr.execute(query, [currency2.id, "line_4", statement.id])

        query1 = """UPDATE account_bank_statement_line
                      SET amount_currency = NULL
                    WHERE name ilike %s
                      AND statement_id = %s"""
        self.env.cr.execute(query1, ["line_2", statement.id])

    def prepare(self):
        res_users_account_manager = self.env.ref("account.group_account_manager")
        partner_manager = self.env.ref("base.group_partner_manager")
        currency = self.env.ref("base.USD")
        currency2 = self.env.ref("base.INR")
        company = self.env["res.company"].create({"name": "company for upgrade tests", "currency_id": currency.id})
        chart_template = self.env.ref("l10n_generic_coa.configurable_chart_template", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading(company=company)
        account_user = (
            self.env["res.users"]
            .with_context({"no_reset_password": True})
            .create(
                {
                    "name": "Accountant for upgrade tests",
                    "company_id": company.id,
                    "company_ids": [(4, company.id)],
                    "login": "acc",
                    "email": "accountuser@yourcompany.com",
                    "groups_id": [(6, 0, [res_users_account_manager.id, partner_manager.id])],
                }
            )
        )
        self_sudo = account_user.with_user(account_user).sudo()
        journal = self_sudo.env["account.journal"].create(
            {"name": "Bank tests upgrade", "type": "bank", "code": "Bank1", "currency_id": currency2.id}
        )
        statement_lines = [
            # Amount_currency is 0.0 and related currency_id are exist :
            (
                0,
                0,
                {
                    "date": fields.Date.from_string("2021-01-01"),
                    "name": "line_1",
                    "currency_id": currency.id,
                    "amount": 1250.0,
                    "amount_currency": 0.0,
                },
            ),
            # Amount_currency is null and related currency_id are exist :
            (
                0,
                0,
                {
                    "date": fields.Date.from_string("2021-01-01"),
                    "name": "line_2",
                    "currency_id": currency.id,
                    "amount": 1000.0,
                    "amount_currency": False,
                },
            ),
            # You can't provide an amount in amount_currency without specifying a currency_id :
            (
                0,
                0,
                {
                    "date": fields.Date.from_string("2021-01-01"),
                    "name": "line_3",
                    "currency_id": currency.id,
                    "amount": 1000,
                    "amount_currency": 2000,
                },
            ),
            # The currency_id must be different than the journal currency_id :
            (
                0,
                0,
                {
                    "date": fields.Date.from_string("2021-01-01"),
                    "name": "line_4",
                    "currency_id": currency.id,
                    "amount": 2400,
                    "amount_currency": 2400,
                },
            ),
        ]

        statement = self_sudo.env["account.bank.statement"].create(
            {
                "name": "Test Bank Statements",
                "company_id": company.id,
                "currency_id": currency.id,
                "date": fields.Date.from_string("2021-01-01"),
                "journal_id": journal.id,
                "balance_end_real": 7650.0,
                "line_ids": statement_lines,
            }
        )
        self._update_lines(currency2, statement)

        return {"test_statement": statement.id}

    def check(self, init):
        expected_statement_lines = [
            {
                "date": fields.Date.from_string("2021-01-01"),
                "payment_ref": "line_1",
                "foreign_currency_id": False,
                "amount": 1250.0,
                "amount_currency": 0.0,
            },
            {
                "date": fields.Date.from_string("2021-01-01"),
                "payment_ref": "line_2",
                "foreign_currency_id": False,
                "amount": 1000.0,
                "amount_currency": 0.0,
            },
            {
                "date": fields.Date.from_string("2021-01-01"),
                "payment_ref": "line_3",
                "foreign_currency_id": False,
                "amount": 1000,
                "amount_currency": 0.0,
            },
            {
                "date": fields.Date.from_string("2021-01-01"),
                "payment_ref": "line_4",
                "foreign_currency_id": False,
                "amount": 2400,
                "amount_currency": 0.0,
            },
        ]

        stment_lines = []
        bank_statement_lines = (
            self.env["account.bank.statement"]
            .browse(init["test_statement"])
            .line_ids.sorted(lambda line: line.payment_ref)
            .read(["date", "payment_ref", "foreign_currency_id", "amount", "amount_currency"])
        )
        for line in bank_statement_lines:
            line.pop("id")
            stment_lines.append(line)

        self.assertEqual(stment_lines, expected_statement_lines)
