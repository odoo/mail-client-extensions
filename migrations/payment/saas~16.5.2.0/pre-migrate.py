from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.provider", "fees_active")
    util.remove_field(cr, "payment.provider", "fees_dom_fixed")
    util.remove_field(cr, "payment.provider", "fees_dom_var")
    util.remove_field(cr, "payment.provider", "fees_int_fixed")
    util.remove_field(cr, "payment.provider", "fees_int_var")
    util.remove_field(cr, "payment.provider", "support_fees")
    util.remove_field(cr, "payment.transaction", "fees")
