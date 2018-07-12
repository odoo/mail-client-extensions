# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    modpat = "project_timesheet_forecast{_sale,}"
    eb = util.expand_braces
    util.move_field_to_module(cr, "project.forecast", "effective_hours", *eb(modpat))
    util.move_field_to_module(cr, "project.forecast", "percentage_hours", *eb(modpat))

    util.create_column(cr, "project_forecast", "working_days_count", "int4")

    util.rename_xmlid(cr, *eb(modpat + ".project_forecast_view_form_inherit_project_timesheet_forecast"))
    util.rename_xmlid(cr, *eb(modpat + ".project_forecast_view_pivot_inherit_project_timesheet_forecast"))
