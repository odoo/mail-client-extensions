# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_company", "expense_extract_show_ocr_option_selection", "varchar")
    # When auto-installed via upgrade, do not send expenses to IAP
    cr.execute("UPDATE res_company SET expense_extract_show_ocr_option_selection = 'no_send'")
