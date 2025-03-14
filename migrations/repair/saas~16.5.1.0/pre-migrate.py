from odoo.upgrade import util


def migrate(cr, version):
    # Renaming those 2 fields for easier reading
    util.rename_field(cr, "stock.lot", "repair_order_ids", "repair_line_ids")
    util.rename_field(cr, "stock.lot", "repair_order_count", "repair_part_count")
    util.remove_field(cr, "repair.order", "allowed_picking_type_ids")
    util.remove_field(cr, "stock.picking.type", "count_repair_waiting")
    util.remove_field(cr, "stock.picking.type", "count_repair_late")

    cr.execute(
        """
          UPDATE stock_picking_type
             SET is_repairable = False
           WHERE is_repairable IS NOT False
             AND id NOT IN (SELECT return_picking_type_id FROM stock_picking_type)
        """,
    )
