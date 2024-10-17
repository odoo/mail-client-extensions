from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "approval.product.line", "product_uom_category_id")
