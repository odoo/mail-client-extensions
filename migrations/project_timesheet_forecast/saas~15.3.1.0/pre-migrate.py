# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE planning_slot s
           SET percentage_hours = s.percentage_hours * 100
         WHERE s.percentage_hours != 0
    """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="planning_slot", alias="s"))
