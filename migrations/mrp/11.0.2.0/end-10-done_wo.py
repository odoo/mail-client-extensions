# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Set done_wo fields
    cr.execute("""UPDATE stock_move_line ml SET done_wo='t' WHERE done_wo IS NULL""")