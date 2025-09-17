from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies


def migrate(cr, version):
    inconsistencies.verify_products(cr, "stock.move", "stock.move.line", "move_id")
    inconsistencies.verify_uoms(cr, "stock.move", uom_field="product_uom")
    inconsistencies.verify_uoms(cr, "stock.move.line", uom_field="product_uom_id")
    with util.named_cursor(cr) as ncr:
        ncr.execute("SELECT id FROM stock_move")
        chunk = ncr.fetchmany(100000)  # avoid getting millions of ids
        while chunk:
            util.recompute_fields(cr, "stock.move", ["quantity_done"], ids=[i for (i,) in chunk], strategy="commit")
            chunk = ncr.fetchmany(100000)
