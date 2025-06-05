"""
Save information to be later used in `end-resequence-custom-report-lines.py`.
"""

from odoo import modules

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("17.0"):  # account.report.line was introduced in Odoo 16
        # what is potentially jeopardized during the upgrade is the relative order between standard and custom lines
        # thus we only need to store ordering information about standard reports with custom lines.
        std_modules = tuple(modules.get_modules() + ["test_upg"])  # for testing purposes
        # Resequencing has been well tested for NL localization. This localization
        # is the one with support tickets, due to changes in the standard reports.
        # More localizations can be added here if we detect them failing as well.
        report_std_modules = (
            "l10n_ch",
            "l10n_ch_reports",
            "l10n_nl",
            "l10n_nl_reports",
            "test_upg",
        )
        cr.execute(
            """
            CREATE TEMPORARY VIEW ___std_reports_with_custom_lines AS (
                SELECT report.id
                  FROM account_report_line line
             LEFT JOIN ir_model_data imd_line
                    ON imd_line.res_id = line.id
                   AND imd_line.model = 'account.report.line'
                   AND imd_line.module IN %s
                  JOIN account_report report
                    ON report.id = line.report_id
                  JOIN ir_model_data imd_report
                    ON imd_report.res_id = report.id
                   AND imd_report.model = 'account.report'
                   AND imd_report.module IN %s
                 WHERE imd_line IS NULL
                 GROUP BY report.id
            )
            """,
            [std_modules, report_std_modules],
        )
        cr.execute(
            """
            CREATE UNLOGGED TABLE ___pre_upg_arl_order_info (id, rank) AS
                SELECT line.id,
                       ROW_NUMBER() OVER (
                           PARTITION BY line.report_id
                               ORDER BY line.sequence, line.id
                       )
                 FROM account_report_line line
                 JOIN ___std_reports_with_custom_lines report
                   ON report.id = line.report_id
            """
        )
