# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version('15.4')
class TestBatchPayments(UpgradeCase):

    def prepare(self):
        test_name = "TestBatchPayments"

        self.company = self.env['res.company'].create({'name': "company for %s" % test_name})

        # Create user.
        user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': 'user %s' % test_name,
            'login': test_name,
            'groups_id': [
                (6, 0, self.env.user.groups_id.ids),
                (4, self.env.ref('account.group_account_user').id),
            ],
            'company_ids': [(6, 0, self.company.ids)],
            'company_id': self.company.id,
        })
        user.partner_id.email = '%s@test.com' % test_name

        self.env = self.env(user=user)
        self.cr = self.env.cr

        chart_template = self.env.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading(company=self.company, install_demo=False)

        self.bank_journal = self.env['account.journal'].search(
            [('company_id', '=', self.company.id), ('type', '=', 'bank')],
            limit=1,
        )

        # First payment with account on the payment method line.
        payment1 = self.env['account.payment'].create({
            'journal_id': self.bank_journal.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'amount': 100.0,
            'currency_id': self.company.currency_id.id,
        })
        payment1.action_post()

        payment2 = self.env['account.payment'].create({
            'journal_id': self.bank_journal.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'amount': 1000.0,
            'currency_id': self.company.currency_id.id,
        })
        payment2.action_post()

        batch = self.env['account.batch.payment'].create({
            'journal_id': self.bank_journal.id,
            'payment_ids': [(6, 0, (payment1 + payment2).ids)],
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'batch_type': 'inbound',
        })
        return batch.id

    def check(self, batch_id):
        batch = self.env['account.batch.payment'].browse(batch_id)
        self.assertRecordValues(batch, [{
            'amount_residual': 1100.0,
            'amount_residual_currency': 1100.0,
        }])
