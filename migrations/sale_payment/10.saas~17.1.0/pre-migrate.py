# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.move_field_to_module(cr, 'payment.transation', 'sale_order_id',
                              'website_portal_sale', 'sale_payment')
    util.move_field_to_module(cr, 'sale.order', 'payment_tx_id', 'website_sale', 'sale_payment')
    util.move_field_to_module(cr, 'sale.order', 'payment_acquirer_id', 'website_sale', 'sale_payment')

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('{website_portal_sale,sale_payment}.payment_transaction_action_pending'))
    util.rename_xmlid(cr, *eb('{website_portal_sale,sale_payment}.payment_transaction_action_authorized'))
