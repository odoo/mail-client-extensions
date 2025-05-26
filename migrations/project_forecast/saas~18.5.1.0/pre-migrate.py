from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_forecast.resource_planning_project_forecast")
