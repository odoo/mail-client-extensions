from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "helpdesk.new_ticket_request_email_template", util.update_record_from_xml)
