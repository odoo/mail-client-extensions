# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(
        """
        DELETE
          FROM ir_act_window_view AS map
         WHERE map.view_mode = 'grid'
           AND map.view_id IS NULL
        """
    )
    cr.execute("SELECT 1 FROM ir_ui_view WHERE type='grid' LIMIT 1")
    if not cr.rowcount:
        default = "list,form" if util.version_gte("saas~17.5") else "tree,form"
        cr.execute(
            """
            UPDATE ir_act_window act
               SET view_mode = COALESCE(
                    NULLIF(
                        ARRAY_TO_STRING(ARRAY_REMOVE(STRING_TO_ARRAY(view_mode, ','), 'grid'), ','),
                        '' -- Invalid value
                    ),
                   %s -- Default value
                )
             WHERE 'grid' = ANY(STRING_TO_ARRAY(act.view_mode, ','))
            """,
            [default],
        )
