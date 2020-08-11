# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, 'sale.view_order_form')
    util.remove_view(cr, 'sale.view_sales_config')
    util.remove_view(cr, 'sale.account_invoice_tree')
    util.remove_view(cr, 'sale.view_order_line_form2')
    util.remove_view(cr, 'sale.view_sales_order_uninvoiced_line_filter')
