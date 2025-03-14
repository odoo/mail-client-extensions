from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "mail.mail_activity_data_meeting")
