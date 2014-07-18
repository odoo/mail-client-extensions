# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'product_packaging', 'product_tmpl_id', 'int4')
    cr.execute("""UPDATE product_packaging pa
                     SET product_tmpl_id = pp.product_tmpl_id
                    FROM product_product pp
                   WHERE pa.product_tmpl_id = pp.id
               """)
