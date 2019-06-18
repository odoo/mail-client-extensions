# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_column(cr, "account_invoice_send", "snailmail_cost")  # field is now computed
    util.remove_field(cr, "account.invoice.send", "letter_ids")
    cr.execute("DROP TABLE snailmail_letter_account_invoice_send_rel")
