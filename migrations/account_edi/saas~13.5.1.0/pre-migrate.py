# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    if util.table_exists(cr, "account_edi_format"):
        util.create_column(cr, "account_edi_format", "has_web_service", "boolean", default=False)
    util.create_column(cr, "account_move", "edi_state", "varchar")

    util.remove_field(cr, "ir.attachment", "edi_format_id")
    util.remove_field(cr, "account.edi.format", "hide_on_journal")
