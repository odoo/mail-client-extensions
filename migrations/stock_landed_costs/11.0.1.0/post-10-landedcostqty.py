# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # landed cost quantity should be 0 according to standard behaviour in v11 its set default 0.
    cr.execute("""
        update account_move_line
        set quantity=0
        where move_id in (select account_move_id from stock_landed_cost)
    """)
