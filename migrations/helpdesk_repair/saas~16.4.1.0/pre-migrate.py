from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "helpdesk_repair.repair_helpdesk_ticket_1", util.update_record_from_xml)
