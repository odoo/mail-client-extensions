# *-* coding:utf-8 *-*

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.payment", "display_qr_code")
    util.remove_field(cr, "account.payment", "qr_code_url")