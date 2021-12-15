from odoo.upgrade import util


def migrate(cr, version):
    query = """
            UPDATE ir_attachment
               SET theme_template_id = NULL
             WHERE original_id IS NOT NULL
            """

    util.parallel_execute(cr, util.explode_query_range(cr, query, table="ir_attachment"))
