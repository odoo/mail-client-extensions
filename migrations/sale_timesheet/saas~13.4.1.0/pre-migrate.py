# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "sale_timesheet.ir_filter_project_profitability_report_manager_and_product")
