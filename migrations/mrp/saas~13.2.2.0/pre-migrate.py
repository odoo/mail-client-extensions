# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "mrp.production", "date_start_wo")
    util.create_column(cr, "mrp_production", "delay_alert", "boolean")
    util.create_column(cr, "mrp_production", "consumption", "varchar")
    cr.execute(
        """
        UPDATE mrp_production p
           SET consumption = b.consumption
          FROM mrp_bom b
         WHERE b.id = p.bom_id
    """
    )

    util.remove_field(cr, "mrp.workorder", "color")
    util.remove_field(cr, "mrp.workorder", "capacity")

    util.create_column(cr, "stock_warn_insufficient_qty_unbuild", "quantity", "float8")
    util.create_column(cr, "stock_warn_insufficient_qty_unbuild", "product_uom_name", "varchar")
