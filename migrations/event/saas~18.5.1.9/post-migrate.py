from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "event.event_registration_mail_template_badge", util.update_record_from_xml)
    util.if_unchanged(cr, "event.event_reminder", util.update_record_from_xml)
    util.if_unchanged(cr, "event.event_subscription", util.update_record_from_xml)
