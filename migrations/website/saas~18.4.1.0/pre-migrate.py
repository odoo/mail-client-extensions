from odoo.upgrade import util


def migrate(cr, version):
    queries = []
    for inh in util.for_each_inherit(cr, "website.seo.metadata"):
        table = util.table_of_model(cr, inh.model)
        util.create_column(cr, table, "is_seo_optimized", "boolean", default=False)
        query = util.format_query(
            cr,
            """
            UPDATE {}
               SET is_seo_optimized = TRUE
             WHERE website_meta_title IS NOT NULL
               AND website_meta_description IS NOT NULL
               AND website_meta_keywords IS NOT NULL
            """,
            table,
        )
        queries.extend(util.explode_query_range(cr, query, table=table))

    if queries:
        util.parallel_execute(cr, queries)
