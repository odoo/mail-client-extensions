from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("16.0", "saas~18.3"):
        table = "account_report_annotation" if util.version_gte("saas~17.4") else "account_report_footnote"
        query = util.format_query(
            cr,
            """
            UPDATE {table}
               SET line_id = regexp_replace(line_id, '(?<!-)-', '~', 'g')
             WHERE line_id LIKE '%-%'
            """,
            table=table,
        )
        util.explode_execute(cr, query, table=table)
