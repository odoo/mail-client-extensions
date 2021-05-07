# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "calendar_contacts", "partner_checked", "bool", default=True)
    util.move_field_to_module(cr, "res.partner", "meeting_ids", "crm", "calendar")
    util.move_field_to_module(cr, "res.partner", "meeting_count", "crm", "calendar")
    util.convert_field_to_html(cr, "calendar.event", "description")
    util.force_noupdate(cr, "calendar.calendar_template_meeting_invitation", False)
    util.force_noupdate(cr, "calendar.calendar_template_meeting_changedate", False)
    util.force_noupdate(cr, "calendar.calendar_template_meeting_reminder", False)
