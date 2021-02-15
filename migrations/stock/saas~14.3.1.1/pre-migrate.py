# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Add expected reservation_date to 'at_confirm' moves
    cr.execute(
        """
            UPDATE stock_move AS sm
               SET reservation_date = sm.create_date
              FROM stock_picking_type AS spt
             WHERE spt.reservation_method = 'at_confirm'
               AND sm.picking_type_id = spt.id
               AND sm.reservation_date IS NULL
        """
    )

    util.create_column(cr, "stock_picking_type", "reservation_days_before_priority", "integer")

    # Don't change current reservation_date logic for users already using a non-zero 'by_date'
    cr.execute(
        """
            UPDATE stock_picking_type
               SET reservation_days_before_priority = reservation_days_before
             WHERE reservation_days_before IS NOT NULL
        """
    )

    util.rename_field(cr, 'stock.quant.package', 'packaging_id', 'package_type_id')
    util.create_column(cr, "stock_putaway_rule", "storage_category_id", "int4")
    util.create_column(cr, "stock_putaway_rule", "active", "boolean", default=True)
    util.create_column(cr, "stock_location", "storage_category_id", "int4")
    util.create_column(cr, "res_config_settings", "group_stock_storage_categories", "boolean")
