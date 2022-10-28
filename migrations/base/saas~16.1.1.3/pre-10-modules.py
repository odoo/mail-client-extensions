# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_module(cr, "project_timesheet_forecast_contract")
    util.remove_module(cr, "pos_cache")
