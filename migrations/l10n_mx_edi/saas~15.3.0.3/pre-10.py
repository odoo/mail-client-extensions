# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "account.move", "l10n_mx_edi_cancel_invoice_id", "l10n_mx_edi_cancel_move_id")
