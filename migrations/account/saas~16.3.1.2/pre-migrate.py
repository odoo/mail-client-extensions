# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move.line", "tax_audit")
    util.rename_field(cr, "res.config.settings", "invoice_is_print", "invoice_is_download")
    util.rename_field(cr, "res.company", "invoice_is_print", "invoice_is_download")
    util.remove_record(cr, "account.action_automatic_entry")
    util.remove_field(cr, "account.move.reversal", "date_mode")
    util.remove_field(cr, "account.move.reversal", "refund_method")
