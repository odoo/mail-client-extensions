# *-* coding:utf-8 *-*

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.payment", "display_qr_code")
    util.remove_field(cr, "account.payment", "qr_code_url")
    util.remove_view(cr, "account_sepa.view_account_payment_form_inherit_sepa")
