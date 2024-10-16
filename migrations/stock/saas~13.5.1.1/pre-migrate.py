from odoo.upgrade import util


def migrate(cr, version):
    for table in ("stock_picking", "stock_move"):
        util.parallel_execute(
            cr,
            util.explode_query_range(
                cr,
                f"""
        UPDATE {table}
           SET priority = CASE WHEN priority IN ('2', '3')
                               THEN '1'
                               ELSE '0'
                          END
         WHERE (priority IN ('1', '2', '3') OR priority IS NULL)
           AND {{parallel_filter}}
                """,
                table=table,
            ),
        )

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
    UPDATE stock_move AS sm
       SET priority = sp.priority
      FROM stock_picking AS sp
     WHERE sm.picking_id = sp.id
            """,
            table="stock_move",
            alias="sm",
        ),
    )

    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
    UPDATE stock_move
       SET date = date_expected
     WHERE state NOT IN ('done', 'cancel')
            """,
            table="stock_move",
        ),
    )

    util.remove_field(cr, "stock.move", "date_expected")
    util.remove_field(cr, "stock.move", "delay_alert")
    util.remove_field(cr, "stock.move", "propagate_date")
    util.remove_field(cr, "stock.move", "propagate_date_minimum_delta")
    util.remove_field(cr, "stock.rule", "delay_alert")
    util.remove_field(cr, "stock.rule", "propagate_date")
    util.remove_field(cr, "stock.rule", "propagate_date_minimum_delta")

    util.remove_view(cr, xml_id="stock.stock_move_tree")
    util.remove_view(cr, xml_id="stock.view_move_picking_tree")
    util.remove_view(cr, xml_id="stock.stock_move_view_kanban")
    util.remove_view(cr, xml_id="stock.view_move_tree_receipt_picking_board")
    util.remove_view(cr, xml_id="stock.view_stock_move_kanban")

    util.rename_xmlid(cr, "stock.report_location_barcode", "stock.report_generic_barcode")
    util.force_noupdate(cr, "stock.report_picking_type_label", noupdate=False)

    util.create_column(cr, "stock_move", "date_deadline", "timestamp without time zone")
    util.create_column(cr, "stock_picking", "date_deadline", "timestamp without time zone")
    util.create_column(cr, "stock_picking", "has_deadline_issue", "boolean", default=False)
