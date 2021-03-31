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

    util.rename_field(cr, "stock.quant.package", "packaging_id", "package_type_id")
    util.create_column(cr, "stock_putaway_rule", "storage_category_id", "int4")
    util.create_column(cr, "stock_putaway_rule", "active", "boolean", default=True)
    util.create_column(cr, "stock_location", "storage_category_id", "int4")
    util.create_column(cr, "res_config_settings", "group_stock_storage_categories", "boolean")

    # Inventory migration
    util.create_column(cr, "res_company", "annual_inventory_day", "int4", default=31)
    util.create_column(cr, "res_company", "annual_inventory_month", "varchar", default="12")

    # Add new fields on stock.quant
    util.create_column(cr, "stock_quant", "inventory_quantity", "numeric")
    util.create_column(cr, "stock_quant", "inventory_diff_quantity", "numeric")
    util.create_column(cr, "stock_quant", "inventory_date", "timestamp without time zone")
    util.create_column(cr, "stock_quant", "user_id", "int4")

    util.create_column(cr, "stock_move", "is_inventory", "boolean", default=False)

    # Merge stock.quant to avoid duplication since we move data on them
    cr.execute(
        """
    WITH
        dupes AS(
            SELECT min(id) as to_update_quant_id,
            (array_agg(id ORDER BY id))[2:array_length(array_agg(id), 1)] as to_delete_quant_ids,
            SUM(reserved_quantity) as reserved_quantity,
            SUM(inventory_quantity) as inventory_quantity,
            SUM(quantity) as quantity,
            MIN(in_date) as in_date
            FROM stock_quant
            GROUP BY product_id, company_id, location_id, lot_id, package_id, owner_id
            HAVING count(id) > 1
        ),
        _up AS(
            UPDATE stock_quant q
            SET quantity=d.quantity,
            reserved_quantity=d.reserved_quantity,
            inventory_quantity=d.inventory_quantity,
            in_date=d.in_date
            FROM dupes d
            WHERE d.to_update_quant_id=q.id
        )
        DELETE FROM stock_quant WHERE id in (SELECT unnest(to_delete_quant_ids) from dupes)
    """
    )

    # Find stock.inventory.line that didn't generate a stock.move.line
    # to keep their history of a correct quantity counted
    cr.execute(
        """
    CREATE TEMPORARY VIEW temp_ongoing_inventory_line AS (
        SELECT
            date,
            il.company_id,
            il.location_id,
            il.package_id,
            prod_lot_id,
            il.partner_id,
            il.product_id,
            product_qty,
            stock_quant.id as quant_id
        FROM stock_inventory as i
        JOIN stock_inventory_line as il ON i.id = il.inventory_id
        LEFT JOIN stock_quant ON stock_quant.product_id = il.product_id
                                AND stock_quant.location_id = il.location_id
                                AND stock_quant.company_id = il.company_id
                                AND stock_quant.lot_id IS NOT DISTINCT FROM il.prod_lot_id
                                AND stock_quant.package_id IS NOT DISTINCT FROM il.package_id
                                AND stock_quant.owner_id IS NOT DISTINCT FROM il.partner_id
        WHERE i.state = 'confirm'
    )
    """
    )

    cr.execute(
        """
    UPDATE
        stock_quant
    SET
        inventory_quantity = inventory_line.product_qty,
        inventory_diff_quantity = inventory_line.product_qty - stock_quant.quantity,
        inventory_date = inventory_line.date
    FROM
        temp_ongoing_inventory_line as inventory_line
    WHERE
        quant_id IS NOT NULL
    """
    )

    cr.execute(
        """
    INSERT INTO
        stock_quant(
            product_id,
            location_id,
            lot_id,
            package_id,
            owner_id,
            company_id,
            quantity,
            reserved_quantity,
            inventory_quantity,
            inventory_diff_quantity,
            inventory_date,
            in_date
        )
    SELECT
        product_id,
        location_id,
        prod_lot_id,
        package_id,
        partner_id,
        company_id,
        0,
        0,
        product_qty,
        product_qty,
        date,
        date
    FROM
        temp_ongoing_inventory_line as inventory_line
    WHERE
        quant_id IS NULL
    """
    )

    if not util.table_exists(cr, "temp_inventory_line"):
        cr.execute(
            """
        CREATE TEMPORARY VIEW temp_inventory_line AS (
            WITH inventory_location_per_company AS (
                SELECT
                    company_id,
                    MIN(SPLIT_PART(value_reference, ',', 2)::int4) as location_dest_id
                FROM
                    ir_property
                WHERE
                    ir_property.name = 'property_stock_inventory'
                GROUP BY
                    company_id
                )
            SELECT
                product_id,
                location_id,
                location_dest_id,
                stock_inventory_line.company_id,
                product_uom_id,
                prod_lot_id,
                package_id,
                partner_id,
                inventory_date
            FROM stock_inventory_line
            JOIN inventory_location_per_company ON inventory_location_per_company.company_id = stock_inventory_line.company_id
            JOIN stock_inventory ON stock_inventory_line.inventory_id = stock_inventory.id
            WHERE
                stock_inventory.state = 'done' AND
                stock_inventory_line.product_qty = stock_inventory_line.theoretical_qty
        )
        """
        )

    # Create stock.move for inventory count
    cr.execute(
        """
    INSERT INTO
        stock_move (
            product_id,
            location_id,
            location_dest_id,
            company_id,
            product_qty,
            product_uom_qty,
            product_uom,
            is_inventory,
            reference,
            name,
            state,
            date,
            procure_method
        )
    SELECT
        product_id,
        location_id,
        location_dest_id,
        company_id,
        0,
        0,
        product_uom_id,
        True,
        'Product Quantity Confirmed',
        'Product Quantity Confirmed',
        'done',
        inventory_date,
        'make_to_stock'
    FROM
        temp_inventory_line
    GROUP BY
        product_id,
        location_id,
        location_dest_id,
        company_id,
        inventory_date,
        product_uom_id
    """
    )

    # Create stock.move.line for inventory count linked to move create in the upper query
    cr.execute(
        """
    INSERT INTO
        stock_move_line (
            product_id,
            move_id,
            location_id,
            location_dest_id,
            company_id,
            product_qty,
            product_uom_qty,
            product_uom_id,
            lot_id,
            package_id,
            owner_id,
            reference,
            state,
            date
        )
    SELECT
        temp_inventory_line.product_id,
        stock_move.id,
        temp_inventory_line.location_id,
        temp_inventory_line.location_dest_id,
        temp_inventory_line.company_id,
        0,
        0,
        product_uom_id,
        prod_lot_id,
        package_id,
        temp_inventory_line.partner_id,
        'Product Quantity Confirmed',
        'done',
        inventory_date
    FROM temp_inventory_line
    JOIN stock_move ON stock_move.product_id = temp_inventory_line.product_id
                   AND stock_move.date = temp_inventory_line.inventory_date
                   AND stock_move.location_id = temp_inventory_line.location_id
                   AND stock_move.location_dest_id = temp_inventory_line.location_dest_id
    WHERE
        stock_move.is_inventory = True
    """
    )

    cr.execute(
        """
    UPDATE stock_move
       SET is_inventory = True
     WHERE inventory_id IS NOT NULL
    """
    )

    # Remove Inventory
    util.remove_model(cr, "stock.inventory.line")
    util.remove_model(cr, "stock.inventory")

    util.remove_field(cr, "stock.move", "inventory_id")
    util.remove_field(cr, "stock.track.confirmation", "inventory_id")
