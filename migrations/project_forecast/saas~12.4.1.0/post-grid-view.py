# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("UPDATE res_company SET forecast_default_view = 'grid'")

    grid_views = (
        util.ref(cr, "project_forecast.project_forecast_action_view_by_user_grid"),
        util.ref(cr, "project_forecast.project_forecast_action_view_by_project_grid"),
    )

    gantt_views = (
        util.ref(cr, "project_forecast.project_forecast_action_view_by_user_gantt"),
        util.ref(cr, "project_forecast.project_forecast_action_view_by_project_gantt"),
    )

    cr.execute("UPDATE ir_act_window_view SET sequence = 1 WHERE id IN %s", [grid_views])
    cr.execute("UPDATE ir_act_window_view SET sequence = 2 WHERE id IN %s", [gantt_views])
