from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("saas~16.1", "17.0"):
        util.remove_record(cr, "l10n_fr_reports.account_financial_report_line_02_0_6_fr_bilan_passif_balance")
