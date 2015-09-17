# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, 'sale.view_order_form', deactivate_custom=True)
    util.remove_view(cr, 'sale.view_sales_config')
    util.remove_view(cr, 'sale.account_invoice_tree')
