# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    #Not using recompute because it's no more a computed field
    cr.execute("SELECT id FROM res_partner_bank WHERE l10n_ch_postal IS NULL")
    for rec in util.iter_browse(util.env(cr)['res.partner.bank'], [b[0] for b in cr.fetchall()]):
        if rec.acc_type == 'iban':
            rec.l10n_ch_postal = rec._retrieve_l10n_ch_postal(rec.sanitized_acc_number)
        else:
            rec.l10n_ch_postal = rec.sanitized_acc_number
    
