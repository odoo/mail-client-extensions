from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_nl_reports_sbr"):
        util.move_model(cr, "l10n_nl.tax.report.handler", "l10n_nl_reports", "l10n_nl_reports_sbr")
    else:
        util.remove_model(cr, "l10n_nl.tax.report.handler")
