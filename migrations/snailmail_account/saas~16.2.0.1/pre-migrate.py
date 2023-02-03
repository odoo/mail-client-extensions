# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "snailmail.confirm.invoice", "model_name")
    util.rename_xmlid(
        cr, "snailmail_account.snailmail_confirm_view", "snailmail_account.snailmail_confirm_invoice_view_form"
    )
