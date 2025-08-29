import logging

from odoo.upgrade import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    if util.table_exists(cr, "l10n_in_gst_return_period"):
        _deduplicate_GST_return_periods(cr)


def _deduplicate_GST_return_periods(cr):
    cr.execute(
        """
        WITH duplicates AS (
            SELECT array_agg(
                    id
                    ORDER BY gstr1_status IN ('to_send', 'sending') AND
                             gstr2b_status IN ('not_received', 'waiting_reception'),
                             id
                    ) AS duplicates_ids
              FROM l10n_in_gst_return_period
             WHERE periodicity = 'monthly'
          GROUP BY company_id, year, month
            HAVING COUNT(*) > 1

            UNION

            SELECT array_agg(
                    id
                    ORDER BY gstr1_status IN ('to_send', 'sending') AND
                             gstr2b_status IN ('not_received', 'waiting_reception'),
                             id
                    ) AS duplicates_ids
              FROM l10n_in_gst_return_period
             WHERE periodicity = 'trimester'
          GROUP BY company_id, year, quarter
            HAVING COUNT(*) > 1
        )
        DELETE FROM l10n_in_gst_return_period p
              USING duplicates d
              WHERE p.id = ANY(d.duplicates_ids[1:])
                AND p.gstr1_status IN ('to_send', 'sending')
                AND p.gstr2b_status IN ('not_received', 'waiting_reception')
          RETURNING p.id, p.company_id, p.year, p.month, p.quarter
        """
    )
    data = cr.fetchall()
    if cr.rowcount:
        msg = """
        <details>
        <summary>
        Deleted the duplicate GST Return Periods with the same periodicity and time period for the same company.
        </summary>
        <ul>{}</ul>
        </details>
        """.format("\n".join("<li>Id={}, company_id={}, year={}, month={}, quarter={}</li>".format(*r) for r in data))
        util.add_to_migration_reports(msg, category="IN Accounting", format="html")
        _logger.warning("Removed duplicated GST return periods: %s", data)

    util.remove_constraint(cr, "l10n_in_gst_return_period", "l10n_in_gst_return_period_unique_period")
    cr.execute("UPDATE l10n_in_gst_return_period SET month = NULL WHERE periodicity = 'trimester'")
    cr.execute("UPDATE l10n_in_gst_return_period SET quarter = NULL WHERE periodicity = 'monthly'")
    util.change_field_selection_values(
        cr,
        "l10n_in.gst.return.period",
        "quarter",
        {"01": "03", "04": "06", "07": "09", "10": "12"},
    )
    cr.execute(
        """
        SELECT array_agg(id)
          FROM l10n_in_gst_return_period
         WHERE periodicity = 'monthly'
      GROUP BY company_id, year, month
        HAVING count(*)>1
        """
    )
    month_dup_ids = cr.fetchall()
    cr.execute(
        """
        SELECT array_agg(id)
          FROM l10n_in_gst_return_period
         WHERE periodicity = 'trimester'
      GROUP BY company_id, year, quarter
        HAVING count(*)>1
        """
    )
    quarter_dup_ids = cr.fetchall()
    if month_dup_ids or quarter_dup_ids:
        raise util.UpgradeError(
            f"Duplicated GST return periods found. Monthly: {month_dup_ids or 'none'}, Quarterly: {quarter_dup_ids or 'none'}"
        )
