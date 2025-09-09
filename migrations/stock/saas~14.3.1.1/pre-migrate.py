from odoo.upgrade import util


def migrate(cr, version):
    # Add expected reservation_date to 'at_confirm' moves
    query = """
            UPDATE stock_move AS sm
               SET reservation_date = sm.create_date
              FROM stock_picking_type AS spt
             WHERE spt.reservation_method = 'at_confirm'
               AND sm.picking_type_id = spt.id
               AND sm.reservation_date IS NULL
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move", alias="sm"))

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
    util.create_column(cr, "stock_quant", "inventory_date", "date")
    util.create_column(cr, "stock_quant", "user_id", "int4")

    util.create_column(cr, "stock_move", "is_inventory", "boolean", default=False)

    # Merge stock.quant to avoid duplication since we move data on them
    cr.execute(
        """
    WITH
        dupes AS(
            SELECT min(id) as to_update_quant_id,
                   (array_agg(id ORDER BY id))[2:count(id)] as to_delete_quant_ids,
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
               SET quantity = d.quantity,
                   reserved_quantity = d.reserved_quantity,
                   inventory_quantity = d.inventory_quantity,
                   in_date = d.in_date
              FROM dupes d
             WHERE d.to_update_quant_id = q.id
        )
        DELETE FROM stock_quant
              WHERE id in (SELECT unnest(to_delete_quant_ids) from dupes)
    """
    )

    # Find stock.inventory.line that didn't generate a stock.move.line
    # to keep their history of a correct quantity counted

    # if the module `stock_account` is installed, the column `accounting_date` moved from the inventory to the quant
    # force creation of the column to easy queries writing (avoid SQL composition).
    util.create_column(cr, "stock_inventory", "accounting_date", "date")
    util.create_column(cr, "stock_quant", "accounting_date", "date")

    cr.execute(
        """
        SELECT
            ROW_NUMBER() OVER () AS id,
            i.date,
            il.company_id,
            il.location_id,
            il.package_id,
            il.prod_lot_id,
            il.partner_id,
            il.product_id,
            il.product_qty,
            stock_quant.id as quant_id,
            i.accounting_date
        INTO UNLOGGED TABLE temp_ongoing_inventory_line
        FROM stock_inventory as i
        JOIN stock_inventory_line as il ON i.id = il.inventory_id
        LEFT JOIN stock_quant ON stock_quant.product_id = il.product_id
                                AND stock_quant.location_id = il.location_id
                                AND stock_quant.company_id = il.company_id
                                AND stock_quant.lot_id IS NOT DISTINCT FROM il.prod_lot_id
                                AND stock_quant.package_id IS NOT DISTINCT FROM il.package_id
                                AND stock_quant.owner_id IS NOT DISTINCT FROM il.partner_id
        WHERE i.state = 'confirm';
        CREATE INDEX temp_ongoing_inventory_line_quant_id_idx
                  ON temp_ongoing_inventory_line (quant_id);
        CREATE INDEX temp_ongoing_inventory_line_id_idx
                  ON temp_ongoing_inventory_line (id);
    """
    )

    util.explode_execute(
        cr,
        """
        UPDATE stock_quant q
           SET inventory_quantity = l.product_qty,
               inventory_diff_quantity = l.product_qty - q.quantity,
               inventory_date = l.date,
               accounting_date = l.accounting_date
          FROM temp_ongoing_inventory_line as l
         WHERE q.id = l.quant_id
           AND {parallel_filter}
        """,
        table="stock_quant",
        alias="q",
    )

    util.explode_execute(
        cr,
        """
        INSERT INTO stock_quant(product_id, location_id, lot_id, package_id, owner_id, company_id,
                                quantity, reserved_quantity, inventory_quantity, inventory_diff_quantity,
                                inventory_date, in_date, accounting_date
        )
             SELECT product_id, location_id, prod_lot_id, package_id, partner_id, company_id,
                    0, 0, product_qty, product_qty,
                    date, date, accounting_date
               FROM temp_ongoing_inventory_line
              WHERE quant_id IS NULL
                AND {parallel_filter}
        """,
        table="temp_ongoing_inventory_line",
    )
    cr.execute("DROP TABLE temp_ongoing_inventory_line")

    # we need to fix UoM inconsistencies before creating the stock moves
    cr.execute(
        """
        WITH bad_lines AS (
            SELECT sil.id sil_id,
                   uom2.id uom_id
              FROM stock_inventory_line sil
              JOIN product_product pp ON pp.id = sil.product_id
              JOIN product_template pt ON pt.id = pp.product_tmpl_id
              JOIN uom_uom uom1 ON uom1.id = sil.product_uom_id
              JOIN uom_uom uom2 ON uom2.id = pt.uom_id
             WHERE uom1.category_id != uom2.category_id
        )
        UPDATE stock_inventory_line sil
           SET product_uom_id = bad_lines.uom_id
          FROM bad_lines
         WHERE sil.id = bad_lines.sil_id
     RETURNING sil.id,sil.product_uom_id
        """
    )

    cr.execute(
        """
        CREATE TEMPORARY VIEW temp_inventory_line AS (
            WITH inventory_location_per_company AS (
                SELECT p.company_id,
                       (SPLIT_PART(p.value_reference, ',', 2))::int4 as location_dest_id
                  FROM ir_property p
                  JOIN ir_model_fields f
                    ON p.fields_id = f.id
                 WHERE p.name = 'property_stock_inventory'
                   AND p.res_id IS NULL
                   AND p.value_reference like 'stock.location,%'
                   AND f.model = 'product.template'
                   AND f.name = 'property_stock_inventory'
            )
            SELECT sil.product_id,
                   sil.location_id,
                   ilpc.location_dest_id,
                   sil.company_id,
                   sil.product_uom_id,
                   sil.prod_lot_id,
                   sil.package_id,
                   sil.partner_id,
                   si.date as inventory_date
              FROM stock_inventory_line AS sil
              JOIN inventory_location_per_company AS ilpc
                ON ilpc.company_id = sil.company_id
              JOIN stock_inventory AS si
                ON sil.inventory_id = si.id
             WHERE si.state = 'done'
               AND sil.product_qty = sil.theoretical_qty
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
        temp_inventory_line.product_uom_id,
        temp_inventory_line.prod_lot_id,
        temp_inventory_line.package_id,
        temp_inventory_line.partner_id,
        'Product Quantity Confirmed',
        'done',
        temp_inventory_line.inventory_date
    FROM temp_inventory_line
    JOIN stock_move ON stock_move.product_id = temp_inventory_line.product_id
                   AND stock_move.date = temp_inventory_line.inventory_date
                   AND stock_move.location_id = temp_inventory_line.location_id
                   AND stock_move.location_dest_id = temp_inventory_line.location_dest_id
    WHERE
        stock_move.is_inventory = True
    """
    )

    query = "UPDATE stock_move SET is_inventory = true WHERE inventory_id IS NOT NULL"
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_move"))

    # Remove Inventory
    util.remove_model(cr, "stock.inventory.line")
    util.remove_model(cr, "stock.inventory")

    util.remove_field(cr, "stock.move", "inventory_id")
    util.remove_field(cr, "stock.track.confirmation", "inventory_id")

    # cleanup
    if not util.module_installed(cr, "stock_account"):
        util.remove_column(cr, "stock_quant", "accounting_date")

    util.create_column(cr, "stock_picking_type", "print_label", "boolean")
    cr.execute(
        """
        UPDATE stock_picking_type
           SET print_label = 't'
         WHERE code = 'outgoing'
    """
    )

    util.remove_column(cr, "stock_track_line", "tracking")
