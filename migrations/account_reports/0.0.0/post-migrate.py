from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("16.0", "saas~18.3"):
        column = "line_id" if util.version_gte("saas~16.3") else "line"
        table = "account_report_annotation" if util.version_gte("saas~17.4") else "account_report_footnote"
        query = util.format_query(
            cr,
            """
            UPDATE {table}
               SET {column} = regexp_replace({column}, '(?<!-)-', '~', 'g')
             WHERE {column} LIKE '%-%'
            """,
            table=table,
            column=column,
        )
        util.explode_execute(cr, query, table=table)
