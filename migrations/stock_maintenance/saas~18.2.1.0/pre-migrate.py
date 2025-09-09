from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("CREATE INDEX idx_stock_location_name ON stock_location(name)")
    cr.execute("CREATE INDEX idx_maintenance_equipment_location ON maintenance_equipment(location)")

    # Field 'comment' removed in 'stock' 18.5
    has_comment = util.column_exists(cr, "stock_location", "comment")
    comment_col = ", comment" if has_comment else ""
    comment_args = ", '<p>Equipment location</p>'" if has_comment else ""
    query = util.format_query(
        cr,
        """
          INSERT INTO stock_location(name, complete_name, usage{})
          SELECT me.location, me.location, 'internal'{}
            FROM maintenance_equipment me
        LEFT JOIN stock_location sl
              ON sl.name = me.location
           WHERE me.location IS NOT NULL
             AND sl.id IS NULL
           GROUP BY me.location
        """,
        util.SQLStr(comment_col),
        util.SQLStr(comment_args),
    )
    cr.execute(query)
    util.create_column(
        cr, "maintenance_equipment", "location_id", "int", fk_table="stock_location", on_delete_action="SET NULL"
    )
    query = """
        UPDATE maintenance_equipment me
           SET location_id = sl.id
          FROM stock_location sl
         WHERE sl.name = me.location
    """
    util.explode_execute(cr, query, table="maintenance_equipment", alias="me")

    cr.execute("DROP INDEX idx_stock_location_name")
    cr.execute("DROP INDEX idx_maintenance_equipment_location")
