from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT model, name FROM ir_model_fields WHERE ttype = 'properties_definition' and store = true")
    for model_name, field_name in cr.fetchall():
        table_name = util.table_of_model(cr, model_name)
        if not util.column_updatable(cr, table_name, field_name):
            continue
        util.explode_execute(
            cr,
            util.format_query(
                cr,
                """
                UPDATE {table_name}
                   SET {field_name} = (
                            SELECT jsonb_agg(
                                CASE
                                    WHEN elem->>'type' = 'tags' THEN elem - ARRAY['comodel', 'domain', 'selection']
                                    WHEN elem->>'type' = 'selection' THEN elem - ARRAY['comodel', 'domain', 'tags']
                                    WHEN elem->>'type' IN ('many2one', 'many2many') THEN elem - ARRAY['selection', 'tags']
                                    ELSE elem - ARRAY['comodel', 'domain', 'tags', 'selection']
                                END)
                            FROM jsonb_array_elements({field_name}) AS elem
                        )
                WHERE {field_name} IS NOT NULL
                """,
                table_name=table_name,
                field_name=field_name,
            ),
            table=table_name,
        )
