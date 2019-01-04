# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "website.layout", False)
    util.remove_view(cr, "website.theme_customize")
    util.rename_xmlid(cr, 'website.menu_homepage','website.menu_home')
    """
    Ensure each website qweb view, and all their inherited views,
    have a key.
    """
    cr.execute(
        """
        WITH RECURSIVE qweb_views AS (
            SELECT v.id, v.key, CONCAT(x.module, '.', x.name) as xid
                FROM ir_ui_view v INNER JOIN
                   ir_model_data x ON (v.id = x.res_id AND x.model = 'ir.ui.view')
                WHERE x.module = 'website' and v.type='qweb'
                  AND (v.inherit_id IS NULL or v.mode='primary')

            UNION

            SELECT v.id, v.key, CONCAT(x.module, '.', x.name) as xid
                FROM ir_ui_view v
                JOIN qweb_views q ON q.id = v.inherit_id
                LEFT JOIN
                   ir_model_data x ON (v.id = x.res_id AND x.model = 'ir.ui.view' AND x.module !~ '^_')
        )
        UPDATE ir_ui_view v
           SET key = COALESCE(q.xid, CONCAT('_website_migration.view_', v.id))
          FROM qweb_views q
         WHERE q.id = v.id
           AND COALESCE(v.key, '') = ''
     """
    )
