# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'sale_order', 'can_directly_mark_as_paid', 'boolean')
    cr.execute("""
        UPDATE sale_order s
           SET can_directly_mark_as_paid = (s.state IN ('sent', 'sale') AND a.provider IN ('transfer', 'manual'))
          FROM payment_acquirer a
         WHERE a.id = s.payment_acquirer_id
           AND s.payment_tx_id IS NOT NULL
    """)
    cr.execute("UPDATE sale_order SET can_directly_mark_as_paid = false WHERE can_directly_mark_as_paid IS NULL")

    env = util.env(cr)
    if (env['ir.default'].get('product.template', 'invoice_policy') == 'order' and
       util.modules_installed(cr, 'account_invoicing', 'payment')):
        cr.execute("SELECT count(*) FROM payment_acquirer WHERE auto_confim='generate_and_pay_invoice'")
        if cr.fetchone()[0]:
            env['ir.config_parameter'].set_param('website_sale.automatic_invoice', True)

    util.rename_field(cr, 'website.config.settings', 'sale_pricelist_setting_split_1', 'multi_sales_price')
    util.rename_field(cr, 'website.config.settings', 'sale_pricelist_setting_split_2', 'multi_sales_price_method')
