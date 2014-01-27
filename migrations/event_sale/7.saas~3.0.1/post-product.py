# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance import util

def migrate(cr, version):
    cr.execute("""UPDATE product_template
                     SET event_ok = p.event_ok,
                         event_type_id = p.event_type_id
                    FROM product_product p
                   WHERE p.product_template_id = id
                """)

    util.remove_field(cr, 'product.product', 'event_ok')
    util.remove_field(cr, 'product.product', 'event_type_id')
