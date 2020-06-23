# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot_template", "project_id", "integer")
    util.create_column(cr, "planning_slot_template", "task_id", "integer")
