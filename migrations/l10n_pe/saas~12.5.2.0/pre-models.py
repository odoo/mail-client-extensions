# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move_line", "l10n_pe_group_id", "int4")
    cr.execute("""
        UPDATE account_move_line l
           SET l10n_pe_group_id = a.group_id
          FROM account_account a
         WHERE a.id = l.account_id
    """)
