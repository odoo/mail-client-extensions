# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.table_exists(cr, "ir_translation"):
        cr.execute(
            r"""
            WITH src_pc AS (
                SELECT id, array_agg(pc) pc
                  FROM (
                    SELECT id,
                           replace((regexp_matches(src, '%(?:\([^)]+\))?[-# 0+]*\d*(?:\.\d+)?[hlL]?[diouxXeEfFgGcrs%]', 'g'))[1],
                                   ' ',
                                   '') AS pc
                      FROM ir_translation
                     WHERE type = 'code'
                  ) x
              GROUP BY id
            ),
            value_pc AS (
                SELECT id, array_agg(pc) pc
                  FROM (
                    SELECT id,
                           replace((regexp_matches(value, '%(?:\([^)]+\))?[-# 0+]*\d*(?:\.\d+)?[hlL]?[diouxXeEfFgGcrs%]', 'g'))[1],
                                   ' ',
                                   '') AS pc
                      FROM ir_translation
                     WHERE type = 'code'
                  ) x
              GROUP BY id
            )

            DELETE FROM ir_translation WHERE id IN (
                    SELECT t.id
                      FROM ir_translation t
                 LEFT JOIN src_pc s USING(id)
                 LEFT JOIN value_pc v USING(id)
                     WHERE s.pc IS DISTINCT FROM v.pc
                       AND t.type = 'code'
            )
        """
        )
