from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~16.1", "17.0"):
        util.remove_record(cr, "l10n_fr_reports.account_financial_report_line_02_0_6_fr_bilan_passif_balance")
    if util.version_between("17.0", "19.0"):
        util.remove_view(cr, "l10n_fr_reports.inherit_view_account_journal_dashboard_kanban")
