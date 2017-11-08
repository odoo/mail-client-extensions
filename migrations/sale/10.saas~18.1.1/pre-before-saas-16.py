# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # if database was older than saas~16, the script website_portal_sale@saas~16 hasn't be run
    # do it now
    util.remove_record(cr, 'sale.access_account_invoice_tax')
    util.remove_record(cr, 'sale.access_account_journal')
    util.remove_record(cr, 'sale.access_product_list')
    util.remove_record(cr, 'sale.access_res_partner')
    util.remove_record(cr, 'sale.access_account_tax')
    util.remove_record(cr, 'sale.access_account_tax_group')
    util.remove_record(cr, 'sale.access_res_partner_category')
    util.remove_record(cr, 'sale.access_product_attribute_portal')
    util.remove_record(cr, 'sale.access_product_attribute_value_portal')
    util.remove_record(cr, 'sale.access_product_attribute_price_portal')
    util.remove_record(cr, 'sale.access_product_attribute_line_portal')
    util.remove_record(cr, 'sale.portal_personal_contact')
