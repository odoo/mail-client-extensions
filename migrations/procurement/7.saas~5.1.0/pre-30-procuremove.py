from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    """
    1 Procurement method moved from procurements to stock moves
    2 Change states from procurements

    If product of type service and mto, it should get auto_create_task
    """
    util.create_column(cr, "stock_move", "procure_method", "varchar")

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE stock_move move
            SET procure_method = p.procure_method
            FROM procurement_order p WHERE p.move_id = move.id
            """,
            table="stock_move",
            alias="move",
        ),
    )

    if util.column_exists(cr, "sale_order_line", "procurement_id"):
        cr.execute(
            """
            ALTER TABLE sale_order_line
                DROP CONSTRAINT sale_order_line_procurement_id_fkey;
            ALTER TABLE stock_warehouse_orderpoint
                DROP CONSTRAINT stock_warehouse_orderpoint_procurement_id_fkey;
            WITH deleted_procurements AS (
                DELETE FROM procurement_order
                    WHERE procure_method='make_to_stock' RETURNING id
            ),
            _updated_sale_order_line AS (
              UPDATE sale_order_line SET procurement_id = NULL WHERE EXISTS (
                  SELECT 1 FROM deleted_procurements
                      WHERE deleted_procurements.id = sale_order_line.procurement_id
              )
            )
            UPDATE stock_warehouse_orderpoint SET procurement_id = NULL WHERE EXISTS (
                SELECT 1 FROM deleted_procurements
                    WHERE deleted_procurements.id = stock_warehouse_orderpoint.procurement_id
            );
            ALTER TABLE sale_order_line
                ADD CONSTRAINT sale_order_line_procurement_id_fkey
                FOREIGN KEY (procurement_id)
                REFERENCES procurement_order(id)
                ON DELETE SET NULL;
            ALTER TABLE stock_warehouse_orderpoint
                ADD CONSTRAINT stock_warehouse_orderpoint_procurement_id_fkey
                FOREIGN KEY (procurement_id)
                REFERENCES procurement_order(id)
                ON DELETE SET NULL;
            """
        )
    else:
        cr.execute("""delete from procurement_order where procure_method='make_to_stock'""")

    # Rename column move_dest_id
    util.rename_field(cr, "procurement.order", "move_id", "move_dest_id")

    # Change states of procurements:
    # draft, ready should be confirmed
    # waiting should pass to running
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE procurement_order po
               SET state = CASE WHEN state='waiting' THEN 'running' ELSE 'confirmed' END
            WHERE po.state in ('draft', 'ready', 'waiting')
            """,
            table="procurement_order",
            alias="po",
        ),
    )

    # Migration of stock_location
    if util.table_exists(cr, "product_pulled_flow"):
        moved = util.splitlines(
            """
        partner_address_id
        location_id
        location_src_id
        procure_method
        cancel_cascade
    """
        )
        for m in moved:
            util.move_field_to_module(cr, "product.pulled.flow", m, "stock_location", "stock")
        util.move_field_to_module(cr, "product.pulled.flow", "invoice_state", "stock_location", "stock_account")
        moved = util.splitlines(
            """
        name
        company_id
        type_proc
    """
        )
        for m in moved:
            util.move_field_to_module(cr, "product.pulled.flow", m, "stock_location", "procurement")
        util.rename_model(cr, "product.pulled.flow", "procurement.rule", rename_table=True)
        util.rename_field(cr, "procurement.rule", "cancel_cascade", "propagate")
        util.rename_field(cr, "procurement.rule", "type_proc", "action")

    util.create_column(cr, "product_template", "auto_create_task", "boolean")
    cr.execute(
        """
    UPDATE product_template SET auto_create_task = 't'
    WHERE product_template.type = 'service' AND product_template.procure_method='make_to_order'
    """
    )
