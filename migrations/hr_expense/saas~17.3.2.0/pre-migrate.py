from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "expense_product_id")
    util.remove_field(cr, "res.company", "expense_product_id")
