from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "helpdesk.ticket.create.timesheet")
    util.remove_field(cr, "helpdesk.ticket", "display_timer_start_secondary")
    util.remove_field(cr, "helpdesk.ticket", "display_timer")
