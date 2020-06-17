# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Migration for PR: odoo/odoo#52949 and odoo/enterprise#11149, task_id: 2241471
    util.create_column(cr, "mrp_routing_workcenter", "bom_id", "int4")
    util.create_column(cr, "mrp_routing_workcenter", "old_id", "int4")  # Working column

    # mrp.routing removing
    if util.column_exists(cr, "mrp_routing_workcenter", "routing_id"):
        column_op, column_op_pre = util.get_columns(
            cr, "mrp_routing_workcenter", ignore=("id", "bom_id", "old_id"), extra_prefixes=["old_operation"]
        )
        # For mrp.routing.workcenter: duplicate operation for each bom using related routing and link via bom_id
        # And Delete old operations
        # Recreate link to operation_id for mrp.bom.line via bom_id
        # Recreate link to operation_id for mrp.bom.byproduct via bom_id
        # Recreate link to operation_id for stock.move via raw_material_production_id
        # In mrp_workorder: Recreate/Duplicate all quality point link to a operation
        # In mrp_plm: Recreate link to old_operation_id, new_operation_id for mrp.eco.bom.change via eco_id.bom_id
        cr.execute(
            """
            WITH old_operation AS (
                SELECT {column_op}, id AS old_id
                  FROM mrp_routing_workcenter
                 WHERE bom_id IS NULL
            ),
            new_operation AS (
                INSERT INTO mrp_routing_workcenter ({column_op}, old_id, bom_id)
                SELECT {column_op_pre}, old_id, mrp_bom.id
                  FROM old_operation
                       JOIN mrp_bom ON mrp_bom.routing_id = old_operation.routing_id
              ORDER BY sequence, old_id
             RETURNING id, routing_id, old_id, bom_id
            )
            SELECT *
              INTO temp_new_mrp_operation
              FROM new_operation
            """.format(
                column_op=", ".join(column_op), column_op_pre=", ".join(column_op_pre)
            )
        )
        update_queries = [
            """
            UPDATE mrp_bom_line
               SET operation_id = new_op.id
              FROM temp_new_mrp_operation AS new_op
             WHERE mrp_bom_line.operation_id = new_op.old_id AND new_op.bom_id = mrp_bom_line.bom_id
            """,
            """
            UPDATE mrp_bom_byproduct
               SET operation_id = new_op.id
              FROM temp_new_mrp_operation AS new_op
             WHERE mrp_bom_byproduct.operation_id = new_op.old_id AND new_op.bom_id = mrp_bom_byproduct.bom_id
            """,
            """
            UPDATE stock_move
               SET operation_id = new_op.id
              FROM temp_new_mrp_operation AS new_op
              JOIN mrp_production ON new_op.bom_id = mrp_production.bom_id
             WHERE stock_move.operation_id = new_op.old_id AND mrp_production.id = stock_move.raw_material_production_id
            """,
        ]
        util.parallel_execute(cr, update_queries)

    # Remove all link to a mrp.routing and remove the model
    util.remove_field(cr, "mrp.bom.line", "routing_id")
    util.remove_field(cr, "mrp.bom.byproduct", "routing_id")
    util.remove_field(cr, "mrp.production", "routing_id")
    util.remove_field(cr, "stock.move", "routing_id")
    util.remove_field(cr, "mrp.routing.workcenter", "routing_id")
    util.remove_field(cr, "mrp.bom", "routing_id")
    # Remove custom target fields
    for table, col, _, _ in util.get_fk(cr, util.table_of_model(cr, "mrp.routing")):
        util.remove_field(cr, util.model_of_table(cr, table), col)
    util.remove_model(cr, "mrp.routing", drop_table=False)

    util.rename_field(cr, "procurement.group", "mrp_production_id", "mrp_production_ids")
    util.create_column(cr, "mrp_production", "backorder_sequence", "int4", default=0)

    util.create_column(cr, "mrp_production", "lot_producing_id", "int4")
    util.create_column(cr, "mrp_production", "qty_producing", "float8")

    # IF qty_producing = 1 in mo AND product is tracked by serial/lot OR
    # IF qty_producing > 1 in mo AND product is tracked by lot and only one lot is used in finished move
    # => Bind lot_producing_id of MO with the unique lot (new paradigm, 1 MO = 1 Finished lot/serial)
    cr.execute(
        """
        WITH mo_lot_id AS (
            SELECT mrp_production.id AS mo_id, min(stock_production_lot.id) AS lot_id
              FROM mrp_production
                   JOIN product_product ON mrp_production.product_id = product_product.id
                   JOIN product_template ON product_product.product_tmpl_id = product_template.id
                   JOIN stock_move ON stock_move.production_id = mrp_production.id
                   JOIN stock_move_line ON stock_move_line.move_id = stock_move.id
                   JOIN stock_production_lot ON stock_move_line.lot_id = stock_production_lot.id
             WHERE product_template.tracking IN ('serial', 'lot')
          GROUP BY mrp_production.id
            HAVING COUNT(DISTINCT stock_production_lot.id) = 1
        )
        UPDATE mrp_production
           SET lot_producing_id = mo_lot_id.lot_id
          FROM mo_lot_id
         WHERE mrp_production.id = mo_lot_id.mo_id
        """
    )

    util.remove_view(cr, xml_id="mrp.view_stock_move_lots")
    util.remove_view(cr, xml_id="mrp.view_move_kanban_inherit_mrp")
    util.remove_view(cr, xml_id="mrp.view_finisehd_move_line")
    util.remove_view(cr, xml_id="mrp.view_stock_move_raw_tree")
    util.remove_field(cr, "stock.move.line", "lot_produced_ids")

    if util.module_installed(cr, "mrp_product_expiry"):
        util.remove_field(cr, "expiry.picking.confirmation", "produce_id")
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

    util.create_column(cr, "mrp_workorder", "product_id", "int4")
    util.create_column(cr, "mrp_workorder", "consumption", "varchar")

    util.remove_field(cr, "mrp.workorder", "raw_workorder_line_ids")
    util.remove_field(cr, "mrp.workorder", "finished_workorder_line_ids")
    util.remove_field(cr, "mrp.workorder", "allowed_lots_domain")
    util.remove_model(cr, "mrp.workorder.line", drop_table=False)

    util.remove_record(cr, "mrp.sequence_mrp_route")
    util.remove_view(cr, xml_id="mrp.mrp_production_workorder_tree_view_inherit")
