# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # removed view
    util.remove_view(cr, "event_sale_dashboard.event_sale_report_view_dashboard")
