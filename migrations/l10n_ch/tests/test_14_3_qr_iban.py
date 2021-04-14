# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.3")
class TestQRIBAN(UpgradeCase):
    def prepare(self):
        no_qr_account = self._create_bank_account('CH1538815158384538437')
        qr_account = self._create_bank_account('CH2130808001234567827')

        return {no_qr_account.id: False, qr_account.id: qr_account.acc_number}

    def _create_bank_account(self, acc_number):
        return self.env['res.partner.bank'].create({
            'acc_number': acc_number,
            'partner_id': self.env.company.partner_id.id,
        })

    def check(self, init):
        for partner_bank_id, expected_qr_iban in init.items():
            partner_bank = self.env['res.partner.bank'].browse(int(partner_bank_id))
            self.assertEqual(partner_bank.l10n_ch_qr_iban, expected_qr_iban)
