# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'stock.product_category_form_view_inherit')
    util.rename_xmlid(cr, 'procurement.sequence_mrp_op_type', 'stock.sequence_mrp_op_type')
