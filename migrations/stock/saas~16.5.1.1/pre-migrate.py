# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.move", "display_clear_serial")
    util.remove_model(cr, "stock.import.lot")
    util.remove_model(cr, "stock.generate.serial")
    util.remove_field(cr, "stock.inventory.adjustment.name", "show_info")

    util.remove_field(cr, "stock.picking", "immediate_transfer")
    util.remove_field(cr, "stock.picking", "show_validate")
    util.remove_field(cr, "stock.picking", "move_line_nosuggest_ids")
    util.remove_field(cr, "stock.move", "show_reserved_availability")
    util.remove_field(cr, "stock.move", "from_immediate_transfer")
    util.remove_field(cr, "stock.move", "move_line_nosuggest_ids")
    util.remove_model(cr, "stock.immediate.transfer")
    util.remove_model(cr, "stock.immediate.transfer.line")
    util.create_column(cr, "stock_move", "picked", "boolean")
    util.create_column(cr, "stock_move_line", "picked", "boolean")
    util.create_column(cr, "stock_move_line", "quantity_product_uom", "numeric")

    query = """
        UPDATE stock_move_line move_line
            SET quantity_product_uom = move_line.qty_done / ml_uom.factor * p_uom.factor
            FROM uom_uom as ml_uom,
                 product_product AS product
            JOIN product_template AS template
              ON product.product_tmpl_id = template.id
            JOIN uom_uom AS p_uom
              ON template.uom_id = p_uom.id
           WHERE product.id = move_line.product_id
             AND move_line.product_uom_id = ml_uom.id
             AND {parallel_filter}
    """
    util.explode_execute(cr, query, table="stock_move_line", alias="move_line")
    # Mark as picked all move that should not be unreserved/rereserved in the end-* script
    query = """
        UPDATE stock_move_line move_line
            SET picked = 't'
          WHERE (move_line.qty_done > 0
             OR  state in ('done', 'cancel'))
            AND {parallel_filter};
    """
    util.explode_execute(cr, query, table="stock_move_line", alias="move_line")
    query = """
        WITH picked_moves AS (
            SELECT move.id
              FROM stock_move move
              JOIN stock_move_line line
                ON line.move_id = move.id
             WHERE line.picked
               AND {parallel_filter}
          GROUP BY move.id
        )
        UPDATE stock_move as move
           SET picked = true
          FROM picked_moves
         WHERE move.id = picked_moves.id
    """
    util.explode_execute(cr, query, table="stock_move", alias="move")

    # remove reservation
    cr.execute("DELETE FROM stock_move_line WHERE picked = false")

    util.rename_field(cr, "stock.move", "quantity_done", "quantity")
    util.rename_field(cr, "stock.move.line", "qty_done", "quantity")

    query = """
        UPDATE stock_move
                SET state =
                    CASE
                    WHEN quantity = 0 THEN 'confirmed'
                    ELSE 'partially_available'
                    END
                WHERE quantity < product_uom_qty
                AND state = 'assigned'
                AND {parallel_filter};
    """
    util.explode_execute(cr, query, table="stock_move")

    util.explode_execute(cr, "UPDATE stock_quant SET reserved_quantity = 0", table="stock_quant")

    # Update the table stock quant base on the sum of quantity
    # of stock move line table group by product_id, location_id, lot_id, package_id, owner_id
    cr.execute(
        """
        WITH move_line_reserved AS (
          SELECT sml.product_id,
                 sml.location_id,
                 sml.lot_id,
                 sml.package_id,
                 sml.owner_id,
                 sml.company_id,
                 sum(sml.quantity_product_uom) as quantity
            FROM stock_move_line sml
            JOIN stock_location location
              ON location.id = sml.location_id
            JOIN product_product product
              ON product.id = sml.product_id
            JOIN product_template template
              ON template.id = product.product_tmpl_id
           WHERE sml.state NOT IN ('done', 'cancel')
         AND NOT (
                   location.usage IN ('supplier', 'customer', 'inventory', 'production') OR
                   location.scrap_location = 't' OR
                   (location.usage = 'transit' AND location.company_id IS NULL)
                )
             AND template.type = 'product'
        GROUP BY sml.product_id, sml.location_id, sml.lot_id, sml.package_id, sml.owner_id, sml.company_id
        )
        INSERT INTO stock_quant (
               product_id,
               location_id,
               lot_id,
               package_id,
               owner_id,
               company_id,
               reserved_quantity,
               in_date
        )
        SELECT move_line.product_id,
               move_line.location_id,
               move_line.lot_id,
               move_line.package_id,
               move_line.owner_id,
               move_line.company_id,
               move_line.quantity,
               now()
          FROM move_line_reserved move_line;
    """
    )

    # warn admins
    util.add_to_migration_reports(
        """
            Transfers and production orders has been unreserved during migration.
            The quantities registered before the migration are now in the quantity
            column and mark as picked.
            You can use the run scheduler action in debug mode to re-reserve other
            operations.
        """,
        category="Inventory",
        format="md",
    )

    util.remove_field(cr, "stock.move", "reserved_availability")
    util.remove_field(cr, "stock.move.line", "reserved_uom_qty")
    util.remove_field(cr, "stock.move.line", "reserved_qty")
    util.remove_field(cr, "stock.move.line", "is_initial_demand_editable")
    util.remove_field(cr, "stock.move.line", "product_packaging_qty_done")

    util.rename_field(cr, "stock.move", "quantity_done", "quantity")
    util.rename_field(cr, "stock.move.line", "qty_done", "quantity")

    util.remove_view(cr, "stock.view_stock_move_nosuggest_operations")

    util.rename_xmlid(cr, "sale_stock.sale_product_catalog_kanban_view_inherit", "stock.product_view_kanban_catalog")

    util.rename_field(cr, "product.label.layout", "picking_quantity", "move_quantity")
    util.remove_field(cr, "lot.label.layout", "picking_ids")
    util.change_field_selection_values(cr, "product.label.layout", "move_quantity", {"picking": "move"})
