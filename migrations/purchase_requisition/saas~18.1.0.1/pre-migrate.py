from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "purchase.requisition.line", "product_uom_category_id")
