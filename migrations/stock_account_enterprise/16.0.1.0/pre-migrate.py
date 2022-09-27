# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed view
    util.remove_view(cr, "stock_account_enterprise.stock_report_dashboard_view_inherit")
