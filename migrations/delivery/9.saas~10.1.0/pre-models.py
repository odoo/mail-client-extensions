# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'delivery_carrier', 'prod_environment', 'boolean')
    util.create_column(cr, 'delivery_carrier', 'margin', 'int4')

    cr.execute("UPDATE delivery_carrier SET prod_environment=true, margin=0")

    pack_fields = {
        'height': ['int4', 0],
        'width': ['int4', 0],
        'length': ['int4', 0],
        'max_weight': ['float8', 0],
        'package_carrier_type': ['varchar', 'none'],
    }
    for name, (type_, value) in pack_fields.items():
        util.create_column(cr, 'product_packaging', name, type_)
        cr.execute("UPDATE product_packaging SET {0}=%s WHERE {0} IS NULL".format(name), [value])
