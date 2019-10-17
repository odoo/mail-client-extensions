# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "res_partner", "l10n_de_datev_identifier", "int4")
    # See task comment: https://www.odoo.com/mail/view?model=project.task&res_id=1942108
    cr.execute("""
        UPDATE res_partner
           SET l10n_de_datev_identifier = id
         WHERE id IN (SELECT l.partner_id
                        FROM account_move_line l
                        JOIN account_move m
                          ON l.move_id = m.id
                       WHERE l.tax_line_id IS NULL
                         AND l.debit != l.credit
                         AND l.account_id != m.l10n_de_datev_main_account_id
                     )
    """)
