# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "stock.valuation.layer", "active")

    cr.execute("""
        SELECT DISTINCT pt.name FROM stock_quant q
            JOIN product_product p ON q.product_id = p.id
            JOIN product_template pt ON pt.id = p.product_tmpl_id
            JOIN stock_location l ON l.id = q.location_id
        WHERE q.quantity > 0
            AND p.active = FALSE
            AND pt.active = TRUE
            AND l.USAGE IN ('internal', 'transit')
            AND l.company_id IS NOT NULL
    """)
    products = ', '.join(n for n, in cr.fetchall())
    if products:
        msg = 'The following product templates quantities will be updated because we now include the quantities of their archived variants: %s' % products
        util.add_to_migration_reports(msg, 'Inventory')