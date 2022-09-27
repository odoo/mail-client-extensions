# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed view
    util.remove_view(cr, "hr_payroll.payroll_report_view_dashboard")
