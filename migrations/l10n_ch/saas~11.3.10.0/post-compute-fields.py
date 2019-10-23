# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    ids = []
    cr.execute("SELECT id FROM res_partner_bank WHERE l10n_ch_postal IS NULL")
    for rec in util.iter_browse(util.env(cr)["res.partner.bank"], [b[0] for b in cr.fetchall()]):
        if rec.sanitized_acc_number.startswith('CH') and rec.acc_type == "iban":
            cr.execute(
                """
                UPDATE res_partner_bank
                   SET l10n_ch_postal=%s
                 WHERE id=%s
                """,
                (rec._retrieve_l10n_ch_postal(rec.sanitized_acc_number), rec.id),
            )
        else:
            ids.append(rec.id)

    if ids:
        cr.execute(
            """
            UPDATE res_partner_bank
               SET l10n_ch_postal=sanitized_acc_number
             WHERE id in %s
        """,
            [tuple(ids)],
        )
