from odoo.upgrade import util
from odoo.upgrade.util import inconsistencies


def migrate(cr, version):
    inconsistencies.verify_products(cr, "stock.move", "stock.move.line", "move_id")
    inconsistencies.verify_uoms(cr, "stock.move", uom_field="product_uom")
    inconsistencies.verify_uoms(cr, "stock.move.line", uom_field="product_uom_id")
    util.recompute_fields(cr, "stock.move", ["quantity_done"], strategy="commit")
