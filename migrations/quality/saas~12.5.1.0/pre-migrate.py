# -*- coding: utf-8 -*-


def migrate(cr, version):
    for table, field, foreign_table in [
        ("quality_point", "picking_type_id", "stock_picking_type"),
        ("quality_check", "team_id", "quality_alert_team"),
        ("quality_alert", "picking_id", "stock_picking"),
    ]:
        cr.execute(
            f"""
                UPDATE {table} t
                   SET company_id = o.company_id
                  FROM {foreign_table} o
                 WHERE o.id = t.{field}
                   AND t.company_id IS NULL
            """
        )
