# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_column(cr, "account_invoice_send", "snailmail_cost")  # field is now computed
    # m2m field `letter_ids` has been removed but a o2m field with the same name is created indirectly via the inherits on mail.compose.message.
    cr.execute("DROP TABLE snailmail_letter_account_invoice_send_rel")
