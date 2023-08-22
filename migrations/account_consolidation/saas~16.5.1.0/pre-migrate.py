# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_consolidation.consolidation_report_pdf_export_main_table_header")
    util.remove_view(cr, "account_consolidation.consolidation_report_pdf_export_line")
