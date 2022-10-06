from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment_demo.verified_token_checkmark")
