from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead.convert2ticket", "ticket_type_id")
