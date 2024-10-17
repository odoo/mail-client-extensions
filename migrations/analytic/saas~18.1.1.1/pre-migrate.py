from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.analytic.line", "product_uom_category_id")
