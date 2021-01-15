# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "event.action_report_event_registration_foldable_badge")
    util.update_record_from_xml(cr, "event.event_registration_mail_template_badge")
