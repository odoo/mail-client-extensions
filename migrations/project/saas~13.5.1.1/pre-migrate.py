# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "allow_recurring_tasks", "boolean")
    util.create_column(cr, "project_task", "recurring_task", "boolean")
    util.create_column(cr, "project_task", "recurrence_id", "int4")
