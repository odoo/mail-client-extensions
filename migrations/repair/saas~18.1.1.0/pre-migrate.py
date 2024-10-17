from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "repair.order", "product_uom_category_id")
