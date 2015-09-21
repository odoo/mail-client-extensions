# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_view(cr, 'portal_sale.sale_order_form_payment')
    util.remove_view(cr, 'portal_sale.invoice_form_payment')
    util.remove_view(cr, 'portal_sale.invoice_form_portal')
    util.remove_view(cr, 'portal_sale.portal_sale_payment_option_config')
