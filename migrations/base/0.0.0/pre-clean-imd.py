# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["000_clean_imd"] = cleaned = set()
    cr.execute("SELECT model FROM ir_model_data GROUP BY model")
    for model, in cr.fetchall():
        table = util.table_of_model(cr, model)
        if util.table_exists(cr, table):
            cond = "NOT EXISTS (SELECT 1 FROM {} t WHERE t.id = d.res_id)".format(table)
        else:
            cond = "true"
        cr.execute("""
            DELETE FROM ir_model_data d
                  WHERE model = %s
                    AND {}
              RETURNING CONCAT(module, '.', name)
        """.format(cond), [model])
        cleaned.update(x for x, in cr.fetchall())
