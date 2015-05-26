# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'account_tax_pos_order_line_rel'):
        cr.execute("""CREATE TABLE account_tax_pos_order_line_rel(
                        pos_order_line_id integer,
                        account_tax_id integer
                      )
                   """)

    cr.execute("""INSERT INTO account_tax_pos_order_line_rel(pos_order_line_id, account_tax_id)
                       SELECT pol.id, pt.tax_id
                         FROM pos_order_line pol
                   INNER JOIN product_product p ON (p.id = pol.product_id)
                   INNER JOIN product_taxes_rel pt ON (pt.prod_id = p.product_tmpl_id)
                   INNER JOIN account_tax t ON (t.id = pt.tax_id)
                        WHERE t.company_id = pol.company_id
               """)
