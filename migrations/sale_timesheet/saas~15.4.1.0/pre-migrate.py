# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.view_hr_timesheet_pivot_view_per_invoice")
    util.remove_view(cr, "sale_timesheet.timesheet_view_pivot_revenue")
