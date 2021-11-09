# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "event.action_report_event_registration_foldable_badge")

    rt = dict(reset_translations={"subject", "body_html", "report_name"})
    util.update_record_from_xml(cr, "event.event_registration_mail_template_badge", **rt)
    util.if_unchanged(cr, "event.event_subscription", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "event.event_reminder", util.update_record_from_xml, **rt)
