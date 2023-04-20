# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE mrp_workcenter_capacity mwc
           SET time_start = mwc.time_start + mw.time_start,
               time_stop = mwc.time_stop + mw.time_stop
          FROM mrp_workcenter mw
         WHERE mwc.workcenter_id = mw.id
    """
    util.explode_execute(cr, query, table="mrp_workcenter_capacity", alias="mwc")
