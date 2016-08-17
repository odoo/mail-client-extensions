# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'sale_mrp.mrp_production_form_view_inherit_sale_mrp')
    util.remove_view(cr, 'sale_mrp.view_order_form_inherit_sale_mrp')
