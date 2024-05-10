from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "stock_location", "replenish_location", "boolean")
    query = """
        UPDATE stock_location l
           SET replenish_location = true
          FROM stock_warehouse w
         WHERE l.id = w.lot_stock_id
           AND l.usage = 'internal'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_location", alias="l"))
    util.create_column(cr, "stock_location", "warehouse_id", "int4")

    query = """
        UPDATE stock_location l
           SET warehouse_id = w.id
          FROM stock_warehouse w
          JOIN stock_location sl ON sl.id = w.view_location_id
         WHERE l.parent_path LIKE sl.parent_path || '%'
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="stock_location", alias="l"))
    cr.execute(
        """
        UPDATE stock_location l
           SET replenish_location = false
          FROM stock_warehouse w
         WHERE l.id = w.lot_stock_id
           AND l.replenish_location = true
           AND l.warehouse_id IS DISTINCT FROM w.id
     RETURNING l.id,
               l.name,
               w.id,
               w.name
    """
    )
    locations_with_wrong_wh = cr.fetchall()
    if locations_with_wrong_wh:
        util.add_to_migration_reports(
            category="Stock Locations",
            message="The following stock locations have a mismatch between their assigned "
            "warehouse id, and the warehouse of their parent view location. They "
            "are automatically marked as non replenishment locations to avoid "
            "failure during the upgrade."
            "\nPlease review the hierarchy of the stock locations and make sure "
            "that the 'view' locations on the warehouses are correct.\n{}".format(
                "\n".join(
                    " - location id:{}, location name:{}, warehouse id:{}, warehouse name:{}".format(
                        id, name, w_id, w_name
                    )
                    for id, name, w_id, w_name in locations_with_wrong_wh
                )
            ),
        )

    util.remove_view(cr, "stock.stock_report_view_search")
    util.remove_menus(cr, [util.ref(cr, "stock.menu_forecast_inventory")])
    util.remove_record(cr, "stock.report_stock_quantity_action")
    util.remove_record(cr, "stock.report_stock_quantity_action_product")

    util.remove_field(cr, "res.config.settings", "stock_mail_confirmation_template_id")

    util.create_column(cr, "stock_move", "quantity_done", "float8")
