from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "mail.mail_activity_data_todo", util.update_record_from_xml)
