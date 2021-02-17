# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "group_project_task_dependencies", "boolean")
    util.create_column(cr, "project_project", "allow_task_dependencies", "boolean")
    util.create_m2m(cr, "task_dependencies_rel", "project_task", "project_task", "task_id", "depends_on_id")
