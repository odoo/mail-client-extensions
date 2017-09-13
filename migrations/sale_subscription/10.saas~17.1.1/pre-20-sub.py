# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'sale_subscription', 'name', 'varchar')
    util.create_column(cr, 'sale_subscription', 'code', 'varchar')
    util.create_column(cr, 'sale_subscription', 'partner_id', 'int4')
    cr.execute("""
        UPDATE sale_subscription s
           SET name = a.name,
               code = a.code,
               partner_id = a.partner_id
          FROM account_analytic_account a
         WHERE a.id = s.analytic_account_id
    """)

    util.create_m2m(cr, 'account_analytic_tag_sale_subscription_rel',
                    'sale_subscription', 'account_analytic_tag')
    cr.execute("""
        INSERT INTO account_analytic_tag_sale_subscription_rel(sale_subscription_id, account_analytic_tag_id)
             SELECT s.id, r.tag_id
               FROM account_analytic_account_tag_rel r
               JOIN sale_subscription s ON (s.analytic_account_id = r.account_id)
    """)

    util.remove_field(cr, 'sale.order', 'subscription_id')
    util.remove_field(cr, 'sale.subscription.line', 'actual_quantity')
    util.remove_field(cr, 'sale.subscription.line', 'sold_quantity')

    util.remove_field(cr, 'sale.subscription.wizard', 'account_id')
    for f in 'subscription_template_id portal_access is_authorized price'.split():
        util.remove_field(cr, 'sale.subscription.wizard.option', f)

    util.move_field_to_module(cr, 'sale.subscription', 'sale_order_count',
                              'website_subscription', 'sale_subscription')

    for f in 'tag_ids subscription_count color'.split():
        util.move_field_to_module(cr, 'sale.subscription.template', f,
                                  'website_subscription', 'sale_subscription')
