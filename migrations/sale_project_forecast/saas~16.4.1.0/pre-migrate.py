# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_project_forecast.planning_analysis_report_view_search_inherit_sale_project_forecast")
