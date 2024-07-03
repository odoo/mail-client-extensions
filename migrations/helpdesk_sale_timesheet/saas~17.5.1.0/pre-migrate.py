from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_sale_timesheet.view_helpdesk_sla_cohort_analysis")
    util.remove_view(cr, "helpdesk_sale_timesheet.view_helpdesk_ticket_cohort_analysis_2")
