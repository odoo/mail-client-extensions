# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "base.user_groups_view", silent=True)

    cr.execute(
        """
        WITH xids AS (
            SELECT v.id,
                   COALESCE(
                        x.module || '.' || x.name,
                        md5(random()::varchar || v.id::varchar || clock_timestamp()::varchar)::uuid::varchar
                   ) as xid
              FROM ir_ui_view v
         LEFT JOIN ir_model_data x ON (x.res_id = v.id AND x.model = 'ir.ui.view')
             WHERE v.type = 'qweb'
               AND v.key IS NULL
        )
        UPDATE ir_ui_view v
           SET key = x.xid
          FROM xids x
         WHERE x.id = v.id
    """
    )

    # Due to bootstrap 4, force update of all qweb views with a known xmlid
    cr.execute(
        """
        UPDATE ir_model_data d
           SET noupdate = false
          FROM ir_ui_view v
         WHERE d.model = 'ir.ui.view'
           AND d.res_id = v.id
           AND COALESCE(d.module, '') NOT IN ('', '__export__')
           AND v.type = 'qweb'
    """
    )

    if util.module_installed(cr, "website"):
        cr.execute(
            """
            UPDATE ir_model_data d
               SET noupdate = True
              FROM website_page w
             WHERE d.model = 'ir.ui.view'
               AND d.module = 'website'
               AND d.res_id = w.view_id
               AND w.url = '/page/'|| d.name
            """
        )
