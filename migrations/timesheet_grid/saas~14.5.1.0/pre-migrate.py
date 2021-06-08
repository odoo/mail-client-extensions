# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "project.project", "allow_timesheet_timer")
    util.remove_view(cr, "timesheet_grid.project_view_form_inherit")
    util.remove_view(cr, "timesheet_grid.project_project_view_form_simplified_inherit")
