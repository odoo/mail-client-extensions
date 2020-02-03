# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Columns needed on stock_move to support FIFO
    util.remove_field(cr, 'product.template', 'property_valuation')
    util.remove_field(cr, 'product.template', 'valuation')
    util.remove_field(cr, 'product.template', 'property_cost_method')
    util.remove_field(cr, 'product.template', 'cost_method')
    util.remove_field(cr, 'product.template', 'property_stock_account_input')
    util.remove_field(cr, 'product.template', 'property_stock_account_output')

    util.remove_view(cr, "stock_account.view_template_property_form")
