from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.sla.report.analysis", "analytic_account_id")
    util.remove_field(cr, "helpdesk.ticket.report.analysis", "analytic_account_id")
