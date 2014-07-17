# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    pt = util.ref(cr, 'point_of_sale.picking_type_posout')
    if pt:
        cr.execute("UPDATE pos_config SET picking_type_id=%s", (pt,))
