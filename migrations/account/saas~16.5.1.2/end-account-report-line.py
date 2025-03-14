from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE account_report_line
           SET user_groupby = groupby
         WHERE user_groupby IS NULL AND groupby IS NOT NULL
        """,
        table="account_report_line",
    )
