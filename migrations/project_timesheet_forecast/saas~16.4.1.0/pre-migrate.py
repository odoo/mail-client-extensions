# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_timesheet_forecast.planning_slot_view_search_inherit_project_timesheet_forecast")
