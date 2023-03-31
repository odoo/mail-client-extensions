# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_reports.filter_info_template")
    util.remove_view(cr, "l10n_be_reports.sales_report_main_template")
    util.remove_view(cr, "l10n_be_reports.tax_report_main_template")
