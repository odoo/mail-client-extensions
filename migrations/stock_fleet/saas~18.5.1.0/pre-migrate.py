from odoo.upgrade import util


def migrate(cr, version):
    util.create_m2m(cr, "dock_location_stock_picking_type_rel", "stock_picking_type", "stock_location")
    cr.execute(
        """
        INSERT INTO dock_location_stock_picking_type_rel (
            stock_picking_type_id,
            stock_location_id
        )
        SELECT
            spt.id,
            loc.id
          FROM stock_location loc
          JOIN stock_picking_type spt
            ON spt.company_id = loc.company_id
         WHERE loc.is_a_dock = True
           AND spt.dispatch_management = True;
        """
    )

    util.remove_field(cr, "stock.location", "is_a_dock")
    util.remove_view(cr, "stock_fleet.stock_location_tree_stock_fleet")
