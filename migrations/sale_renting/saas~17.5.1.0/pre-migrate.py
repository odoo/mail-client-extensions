from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.rental.schedule", "analytic_account_id")
