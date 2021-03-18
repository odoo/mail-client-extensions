# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # reset mail templates (rendering context changed)
    util.update_record_from_xml(cr, "calendar.calendar_template_meeting_invitation")
    util.update_record_from_xml(cr, "calendar.calendar_template_meeting_changedate")
    util.update_record_from_xml(cr, "calendar.calendar_template_meeting_reminder")
