# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed view
    util.remove_view(cr, "purchase_enterprise.purchase_report_view_dashboard")
