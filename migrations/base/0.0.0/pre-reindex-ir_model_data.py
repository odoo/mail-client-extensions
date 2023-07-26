# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.str2bool(os.getenv("UPG_NO_CLEAN_EXPORT_IMD", "0")):
        cr.execute(
            """
            WITH info AS (
                SELECT model,
                       count(*) AS rem
                  FROM ir_model_data
                 WHERE module = '__export__'
              GROUP BY model
                HAVING count(*) > 10000
            ),
            __ AS (
            DELETE FROM ir_model_data d
                  USING info
                  WHERE d.module = '__export__'
                    AND d.model = info.model
            )
            SELECT * FROM info
            """
        )
        if cr.rowcount:
            util._logger.info("Cleaned __export__ entries from ir_model_data: %s", cr.fetchall())

    if not util.str2bool(os.getenv("UPG_NO_REINDEX_IMD", "0")):
        cr.execute("REINDEX TABLE ir_model_data")
