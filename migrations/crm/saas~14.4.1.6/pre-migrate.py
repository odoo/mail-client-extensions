# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "crm.lead", "description")
    util.rename_field(cr, "crm.lead", "meeting_count", "calendar_event_count")
