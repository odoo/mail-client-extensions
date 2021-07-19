# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE planning_slot slot
           SET sale_line_id = task.sale_line_id
          FROM project_task task
         WHERE slot.sale_line_id IS NULL
           AND task.id = slot.task_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="planning_slot", prefix="slot."))

    query = """
        UPDATE planning_slot slot
           SET sale_line_id = project.sale_line_id
          FROM project_project project
         WHERE slot.sale_line_id IS NULL
           AND project.id = slot.project_id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="planning_slot", prefix="slot."))

    query = """
        UPDATE planning_slot
           SET sale_order_id = sol.order_id
          FROM sale_order_line sol
         WHERE sale_line_id = sol.id
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="planning_slot"))
