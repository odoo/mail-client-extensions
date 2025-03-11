from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    cr.execute("SELECT id FROM stock_warehouse")
    warehouse_ids = [row[0] for row in cr.fetchall()]
    for warehouse in util.iter_browse(env["stock.warehouse"], warehouse_ids):
        vals = {
            "reception_steps": warehouse.reception_steps,
            "delivery_steps": warehouse.delivery_steps,
            "company_id": warehouse.company_id.id,
        }
        warehouse._create_missing_locations(vals)
        # Will create all missing picking types and sequences for every existing warehouses
        new_types_vals = warehouse._create_or_update_sequences_and_picking_types()
        if new_types_vals:
            # avoid triggering company check for all fields if only some are written
            warehouse.with_context(upgrade_check_company_write_vals=list(new_types_vals)).write(new_types_vals)
            env["stock.picking.type"].browse(new_types_vals.values()).write({"color": warehouse.in_type_id.color})

    # Update all rules from Input/Quality Control -> Stock to new 'Storage' picking type
    cr.execute(
        """
        UPDATE stock_rule sru
           SET location_dest_from_rule = False,
               picking_type_id = sw.store_type_id
          FROM stock_warehouse sw
          JOIN stock_route sro
            ON sw.reception_route_id = sro.id
         WHERE sru.picking_type_id = sw.int_type_id
           AND sru.location_dest_id = sw.lot_stock_id
           AND CASE WHEN sw.reception_steps = 'two_steps' THEN sru.location_src_id = sw.wh_input_stock_loc_id
                    ELSE sru.location_src_id = sw.wh_qc_stock_loc_id
                END
    """
    )
    # Update all rules from Input -> Quality Control to new 'Quality Control' picking type
    cr.execute(
        """
        UPDATE stock_rule sru
           SET location_dest_from_rule = False,
               picking_type_id = sw.qc_type_id
          FROM stock_warehouse sw
          JOIN stock_route sro
            ON sw.reception_route_id = sro.id
         WHERE sru.picking_type_id = sw.int_type_id
           AND sru.location_src_id = sw.wh_input_stock_loc_id
           AND sru.location_dest_id = sw.wh_qc_stock_loc_id
    """
    )
    # Update all cross-dock rules from Input -> Output to use the new 'Cross-Dock' picking type
    cr.execute(
        """
        UPDATE stock_rule sru
           SET location_dest_from_rule = False,
               picking_type_id = sw.xdock_type_id
          FROM stock_warehouse sw
          JOIN stock_route sro
            ON sw.crossdock_route_id = sro.id
         WHERE sru.picking_type_id = sw.int_type_id
           AND sru.location_src_id = sw.wh_input_stock_loc_id
           AND sru.location_dest_id = sw.wh_output_stock_loc_id
    """
    )
