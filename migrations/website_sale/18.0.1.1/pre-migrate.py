from psycopg2 import sql

from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        util.format_query(
            cr,
            """
            WITH data AS (
                SELECT pt.id,
                       jsonb_object_agg(d.lang, {}) AS description_ecommerce
                  FROM product_template pt,
                       jsonb_each_text(pt.description_sale) d(lang, value)
                 WHERE description_ecommerce IS NULL
                   AND description_sale IS NOT NULL
              GROUP BY pt.id
                HAVING {{parallel_filter}}
            )
            UPDATE product_template pt
               SET description_ecommerce = data.description_ecommerce
              FROM data
             WHERE pt.id = data.id
            """,
            sql.SQL(util.pg_text2html("d.value")),
        ),
        table="product_template",
        alias="pt",
    )
