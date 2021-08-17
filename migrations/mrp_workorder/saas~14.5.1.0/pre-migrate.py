# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "quality_check", "finished_lot_id", "int4")

    cr.execute(
        """
        UPDATE quality_check qc
           SET finished_lot_id = mp.lot_producing_id
          FROM mrp_production mp
         WHERE qc.production_id = mp.id
        """
    )
