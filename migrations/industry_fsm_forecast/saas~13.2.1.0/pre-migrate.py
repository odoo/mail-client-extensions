# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "allow_forecast", "boolean")
    cr.execute("UPDATE project_project SET allow_forecast = not is_fsm")
