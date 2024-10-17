from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.expense", "product_uom_category_id")
