# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for p in ['old', 'new']:
        util.create_column(cr, 'mrp_eco_bom_change', p + '_uom_id', 'int4')
        cr.execute("""
            UPDATE mrp_eco_bom_change
               SET {0}_uom_id = product_uom_id
             WHERE COALESCE({0}_product_qty, 0) != 0
        """.format(p))
    util.remove_field(cr, 'mrp.eco.bom.change', 'product_uom_id')

    util.remove_view(cr, 'mrp_plm.mrp_eco_tag_view_form')
