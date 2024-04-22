from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_timesheet.view_helpdesk_ticket_pivot_analysis")
    util.remove_constraint(cr, "helpdesk_ticket_create_timesheet", "helpdesk_ticket_create_timesheet_time_positive")
