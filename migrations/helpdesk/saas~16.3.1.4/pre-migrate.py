# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.sla.report.analysis", "successful_sla_rate")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "failed_sla_rate")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ongoing_sla_rate")
    util.remove_record(cr, "helpdesk.helpdesk_sla_report_analysis_filter_status_per_deadline")
    util.remove_record(cr, "helpdesk.helpdesk_sla_report_analysis_filter_stage_failed")
