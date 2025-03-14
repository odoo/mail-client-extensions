from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    for model in (
        "l10n_co_reports.certification_report",
        "l10n_co_reports.certification_report.ica",
        "l10n_co_reports.certification_report.iva",
        "l10n_co_reports.certification_report.fuente",
    ):
        util.remove_model(cr, model)
