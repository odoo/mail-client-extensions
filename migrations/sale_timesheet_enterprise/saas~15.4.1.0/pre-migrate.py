# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet_enterprise.timesheet_action_view_report_by_billing_rate_grid")
