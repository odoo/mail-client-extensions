# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    rt = dict(reset_translations={"subject", "body_html"})

    util.if_unchanged(cr, "calendar.calendar_template_meeting_invitation", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "calendar.calendar_template_meeting_changedate", util.update_record_from_xml, **rt)
    util.if_unchanged(cr, "calendar.calendar_template_meeting_reminder", util.update_record_from_xml, **rt)
