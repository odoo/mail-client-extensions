from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "crm_helpdesk.helpdesk_ticket_view_form")
