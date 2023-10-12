# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "calendar.calendar_template_meeting_invitation", util.update_record_from_xml)
