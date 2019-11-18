# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute('''
        UPDATE account_move am
        SET sdd_paying_mandate_id = inv.sdd_paying_mandate_id
        FROM account_invoice inv
        WHERE inv.move_id = am.id
    ''')

    util.remove_column(cr, 'account_move', 'sdd_paying_mandate_id')
