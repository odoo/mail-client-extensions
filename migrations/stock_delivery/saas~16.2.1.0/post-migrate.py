from odoo.upgrade import util


def migrate(cr, version):
    if util.ENVIRON.get("stock_delivery_create_column"):
        # On a fresh install of stock_delivery in 16.2 we need to fill the column
        query = """
            UPDATE stock_move_line sml
               SET carrier_id = sp.carrier_id
              FROM stock_picking sp
             WHERE sml.picking_id = sp.id
               AND sp.carrier_id IS NOT NULL
        """
        util.explode_execute(cr, query, table="stock_move_line", alias="sml")
