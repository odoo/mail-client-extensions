# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed view
    util.remove_view(cr, "mrp_account_enterprise.mrp_report_dashboard_view")
