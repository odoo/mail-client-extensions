from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.slot.template", "task_id")
    util.remove_field(cr, "project.task", "allow_forecast")
    util.remove_field(cr, "project.task", "forecast_hours")
    util.remove_field(cr, "planning.slot", "task_id")
    util.remove_field(cr, "planning.slot", "planned_hours")
    util.remove_field(cr, "planning.slot", "forecast_hours")
    util.remove_field(cr, "planning.slot", "parent_id")
    util.remove_constraint(cr, "planning_slot", "planning_slot_project_required_if_task")
    util.remove_field(cr, "planning.analysis.report", "task_id")
    util.remove_field(cr, "planning.analysis.report", "parent_id")
    util.remove_view(cr, "project_forecast.project_task_view_form")
    util.remove_record(cr, "project_forecast.action_project_task_view_planning")
