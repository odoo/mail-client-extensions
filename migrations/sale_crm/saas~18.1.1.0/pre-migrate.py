from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "target_sales_invoiced")
