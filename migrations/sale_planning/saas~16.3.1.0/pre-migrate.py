# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "sale_planning.planning_action_orders_planned")
    util.remove_record(cr, "sale_planning.planning_action_orders_planned_gantt")
    util.remove_view(cr, "sale_planning.planning_view_gantt_orders_planned")
