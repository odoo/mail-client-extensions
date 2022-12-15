# -*- coding: utf-8 -*-
from odoo import modules


def migrate(cr, version):
    # Replace odoo.session_info with odoo.__session_info__
    # in all custom views and views with no xmlid
    standard_modules = set(modules.get_modules()) - {"studio_customization", "__export__"}
    cr.execute(
        r""" WITH v AS (
                SELECT v.id
                  FROM ir_ui_view v
             LEFT JOIN ir_model_data d ON d.res_id = v.id AND d.model = 'ir.ui.view'
                 WHERE v.arch_db ~ '\yodoo\.session_info\y'
              GROUP BY v.id
                HAVING NOT %s::varchar[] && array_agg(d.module)
                    OR min(d.id) IS NULL
            )
            UPDATE ir_ui_view iv
               SET arch_db = regexp_replace(arch_db, '\yodoo\.session_info\y', 'odoo.__session_info__', 'g')
              FROM v
             WHERE iv.id = v.id
            """,
        [list(standard_modules)],
    )
