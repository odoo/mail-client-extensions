from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "event.mail_template_data_track_reminder", util.update_record_from_xml)
