# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "project_forecast.planning_slot_view_tree_project_user")
    util.remove_view(cr, "project_forecast.planning_slot_view_form_project_user")
