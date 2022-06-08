# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "project_task", "timesheet_timer_pause", "timestamp without time zone")
    util.rename_field(cr, "project.task", "use_timesheet_timer", "display_timesheet_timer")
