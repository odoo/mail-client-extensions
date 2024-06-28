from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "crm_helpdesk.helpdesk_ticket_to_lead_action")
