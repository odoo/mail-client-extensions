from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.location", "posx")
    util.remove_field(cr, "stock.location", "posy")
    util.remove_field(cr, "stock.location", "posz")
    util.create_column(cr, "stock_move", "inventory_name", "varchar")
    query = """
        UPDATE stock_move sm
           SET inventory_name = name
         WHERE is_inventory
           AND name NOT IN ('Product Quantity Updated', 'Product Quantity Confirmed')
    """
    util.explode_execute(cr, query, table="stock_move", alias="sm")
    util.remove_field(cr, "stock.move", "name")
    cr.execute("ALTER TABLE stock_move RENAME COLUMN description_picking TO description_picking_manual")
    util.make_field_non_stored(cr, "stock.move", "description_picking", selectable=False)
    util.make_field_non_stored(cr, "stock.move.line", "description_picking", selectable=False)
