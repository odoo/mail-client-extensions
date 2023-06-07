# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_report_cash_basis.search_template_extra_options")
    util.remove_view(cr, "account_report_cash_basis.filter_cash_basis_template")
