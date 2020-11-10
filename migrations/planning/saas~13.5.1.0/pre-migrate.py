# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "default_planning_role_id", "int4")
    util.create_column(cr, "planning_slot", "template_reset", "boolean", default=False)
    util.create_column(cr, "planning_slot", "previous_template_id", "int4")

    util.remove_model(cr, "planning.slot.report.analysis")

    util.remove_view(cr, "planning.assets_common_planning")
    util.remove_view(cr, "planning.planning_view_gantt_inherit")
