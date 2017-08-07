# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_record(cr, 'website_portal_sale.access_account_invoice_tax')
    util.remove_record(cr, 'website_portal_sale.access_account_journal')
    util.remove_record(cr, 'website_portal_sale.access_product_list')
    util.remove_record(cr, 'website_portal_sale.access_res_partner')
    util.remove_record(cr, 'website_portal_sale.access_account_tax')
    util.remove_record(cr, 'website_portal_sale.access_account_tax_group')
    util.remove_record(cr, 'website_portal_sale.access_res_partner_category')
    util.remove_record(cr, 'website_portal_sale.access_product_attribute_portal')
    util.remove_record(cr, 'website_portal_sale.access_product_attribute_value_portal')
    util.remove_record(cr, 'website_portal_sale.access_product_attribute_price_portal')
    util.remove_record(cr, 'website_portal_sale.access_product_attribute_line_portal')
    util.remove_record(cr, 'website_portal_sale.portal_personal_contact')
