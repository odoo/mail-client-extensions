from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.transaction", "validation_route")
