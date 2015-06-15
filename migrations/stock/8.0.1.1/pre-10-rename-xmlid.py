# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'stock.view_move_tree_reception_picking', 'stock.view_move_tree_receipt_picking')