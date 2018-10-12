# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.module_installed(cr, "hr_timesheet"):
        util.remove_field(cr, "res.company", "project_time_mode_id")
        util.remove_field(cr, "res.config.settings", "project_time_mode_id")
    else:
        util.move_field_to_module(cr, "res.config.settings", "project_time_mode_id", "project", "hr_timesheet")
