# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # removed view
    util.remove_view(cr, "hr_referral.hr_recruitment_report_view_dashboard_inherit")
    util.remove_view(cr, "hr_referral.employee_referral_report_view_dashboard")
