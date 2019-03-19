# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "project_task", "timesheet_timer_start", "timestamp without time zone")
