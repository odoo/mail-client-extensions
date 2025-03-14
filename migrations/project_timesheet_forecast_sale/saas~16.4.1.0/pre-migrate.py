from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_timesheet_forecast_sale.project_update_default_description")
