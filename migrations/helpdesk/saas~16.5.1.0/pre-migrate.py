from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "helpdesk.ticket.report.analysis", "ticket_deadline", "sla_deadline")
