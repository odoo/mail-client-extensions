# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'purchase.view_purchase_config')
    util.remove_view(cr, 'purchase.purchase_order_2_stock_picking')
    util.remove_view(cr, 'purchase.view_product_normal_purchase_buttons_from')
    util.remove_view(cr, 'purchase.purchase_order_line_form')

    for r in 'order quotation'.split():
        util.force_noupdate(cr, 'purchase.report_purchase%s' % r, False)
        util.force_noupdate(cr, 'purchase.report_purchase%s_document' % r, False)
