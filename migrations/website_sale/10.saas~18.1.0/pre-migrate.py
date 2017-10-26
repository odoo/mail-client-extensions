# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("UPDATE product_attribute SET type='select' WHERE type='hidden'")
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb('website_sale.{orders_followup,portal_order_page}_products_link'))

    if not util.module_installed(cr, 'website_sale_stock'):
        util.remove_field(cr, 'product.template', 'availability')
        util.remove_field(cr, 'product.template', 'availability_warning')
    else:
        util.rename_field(cr, 'product.template', 'availability', 'inventory_availability')
        util.move_field_to_module(cr, 'product.template', 'inventory_availability',
                                  'website_sale', 'website_sale_stock')

        util.rename_field(cr, 'product.template', 'availablity_warning', 'custom_message')
        util.move_field_to_module(cr, 'product.template', 'custom_message',
                                  'website_sale', 'website_sale_stock')
