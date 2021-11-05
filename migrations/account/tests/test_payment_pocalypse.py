# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~13.4")
class TestPaymentPocalypse(UpgradeCase):

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def get_bank_accounts(self, journal):
        if util.version_gte("saas~13.5"):
            return journal.default_account_id
        else:
            return journal.default_debit_account_id + journal.default_credit_account_id

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_1_payment_without_move_lines(self):
        """Test the migration of an account.payment that is no longer linked to any account.move.line."""
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
        return [payment.id]

    def _check_test_1_payment_without_move_lines(self, config, payment_id):
        """Check result of '_prepare_test_1_payment_without_move_lines'."""
        payment = self.env["account.payment"].browse(payment_id)
        journal = self.env["account.journal"].browse(config["bank_journal_id"])
        currency = journal.company_id.currency_id
        self.assertRecordValues(
            payment,
            [
                {
                    "payment_method_id": config["pay_method_manual_in_id"],
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "amount": 100.0,
                    "currency_id": currency.id,
                    "partner_id": config["partner_id"],
                }
            ],
        )
        self.assertRecordValues(
            payment.move_id,
            [
                {
                    "journal_id": journal.id,
                    "date": fields.Date.from_string("2017-01-01"),
                    "currency_id": currency.id,
                    "partner_id": config["partner_id"],
                }
            ],
        )
        self.assertRecordValues(
            payment.move_id.line_ids.sorted("account_id"),
            [
                {"account_id": config["account_receivable_id"], "debit": 0.0, "credit": 100.0},
                {"account_id": journal.default_account_id.id, "debit": 100.0, "credit": 0.0},
            ],
        )

    def _prepare_test_2_payment_draft_wrong_partner_company_deprecated_account(self):
        """Test the migration of an account.payment on which there is:
        - unconsistent company set on partner
        - deprecated account
        """
        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal_deprecated_account.id,
                "payment_method_id": self.pay_method_manual_in.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "payment_date": fields.Date.from_string("2017-01-01"),
                "amount": 100.0,
                "currency_id": self.company.currency_id.id,
                "partner_id": self.partner_another_company.id,
            }
        )
        return [payment.id]

    def _check_test_2_payment_draft_wrong_partner_company_deprecated_account(self, config, payment_id):
        """Check result of '_prepare_test_2_payment_draft_wrong_partner_company_deprecated_account'."""
        payment = self.env["account.payment"].browse(payment_id)
        journal = self.env["account.journal"].browse(config["bank_journal_deprecated_account_id"])
        partner_another_company = self.env["res.partner"].browse(config["partner_another_company_id"])
        self.assertRecordValues(
            payment,
            [
                {
                    "journal_id": journal.id,
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "date": fields.Date.from_string("2017-01-01"),
                    "amount": 100.0,
                    "currency_id": journal.company_id.currency_id.id,
                    "partner_id": partner_another_company.id,
                    "company_id": journal.company_id.id,
                }
            ],
        )
        self.assertRecordValues(
            payment.move_id.line_ids.sorted("account_id"),
            [
                {"account_id": journal.payment_debit_account_id.id, "debit": 100.0, "credit": 0.0},
                {"account_id": config["account_receivable_id"], "debit": 0.0, "credit": 100.0},
            ],
        )
        self.assertRecordValues(partner_another_company, [{"company_id": config["company_2_id"]}])

    def _prepare_test_3_statement_line_reconciled_to_internal_transfer(self):
        """Test the reconciliation of a statement line with a payment generated with internal_transfer."""
        if util.version_gte("saas~13.3"):
            payments = self.env["account.payment"].create(
                [
                    {
                        "journal_id": self.bank_journal.id,
                        "payment_method_id": self.pay_method_manual_out.id,
                        "payment_type": "outbound",
                        "payment_date": fields.Date.from_string("2017-01-01"),
                        "amount": 100.0,
                        "currency_id": self.company.currency_id.id,
                        "partner_id": self.company.partner_id.id,
                    },
                    {
                        "journal_id": self.bank_journal_2.id,
                        "payment_method_id": self.pay_method_manual_out.id,
                        "payment_type": "inbound",
                        "payment_date": fields.Date.from_string("2017-01-01"),
                        "amount": 100.0,
                        "currency_id": self.company.currency_id.id,
                        "partner_id": self.company.partner_id.id,
                    },
                ]
            )
        else:
            payments = self.env["account.payment"].create(
                {
                    "journal_id": self.bank_journal.id,
                    "destination_journal_id": self.bank_journal_2.id,
                    "payment_method_id": self.pay_method_manual_out.id,
                    "payment_type": "transfer",
                    "payment_date": fields.Date.from_string("2017-01-01"),
                    "amount": 100.0,
                    "currency_id": self.company.currency_id.id,
                }
            )
        payments.post()

        bank_statement = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal_2.id,
                "balance_end_real": 100.0,
                "date": fields.Date.from_string("2017-01-01"),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "amount": 100.0,
                            "date": fields.Date.from_string("2017-01-01"),
                        },
                    )
                ],
            }
        )
        bank_statement_line = bank_statement.line_ids

        bank_accounts = self.get_bank_accounts(self.bank_journal_2)
        counterpart_line = payments.move_line_ids.filtered(lambda line: line.account_id in bank_accounts)
        bank_statement_line.process_reconciliation(payment_aml_rec=counterpart_line)

        bank_statement.check_confirm_bank()

        return [payments.ids, bank_statement_line.id]

    def _check_test_3_statement_line_reconciled_to_internal_transfer(self, config, payment_ids, statement_line_id):
        """Check result of '_prepare_test_3_statement_line_reconciled_to_internal_transfer'."""
        payments = self.env["account.payment"].browse(payment_ids)
        payment_1 = payments[0]
        payment_2 = payments[1] if len(payments) > 1 else self.env["account.payment"]
        bank_statement_line = self.env["account.bank.statement.line"].browse(statement_line_id)
        company = payment_1.company_id
        st_bank_accounts = self.get_bank_accounts(bank_statement_line.journal_id)

        self.assertRecordValues(
            payment_1.move_id,
            [
                {
                    "payment_id": payment_1.id,
                    "statement_line_id": False,
                    "journal_id": config["bank_journal_id"],
                }
            ],
        )
        self.assertRecordValues(
            payment_1.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {"account_id": company.transfer_account_id.id, "debit": 100.0, "credit": 0.0},
                {"account_id": payment_1.journal_id.default_account_id.id, "debit": 0.0, "credit": 100.0},
            ],
        )

        self.assertRecordValues(
            bank_statement_line.move_id,
            [
                {
                    "payment_id": payment_2.id,
                    "statement_line_id": bank_statement_line.id,
                    "journal_id": config["bank_journal_2_id"],
                }
            ],
        )
        self.assertRecordValues(
            bank_statement_line.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {"account_id": company.transfer_account_id.id, "debit": 0.0, "credit": 100.0},
                {"account_id": st_bank_accounts[0].id, "debit": 100.0, "credit": 0.0},
            ],
        )

    def _prepare_test_4_statement_line_payment_shared_move(self):
        """Test the migration of a statement line when the journal entry is shared between the payment and the
        statement line.
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

        bank_statement = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": fields.Date.from_string("2017-01-01"),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 100.0,
                            "date": fields.Date.from_string("2017-01-01"),
                        },
                    )
                ],
            }
        )
        bank_statement_line = bank_statement.line_ids

        bank_accounts = self.get_bank_accounts(self.bank_journal)
        counterpart_line = payment.move_line_ids.filtered(lambda line: line.account_id in bank_accounts)
        bank_statement_line.process_reconciliation(payment_aml_rec=counterpart_line)

        return [payment.id, bank_statement_line.id]

    def _check_test_4_statement_line_payment_shared_move(self, config, payment_id, statement_line_id):
        """Check result of '_prepare_test_4_statement_line_payment_shared_move'."""
        payment = self.env["account.payment"].browse(payment_id)
        bank_statement_line = self.env["account.bank.statement.line"].browse(statement_line_id)
        bank_accounts = self.get_bank_accounts(bank_statement_line.journal_id)

        self.assertRecordValues(
            payment.move_id,
            [
                {
                    "payment_id": payment.id,
                    "statement_line_id": bank_statement_line.id,
                }
            ],
        )
        self.assertEqual(payment.move_id, bank_statement_line.move_id)

        self.assertRecordValues(
            payment.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {"account_id": config["account_receivable_id"], "debit": 0.0, "credit": 100.0},
                {"account_id": bank_accounts[0].id, "debit": 100.0, "credit": 0.0},
            ],
        )

    def _prepare_test_5_post_at_bank_rec_reconciled_payment(self):
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
                            "price_unit": 1.0,
                            "account_id": self.account_income.id,
                        },
                    )
                ],
            }
        )
        invoice.post()

        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal_3_post_at_bank_rec.id,
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

        (invoice.line_ids + payment.move_line_ids).filtered(
            lambda line: line.account_id.internal_type == "receivable"
        ).reconcile()

        self.assertRecordValues(payment, [{"state": "posted"}])
        self.assertRecordValues(payment.move_line_ids.move_id, [{"state": "draft"}])

        return [payment.id]

    def _check_test_5_post_at_bank_rec_reconciled_payment(self, config, payment_id):
        """Check result of '_prepare_test_5_post_at_bank_rec_payment'."""
        payment = self.env["account.payment"].browse(payment_id)
        self.assertRecordValues(payment.move_id, [{"state": "posted"}])

    def _prepare_test_6_post_at_bank_rec_not_reconciled_payment(self):
        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal_3_post_at_bank_rec.id,
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

        self.assertRecordValues(payment, [{"state": "posted"}])
        self.assertRecordValues(payment.move_line_ids.move_id, [{"state": "draft"}])

        return [payment.id]

    def _check_test_6_post_at_bank_rec_not_reconciled_payment(self, config, payment_id):
        """Check result of '_prepare_test_5_post_at_bank_rec_payment'."""
        payment = self.env["account.payment"].browse(payment_id)
        self.assertRecordValues(payment.move_id, [{"state": "posted"}])

    def _prepare_test_7_manual_internal_transfer_using_statement_lines(self):
        bank_accounts_1 = self.get_bank_accounts(self.bank_journal)
        bank_accounts_2 = self.get_bank_accounts(self.bank_journal_2)

        bank_statement_debit = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": fields.Date.from_string("2017-01-01"),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": -100.0,
                            "date": fields.Date.from_string("2017-01-01"),
                        },
                    )
                ],
            }
        )
        bank_statement_line_debit = bank_statement_debit.line_ids

        bank_statement_line_debit.process_reconciliation(
            new_aml_dicts=[
                {
                    "name": "test",
                    "debit": 100.0,
                    "credit": 0.0,
                    "account_id": self.company.transfer_account_id.id,
                }
            ]
        )
        payment_debit = bank_statement_debit.move_line_ids.payment_id

        bank_statement_credit = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal_2.id,
                "date": fields.Date.from_string("2017-01-01"),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 100.0,
                            "date": fields.Date.from_string("2017-01-01"),
                        },
                    )
                ],
            }
        )
        bank_statement_line_credit = bank_statement_credit.line_ids

        counterpart_line = bank_statement_debit.move_line_ids.filtered(
            lambda line: line.account_id == self.company.transfer_account_id
        )
        bank_statement_line_credit.process_reconciliation(
            counterpart_aml_dicts=[
                {
                    "move_line": counterpart_line,
                    "debit": 0.0,
                    "credit": 100.0,
                }
            ]
        )
        payment_credit = bank_statement_credit.move_line_ids.payment_id

        self.assertRecordValues(
            bank_statement_debit.move_line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {
                    "account_id": self.company.transfer_account_id.id,
                    "debit": 100.0,
                    "credit": 0.0,
                    "payment_id": payment_debit.id,
                    "statement_line_id": bank_statement_line_debit.id,
                },
                {
                    "account_id": bank_accounts_1[0].id,
                    "debit": 0.0,
                    "credit": 100.0,
                    "payment_id": payment_debit.id,
                    "statement_line_id": bank_statement_line_debit.id,
                },
            ],
        )
        self.assertRecordValues(
            bank_statement_credit.move_line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {
                    "account_id": self.company.transfer_account_id.id,
                    "debit": 0.0,
                    "credit": 100.0,
                    "payment_id": payment_credit.id,
                    "statement_line_id": bank_statement_line_credit.id,
                },
                {
                    "account_id": bank_accounts_2[0].id,
                    "debit": 100.0,
                    "credit": 0.0,
                    "payment_id": payment_credit.id,
                    "statement_line_id": bank_statement_line_credit.id,
                },
            ],
        )

        return [bank_statement_line_debit.id, payment_debit.id, bank_statement_line_credit.id, payment_credit.id]

    def _check_test_7_manual_internal_transfer_using_statement_lines(
        self, config, st_debit_line_id, pay_debit_id, st_credit_line_id, pay_credit_id
    ):
        """Check result of '_prepare_test_7_manual_internal_transfer_using_statement_lines'."""
        bank_journal = self.env["account.journal"].browse(config["bank_journal_id"])
        bank_journal_2 = self.env["account.journal"].browse(config["bank_journal_2_id"])
        bank_accounts_1 = self.get_bank_accounts(bank_journal)
        bank_accounts_2 = self.get_bank_accounts(bank_journal_2)
        company = bank_journal.company_id

        bank_statement_line_debit = self.env["account.bank.statement.line"].browse(st_debit_line_id)
        payment_debit = self.env["account.payment"].browse(pay_debit_id)
        bank_statement_line_credit = self.env["account.bank.statement.line"].browse(st_credit_line_id)
        payment_credit = self.env["account.payment"].browse(pay_credit_id)

        self.assertRecordValues(
            bank_statement_line_debit.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {
                    "account_id": company.transfer_account_id.id,
                    "debit": 100.0,
                    "credit": 0.0,
                    "payment_id": payment_debit.id,
                    "statement_line_id": bank_statement_line_debit.id,
                },
                {
                    "account_id": bank_accounts_1[0].id,
                    "debit": 0.0,
                    "credit": 100.0,
                    "payment_id": payment_debit.id,
                    "statement_line_id": bank_statement_line_debit.id,
                },
            ],
        )
        self.assertRecordValues(
            bank_statement_line_credit.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {
                    "account_id": company.transfer_account_id.id,
                    "debit": 0.0,
                    "credit": 100.0,
                    "payment_id": payment_credit.id,
                    "statement_line_id": bank_statement_line_credit.id,
                },
                {
                    "account_id": bank_accounts_2[0].id,
                    "debit": 100.0,
                    "credit": 0.0,
                    "payment_id": payment_credit.id,
                    "statement_line_id": bank_statement_line_credit.id,
                },
            ],
        )

    def _prepare_test_8_manual_internal_transfer_using_statement_lines_no_f08204_fix(self):
        """Same as _prepare_test_7_manual_internal_transfer_using_statement_lines but without the following fix:
        https://github.com/odoo/odoo/commit/f08204c69c684a6614bbbebc834178355b4aad03

        In that case, one journal entry is shared between two statement lines.
        """
        bank_statement_debit = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": fields.Date.from_string("2017-01-01"),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": -100.0,
                            "date": fields.Date.from_string("2017-01-01"),
                        },
                    )
                ],
            }
        )
        bank_statement_line_debit = bank_statement_debit.line_ids

        bank_statement_line_debit.process_reconciliation(
            new_aml_dicts=[
                {
                    "name": "test",
                    "debit": 100.0,
                    "credit": 0.0,
                    "account_id": self.company.transfer_account_id.id,
                }
            ]
        )
        payment_debit = bank_statement_debit.move_line_ids.payment_id

        bank_statement_credit = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal_2.id,
                "date": fields.Date.from_string("2017-01-01"),
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 100.0,
                            "date": fields.Date.from_string("2017-01-01"),
                        },
                    )
                ],
            }
        )
        bank_statement_line_credit = bank_statement_credit.line_ids

        counterpart_line = bank_statement_debit.move_line_ids.filtered(
            lambda line: line.account_id == self.company.transfer_account_id
        )
        bank_statement_line_credit.process_reconciliation(
            counterpart_aml_dicts=[
                {
                    "move_line": counterpart_line,
                    "debit": 0.0,
                    "credit": 100.0,
                }
            ]
        )
        payment_credit = bank_statement_credit.move_line_ids.payment_id

        # Reproduce the bug before the fix.
        wrong_move_line = bank_statement_debit.move_line_ids.filtered(
            lambda line: line.account_id == self.company.transfer_account_id
        )
        wrong_move_line.statement_line_id = bank_statement_line_credit

        return [bank_statement_line_debit.id, payment_debit.id, bank_statement_line_credit.id, payment_credit.id]

    def _check_test_8_manual_internal_transfer_using_statement_lines_no_f08204_fix(
        self, config, st_debit_line_id, pay_debit_id, st_credit_line_id, pay_credit_id
    ):
        """Check result of '_prepare_test_8_manual_internal_transfer_using_statement_lines_no_f08204_fix'."""
        bank_journal = self.env["account.journal"].browse(config["bank_journal_id"])
        bank_journal_2 = self.env["account.journal"].browse(config["bank_journal_2_id"])
        bank_accounts_1 = self.get_bank_accounts(bank_journal)
        bank_accounts_2 = self.get_bank_accounts(bank_journal_2)
        company = bank_journal.company_id

        bank_statement_line_debit = self.env["account.bank.statement.line"].browse(st_debit_line_id)
        payment_debit = self.env["account.payment"].browse(pay_debit_id)
        bank_statement_line_credit = self.env["account.bank.statement.line"].browse(st_credit_line_id)
        payment_credit = self.env["account.payment"].browse(pay_credit_id)

        self.assertRecordValues(
            bank_statement_line_debit.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {
                    "account_id": company.transfer_account_id.id,
                    "debit": 100.0,
                    "credit": 0.0,
                    "payment_id": payment_debit.id,
                    "statement_line_id": bank_statement_line_debit.id,
                },
                {
                    "account_id": bank_accounts_1[0].id,
                    "debit": 0.0,
                    "credit": 100.0,
                    "payment_id": payment_debit.id,
                    "statement_line_id": bank_statement_line_debit.id,
                },
            ],
        )
        self.assertRecordValues(
            bank_statement_line_credit.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {
                    "account_id": company.transfer_account_id.id,
                    "debit": 0.0,
                    "credit": 100.0,
                    "payment_id": payment_credit.id,
                    "statement_line_id": bank_statement_line_credit.id,
                },
                {
                    "account_id": bank_accounts_2[0].id,
                    "debit": 100.0,
                    "credit": 0.0,
                    "payment_id": payment_credit.id,
                    "statement_line_id": bank_statement_line_credit.id,
                },
            ],
        )

    def _prepare_test_9_manual_payment_journal_entry_deletion(self):
        """Nothing was preventing to delete a journal entry linked to a posted payment."""
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

        move = payment.move_line_ids.move_id
        self.cr.execute("DELETE FROM account_move WHERE id = %s", [move.id])
        return [payment.id]

    def _check_test_9_manual_payment_journal_entry_deletion(self, config, payment_id):
        """Check result of '_prepare_test_9_manual_payment_journal_entry_deletion'."""
        payment = self.env["account.payment"].browse(payment_id)
        self.assertFalse(payment.exists())

    def _prepare_test_10_unconsistent_journal_on_payment_journal_entry(self):
        """Check the case when the journal entry and the payment are not sharing the same journal."""
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

        move = payment.move_line_ids.move_id
        self.cr.execute(
            "UPDATE account_move SET name = %s, journal_id = %s WHERE id = %s",
            ["TURLUTUTU2017/01", self.bank_journal_2.id, move.id],
        )
        return [payment.id, move.id]

    def _check_test_10_unconsistent_journal_on_payment_journal_entry(self, config, payment_id, move_id):
        """Check result of '_prepare_test_10_unconsistent_journal_on_payment_journal_entry'."""
        payment = self.env["account.payment"].browse(payment_id)
        self.assertRecordValues(
            payment,
            [
                {
                    "journal_id": config["bank_journal_2_id"],
                    "move_id": move_id,
                }
            ],
        )

    def _prepare_test_11_reconciled_liquidity_line_payment(self):
        """Ensure the liquidity account are not replaced if reconciled."""
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
        payment.move_line_ids.move_id._reverse_moves(default_values_list=[{"date": "2017-01-01"}], cancel=True)
        return [payment.id]

    def _check_test_11_reconciled_liquidity_line_payment(self, config, payment_id):
        """Check result of '_prepare_test_11_reconciled_liquidity_line_payment'."""
        payment = self.env["account.payment"].browse(payment_id)
        bank_journal = self.env["account.journal"].browse(config["bank_journal_id"])
        bank_accounts = self.get_bank_accounts(bank_journal)

        lines = payment.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance))
        self.assertRecordValues(
            lines,
            [
                {"account_id": config["account_receivable_id"]},
                {"account_id": bank_accounts[0].id},
            ],
        )
        self.assertTrue(len(lines.full_reconcile_id), 2)

    def _prepare_test_12_account_type(self):
        account_bancontact = self.env["account.account"].create(
            {
                "name": "bancontact",
                "code": "580070",
                "user_type_id": self.env.ref("account.data_account_type_current_assets").id,
                "deprecated": True,
            }
        )
        account_bank = self.env["account.account"].create(
            {
                "name": "bank",
                "code": "550100",
                "user_type_id": self.env.ref("account.data_account_type_liquidity").id,
                "deprecated": True,
            }
        )
        journal_bancontact = self.env["account.journal"].create(
            {
                "name": "bancontact",
                "code": "bnkctc",
                "type": "bank",
                "default_debit_account_id": account_bancontact.id,
                "active": False,
            }
        )
        journal_bank = self.env["account.journal"].create(
            {
                "name": "bank",
                "code": "bank",
                "type": "bank",
                "default_debit_account_id": account_bank.id,
                "active": False,
            }
        )
        return {
            "account_bank": account_bank.id,
            "account_bancontact": account_bancontact.id,
            "journal_bancontact": journal_bancontact.id,
            "journal_bank": journal_bank.id,
        }

    def _check_test_12_account_type(self, config, res):
        journal_bank = self.env["account.journal"].browse(res["journal_bank"])
        journal_bancontact = self.env["account.journal"].browse(res["journal_bancontact"])
        self.assertTrue(journal_bank.payment_credit_account_id)
        self.assertTrue(journal_bancontact.payment_credit_account_id)
        self.assertEqual(journal_bancontact.payment_credit_account_id.id, res["account_bancontact"])
        self.assertNotEqual(journal_bank.payment_credit_account_id.id, res["account_bank"])

    def _prepare_test_13_statement_line_black_and_blue_lines_reconciliation(self):
        """Test the migration of a statement line reconciled with a lot of things."""
        bank_accounts = self.get_bank_accounts(self.bank_journal)
        payments = self.env["account.payment"].create(
            [
                {
                    "journal_id": self.bank_journal.id,
                    "payment_method_id": self.pay_method_manual_in.id,
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "payment_date": "2017-01-01",
                    "amount": amount,
                    "currency_id": self.company.currency_id.id,
                    "partner_id": self.partner.id,
                }
                for amount in (100.0, 200.0, 300.0)
            ]
        )
        payments.post()
        blue_lines = payments.move_line_ids.filtered(lambda line: line.account_id in bank_accounts)

        move = self.env["account.move"].create(
            {
                "journal_id": self.sale_journal.id,
                "date": "2017-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "black_line",
                            "account_id": self.account_receivable.id,
                            "debit": 400.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "black_line",
                            "account_id": self.account_receivable.id,
                            "debit": 500.0,
                            "credit": 0.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "credit_line",
                            "account_id": self.account_income.id,
                            "debit": 0.0,
                            "credit": 900.0,
                        },
                    ),
                ],
            }
        )
        move.action_post()
        black_lines = move.line_ids.filtered("debit")

        bank_statement = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": "2017-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 1500.0,
                            "date": "2017-01-01",
                        },
                    )
                ],
            }
        )
        bank_statement_line = bank_statement.line_ids

        counterpart_aml_dicts = [
            {"move_line": counterpart_line, "debit": 0.0, "credit": counterpart_line.debit}
            for counterpart_line in black_lines
        ]
        bank_statement_line.process_reconciliation(
            payment_aml_rec=blue_lines,
            counterpart_aml_dicts=counterpart_aml_dicts,
        )

        auto_generated_move = black_lines.matched_credit_ids.credit_move_id.move_id
        linked_moves = blue_lines.move_id + auto_generated_move
        self.assertEqual(bank_statement_line.journal_entry_ids.move_id.sorted(), linked_moves.sorted())

        return [bank_statement_line.id, auto_generated_move.id]

    def _check_test_13_statement_line_black_and_blue_lines_reconciliation(
        self, config, bank_statement_line_id, move_id
    ):
        """Check result of '_prepare_test_13_statement_line_black_and_blue_lines_reconciliation'."""
        st_line = self.env["account.bank.statement.line"].browse(bank_statement_line_id)
        self.assertRecordValues(st_line, [{"move_id": move_id}])

    def _prepare_test_14_statement_line_blue_lines_reconciliation(self):
        """Test the migration of a statement line reconciled with multiple payments."""
        bank_accounts = self.get_bank_accounts(self.bank_journal)
        payments = self.env["account.payment"].create(
            [
                {
                    "journal_id": self.bank_journal.id,
                    "payment_method_id": self.pay_method_manual_in.id,
                    "payment_type": "inbound",
                    "partner_type": "customer",
                    "payment_date": "2017-01-01",
                    "amount": amount,
                    "currency_id": self.company.currency_id.id,
                    "partner_id": self.partner.id,
                }
                for amount in (100.0, 200.0, 300.0)
            ]
        )
        payments.post()
        blue_lines = payments.move_line_ids.filtered(lambda line: line.account_id in bank_accounts)

        bank_statement = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": "2017-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 1500.0,
                            "date": "2017-01-01",
                        },
                    )
                ],
            }
        )
        bank_statement_line = bank_statement.line_ids
        bank_statement_line.process_reconciliation(payment_aml_rec=blue_lines)

        self.assertEqual(bank_statement_line.journal_entry_ids.move_id.sorted(), blue_lines.move_id.sorted())

        return [bank_statement_line.id, blue_lines.move_id.ids, payments.ids]

    def _check_test_14_statement_line_blue_lines_reconciliation(
        self, config, bank_statement_line_id, move_ids, payment_ids
    ):
        """Check result of '_prepare_test_14_statement_line_blue_lines_reconciliation'."""
        bank_journal = self.env["account.journal"].browse(config["bank_journal_id"])
        st_line = self.env["account.bank.statement.line"].browse(bank_statement_line_id)
        payments = self.env["account.payment"].browse(payment_ids)
        outstanding_lines = payments.move_id.line_ids.filtered(
            lambda line: line.account_id == bank_journal.payment_debit_account_id
        )

        self.assertRecordValues(st_line, [{"move_id": max(move_ids)}])
        self.assertFalse(outstanding_lines)
        self.assertTrue(min(payments.mapped("is_matched")))

    def _prepare_test_15_draft_statement_line_locked_period(self):
        """Test the migration of a draft statement line that is inside a locked period but owned by a validated
        statement.
        """
        bank_accounts = self.get_bank_accounts(self.bank_journal_comp2)
        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal_comp2.id,
                "payment_method_id": self.pay_method_manual_in.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "payment_date": "2017-01-01",
                "amount": 200.0,
                "currency_id": self.company_2.currency_id.id,
                "partner_id": self.partner_another_company.id,
            }
        )
        payment.post()
        blue_lines = payment.move_line_ids.filtered(lambda line: line.account_id in bank_accounts)

        bank_statement = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal_comp2.id,
                "date": "2017-01-01",
                "balance_end_real": 200.0,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner_another_company.id,
                            "amount": 200.0,
                            "date": "2017-01-01",
                        },
                    )
                ],
            }
        )
        bank_statement_line = bank_statement.line_ids
        bank_statement_line.process_reconciliation(payment_aml_rec=blue_lines)
        bank_statement.button_confirm_bank()

        payment.move_name = False
        payment.action_draft()
        payment.unlink()

        return [bank_statement_line.id]

    def _check_test_15_draft_statement_line_locked_period(self, config, bank_statement_line_id):
        """Check result of '_prepare_test_15_draft_statement_line_locked_period'."""
        st_line = self.env["account.bank.statement.line"].browse(bank_statement_line_id)
        self.assertRecordValues(st_line.move_id, [{"state": "cancel"}])

    def _prepare_test_16_posted_payment_locked_period(self):
        """Test the migration of a posted payment that is inside a locked period but not already matched with a
        statement line.
        """
        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal_comp2.id,
                "payment_method_id": self.pay_method_manual_in.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "payment_date": "2017-01-01",
                "amount": 200.0,
                "currency_id": self.company_2.currency_id.id,
                "partner_id": self.partner_another_company.id,
            }
        )
        payment.post()

        return [payment.id]

    def _check_test_16_posted_payment_locked_period(self, config, payment_id):
        """Check result of '_prepare_test_16_posted_payment_locked_period'."""
        payment = self.env["account.payment"].browse(payment_id)
        bank_journal = self.env["account.journal"].browse(config["bank_journal_comp2_id"])

        outstanding_lines = payment.move_id.line_ids.filtered(
            lambda line: line.account_id
            in (
                bank_journal.payment_debit_account_id,
                bank_journal.payment_credit_account_id,
            )
        )
        self.assertFalse(outstanding_lines)

    def _prepare_test_17_matched_payment_with_writeoff(self):
        """Test the migration of a statement line matched to a payment but with an additional write-off line."""
        bank_accounts = self.get_bank_accounts(self.bank_journal)
        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal.id,
                "payment_method_id": self.pay_method_manual_in.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "payment_date": "2017-01-01",
                "amount": 100.0,
                "currency_id": self.company.currency_id.id,
                "partner_id": self.partner.id,
            }
        )
        payment.post()
        blue_line = payment.move_line_ids.filtered(lambda line: line.account_id in bank_accounts)

        bank_statement = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": "2017-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 200.0,
                            "date": "2017-01-01",
                        },
                    )
                ],
            }
        )
        bank_statement_line = bank_statement.line_ids

        bank_statement_line.process_reconciliation(
            payment_aml_rec=blue_line,
            new_aml_dicts=[
                {
                    "name": "test",
                    "debit": 0.0,
                    "credit": 100.0,
                    "account_id": self.account_income.id,
                }
            ],
        )
        return [bank_statement_line.id, payment.id]

    def _check_test_17_matched_payment_with_writeoff(self, config, st_line_id, payment_id):
        """Check result of '_prepare_test_17_matched_payment_with_writeoff'."""
        st_line = self.env["account.bank.statement.line"].browse(st_line_id)
        payment = self.env["account.payment"].browse(payment_id)

        self.assertRecordValues(st_line, [{"is_reconciled": True}])
        self.assertRecordValues(payment, [{"is_reconciled": False, "is_matched": True}])

    def _prepare_test_18_invoice_state_paid_to_in_payment(self):
        """Ensure the replacement of the bank account by the oustanding one will recompute invoice state accordingly."""
        move_type_field = "move_type" if util.version_gte("saas~13.3") else "type"
        today = fields.Date.today()
        invoice = self.env["account.move"].create(
            {
                move_type_field: "out_invoice",
                "partner_id": self.partner.id,
                "invoice_date": today,
                "date": today,
                "invoice_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "line",
                            "quantity": 1.0,
                            "price_unit": 1.0,
                            "account_id": self.account_income.id,
                        },
                    )
                ],
            }
        )
        invoice.post()

        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal.id,
                "payment_method_id": self.pay_method_manual_in.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "payment_date": today,
                "amount": 100.0,
                "currency_id": self.company.currency_id.id,
                "partner_id": self.partner.id,
            }
        )
        payment.post()

        (invoice.line_ids + payment.move_line_ids).filtered(
            lambda line: line.account_id.internal_type == "receivable"
        ).reconcile()

        self.assertRecordValues(invoice, [{"invoice_payment_state": "paid"}])
        return [invoice.id]

    def _check_test_18_invoice_state_paid_to_in_payment(self, config, invoice_id):
        invoice = self.env["account.move"].browse(invoice_id)
        self.assertRecordValues(invoice, [{"payment_state": invoice._get_invoice_in_payment_state()}])

    def _prepare_test_19_invalid_statement_with_reconciled_line(self):
        """Test the case when a bank statement has an invalid balance but at least one reconciled line."""
        bank_accounts = self.get_bank_accounts(self.bank_journal)
        payment = self.env["account.payment"].create(
            {
                "journal_id": self.bank_journal.id,
                "payment_method_id": self.pay_method_manual_in.id,
                "payment_type": "inbound",
                "partner_type": "customer",
                "payment_date": "2017-01-01",
                "amount": 100.0,
                "currency_id": self.company.currency_id.id,
                "partner_id": self.partner.id,
            }
        )
        payment.post()
        blue_line = payment.move_line_ids.filtered(lambda line: line.account_id in bank_accounts)

        # Create 2 statements making the first one invalid during the migration.
        self.env["account.bank.statement"].create(
            {
                "balance_end_real": 200.0,
                "journal_id": self.bank_journal.id,
                "date": "2017-01-01",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 200.0,
                            "date": "2017-01-01",
                        },
                    )
                ],
            }
        )
        bank_statement = self.env["account.bank.statement"].create(
            {
                "balance_end_real": 800.0,
                "journal_id": self.bank_journal.id,
                "date": "2017-01-02",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 200.0,
                            "date": "2017-01-02",
                        },
                    )
                ],
            }
        )
        self.env["account.bank.statement"].create(
            {
                "balance_end_real": 600.0,
                "journal_id": self.bank_journal.id,
                "date": "2017-01-03",
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "test",
                            "partner_id": self.partner.id,
                            "amount": 200.0,
                            "date": "2017-01-03",
                        },
                    )
                ],
            }
        )
        bank_statement_line = bank_statement.line_ids

        bank_statement_line.process_reconciliation(
            payment_aml_rec=blue_line,
            new_aml_dicts=[
                {
                    "name": "test",
                    "debit": 0.0,
                    "credit": 100.0,
                    "account_id": self.account_income.id,
                }
            ],
        )
        return [bank_statement_line.id]

    def _check_test_19_invalid_statement_with_reconciled_line(self, config, st_line_id):
        st_line = self.env["account.bank.statement.line"].browse(st_line_id)

        self.assertRecordValues(
            st_line.statement_id,
            [
                {
                    "state": "open",
                    "is_valid_balance_start": False,
                }
            ],
        )
        self.assertRecordValues(st_line.move_id, [{"state": "posted"}])

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        test_name = "TestPaymentPocalypse"

        self.company = self.env["res.company"].create({"name": "company for %s" % test_name})
        self.company_2 = self.env["res.company"].create({"name": "company_2 for %s" % test_name})

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
                    "company_ids": [(6, 0, (self.company + self.company_2).ids)],
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
        chart_template.try_loading(company=self.company_2)

        # Setup accounts.
        revenue = self.env.ref("account.data_account_type_revenue").id
        self.account_income = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id", "=", revenue)], limit=1
        )
        self.account_receivable = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id.type", "=", "receivable")], limit=1
        )
        self.account_receivable_comp2 = self.env["account.account"].search(
            [
                ("company_id", "=", self.company_2.id),
                ("user_type_id.type", "=", "receivable"),
            ],
            limit=1,
        )
        self.account_payable = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id.type", "=", "payable")], limit=1
        )

        # Setup journals.
        self.bank_journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company.id),
                ("type", "=", "bank"),
            ],
            limit=1,
        )
        self.bank_journal_comp2 = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company_2.id),
                ("type", "=", "bank"),
            ],
            limit=1,
        )
        self.sale_journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company.id),
                ("type", "=", "sale"),
            ],
            limit=1,
        )
        self.bank_journal_2 = self.env["account.journal"].create(
            {
                "name": "bank_journal_2",
                "code": "TEST2",
                "type": "bank",
                "company_id": self.company.id,
            }
        )
        self.bank_journal_3_post_at_bank_rec = self.env["account.journal"].create(
            {
                "name": "bank_journal_3",
                "code": "TEST3",
                "type": "bank",
                "company_id": self.company.id,
                "post_at": "bank_rec",
            }
        )
        self.bank_journal_deprecated_account = self.env["account.journal"].create(
            {
                "name": "bank_journal_deprecated_account",
                "code": "TEST",
                "type": "bank",
                "company_id": self.company.id,
            }
        )
        self.get_bank_accounts(self.bank_journal_deprecated_account).write({"deprecated": True})

        # Setup partner.
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test partner %s" % test_name,
                "property_account_receivable_id": self.account_receivable.id,
                "property_account_payable_id": self.account_payable.id,
                "company_id": self.company.id,
            }
        )
        self.partner_another_company = self.env["res.partner"].create(
            {
                "name": "Test partner_another_company %s" % test_name,
                "property_account_receivable_id": self.account_receivable.id,
                "property_account_payable_id": self.account_payable.id,
                "company_id": self.company.id,
            }
        )
        self.partner_another_company.company_id = self.company_2

        # Setup payment methods.
        self.pay_method_manual_in = self.env.ref("account.account_payment_method_manual_in")
        self.pay_method_manual_out = self.env.ref("account.account_payment_method_manual_out")

        res = {
            "tests": [
                self._prepare_test_1_payment_without_move_lines(),
                self._prepare_test_2_payment_draft_wrong_partner_company_deprecated_account(),
                self._prepare_test_3_statement_line_reconciled_to_internal_transfer(),
                self._prepare_test_4_statement_line_payment_shared_move(),
                self._prepare_test_5_post_at_bank_rec_reconciled_payment(),
                self._prepare_test_6_post_at_bank_rec_not_reconciled_payment(),
                self._prepare_test_7_manual_internal_transfer_using_statement_lines(),
                self._prepare_test_8_manual_internal_transfer_using_statement_lines_no_f08204_fix(),
                self._prepare_test_9_manual_payment_journal_entry_deletion(),
                self._prepare_test_10_unconsistent_journal_on_payment_journal_entry(),
                self._prepare_test_11_reconciled_liquidity_line_payment(),
                self._prepare_test_12_account_type(),
                self._prepare_test_13_statement_line_black_and_blue_lines_reconciliation(),
                self._prepare_test_14_statement_line_blue_lines_reconciliation(),
                self._prepare_test_15_draft_statement_line_locked_period(),
                self._prepare_test_16_posted_payment_locked_period(),
                self._prepare_test_17_matched_payment_with_writeoff(),
                self._prepare_test_18_invoice_state_paid_to_in_payment(),
                self._prepare_test_19_invalid_statement_with_reconciled_line(),
            ],
            "config": {
                "company_id": self.company.id,
                "company_2_id": self.company_2.id,
                "partner_id": self.partner.id,
                "partner_another_company_id": self.partner_another_company.id,
                "bank_journal_id": self.bank_journal.id,
                "bank_journal_comp2_id": self.bank_journal_comp2.id,
                "sale_journal_id": self.sale_journal.id,
                "bank_journal_2_id": self.bank_journal_2.id,
                "bank_journal_3_post_at_bank_rec_id": self.bank_journal_3_post_at_bank_rec.id,
                "bank_journal_deprecated_account_id": self.bank_journal_deprecated_account.id,
                "account_receivable_id": self.account_receivable.id,
                "account_payable_id": self.account_payable.id,
                "account_receivable_comp2_2": self.account_receivable_comp2.id,
                "pay_method_manual_in_id": self.pay_method_manual_in.id,
                "pay_method_manual_out_id": self.pay_method_manual_out.id,
            },
        }

        # Lock the period.
        self.company_2.fiscalyear_lock_date = "2019-12-31"

        return res

    def check(self, init):
        config = init["config"]

        self._check_test_1_payment_without_move_lines(config, *init["tests"][0])
        self._check_test_2_payment_draft_wrong_partner_company_deprecated_account(config, *init["tests"][1])
        self._check_test_3_statement_line_reconciled_to_internal_transfer(config, *init["tests"][2])
        self._check_test_4_statement_line_payment_shared_move(config, *init["tests"][3])
        self._check_test_5_post_at_bank_rec_reconciled_payment(config, *init["tests"][4])
        self._check_test_6_post_at_bank_rec_not_reconciled_payment(config, *init["tests"][5])
        self._check_test_7_manual_internal_transfer_using_statement_lines(config, *init["tests"][6])
        self._check_test_8_manual_internal_transfer_using_statement_lines_no_f08204_fix(config, *init["tests"][7])
        self._check_test_9_manual_payment_journal_entry_deletion(config, *init["tests"][8])
        self._check_test_10_unconsistent_journal_on_payment_journal_entry(config, *init["tests"][9])
        self._check_test_11_reconciled_liquidity_line_payment(config, *init["tests"][10])
        self._check_test_12_account_type(config, init["tests"][11])
        self._check_test_13_statement_line_black_and_blue_lines_reconciliation(config, *init["tests"][12])
        self._check_test_14_statement_line_blue_lines_reconciliation(config, *init["tests"][13])
        self._check_test_15_draft_statement_line_locked_period(config, *init["tests"][14])
        self._check_test_16_posted_payment_locked_period(config, *init["tests"][15])
        self._check_test_17_matched_payment_with_writeoff(config, *init["tests"][16])
        self._check_test_18_invoice_state_paid_to_in_payment(config, init["tests"][17])
        self._check_test_19_invalid_statement_with_reconciled_line(config, init["tests"][18])
