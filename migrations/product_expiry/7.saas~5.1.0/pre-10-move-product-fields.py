# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):

    for f in 'life use removal alert'.split():
        f += '_time'
        util.create_column(cr, "product_template", f, "int")

        cr.execute("UPDATE product_template SET {0}=0".format(f))

        cr.execute("""UPDATE product_template t
                         SET {0}=p.tm
                        FROM (SELECT product_tmpl_id,
                                     MIN({0}) as tm
                                FROM product_product
                               WHERE {0} > 0
                            GROUP BY product_tmpl_id
                        ) AS p
                       WHERE t.id = p.product_tmpl_id
                   """.format(f))

        util.remove_field(cr, "product.product", f)
