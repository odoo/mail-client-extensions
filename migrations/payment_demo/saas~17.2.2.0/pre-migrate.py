from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment_demo.token_form")
    util.remove_view(cr, "payment_demo.payment_method_form")
