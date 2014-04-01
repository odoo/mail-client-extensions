# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_supplierinfo', 'product_tmpl_id', 'int4')
    cr.execute("""UPDATE product_supplierinfo i
                     SET product_tmpl_id = p.product_tmpl_id
                    FROM product_product p
                   WHERE p.id = i.product_id
               """)
