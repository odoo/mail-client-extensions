# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_sale_timesheet.timesheet_view_search_inherit_timesheet_report_search")
