# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    # removed view
    util.remove_view(cr, "hr_recruitment_reports.hr_recruitment_report_view_dashboard")
    util.remove_view(cr, "hr_recruitment_reports.hr_recruitment_report_source_view_dashboard")
    util.remove_view(cr, "hr_recruitment_reports.hr_recruitment_report_team_view_dashboard")
    util.remove_view(cr, "hr_recruitment_reports.hr_recruitment_stage_report_view_dashboard")
