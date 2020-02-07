# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("CREATE TABLE _upgrade_clean_imd(module varchar, name varchar)")
    cr.execute("SELECT model FROM ir_model_data GROUP BY model")
    for model, in util.log_progress(cr.fetchall(), qualifier="models", size=cr.rowcount):
        table = util.table_of_model(cr, model)
        if util.table_exists(cr, table):
            cond = "NOT EXISTS (SELECT 1 FROM {} t WHERE t.id = d.res_id)".format(table)
        else:
            cond = "true"
        cr.execute("""
            WITH del AS (
                DELETE FROM ir_model_data d
                      WHERE model = %s
                        AND {}
                  RETURNING module, name
             )
            INSERT INTO _upgrade_clean_imd(module, name)
                 SELECT module,name
                   FROM del
        """.format(cond), [model])
