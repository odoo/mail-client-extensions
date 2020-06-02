# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "mrp_routing_workcenter", "bom_id", "int4")
    util.create_column(cr, "mrp_routing_workcenter", "old_id", "int4")  # Working column

    column_op, column_op_pre = util.get_columns(
        cr, "mrp_routing_workcenter", ignore=("id", "bom_id", "old_id"), extra_prefixes=["old_operation"]
    )

    if util.column_exists(cr, "mrp_routing_workcenter", "routing_id"):
        # For mrp.routing.workcenter: duplicate operation for each bom using related routing and link via bom_id
        # And Delete old operations
        # Recreate link to operation_id for mrp.bom.line (module mrp) via bom_id
        # Recreate link to operation_id for mrp.bom.byproduct (module mrp) via bom_id
        # Recreate link to operation_id for stock.move (module mrp) via raw_material_production_id
        # TODO: Recreate all quality point link to a operation
        # TODO: Recreate link to old_operation_id, new_operation_id for mrp.eco.bom.change (module mrp_plm) via eco_id.bom_id
        other_updates = []
        if util.module_installed(cr, "mrp_workorder"):
            pass
            # TODO
            # other_updates.append("""
            # insert_new_quality_point AS (
            # )""")
        if util.module_installed(cr, "mrp_plm"):
            pass
            # TODO
            # other_updates.append("""
            # update_mrp_bom_line AS (
            # )""")
        cr.execute(
            """
            WITH old_operation AS (
                DELETE FROM mrp_routing_workcenter
                WHERE bom_id IS NULL
                RETURNING {column_op}, id AS old_id
            ), new_operation AS (
                INSERT INTO mrp_routing_workcenter ({column_op}, old_id, bom_id)
                    SELECT {column_op_pre}, old_id, mrp_bom.id
                    FROM old_operation INNER JOIN mrp_bom ON (mrp_bom.routing_id = old_operation.routing_id)
                RETURNING id, routing_id, old_id, bom_id
            ), update_mrp_bom_line AS (
                UPDATE mrp_bom_line
                SET operation_id=new_operation.id
                FROM new_operation
                WHERE mrp_bom_line.operation_id=new_operation.old_id AND new_operation.bom_id=mrp_bom_line.bom_id
            ), update_mrp_bom_byproduct AS (
                UPDATE mrp_bom_byproduct
                SET operation_id=new_operation.id
                FROM new_operation
                WHERE operation_id=new_operation.old_id AND new_operation.bom_id=mrp_bom_byproduct.bom_id
            ) {other_updates}
            UPDATE stock_move
            SET operation_id=new_operation.id
            FROM new_operation INNER JOIN mrp_production ON (new_operation.bom_id=mrp_production.bom_id)
            WHERE operation_id=new_operation.old_id AND mrp_production.id=stock_move.raw_material_production_id
        """.format(
                column_op=", ".join(column_op),
                column_op_pre=", ".join(column_op_pre),
                other_updates=",".join(other_updates),
            )
        )

    util.remove_column(cr, "mrp_routing_workcenter", "old_id")  # Working column

    util.remove_field(cr, "mrp.bom.line", "routing_id")
    util.remove_field(cr, "mrp.bom.byproduct", "routing_id")
    util.remove_field(cr, "mrp.production", "routing_id")
    util.remove_field(cr, "stock.move", "routing_id")
    util.remove_field(cr, "mrp.routing.workcenter", "routing_id")
    util.remove_field(cr, "mrp.bom", "routing_id")
    if util.module_installed(cr, "mrp_workorder"):
        util.remove_field(cr, "quality.point", "routing_ids")
        util.remove_field(cr, "quality.point", "routing_id")
        util.remove_field(cr, "mrp.workorder", "workorder_line_id")
    if util.module_installed(cr, "mrp_plm"):
        util.remove_field(cr, "mrp.eco", "new_routing_revision")
        util.remove_field(cr, "mrp.eco", "new_routing_id")
        util.remove_field(cr, "mrp.eco", "routing_id")

    util.remove_model(cr, "mrp.routing")

    util.rename_field(cr, "procurement.group", "mrp_production_id", "mrp_production_ids")
    util.create_column(cr, "mrp_production", "backorder_sequence", "int4", default=0)

    util.create_column(cr, "mrp_production", "lot_producing_id", "int4")
    util.create_column(cr, "mrp_production", "qty_producing", "float8")

    # IF qty_producing = 1 in mo AND product is tracked by serial/lot OR
    # IF qty_producing > 1 in mo AND product is tracked by lot and only one lot is used in finished move
    # => bind lot_producing_id of MO with the unique lot
    cr.execute(
        """
        WITH mo_lot_id AS (
            SELECT mrp_production.id as mo_id, array_agg(stock_production_lot.id) as lot_id
            FROM
                (
                    SELECT mrp_production.id AS id
                    FROM
                        mrp_production
                        INNER JOIN product_product ON mrp_production.product_id=product_product.id
                        INNER JOIN product_template ON product_product.product_tmpl_id=product_template.id
                    WHERE product_template.tracking in ('serial', 'lot')
                ) AS mrp_production
                INNER JOIN stock_move ON stock_move.production_id = mrp_production.id
                INNER JOIN stock_move_line ON stock_move_line.move_id = stock_move.id
                INNER JOIN stock_production_lot ON stock_move_line.lot_id = stock_production_lot.id
            GROUP BY mrp_production.id
            HAVING COUNT(DISTINCT stock_production_lot.id) = 1
        )
        UPDATE mrp_production
        SET lot_producing_id=mo_lot_id.lot_id[1]
        FROM mo_lot_id
        WHERE mrp_production.id=mo_lot_id.mo_id
    """
    )

    util.remove_view(cr, xml_id="mrp.view_stock_move_lots")
    util.remove_view(cr, xml_id="mrp.view_move_kanban_inherit_mrp")
    util.remove_view(cr, xml_id="mrp.view_finisehd_move_line")
    util.remove_view(cr, xml_id="mrp.view_stock_move_raw_tree")
    util.remove_field(cr, "stock.move.line", "lot_produced_ids")

    if util.module_installed(cr, "mrp_product_expiry"):
        util.remove_field(cr, "expiry.picking.confirmation", "produce_id")
        # TODO: It is better to add production_ids m2m table in migration ?
    if util.module_installed(cr, "mrp_subcontracting"):
        util.remove_view(cr, xml_id="mrp.mrp_subcontracting_move_tree_view")

    util.remove_model(cr, "mrp.product.produce.line")
    util.remove_model(cr, "mrp.product.produce")

    util.remove_field(cr, "mrp.production", "post_visible")

    cr.execute("UPDATE mrp_production SET state='confirmed' WHERE state='planned'")

    util.remove_menus(cr, [util.ref(cr, "mrp.menu_mrp_dashboard")])

    util.create_column(cr, "mrp_production", "production_location_id", "int4")

    util.create_column(cr, "res_config_settings", "group_locked_by_default", "bool")

    util.remove_field(cr, "mrp.production", "workorder_count")
    util.remove_field(cr, "mrp.production", "bom_has_operations")

    util.remove_field(cr, "mrp.workorder", "is_finished_lines_editable")
    util.remove_model(cr, "mrp.abstract.workorder")
    util.remove_model(cr, "mrp.abstract.workorder.line")

    # TODO : Fix Data
    if util.module_installed(cr, "mrp_workorder"):
        util.remove_field(cr, "quality.check", "workorder_line_id")
    util.remove_field(cr, "mrp.workorder", "raw_workorder_line_ids")
    util.remove_field(cr, "mrp.workorder", "finished_workorder_line_ids")
    util.remove_field(cr, "mrp.workorder", "allowed_lots_domain")
    util.remove_model(cr, "mrp.workorder.line")

    util.remove_record(cr, "mrp.sequence_mrp_route")
    util.remove_view(cr, xml_id="mrp.mrp_production_workorder_tree_view_inherit")
    if util.module_installed(cr, "mrp_plm"):
        util.remove_record(cr, "mrp_plm.mrp_eco_action_routing")
        util.remove_menus(cr, [util.ref(cr, "mrp_plm.menu_mrp_plm_routings")])
    if util.module_installed(cr, "mrp_workorder"):
        util.remove_view(cr, xml_id="mrp_workorder.mrp_workorder_view_tree_inherit_quality")
        util.remove_view(cr, xml_id="mrp_workorder.mrp_routing_view_form_inherit_quality")
