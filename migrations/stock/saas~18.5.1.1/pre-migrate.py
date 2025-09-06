from odoo.upgrade import util


def migrate(cr, version):
    query = "UPDATE stock_picking SET create_date = date WHERE create_date IS NULL AND date IS NOT NULL"
    util.explode_execute(cr, query, table="stock_picking")
    util.update_field_usage(cr, "stock.picking", "date", "create_date")
    util.remove_field(cr, "stock.picking", "date")
    if util.module_installed(cr, "stock_sms"):
        util.move_field_to_module(cr, "res.company", "stock_move_sms_validation", "stock_sms", "stock")
        util.rename_field(cr, "res.company", "stock_move_sms_validation", "stock_text_confirmation")

    util.rename_model(cr, "stock.quant.package", "stock.package")
    util.rename_xmlid(cr, "stock.view_quant_package_kanban", "stock.stock_package_view_kanban")
    util.rename_xmlid(cr, "stock.view_quant_package_tree", "stock.stock_package_view_list")
    util.rename_xmlid(cr, "stock.view_quant_package_form", "stock.stock_package_view_form")
    util.rename_xmlid(cr, "stock.quant_package_search_view", "stock.stock_package_view_search")
    util.rename_xmlid(cr, "stock.seq_quant_package", "stock.seq_package")
    util.rename_xmlid(cr, "stock.stock_quant_package_comp_rule", "stock.stock_package_comp_rule")
    util.rename_xmlid(cr, "stock.access_stock_quant_package_all", "stock.access_stock_package_all")
    util.rename_xmlid(cr, "stock.access_stock_quant_package_stock_manager", "stock.access_stock_package_stock_manager")
    util.rename_xmlid(cr, "stock.access_stock_quant_package_stock_user", "stock.access_stock_package_stock_user")
    util.rename_xmlid(cr, "stock.action_report_quant_package_barcode", "stock.action_report_package_barcode")
    util.rename_xmlid(
        cr, "stock.action_report_quant_package_barcode_small", "stock.action_report_package_barcode_small"
    )
    cr.execute("UPDATE ir_sequence SET code = 'stock.package' WHERE code = 'stock.quant.package'")

    util.create_column(cr, "stock_package_type", "package_use", "varchar", default="disposable")
    cr.execute("""
        WITH reusable_types AS (
                     SELECT sp.package_type_id AS type_id
                       FROM stock_package sp
                      WHERE sp.package_type_id IS NOT NULL
                        AND sp.package_use = 'reusable'
                   GROUP BY sp.package_type_id
        )
        UPDATE stock_package_type spt
           SET package_use = 'reusable'
          FROM reusable_types rt
         WHERE spt.id = rt.type_id
    """)
    util.remove_field(cr, "stock.move", "picking_type_entire_packs")
    util.remove_field(cr, "stock.move.line", "picking_type_entire_packs")
    util.remove_field(cr, "stock.picking", "has_packages")
    util.remove_field(cr, "stock.picking", "move_line_exist")
    util.remove_field(cr, "stock.package", "package_use")

    # compute new fields
    util.create_column(cr, "stock_package", "complete_name", "varchar")
    query = """
        UPDATE stock_package sp
           SET complete_name = sp.name
    """
    util.explode_execute(cr, query, table="stock_package", alias="sp")

    cr.execute(
        """
        SELECT spi.name,
               string_agg(spa.name, ', ' ORDER BY spa.name)
          FROM stock_package_level spl
          JOIN stock_picking spi
            ON spl.picking_id = spi.id
          JOIN stock_package spa
            ON spl.package_id = spa.id
     LEFT JOIN stock_move_line sml
            ON spl.id = sml.package_level_id
         WHERE sml.id IS NULL
           AND spi.state NOT IN ('cancel', 'done')
      GROUP BY spi.name
    """
    )
    if cr.rowcount:
        li = " ".join(
            f"<li>{util.html_escape(pick_name)}: {util.html_escape(pack_names)}</li>"
            for (pick_name, pack_names) in cr.fetchall()
        )
        util.add_to_migration_reports(
            f"""
            <details>
                <summary>
                    The following transfers had some entire packages assigned to them but still in a Draft state.
                    As this is no longer a valid state, these have been removed from their transfer.
                </summary>
                <ul>{li}</ul>
            </details>
            """,
            category="Inventory",
            format="html",
        )
    util.remove_field(cr, "stock.move", "package_level_id")
    util.remove_field(cr, "stock.move.line", "package_level_id")
    util.update_field_usage(cr, "stock.picking", "move_ids_without_package", "move_ids")
    util.remove_field(cr, "stock.picking", "move_ids_without_package")
    util.update_field_usage(cr, "stock.picking", "move_line_ids_without_package", "move_line_ids")
    util.remove_field(cr, "stock.picking", "move_line_ids_without_package")
    util.remove_field(cr, "stock.picking", "package_level_ids")
    util.remove_field(cr, "stock.picking", "package_level_ids_details")
    util.remove_model(cr, "stock.package_level")

    util.create_column(cr, "res_company", "horizon_days", "float8")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='stock.visibility_days' RETURNING CAST(value AS FLOAT)")
    visibility_days = cr.fetchone()[0] if cr.rowcount == 1 else 0
    if visibility_days > 0:
        util.create_column(cr, "res_company", "horizon_days", "float8", default=visibility_days)
    else:
        util.create_column(cr, "res_company", "horizon_days", "float8")
        po_lead = util.column_exists(cr, "res_company", "po_lead")
        manufacturing_lead = util.column_exists(cr, "res_company", "manufacturing_lead")
        cr.execute(
            util.format_query(
                cr,
                """
                UPDATE res_company
                    SET horizon_days = COALESCE(NULLIF({col}, 0), 365)
                """,
                col=util.SQLStr(
                    "GREATEST(po_lead, manufacturing_lead)"
                    if po_lead and manufacturing_lead
                    else "po_lead"
                    if po_lead
                    else "manufacturing_lead"
                    if manufacturing_lead
                    else "NULL"
                ),
            )
        )
    util.create_column(cr, "stock_warehouse_orderpoint", "deadline_date", "date")
    util.remove_field(cr, "stock.warehouse.orderpoint", "visibility_days")
    util.rename_field(cr, "stock.warehouse.orderpoint", "lead_days_date", "lead_horizon_date")
    util.rename_field(cr, "stock.replenishment.info", "json_replenishment_history", "json_replenishment_graph")

    util.remove_field(cr, "stock.request.count", "set_count")
    util.remove_view(cr, "stock.duplicated_sn_warning")
    util.remove_field(cr, "stock.location", "comment", drop_column=False)
    util.remove_field(cr, "stock.location", "scrap_location")
    util.update_field_usage(cr, "stock.move", "scrapped", "scrap_id")
    util.remove_field(cr, "stock.move", "scrapped")
    util.update_field_usage(cr, "stock.move.line", "is_scrap", "scrap_id")
    util.remove_field(cr, "stock.move.line", "is_scrap")
