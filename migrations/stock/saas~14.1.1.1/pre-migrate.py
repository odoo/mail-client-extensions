# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, xml_id="stock.view_picking_type_list")

    util.remove_field(cr, "stock.picking.type", "rate_picking_late")
    util.remove_field(cr, "stock.picking.type", "rate_picking_backorders")
    util.remove_field(cr, "stock.warehouse", "warehouse_count")
    util.remove_field(cr, "stock.warehouse", "show_resupply")

    util.move_field_to_module(cr, "stock.quant.package", "package_use", "stock_barcode_picking_batch", "stock")
    util.create_column(cr, "stock_quant_package", "package_use", "varchar", default="disposable")

    # Remove duplicate reordering rules
    cr.execute(
        """
            DELETE FROM stock_warehouse_orderpoint WHERE id IN (
                  SELECT unnest((array_agg(id ORDER BY NOT active, id))[2:])
                    FROM stock_warehouse_orderpoint
                GROUP BY product_id, location_id, company_id
                  HAVING count(*) > 1
            )
        """
    )

    util.create_column(cr, "stock_location", "cyclic_inventory_frequency", "integer", default=0)
    util.create_column(cr, "stock_location", "last_inventory_date", "timestamp without time zone")
    util.create_column(cr, "stock_location", "next_inventory_date", "date")
    util.create_column(cr, "stock_inventory", "is_conflict_inventory", "boolean")
    util.create_m2m(cr, "stock_inventory_stock_production_lot_rel", "stock_inventory", "stock_production_lot")

    util.create_column(cr, "stock_move", "reservation_date", "date")
    util.create_column(cr, "stock_picking_type", "reservation_method", "character varying", default="at_confirm")
    util.create_column(cr, "stock_picking_type", "reservation_days_before", "integer")
    util.remove_field(cr, "res.config.settings", "module_procurement_jit")
