# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_field(cr, "account.move", *eb("l10n_ch_isr_{postal,subscription}"))
    util.rename_field(cr, "account.move", *eb("l10n_ch_isr_{postal,subscription}_formatted"))

    util.create_column(cr, "res_partner_bank", "l10n_ch_isr_subscription_chf", "varchar")
    util.create_column(cr, "res_partner_bank", "l10n_ch_isr_subscription_eur", "varchar")
    cr.execute(
        """
        UPDATE res_partner_bank p
           SET l10n_ch_isr_subscription_chf = b.l10n_ch_postal_chf,
               l10n_ch_isr_subscription_eur = b.l10n_ch_postal_eur
          FROM res_bank b
         WHERE b.id = p.bank_id
    """
    )
    util.remove_field(cr, "res.bank", "l10n_ch_postal_chf")
    util.remove_field(cr, "res.bank", "l10n_ch_postal_eur")

    util.remove_view(cr, "l10n_ch.isr_res_bank_form")
