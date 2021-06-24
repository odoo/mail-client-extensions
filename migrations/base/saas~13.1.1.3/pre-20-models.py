# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Avoid unique constraint violations by suffixing the create date to the xmlid (tg-63)
    # (ok, there still can be conflicts, but they are less likely)
    cr.execute(
        r"""
        WITH conflictuals AS (
            SELECT unnest(array_agg(id) FILTER (WHERE name != new_name)) as id
              FROM (SELECT id, module, name, replace(name, ' ', '_') as new_name FROM ir_model_data) imd
          GROUP BY module, new_name
            HAVING count(id) > 1
        )
        UPDATE ir_model_data d
           SET name = replace(d.name, ' ', '_') || '_' || to_char(coalesce(d.date_init, d.create_date), 'J-SSSS-US')
          FROM conflictuals c
         WHERE d.id = c.id

    """
    )
    cr.execute(
        r"""
        UPDATE ir_model_data
           SET name = REPLACE(name, ' ', '_')
         WHERE name LIKE '% %'
    """
    )

    cr.execute("SELECT id FROM ir_ui_view WHERE type='diagram'")
    for (vid,) in cr.fetchall():
        util.remove_view(cr, view_id=vid)

    util.remove_field(cr, "ir.ui.view", "model_ids")

    # deduplicate properties
    cr.execute(
        """
       WITH dupes AS (
            SELECT unnest((array_agg(id ORDER BY id DESC))[2:]) as id
              FROM ir_property
          GROUP BY fields_id, COALESCE(company_id, 0), COALESCE(res_id, '')
            HAVING count(id) > 1
      )
      DELETE FROM ir_property p
            USING dupes d
            WHERE p.id = d.id
    """
    )
