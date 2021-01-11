# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "project_forecast.view_task_tree2_planning")
