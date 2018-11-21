# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record_if_unchanged(cr, "calendar.calendar_template_meeting_invitation")
    util.remove_record_if_unchanged(cr, "calendar.calendar_template_meeting_changedate")
    util.remove_record_if_unchanged(cr, "calendar.calendar_template_meeting_reminder")
