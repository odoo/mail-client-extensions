# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cleaned = util.ENVIRON["000_clean_imd"]
    if not cleaned:
        return
    cr.execute("""
        SELECT model, array_agg(res_id)
          FROM ir_model_data
         WHERE CONCAT(module, '.', name) IN %s
      GROUP BY model
    """, [tuple(cleaned)])
    for model, ids in cr.fetchall():
        table = util.table_of_model(cr, model)
        if util.column_exists(cr, table, "active"):
            cr.execute("UPDATE {} SET active = false WHERE id IN %s".format(table), [tuple(ids)])
