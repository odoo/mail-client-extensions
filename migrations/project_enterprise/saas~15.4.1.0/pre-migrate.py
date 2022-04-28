# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "report.project.task.user", "planning_overlap", "industry_fsm", "project_enterprise")
