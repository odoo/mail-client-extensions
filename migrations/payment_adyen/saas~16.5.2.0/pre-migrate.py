from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "payment_adyen.checkout")
    util.remove_view(cr, "payment_adyen.manage")
    util.remove_view(cr, "payment_adyen.sdk_assets")
