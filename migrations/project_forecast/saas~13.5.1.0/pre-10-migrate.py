# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot", "parent_id", "int4")
    cr.execute(
        """
             UPDATE planning_slot s
                SET parent_id = t.parent_id
               FROM project_task t
              WHERE t.id = s.task_id
        """
    )
    util.create_column(cr, "res_config_settings", "group_project_forecast_display_allocate_time", "boolean")

    for view in {"gantt", "pivot", "graph", "grid"}:
        util.remove_view(cr, f"project_forecast.project_forecast_view_{view}")

    util.remove_record(cr, "project_forecast.planning_rule_project_adminis_published")

    actions = """
        analysis_pivot
        analysis_graph
        analysis_gantt
        analysis

        view_by_user_gantt
        by_user

        view_by_project_gantt
        by_project
    """

    for action in util.splitlines(actions):
        util.remove_record(cr, f"project_forecast.project_forecast_action_{action}")

    util.remove_menus(
        cr,
        [
            util.ref(cr, "project_forecast.project_forecast_report_activities"),
            util.ref(cr, "project_forecast.project_forecast_group_by_user"),
            util.ref(cr, "project_forecast.project_forecast_group_by_project"),
            util.ref(cr, "project_forecast.project_forecast_menu"),
        ],
    )
