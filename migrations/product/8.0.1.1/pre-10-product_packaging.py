# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("ALTER TABLE product_packaging DROP CONSTRAINT product_packaging_product_id_fkey")
    cr.execute("""UPDATE product_packaging pa
                     SET product_tmpl_id = pp.product_tmpl_id
                    FROM product_product pp
                   WHERE pa.product_tmpl_id = pp.id
               """)
