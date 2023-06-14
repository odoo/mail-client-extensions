# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations.util import module_installed


@change_version("saas~14.3")
class TestHRExpenseSheetPaymentStatus(UpgradeCase):
    def prepare(self):
        company = self.env["res.company"].create({"name": "company for TestHRExpenseSheetPaymentStatus"})
        chart_template = self.env.ref("l10n_generic_coa.configurable_chart_template", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")
        chart_template.try_loading(company=company)
        expense_user_employee = self.env["res.users"].create(
            {
                "name": "Expense tests employee",
                "login": "Bob",
                "email": "Bob@example.com",
                "company_id": company.id,
                "company_ids": [(4, company.id)],
            }
        )
        expense_employee = self.env["hr.employee"].create(
            {
                "name": "expense_employee",
                "user_id": expense_user_employee.id,
                "address_home_id": self.env["res.partner"]
                .create({"name": "Private contact", "email": "private@email.com"})
                .id,
                "company_id": company.id,
            }
        )
        bank_journal = self.env["account.journal"].search(
            [("company_id", "=", company.id), ("type", "=", "bank")], limit=1
        )

        def get_expense_sheet(create_move=True):
            expense_sheet = (
                self.env["hr.expense.sheet"]
                .with_user(expense_user_employee)
                .create(
                    {
                        "name": "Test sheet",
                        "employee_id": expense_employee.id,
                        "expense_line_ids": [
                            (
                                0,
                                0,
                                {
                                    "name": "test expense",
                                    "unit_amount": 1000.0,
                                    "employee_id": expense_employee.id,
                                },
                            )
                        ],
                    }
                )
            )
            expense_sheet.action_submit_sheet()
            expense_sheet.approve_expense_sheets()
            if create_move:
                expense_sheet.action_sheet_move_create()
            return expense_sheet

        def get_payment(expense_sheet, amount, reconcile=False):
            ctx = {"active_model": "account.move", "active_ids": expense_sheet.account_move_id.ids}
            payment_register = (
                self.env["account.payment.register"]
                .with_context(**ctx)
                .create(
                    {
                        "amount": amount,
                        "journal_id": bank_journal.id,
                        "payment_method_id": self.env.ref("account.account_payment_method_manual_in").id,
                    }
                )
            )
            payment = payment_register._create_payments()
            if reconcile:
                statement = self.env["account.bank.statement"].create(
                    {
                        "name": "test_statement",
                        "journal_id": bank_journal.id,
                        "line_ids": [
                            (
                                0,
                                0,
                                {
                                    "payment_ref": "pay_ref",
                                    "amount": amount,
                                    "partner_id": expense_employee.address_home_id.id,
                                },
                            )
                        ],
                    }
                )
                statement.button_post()
                statement.line_ids.reconcile([{"id": payment._seek_for_lines()[0].id}])
            return payment

        sheet_ids = []

        # not paid, no move
        sheet_ids.append(get_expense_sheet(create_move=False).id)

        # not paid
        sheet_ids.append(get_expense_sheet().id)

        # partial
        sheet = get_expense_sheet()
        get_payment(sheet, 500.0)
        sheet_ids.append(sheet.id)

        # partial with 2 payments of wich one is reconiled
        sheet = get_expense_sheet()
        get_payment(sheet, 500.0)
        get_payment(sheet, 300.0, reconcile=True)
        sheet_ids.append(sheet.id)

        # in payment
        sheet = get_expense_sheet()
        get_payment(sheet, 1000.0)
        sheet_ids.append(sheet.id)

        # paid
        sheet = get_expense_sheet()
        get_payment(sheet, 1000.0, reconcile=True)
        sheet_ids.append(sheet.id)

        return {"data_ids": sheet_ids}

    def check(self, init):
        data_ids = iter(self.env["hr.expense.sheet"].browse(init["data_ids"]))
        in_payment_state = "in_payment" if module_installed(self.env.cr, "account_accountant") else "paid"
        self.assertEqual(next(data_ids).payment_state, "not_paid")
        self.assertEqual(next(data_ids).payment_state, "not_paid")
        self.assertEqual(next(data_ids).payment_state, in_payment_state)
        self.assertEqual(next(data_ids).payment_state, in_payment_state)
        self.assertEqual(next(data_ids).payment_state, in_payment_state)
        self.assertEqual(next(data_ids).payment_state, "paid")
