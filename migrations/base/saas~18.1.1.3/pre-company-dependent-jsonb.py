from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT name, model
          FROM ir_model_fields
         WHERE company_dependent = True
           AND ttype IN ('boolean', 'integer', 'float')
           AND store = True
        """
    )
    for field_name, model_name in cr.fetchall():
        table_name = util.table_of_model(cr, model_name)
        if not util.column_updatable(cr, table_name, field_name):
            continue
        util.explode_execute(
            cr,
            util.format_query(
                cr,
                """
                UPDATE {table_name}
                   SET {field_name} = NULLIF(
                           jsonb_strip_nulls({field_name}),
                           jsonb_build_object()
                       )
                 WHERE {field_name} IS NOT NULL
                   AND {field_name}::text LIKE '%null%'
                """,
                table_name=table_name,
                field_name=field_name,
            ),
            table=table_name,
        )
