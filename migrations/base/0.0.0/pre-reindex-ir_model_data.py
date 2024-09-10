# -*- coding: utf-8 -*-
import os

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if not util.str2bool(os.getenv("UPG_NO_CLEAN_EXPORT_IMD", "0")):
        cr.execute(
            """
                SELECT model,
                       count(*) AS rem
                  FROM ir_model_data
                 WHERE module = '__export__'
              GROUP BY model
                HAVING count(*) > 10000
            """
        )
        if cr.rowcount:
            to_delete = cr.fetchall()
            qry = cr.mogrify(
                """
                DELETE FROM ir_model_data
                      WHERE module = '__export__'
                        AND model IN %s
                """,
                [tuple(t[0] for t in to_delete)],
            ).decode()
            util.explode_execute(cr, qry, table="ir_model_data")
            util._logger.info("Cleaned __export__ entries from ir_model_data: %s", to_delete)

    if not util.str2bool(os.getenv("UPG_NO_REINDEX_IMD", "0")):
        cr.execute("REINDEX TABLE ir_model_data")
