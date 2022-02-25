# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "planning.planning_slot_report_view_form_in_gantt")
    util.remove_view(cr, "planning.planning_slot_report_view_gantt")
    util.remove_view(cr, "planning.planning_view_pivot")
    util.remove_view(cr, "planning.planning_view_graph")
    util.remove_record(cr, "planning.planning_slot_report_action_view_gantt")
