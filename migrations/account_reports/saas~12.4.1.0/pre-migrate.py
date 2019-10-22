# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.financial.html.report", "cash_basis")

    util.remove_view(cr, "account_reports.search_template_multi_company")
