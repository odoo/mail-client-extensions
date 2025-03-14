from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_timesheet.hr_timesheet_report_search_helpdesk")
