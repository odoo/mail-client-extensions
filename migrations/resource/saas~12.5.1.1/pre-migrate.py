# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "resource_calendar", "two_weeks_calendar", "boolean")
    util.create_column(cr, "resource_calendar_attendance", "week_type", "varchar")
    util.create_column(cr, "resource_calendar_attendance", "display_type", "varchar")
    util.create_column(cr, "resource_calendar_attendance", "sequence", "int4")
    cr.execute("UPDATE resource_calendar_attendance SET sequence=10")
