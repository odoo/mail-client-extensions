from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_forecast.planning_analysis_report_view_search")
    util.remove_field(cr, "project.project", "allow_forecast")
    util.remove_field(cr, "planning.slot", "allow_forecast")
    util.remove_view(cr, "project_forecast.project_view_kanban_inherit_project_forecast")
    util.remove_view(cr, "project_forecast.project_project_view_form_simplified_inherit_forecast")
