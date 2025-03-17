from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "account_payment.payment_icon_menu", "account_payment.payment_method_menu")
