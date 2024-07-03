from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_timesheet.helpdesk_sla_analysis_cohort_view")
    util.remove_view(cr, "helpdesk_timesheet.view_helpdesk_ticket_cohort_analysis")
    util.remove_view(cr, "helpdesk_timesheet.helpdesk_ticket_view_cohort_inherit_helpdesk_timesheet")
