from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "hr_timesheet.timesheet_line_rule_portal_user")
    util.update_record_from_xml(cr, "hr_timesheet.timesheet_line_rule_approver")
    util.update_record_from_xml(cr, "hr_timesheet.timesheet_line_rule_user")
    util.update_record_from_xml(cr, "hr_timesheet.timesheet_analysis_report_user")
    util.update_record_from_xml(cr, "hr_timesheet.timesheet_analysis_report_approver")
