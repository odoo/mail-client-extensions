import html
import os

from odoo.upgrade import util


def migrate(cr, version):
    suffix = "_" + os.urandom(8).hex()  # Avoid collision when renaming

    cr.execute(
        """
        SELECT model, name
          FROM ir_model_fields
         WHERE ttype = 'properties'
           AND store = TRUE
        """,
    )

    updated = []
    for model, field_name in cr.fetchall():
        rowcount = util.explode_execute(
            cr,
            cr.mogrify(
                util.format_query(
                    cr,
                    """
      WITH to_update AS (
            SELECT l.id,
                   jsonb_object_agg(
                       REGEXP_REPLACE(j.key, '_html$', %s),
                       j.value
                   ) AS properties
              FROM {table} AS l, jsonb_each(l.{field_name}) AS j(key,value)
             WHERE l.{field_name} IS NOT NULL
               AND {{parallel_filter}}
          GROUP BY l.id
                   -- early filter to avoid unnecessary update
            HAVING bool_or(right(j.key, 5) = '_html')
     )
            UPDATE {table}
               SET {field_name} = l.properties
              FROM to_update AS l
             WHERE l.id = {table}.id
                """,
                    table=util.table_of_model(cr, model),
                    field_name=field_name,
                ),
                [suffix],
            ).decode(),
            table=util.table_of_model(cr, model),
            alias="l",
        )

        if rowcount:
            updated.append((model, field_name))

    cr.execute(
        """
        SELECT model, name
          FROM ir_model_fields
         WHERE ttype = 'properties_definition'
           AND store = TRUE
        """,
    )
    for model, field_name in cr.fetchall():
        util.explode_execute(
            cr,
            cr.mogrify(
                util.format_query(
                    cr,
                    """
      WITH to_update AS (
            SELECT l.id,
                   jsonb_agg(
                       definition || jsonb_build_object(
                           'name',
                           REGEXP_REPLACE(definition->>'name', '_html$', %s)
                       )
                   ) AS definitions
              FROM {table} AS l, jsonb_array_elements(l.{field_name}) AS definition
             WHERE l.{field_name} IS NOT NULL
               AND {{parallel_filter}}
          GROUP BY l.id
                   -- early filter to avoid unnecessary update
            HAVING bool_or(right(definition->>'name', 5) = '_html')
      )
            UPDATE {table}
               SET {field_name} = l.definitions
              FROM to_update AS l
             WHERE l.id = {table}.id
                """,
                    table=util.table_of_model(cr, model),
                    field_name=field_name,
                ),
                [suffix],
            ).decode(),
            table=util.table_of_model(cr, model),
            alias="l",
        )

    if updated:
        util.add_to_migration_reports(
            """
                <details>
                    <summary>
                        The following fields had "HTML tagged" properties (probably malicious) than have been renamed.
                    </summary>
                    <ul>{}</ul>
                </details>
            """.format(
                " ".join(
                    f"<li>Model: {html.escape(model)}, Field: {html.escape(field_name)}</li>"
                    for model, field_name in updated
                )
            ),
            category="Base",
            format="html",
        )
