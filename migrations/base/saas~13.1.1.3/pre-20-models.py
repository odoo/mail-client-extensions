# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(r"""
        UPDATE ir_model_data
           SET name = REPLACE(name, ' ', '_')
         WHERE name LIKE '% %'
    """)

    cr.execute("SELECT id FROM ir_ui_view WHERE type='diagram'")
    for vid, in cr.fetchall():
        util.remove_view(cr, view_id=vid)

    util.remove_field(cr, "ir.ui.view", "model_ids")

    # deduplicate properties
    cr.execute("""
       WITH dupes AS (
            SELECT unnest((array_agg(id ORDER BY id DESC))[2:]) as id
              FROM ir_property
          GROUP BY fields_id, COALESCE(company_id, 0), COALESCE(res_id, '')
            HAVING count(id) > 1
      )
      DELETE FROM ir_property p
            USING dupes d
            WHERE p.id = d.id
    """)
