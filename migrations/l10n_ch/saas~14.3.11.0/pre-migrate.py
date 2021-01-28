# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, 'l10n_ch.isr_bank_journal_form')

    # Those views were merged into l10n_ch from l10n_ch_qriban in base; we now want to remove them
    util.remove_view(cr, 'l10n_ch.l10n_ch_swissqr_qriban_template')
    util.remove_view(cr, 'l10n_ch.view_partner_bank_form')
    util.remove_view(cr, 'l10n_ch.setup_bank_account_wizard_qr_inherit')

    util.remove_field(cr, 'account.journal', 'l10n_ch_postal')

    util.create_column(cr, 'res_partner_bank', 'l10n_ch_qr_iban', 'varchar')
