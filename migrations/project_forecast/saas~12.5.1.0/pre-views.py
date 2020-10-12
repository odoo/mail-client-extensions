# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("project_forecast.{project_forecast,planning_slot}_view_tree"))
    util.rename_xmlid(cr, *eb("project_forecast.{project_forecast,planning_slot}_view_form"))
    util.rename_xmlid(cr, *eb("project_forecast.{project_forecast,planning_slot}_view_search"))
