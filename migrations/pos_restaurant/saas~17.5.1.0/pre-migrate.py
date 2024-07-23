from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "restaurant_table", "table_number", "integer")

    cr.execute(
        r"""
        WITH upd AS (
             UPDATE restaurant_table
                SET table_number = name::integer
              WHERE name ~ '^\d+$'
          RETURNING table_number
        )
        SELECT COALESCE(MAX(table_number), 0) FROM upd
        """
    )

    offset = cr.fetchone()[0]

    cr.execute(
        """
             WITH numbered_rows AS (
                  SELECT id,
                         %s + ROW_NUMBER() OVER (ORDER BY id) AS new_number
                    FROM restaurant_table
                   WHERE table_number IS NULL
              )
           UPDATE restaurant_table
              SET table_number = numbered_rows.new_number
             FROM numbered_rows
            WHERE restaurant_table.id = numbered_rows.id
        RETURNING restaurant_table.id, restaurant_table.name, restaurant_table.table_number
        """,
        [offset],
    )

    res = cr.fetchall()
    if res:
        msg = """
        <details>
        <summary>
            Tables names have been changed to table numbers. Some of them were already numbers, they have been kept as is.
            For the others, they have been assigned a number starting from the highest existing number.
            Here are the tables for which an automatic number was assigned:
        </summary>
        <ul>
            {}
        </ul>
        </details>
        """.format(
            "\n        ".join(
                "<li>{} got the table number {}</li>".format(
                    util.get_anchor_link_to_record("restaurant.table", table_id, table_name),
                    table_number,
                )
                for table_id, table_name, table_number in res
            )
        )
        util.add_to_migration_reports(category="Restaurant", format="html", message=msg)

    util.remove_field(cr, "restaurant.table", "name")
