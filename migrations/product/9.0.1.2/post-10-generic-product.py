# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # sol and pol now have a not null constraint on product_id
    # so let's create the product here if needed and use it in the right module

    def count(t):
        if not util.table_exists(cr, t):
            return 0
        cr.execute("SELECT count(1) FROM {t} WHERE product_id IS NULL".format(t=t))
        return cr.fetchone()[0]

    tables = ['sale_order_line', 'purchase_order_line', 'hr_expense_line', 'account_analytic_line']
    if any(count(t) for t in tables):
        env = util.env(cr)
        categ_id = util.ref(cr, 'product.product_category_all')
        uom_id = util.ref(cr, 'product.product_uom_unit')
        env['product.product'].create({
            'name': 'Generic Product',
            'default_code': 'GEN_ODOO9_MIG',
            'list_price': 0.0,
            'categ_id': categ_id,
            'uom_id': uom_id,
            'uom_po_id': uom_id,
            'type': 'service',
            'description_sale': 'Generic product created automatically during the migration to Odoo 9 due to new constraints.',
            'active': False,
        })
