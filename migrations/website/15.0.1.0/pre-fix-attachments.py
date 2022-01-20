from odoo.upgrade import util


def migrate(cr, version):

    # Column check intended to handle databases from 13.x that have website_theme_install uninstalled
    if util.column_exists(cr, "ir_attachment", "theme_template_id"):
        query = """
                UPDATE ir_attachment
                   SET theme_template_id = NULL
                 WHERE original_id IS NOT NULL
                """

        util.parallel_execute(cr, util.explode_query_range(cr, query, table="ir_attachment"))
