# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("ALTER TABLE sale_subscription RENAME COLUMN template_id TO _tmpl_id")

    cr.execute("UPDATE sale_subscription SET user_id=manager_id WHERE user_id IS NULL")
    util.update_field_usage(cr, 'sale.subscription', 'manager_id', 'user_id')
    util.update_field_usage(cr, 'sale.subscription.report', 'manager_id', 'user_id')
    util.remove_field(cr, 'sale.subscription', 'manager_id')

    # pricelist is now required
    PL = util.env(cr)['product.pricelist']
    cr.execute("""
        SELECT s.id, a.partner_id, a.company_id
          FROM sale_subscription s
          JOIN account_analytic_account a
            ON s.analytic_account_id = a.id
         WHERE s.pricelist_id IS NULL
           AND a.partner_id IS NOT NULL
    """)
    for sid, pid, cid in cr.fetchall():
        # XXX browse all partners at once?
        cr.execute("UPDATE sale_subscription SET pricelist_id = %s WHERE id = %s",
                   [PL._get_partner_pricelist(pid, cid) or None, sid])
