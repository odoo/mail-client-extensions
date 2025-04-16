from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "sale_order", "analytic_account_id")
