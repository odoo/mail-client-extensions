from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE l10n_in_gst_return_period
           SET return_period_month_year = TO_CHAR(end_date::timestamp without time zone, 'MMYYYY')
        """,
        table="l10n_in_gst_return_period",
    )
