from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sign.sign_iap_credits_banner")
