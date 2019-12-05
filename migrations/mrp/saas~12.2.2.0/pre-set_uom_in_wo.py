# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mrp_workorder", "product_uom_id", "int4")

    cr.execute(
        """
        UPDATE mrp_workorder mwo
           SET product_uom_id = mp.product_uom_id
          FROM mrp_production mp
         WHERE mp.id = mwo.production_id
           AND mwo.product_uom_id IS NULL
    """
    )
