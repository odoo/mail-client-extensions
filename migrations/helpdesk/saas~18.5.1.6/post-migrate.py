from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "helpdesk.seq_helpdesk_ticket", util.update_record_from_xml)
