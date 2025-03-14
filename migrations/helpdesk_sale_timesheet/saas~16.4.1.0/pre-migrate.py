from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_sale_timesheet.helpdesk_sla_view_search_inherit_sale_timesheet")
    util.remove_view(cr, "helpdesk_sale_timesheet.helpdesk_ticket_view_search_inherit_helpdesk_sale_timesheet")
