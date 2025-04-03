# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    queries = []
    cr.execute(
        """
        SELECT model, array_agg(res_id)
          FROM ir_model_data
          JOIN _upgrade_clean_imd USING(module, name)
      GROUP BY model
    """
    )
    for model, ids in util.log_progress(cr.fetchall(), util._logger, qualifier="models", size=cr.rowcount):
        table = util.table_of_model(cr, model)
        if util.column_exists(cr, table, "active"):
            queries.append(
                cr.mogrify(
                    util.format_query(cr, "UPDATE {} SET active = false WHERE id IN %s", table),
                    [tuple(ids)],
                ).decode()
            )
    if queries:
        util.parallel_execute(cr, queries)
    cr.execute("DROP TABLE _upgrade_clean_imd")
