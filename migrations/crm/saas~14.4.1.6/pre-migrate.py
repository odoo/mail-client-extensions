# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "crm.lead", "meeting_count", "calendar_event_count")
