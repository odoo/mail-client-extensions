from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_sale_timesheet.portal_helpdesk_ticket_inherit")
