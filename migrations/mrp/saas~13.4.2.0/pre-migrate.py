# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Migration for PR: odoo/odoo#52949 and odoo/enterprise#11149, task_id: 2241471
    util.create_column(cr, "mrp_routing_workcenter", "bom_id", "int4")
    util.create_column(cr, "mrp_routing_workcenter", "old_id", "int4")  # Working column

    # mrp.routing removing
    if util.column_exists(cr, "mrp_routing_workcenter", "routing_id"):

        # For PLM
        if util.module_installed(cr, "mrp_plm"):
            # Because `routing` won't exist anymore, routing type ECO should point to one (or multiple) BoM instead
            # to keep changing information of operations, multiple case:
            # (plm 1.) ECO of 'both' type
            #   => Only Change the type of ECO A 'both' into a 'bom' type, because the `new_bom_id`
            #      point to the `new_routing_id`
            # (plm 2.) ECO of 'routing' type:
            #   - (plm 2.A) if ECO is on state 'confirmed'
            #       => Duplicate the ECO for each bom using this routing
            #   - (plm 2.B) if ECO is in progress ('progress', 'rebase', 'conflict')
            #       => To avoid to lose this change, create a ECO and a BOM where routing is used.
            #          Note: it is not completely correct because we cannot know where this new routing will be
            #          used, then we can suppose it will replace it for each bom using the old one.
            #   - (plm 2.C) if ECO is 'done'
            #       => We should reconstruct a previous_bom to keep track of historic change
            #          Note: we cannot know if the routing_id of the bom has been changed before or after than the eco
            #          on the related routing has been made. In this situation, we create a "fake" historic,
            #          we prefer to get a inaccurate historic than none.
            # Note: We choose to avoid any lost information about routing ECO, but a other strategy could
            # be: remove all information about routing ECO, it would much more easier/cleaner technically. But we
            # consider ECO information important to track, even if it leads to duplicate some
            # information multiple times.

            # We should do this before any other mrp migration to keep the same logic than
            # for other routing (operations relink)
            util.create_column(cr, "mrp_eco", "old_eco_id", "int4")  # Working column
            util.create_column(cr, "mrp_bom", "old_bom_id", "int4")  # Working column
            column_eco, column_eco_pre = util.get_columns(
                cr,
                "mrp_eco",
                ignore=("id", "type", "product_tmpl_id", "bom_id", "new_bom_id", "old_eco_id"),
                extra_prefixes=["me"],
            )
            column_bom, column_bom_pre = util.get_columns(
                cr,
                "mrp_bom",
                ignore=("id", "version", "active", "previous_bom_id", "routing_id", "old_bom_id"),
                extra_prefixes=["mb"],
            )

            # (plm 1.)
            cr.execute(
                """
                UPDATE mrp_eco
                   SET type = 'bom',
                       routing_id = NULL,
                       new_routing_id = NULL
                 WHERE mrp_eco.type = 'both'
                """
            )

            cr.execute(
                """
                SELECT me.name
                  FROM mrp_eco AS me
                       JOIN mrp_bom AS mb ON mb.routing_id = me.routing_id
                 WHERE me.type = 'routing'
                   AND me.state != 'done'
             UNION ALL
                SELECT me.name
                  FROM mrp_eco AS me
                       JOIN mrp_bom AS mb ON mb.routing_id = me.new_routing_id
                 WHERE me.type = 'routing'
                   AND me.state = 'done'
                """
            )
            mrp_eco_transform = cr.fetchall()
            if mrp_eco_transform:
                util.add_to_migration_reports(
                    f"""
                        <details>
                        <summary>
                            Because Routing (Manufacturing) is gone in version 14,
                            {len(mrp_eco_transform)} Engineering Change Orders (ECO - PLM) applied on routing will
                            be duplicated and applied on new Bills of Material (BoM) instead.
                            For the already validated ECO, we have created a history of Bills of Material
                            related to the new routing (it can be inaccurate because we don't track `routing` in BoM).
                            For no-validated ECO, we have duplicated ECO for each Bill of Material
                            using the targeted routing.
                        </summary>
                        <h4>Impacted ECO</h4>
                            <ul>{", ".join(f"<li>{util.html_escape(name)}</li>" for name, in mrp_eco_transform)}</ul>
                        </details>
                    """,
                    "PLM",
                    format="html",
                )

            # (plm 2.A and B) for mrp_eco.state is not 'done'
            # For the 'confirmed', we don't create a new_bom_id
            cr.execute(
                """
                WITH inserted_new_bom AS (
                       INSERT INTO mrp_bom (
                              {column_bom},
                              version,
                              active,
                              previous_bom_id,
                              routing_id,
                              old_bom_id
                       )
                       SELECT {column_bom_pre},
                              mb.version + 1,
                              FALSE,
                              mb.id,
                              me.new_routing_id,
                              mb.id
                         FROM mrp_eco AS me
                              JOIN mrp_bom AS mb ON mb.routing_id = me.routing_id
                        WHERE me.state NOT IN ('confirmed', 'done')
                          AND me.type = 'routing'
                    RETURNING id, previous_bom_id, routing_id
                )
                INSERT INTO mrp_eco (
                       {column_eco},
                       type,
                       product_tmpl_id,
                       bom_id,
                       new_bom_id,
                       old_eco_id
                )
                SELECT {column_eco_pre},
                      'bom',
                       mb.product_tmpl_id,
                       mb.id,
                       inm.id,
                       me.id
                  FROM mrp_eco AS me
                       JOIN mrp_bom AS mb
                         ON mb.routing_id = me.routing_id
                       LEFT JOIN inserted_new_bom AS inm
                         ON inm.routing_id = me.new_routing_id
                        AND inm.previous_bom_id = mb.id
                 WHERE me.type = 'routing'
                """.format(
                    column_bom=", ".join(column_bom),
                    column_bom_pre=", ".join(column_bom_pre),
                    column_eco=", ".join(column_eco),
                    column_eco_pre=", ".join(column_eco_pre),
                )
            )
            # (plm 2.C) for mrp_eco.state = 'done'
            cr.execute(
                """
                WITH inserted_new_bom AS (
                        INSERT INTO mrp_bom (
                               {column_bom},
                               version,
                               active,
                               previous_bom_id,
                               routing_id,
                               old_bom_id
                        )
                        SELECT {column_bom_pre},
                               mb.version - 1,
                               FALSE,
                               NULL,
                               me.routing_id,
                               mb.id
                          FROM mrp_eco AS me
                               JOIN mrp_bom AS mb
                               ON mb.routing_id = me.new_routing_id
                         WHERE me.type = 'routing'
                           AND me.state = 'done'
                           AND me.create_date >= mb.create_date
                     RETURNING id, old_bom_id, routing_id
                )
                INSERT INTO mrp_eco (
                       {column_eco},
                       type,
                       product_tmpl_id,
                       bom_id,
                       new_bom_id,
                       old_eco_id
                )
                SELECT {column_eco_pre},
                       'bom',
                       mb.product_tmpl_id,
                       inm.id,
                       mb.id,
                       me.id
                  FROM mrp_eco AS me
                       JOIN mrp_bom AS mb
                         ON mb.routing_id = me.new_routing_id
                       LEFT JOIN inserted_new_bom AS inm
                         ON inm.routing_id = me.routing_id
                        AND inm.old_bom_id = mb.id
                 WHERE me.type = 'routing'
                   AND me.state = 'done'
                   AND me.create_date >= mb.create_date
                """.format(
                    column_bom=", ".join(column_bom),
                    column_bom_pre=", ".join(column_bom_pre),
                    column_eco=", ".join(column_eco),
                    column_eco_pre=", ".join(column_eco_pre),
                )
            )

            column_approval, column_approval_pre_1, column_approval_pre_2 = util.get_columns(
                cr,
                "mrp_eco_approval",
                ignore=("id", "eco_id"),
                extra_prefixes=["mrp_eco_approval", "delete_eco_approval"],
            )
            # Duplicate/Reassign ECO approvals on the duplicate ECO
            cr.execute(
                """
                WITH delete_eco_approval AS (
                        DELETE FROM mrp_eco_approval
                         USING mrp_eco
                         WHERE mrp_eco.old_eco_id = mrp_eco_approval.eco_id
                     RETURNING {column_approval_pre_1}, mrp_eco_approval.eco_id
                )
                INSERT INTO mrp_eco_approval ({column_approval}, eco_id)
                     SELECT {column_approval_pre_2}, me.id
                       FROM mrp_eco AS me
                            JOIN delete_eco_approval
                            ON me.old_eco_id = delete_eco_approval.eco_id
                      WHERE me.old_eco_id IS NOT NULL
                """.format(
                    column_approval=", ".join(column_approval),
                    column_approval_pre_1=", ".join(column_approval_pre_1),
                    column_approval_pre_2=", ".join(column_approval_pre_2),
                )
            )
            # Reassign product documents to the correct eco (`mrp.document`)
            cr.execute(
                """
                WITH mrp_document_to_update AS (
                    SELECT mp_old.id AS old_id, mp_new.id AS new_id
                      FROM mrp_eco AS mp_old
                           JOIN mrp_eco AS mp_new
                           ON mp_old.id = mp_new.old_eco_id
                           AND mp_old.product_tmpl_id = mp_new.product_tmpl_id
                )
                UPDATE ir_attachment
                   SET res_id = mrp_document_to_update.new_id
                  FROM mrp_document_to_update
                 WHERE ir_attachment.res_model = 'mrp.eco'
                   AND ir_attachment.res_id = mrp_document_to_update.old_id
                """
            )

            # Duplicate bom line and byproduct for the duplicate BoM
            column_bom_line, column_bom_line_pre = util.get_columns(
                cr,
                "mrp_bom_line",
                ignore=("id", "bom_id"),
                extra_prefixes=["mbl"],
            )
            column_bom_by_product, column_bom_by_product_pre = util.get_columns(
                cr,
                "mrp_bom_byproduct",
                ignore=("id", "bom_id"),
                extra_prefixes=["mbp"],
            )
            cr.execute(
                """
                INSERT INTO mrp_bom_line ({column_bom_line}, bom_id)
                     SELECT {column_bom_line_pre}, mb.id
                       FROM mrp_bom_line AS mbl
                            JOIN mrp_bom AS mb ON mb.old_bom_id = mbl.bom_id
                      WHERE mbl.bom_id IS NOT NULL
                """.format(
                    column_bom_line=", ".join(column_bom_line),
                    column_bom_line_pre=", ".join(column_bom_line_pre),
                )
            )
            cr.execute(
                """
                INSERT INTO mrp_bom_byproduct ({column_bom_by_product}, bom_id)
                     SELECT {column_bom_by_product_pre}, mb.id
                       FROM mrp_bom_byproduct AS mbp
                            JOIN mrp_bom AS mb ON mb.old_bom_id = mbp.bom_id
                      WHERE mbp.bom_id IS NOT NULL
                """.format(
                    column_bom_by_product=", ".join(column_bom_by_product),
                    column_bom_by_product_pre=", ".join(column_bom_by_product_pre),
                )
            )

            # Remove routing ECO (already duplicate)
            cr.execute("DELETE FROM mrp_eco WHERE type IN ('routing', 'both')")
            # Clean working columns
            util.remove_column(cr, "mrp_eco", "old_eco_id")
            util.remove_column(cr, "mrp_bom", "old_bom_id")

        column_op, column_op_pre = util.get_columns(
            cr, "mrp_routing_workcenter", ignore=("id", "bom_id", "old_id"), extra_prefixes=["old_operation"]
        )

        # For mrp.routing.workcenter:
        # 1) just set bom_id if there is only one bom_id linked to this operation
        cr.execute(
            """
            WITH operations AS (
                  SELECT rw.id AS id, unnest(array_agg(mb.id)) AS bom_id
                    FROM mrp_routing_workcenter rw
                    JOIN mrp_bom mb ON mb.routing_id = rw.routing_id
                GROUP BY rw.id
                  HAVING count(rw.id) = 1
            )
            UPDATE mrp_routing_workcenter rw
               SET bom_id = o.bom_id
              FROM operations o
             WHERE o.id = rw.id
            """
        )

        # 2) else:
        #    Duplicate the operation for each bom using related routing and link via bom_id and Delete old operations
        #    Recreate link to operation_id for mrp.bom.line via bom_id
        #    Recreate link to operation_id for mrp.bom.byproduct via bom_id
        #    Recreate link to operation_id for stock.move via raw_material_production_id
        #    In mrp_workorder: Recreate/Duplicate all quality point link to a operation
        #    In mrp_plm: Recreate link to old_operation_id, new_operation_id for mrp.eco.bom.change via eco_id.bom_id
        cr.execute(
            """
            WITH old_operation AS (
                SELECT {column_op}, id AS old_id
                  FROM mrp_routing_workcenter
                 WHERE bom_id IS NULL
            ),
            new_operation AS (
                INSERT INTO mrp_routing_workcenter ({column_op}, old_id, bom_id)
                SELECT {column_op_pre}, old_operation.old_id, mrp_bom.id
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

        cols, pre_cols = util.get_columns(cr, "ir_attachment", ignore=("id", "res_id"), extra_prefixes=["a"])
        update_queries = [
            """
            INSERT INTO ir_attachment({cols}, res_id)
            SELECT {pre_cols}, new_op.id
              FROM temp_new_mrp_operation new_op
              JOIN ir_attachment a ON a.res_id = new_op.old_id AND a.res_model = 'mrp.routing.workcenter'
            """.format(
                cols=", ".join(cols), pre_cols=", ".join(pre_cols)
            ),
            """
            UPDATE mrp_workorder wo
               SET operation_id = new_op.id
              FROM temp_new_mrp_operation AS new_op
              JOIN mrp_production mo ON mo.bom_id = new_op.bom_id
             WHERE wo.operation_id = new_op.old_id AND wo.production_id = mo.id
            """,
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
    util.remove_field(cr, "stock.move.line", "lot_produced_ids", drop_column=False)

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
