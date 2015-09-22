# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("SELECT count(*) FROM purchase_order_line WHERE product_id IS NULL")
    if cr.fetchone()[0]:
        env = util.env(cr)
        domain = [('default_code', '=', 'GEN_ODOO9_MIG')]
        product = env['product.product'].with_context(active_test=False).search(domain)
        cr.execute("UPDATE purchase_order_line SET product_id = %s WHERE product_id IS NULL",
                   [product.id])
