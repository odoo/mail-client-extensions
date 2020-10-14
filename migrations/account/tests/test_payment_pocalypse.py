# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations import util


@change_version("13.4")
class TestPaymentPocalypse(UpgradeCase):

    # -------------------------------------------------------------------------
    # HELPERS
    # -------------------------------------------------------------------------

    def get_bank_accounts(self, journal):
        if util.version_gte('saas~13.5'):
            return journal.default_account_id
        else:
            return journal.default_debit_account_id + journal.default_credit_account_id

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_1_payment_without_move_lines(self):
        ''' Test the migration of an account.payment that is no longer linked to any account.move.line. '''
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
        """ Check result of '_prepare_test_1_payment_without_move_lines'. """
        payment = self.env['account.payment'].browse(payment_id)
        journal = self.env['account.journal'].browse(config["bank_journal_id"])
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
                {"account_id": journal.payment_debit_account_id.id, "debit": 100.0, "credit": 0.0},
            ],
        )

    def _prepare_test_2_payment_draft_wrong_partner_company_deprecated_account(self):
        '''Test the migration of an account.payment on which there is:
         - unconsistent company set on partner
         - deprecated account
        '''
        payment = self.env['account.payment'].create({
            'journal_id': self.bank_journal_deprecated_account.id,
            'payment_method_id': self.pay_method_manual_in.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_date': fields.Date.from_string('2017-01-01'),
            'amount': 100.0,
            'currency_id': self.company.currency_id.id,
            'partner_id': self.partner_another_company.id,
        })
        return [payment.id]

    def _check_test_2_payment_draft_wrong_partner_company_deprecated_account(self, config, payment_id):
        ''' Check result of '_prepare_test_2_payment_draft_wrong_partner_company_deprecated_account'. '''
        payment = self.env['account.payment'].browse(payment_id)
        journal = self.env['account.journal'].browse(config['bank_journal_deprecated_account_id'])
        partner_another_company = self.env['res.partner'].browse(config['partner_another_company_id'])
        self.assertRecordValues(payment, [{
            'journal_id': journal.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'date': fields.Date.from_string('2017-01-01'),
            'amount': 100.0,
            'currency_id': journal.company_id.currency_id.id,
            'partner_id': partner_another_company.id,
            'company_id': journal.company_id.id,
        }])
        self.assertRecordValues(
            payment.move_id.line_ids.sorted('account_id'),
            [
                {'account_id': journal.payment_debit_account_id.id, 'debit': 100.0, 'credit': 0.0},
                {'account_id': config['account_receivable_id'], 'debit': 0.0, 'credit': 100.0},
            ],
        )
        self.assertRecordValues(partner_another_company, [{'company_id': config['company_2_id']}])

    def _prepare_test_3_statement_line_reconciled_to_internal_transfer(self):
        ''' Test the reconciliation of a statement line with a payment generated with internal_transfer. '''
        if util.version_gte('saas~13.3'):
            payments = self.env['account.payment'].create([
                {
                    'journal_id': self.bank_journal.id,
                    'payment_method_id': self.pay_method_manual_out.id,
                    'payment_type': 'outbound',
                    'payment_date': fields.Date.from_string('2017-01-01'),
                    'amount': 100.0,
                    'currency_id': self.company.currency_id.id,
                    'partner_id': self.company.partner_id.id,
                },
                {
                    'journal_id': self.bank_journal_2.id,
                    'payment_method_id': self.pay_method_manual_out.id,
                    'payment_type': 'inbound',
                    'payment_date': fields.Date.from_string('2017-01-01'),
                    'amount': 100.0,
                    'currency_id': self.company.currency_id.id,
                    'partner_id': self.company.partner_id.id,
                },
            ])
        else:
            payments = self.env['account.payment'].create({
                'journal_id': self.bank_journal.id,
                'destination_journal_id': self.bank_journal_2.id,
                'payment_method_id': self.pay_method_manual_out.id,
                'payment_type': 'transfer',
                'payment_date': fields.Date.from_string('2017-01-01'),
                'amount': 100.0,
                'currency_id': self.company.currency_id.id,
            })
        payments.post()

        bank_statement = self.env['account.bank.statement'].create({
            'journal_id': self.bank_journal_2.id,
            'balance_end_real': 100.0,
            'date': fields.Date.from_string('2017-01-01'),
            'line_ids': [(0, 0, {
                'name': 'test',
                'amount': 100.0,
                'date': fields.Date.from_string('2017-01-01'),
            })],
        })
        bank_statement_line = bank_statement.line_ids

        counterpart_line = payments.move_line_ids.filtered(lambda line: line.account_id in self.get_bank_accounts(self.bank_journal_2))
        bank_statement_line.process_reconciliation(payment_aml_rec=counterpart_line)

        bank_statement.check_confirm_bank()

        return [payments.ids, bank_statement_line.id]

    def _check_test_3_statement_line_reconciled_to_internal_transfer(self, config, payment_ids, statement_line_id):
        ''' Check result of '_prepare_test_3_statement_line_reconciled_to_internal_transfer'. '''
        payments = self.env['account.payment'].browse(payment_ids)
        payment_1 = payments[0]
        payment_2 = payments[1] if len(payments) > 1 else self.env['account.payment']
        bank_statement_line = self.env['account.bank.statement.line'].browse(statement_line_id)
        company = payment_1.company_id
        st_bank_accounts = self.get_bank_accounts(bank_statement_line.journal_id)

        self.assertRecordValues(payment_1.move_id, [{
            'payment_id': payment_1.id,
            'statement_line_id': False,
            'journal_id': config['bank_journal_id'],
        }])
        self.assertRecordValues(
            payment_1.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {'account_id': company.transfer_account_id.id,                      'debit': 100.0, 'credit': 0.0},
                {'account_id': payment_1.journal_id.payment_credit_account_id.id,   'debit': 0.0,   'credit': 100.0},
            ],
        )

        self.assertRecordValues(bank_statement_line.move_id, [{
            'payment_id': payment_2.id,
            'statement_line_id': bank_statement_line.id,
            'journal_id': config['bank_journal_2_id'],
        }])
        self.assertRecordValues(
            bank_statement_line.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {'account_id': company.transfer_account_id.id,                  'debit': 0.0,   'credit': 100.0},
                {'account_id': st_bank_accounts[0].id,                          'debit': 100.0, 'credit': 0.0},
            ],
        )

    def _prepare_test_4_statement_line_payment_shared_move(self):
        ''' Test the migration of a statement line when the journal entry is shared between the payment and the
        statement line.
        '''
        payment = self.env['account.payment'].create({
            'journal_id': self.bank_journal.id,
            'payment_method_id': self.pay_method_manual_in.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_date': fields.Date.from_string('2017-01-01'),
            'amount': 100.0,
            'currency_id': self.company.currency_id.id,
            'partner_id': self.partner.id,
        })
        payment.post()

        bank_statement = self.env['account.bank.statement'].create({
            'journal_id': self.bank_journal.id,
            'date': fields.Date.from_string('2017-01-01'),
            'line_ids': [(0, 0, {
                'name': 'test',
                'partner_id': self.partner.id,
                'amount': 100.0,
                'date': fields.Date.from_string('2017-01-01'),
            })],
        })
        bank_statement_line = bank_statement.line_ids

        counterpart_line = payment.move_line_ids.filtered(lambda line: line.account_id in self.get_bank_accounts(self.bank_journal))
        bank_statement_line.process_reconciliation(payment_aml_rec=counterpart_line)

        return [payment.id, bank_statement_line.id]

    def _check_test_4_statement_line_payment_shared_move(self, config, payment_id, statement_line_id):
        ''' Check result of '_prepare_test_4_statement_line_payment_shared_move'. '''
        payment = self.env['account.payment'].browse(payment_id)
        bank_statement_line = self.env['account.bank.statement.line'].browse(statement_line_id)
        bank_accounts = self.get_bank_accounts(bank_statement_line.journal_id)

        self.assertRecordValues(payment.move_id, [{
            'payment_id': payment.id,
            'statement_line_id': bank_statement_line.id,
        }])
        self.assertEqual(payment.move_id, bank_statement_line.move_id)

        self.assertRecordValues(
            payment.move_id.line_ids.sorted(lambda line: (line.account_id, line.balance)),
            [
                {'account_id': config['account_receivable_id'],     'debit': 0.0,   'credit': 100.0},
                {'account_id': bank_accounts[0].id,                 'debit': 100.0, 'credit': 0.0},
            ],
        )

    def _prepare_test_5_post_at_bank_rec_reconciled_payment(self):
        move_type_field = 'move_type' if util.version_gte('saas~13.3') else 'type'
        invoice = self.env['account.move'].create({
            move_type_field: 'out_invoice',
            'partner_id': self.partner.id,
            'invoice_date': '2016-01-01',
            'date': '2016-01-01',
            'invoice_line_ids': [(0, 0, {
                'name': 'line',
                'quantity': 1.0,
                'price_unit': 1.0,
                'account_id': self.account_income.id,
            })],
        })
        invoice.post()

        payment = self.env['account.payment'].create({
            'journal_id': self.bank_journal_3_post_at_bank_rec.id,
            'payment_method_id': self.pay_method_manual_in.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_date': fields.Date.from_string('2017-01-01'),
            'amount': 100.0,
            'currency_id': self.company.currency_id.id,
            'partner_id': self.partner.id,
        })
        payment.post()

        (invoice.line_ids + payment.move_line_ids)\
            .filtered(lambda line: line.account_id.internal_type == 'receivable')\
            .reconcile()

        self.assertRecordValues(payment, [{'state': 'posted'}])
        self.assertRecordValues(payment.move_line_ids.move_id, [{'state': 'draft'}])

        return [payment.id]

    def _check_test_5_post_at_bank_rec_reconciled_payment(self, config, payment_id):
        ''' Check result of '_prepare_test_5_post_at_bank_rec_payment'. '''
        payment = self.env['account.payment'].browse(payment_id)
        self.assertRecordValues(payment.move_id, [{'state': 'posted'}])

    def _prepare_test_6_post_at_bank_rec_not_reconciled_payment(self):
        payment = self.env['account.payment'].create({
            'journal_id': self.bank_journal_3_post_at_bank_rec.id,
            'payment_method_id': self.pay_method_manual_in.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_date': fields.Date.from_string('2017-01-01'),
            'amount': 100.0,
            'currency_id': self.company.currency_id.id,
            'partner_id': self.partner.id,
        })
        payment.post()

        self.assertRecordValues(payment, [{'state': 'posted'}])
        self.assertRecordValues(payment.move_line_ids.move_id, [{'state': 'draft'}])

        return [payment.id]

    def _check_test_6_post_at_bank_rec_not_reconciled_payment(self, config, payment_id):
        ''' Check result of '_prepare_test_5_post_at_bank_rec_payment'. '''
        payment = self.env['account.payment'].browse(payment_id)
        self.assertRecordValues(payment.move_id, [{'state': 'posted'}])

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

        chart_template.try_loading_for_current_company()

        # Setup accounts.
        self.account_income = self.env['account.account'].search(
            [('company_id', '=', self.company.id), ('user_type_id', '=', self.env.ref('account.data_account_type_revenue').id)], limit=1,
        )
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
        self.bank_journal_2 = self.env['account.journal'].create({
            'name': 'bank_journal_2',
            'code': 'TEST2',
            'type': 'bank',
            'company_id': self.company.id,
        })
        self.bank_journal_3_post_at_bank_rec = self.env['account.journal'].create({
            'name': 'bank_journal_3',
            'code': 'TEST3',
            'type': 'bank',
            'company_id': self.company.id,
            'post_at': 'bank_rec',
        })
        self.bank_journal_deprecated_account = self.env['account.journal'].create({
            'name': 'bank_journal_deprecated_account',
            'code': 'TEST',
            'type': 'bank',
            'company_id': self.company.id,
        })
        self.get_bank_accounts(self.bank_journal_deprecated_account).write({'deprecated': True})

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

        return {
            "tests": [
                self._prepare_test_1_payment_without_move_lines(),
                self._prepare_test_2_payment_draft_wrong_partner_company_deprecated_account(),
                self._prepare_test_3_statement_line_reconciled_to_internal_transfer(),
                self._prepare_test_4_statement_line_payment_shared_move(),
                self._prepare_test_5_post_at_bank_rec_reconciled_payment(),
                self._prepare_test_6_post_at_bank_rec_not_reconciled_payment(),
            ],
            "config": {
                "company_id": self.company.id,
                "company_2_id": self.company_2.id,
                "partner_id": self.partner.id,
                "partner_another_company_id": self.partner_another_company.id,
                "bank_journal_id": self.bank_journal.id,
                "bank_journal_2_id": self.bank_journal_2.id,
                "bank_journal_3_post_at_bank_rec_id": self.bank_journal_3_post_at_bank_rec.id,
                "bank_journal_deprecated_account_id": self.bank_journal_deprecated_account.id,
                "account_receivable_id": self.account_receivable.id,
                "account_payable_id": self.account_payable.id,
                "pay_method_manual_in_id": self.pay_method_manual_in.id,
                "pay_method_manual_out_id": self.pay_method_manual_out.id,
            },
        }

    def check(self, init):
        config = init["config"]

        self._check_test_1_payment_without_move_lines(config, *init['tests'][0])
        self._check_test_2_payment_draft_wrong_partner_company_deprecated_account(config, *init['tests'][1])
        self._check_test_3_statement_line_reconciled_to_internal_transfer(config, *init['tests'][2])
        self._check_test_4_statement_line_payment_shared_move(config, *init['tests'][3])
        self._check_test_5_post_at_bank_rec_reconciled_payment(config, *init['tests'][4])
        self._check_test_6_post_at_bank_rec_not_reconciled_payment(config, *init['tests'][5])
