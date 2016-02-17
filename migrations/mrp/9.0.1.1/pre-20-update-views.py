# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.rename_xmlid(cr, 'mrp.mrp_bom_tree_view', 'mrp.mrp_bom_line_tree_view')
