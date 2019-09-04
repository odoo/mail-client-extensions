# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_invoice", "extract_status_code", "int4")
    util.create_column(cr, "res_company", "extract_single_line_per_tax", "boolean")
    cr.execute("UPDATE res_company SET extract_single_line_per_tax=TRUE")

    # Do not send invoices to IAP during upgrade (reactivated in end- script)
    cr.execute("""
        SELECT extract_show_ocr_option_selection, id
          FROM res_company
         WHERE extract_show_ocr_option_selection != 'no_send'
    """)
    if cr.rowcount:
        util.ENVIRON["extract_show_ocr_option_selection"] = list(cr.fetchall())
        cr.execute("UPDATE res_company SET extract_show_ocr_option_selection = 'no_send'")
