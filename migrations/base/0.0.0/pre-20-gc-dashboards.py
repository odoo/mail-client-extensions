# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
            WITH old_dashboards(id) AS (
                SELECT unnest((array_agg(id ORDER BY create_date DESC))[2:])
                  FROM ir_ui_view_custom
              GROUP BY ref_id, user_id
            )
            DELETE FROM ir_ui_view_custom c
                  USING old_dashboards od
                  WHERE od.id = c.id
        """
    )
