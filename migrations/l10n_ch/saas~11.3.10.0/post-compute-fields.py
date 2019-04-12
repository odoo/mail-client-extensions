# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    #Using SQL queries to avoid a recomputation hell due to _compute_l10n_ch_isr_number
    cr.execute("""
        UPDATE res_partner_bank
           SET l10n_ch_postal=sanitized_acc_number
         WHERE l10n_ch_postal IS NULL AND acc_type!='iban'
    """)
    cr.execute("SELECT id FROM res_partner_bank WHERE l10n_ch_postal IS NULL and acc_type='iban' AND sanitized_acc_number like 'CH%'")
    for rec in util.iter_browse(util.env(cr)['res.partner.bank'], [b[0] for b in cr.fetchall()]):
        cr.execute("""
            UPDATE res_partner_bank
               SET l10n_ch_postal=%s
             WHERE id=%s
        """, (rec.id, rec._retrieve_l10n_ch_postal(rec.sanitized_acc_number)))
