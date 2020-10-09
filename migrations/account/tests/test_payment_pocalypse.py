# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("13.4")
class TestPaymentPocalypse(UpgradeCase):
    def _prepare_test_1_payment_without_move_lines(self):
        """Test the migration of an account.payment that is no longer linked to any account.move.line.

        :return: The newly created account.payment's id.
        """
        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal.id,
                "payment_method_id": self.pay_method_manual_in.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "payment_date": fields.Date.from_string("2017-01-01"),
                "amount": 100.0,
                "currency_id": self.company.currency_id.id,
                "partner_id": self.partner.id,
            }
        )
        payment.post()

        payment.move_line_ids.write({"payment_id": False})
        return payment.id

    def _check_test_1_payment_without_move_lines(self, config, payment):
        """ Check result of '_prepare_test_1_payment_without_move_lines'. """
        self.assertRecordValues(
            payment,
            [
                {
                    "payment_method_id": config["pay_method_manual_in_id"],
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "amount": 100.0,
                    "currency_id": config["currency_id"],
                    "partner_id": config["partner_id"],
                }
            ],
        )
        self.assertRecordValues(
            payment.move_id,
            [
                {
                    "journal_id": config["bank_journal_id"],
                    "date": fields.Date.from_string("2017-01-01"),
                    "currency_id": config["currency_id"],
                    "partner_id": config["partner_id"],
                }
            ],
        )
        self.assertRecordValues(
            payment.move_id.line_ids.sorted("account_id"),
            [
                {"account_id": config["account_receivable_id"], "debit": 0.0, "credit": 100.0},
                {"account_id": config["payment_credit_account_id"], "debit": 100.0, "credit": 0.0},
            ],
        )

    def prepare(self):
        test_name = "TestPaymentPocalypse"

        self.company = self.env["res.company"].create({"name": "company for %s" % test_name})

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
            self.skipTest(self, "Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading_for_current_company()

        # Setup accounts.
        self.account_receivable = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id.type", "=", "receivable")], limit=1
        )
        self.account_payable = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id.type", "=", "payable")], limit=1
        )

        # Setup journals.
        self.bank_journal = self.env["account.journal"].search(
            [("company_id", "=", self.company.id), ("type", "=", "bank")], limit=1
        )

        # Setup partner.
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner %s" % test_name,
                "property_account_receivable_id": self.account_receivable.id,
                "property_account_payable_id": self.account_payable.id,
                "company_id": self.company.id,
            }
        )

        # Setup payment methods.
        self.pay_method_manual_in = self.env.ref("account.account_payment_method_manual_in")
        self.pay_method_manual_out = self.env.ref("account.account_payment_method_manual_out")

        return {
            "tests": [
                self._prepare_test_1_payment_without_move_lines(),
            ],
            "config": {
                "currency_id": self.company.currency_id.id,
                "partner_id": self.partner.id,
                "bank_journal_id": self.bank_journal.id,
                "bank_debit_account_id": self.bank_journal.default_debit_account_id.id,
                "bank_credit_account_id": self.bank_journal.default_credit_account_id.id,
                "account_receivable_id": self.account_receivable.id,
                "account_payable_id": self.account_payable.id,
                "pay_method_manual_in_id": self.pay_method_manual_in.id,
                "pay_method_manual_out_id": self.pay_method_manual_out.id,
            },
        }

    def check(self, init):
        payments = self.env["account.payment"].browse(init["tests"])
        config = init["config"]
        bank_journal = self.env["account.journal"].browse(config["bank_journal_id"])
        config.update(
            {
                "payment_debit_account_id": bank_journal.payment_debit_account_id.id,
                "payment_credit_account_id": bank_journal.payment_credit_account_id.id,
            }
        )

        self._check_test_1_payment_without_move_lines(config, payments[0])
