from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "payment_provider", "module_state")
