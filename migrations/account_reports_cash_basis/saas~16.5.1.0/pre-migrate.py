# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_reports_cash_basis.filter_extra_options_template_cash_basis")
