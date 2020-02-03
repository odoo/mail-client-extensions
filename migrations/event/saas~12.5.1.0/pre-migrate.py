# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.if_unchanged(cr, "event.event_registration_mail_template_badge", util.update_record_from_xml)
    util.if_unchanged(cr, "event.event_subscription", util.update_record_from_xml)
    util.if_unchanged(cr, "event.event_reminder", util.update_record_from_xml)
    util.env(cr)["mail.template"].flush()

    util.create_column(cr, "event_registration", "mobile", "varchar")
    util.create_column(cr, "event_type_mail", "notification_type", "varchar")
    cr.execute("UPDATE event_type_mail SET notification_type = 'mail'")
    util.create_column(cr, "event_mail", "notification_type", "varchar")
    cr.execute("UPDATE event_mail SET notification_type = 'mail'")
