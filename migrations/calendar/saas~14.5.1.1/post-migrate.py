# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "calendar.calendar_template_meeting_invitation", util.update_record_from_xml)
    util.if_unchanged(cr, "calendar.calendar_template_meeting_changedate", util.update_record_from_xml)
    util.if_unchanged(cr, "calendar.calendar_template_meeting_reminder", util.update_record_from_xml)
    util.if_unchanged(cr, "calendar.calendar_template_meeting_update", util.update_record_from_xml)
