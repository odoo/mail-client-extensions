# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "planning_slot_template", "sequence", "int4")
    util.create_column(cr, "planning_slot_template", "active", "bool", default=True)
    util.create_column(cr, "planning_role", "active", "bool", default=True)
    util.remove_field(cr, "planning.slot.template", "company_id")
    util.remove_record(cr, "planning.planning_action_my_gantt")
