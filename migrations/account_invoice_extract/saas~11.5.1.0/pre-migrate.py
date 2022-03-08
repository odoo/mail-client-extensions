# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_invoice", "extract_state", "varchar", default="no_extract_requested")
    util.create_column(cr, "account_invoice", "extract_remoteid", "int4")
    util.create_column(cr, "res_company", "extract_show_ocr_option_selection", "varchar", default="manual_send")
