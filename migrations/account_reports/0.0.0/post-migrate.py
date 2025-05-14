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

    if util.version_between("saas~17.3", "saas~18.3"):
        cr.execute(
            """
            UPDATE account_report_column
               SET figure_type = 'monetary'
             WHERE id IN %s
               AND figure_type = 'string'
            """,
            [
                (
                    util.ref(cr, "account_reports.journal_report_credit"),
                    util.ref(cr, "account_reports.journal_report_balance"),
                ),
            ],
        )
