# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # The field "name" is not translatable anymore, but the new field "title" is
    # and has the same value as "name", so to keep translations, we rename "name"
    # into "title" and create a new field, "name"
    util.rename_field(cr, "utm.campaign", "name", "title")
    util.create_column(cr, "utm_campaign", "name", "varchar")
    cr.execute(
        """
        UPDATE utm_campaign
           SET name = title
        """
    )

    for table in ("utm_campaign", "utm_medium", "utm_source"):
        cr.execute(
            f"""
            WITH duplicates AS (
              SELECT unnest((array_agg(id))[2:]) id
                    FROM {table}
                GROUP BY name
            )
            UPDATE {table} t
               SET name = CONCAT(t.name, ' [', t.id::text, ']')
              FROM duplicates d
             WHERE d.id = t.id
            """
        )

    cr.execute(
        """
       DELETE FROM ir_translation
        WHERE type = 'model_terms'
          AND name in ('utm.medium,name', 'utm.source,name')
        """,
    )
