# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.company", "extract_show_ocr_option_selection", "extract_in_invoice_digitalization_mode")
    util.create_column(cr, "res_company", "extract_out_invoice_digitalization_mode", "varchar")
    cr.execute(
        "UPDATE res_company SET extract_out_invoice_digitalization_mode = extract_in_invoice_digitalization_mode"
    )
    util.rename_field(
        cr, "res.config.settings", "extract_show_ocr_option_selection", "extract_in_invoice_digitalization_mode"
    )
