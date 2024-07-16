from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sign.cancel_sign_request_item_with_confirmation")
    util.remove_view(cr, "sign.canceled_sign_request_item")
