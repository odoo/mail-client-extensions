# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    # Need to change many2many for consume lines to one2many
    util.create_column(cr, 'stock_move', 'raw_material_production_id', 'int4')
    cr.execute("""
        UPDATE stock_move
        SET raw_material_production_id = mrp.id
        FROM mrp_production mrp, mrp_production_move_ids mrpmove
        WHERE mrpmove.move_id = stock_move.id AND mrpmove.production_id = mrp.id
    """)
    # It is easiest to rebuild this report as the value field does not get well migrated
    cr.execute("DROP VIEW IF EXISTS report_mrp_inout")
