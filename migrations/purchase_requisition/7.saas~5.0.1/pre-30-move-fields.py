# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, "product_template", "purchase_requisition", "boolean")

    cr.execute("UPDATE product_template SET purchase_requisition='f'")

    cr.execute("""UPDATE product_template t
                     SET purchase_requisition=p.pr
                    FROM (SELECT product_tmpl_id,
                                 MAX(purchase_requisition::int)::boolean as pr
                            FROM product_product
                        GROUP BY product_tmpl_id
                    ) AS p
                   WHERE p.product_tmpl_id = t.id
               """)
