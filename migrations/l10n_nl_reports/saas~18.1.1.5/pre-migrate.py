from odoo.upgrade import util


def migrate(cr, version):
    util.move_model(cr, "l10n_nl.ec.sales.report.handler", "l10n_nl_intrastat", "l10n_nl_reports")

    util.rename_model(cr, "l10n_nl.ec.sales.report.handler", "l10n_nl_reports.ec.sales.report.handler")
    util.rename_model(cr, "l10n_nl.tax.report.handler", "l10n_nl_reports.tax.report.handler")
    util.rename_model(cr, "l10n_nl_reports_sbr.status.service", "l10n_nl_reports.sbr.status.service")
    util.rename_model(cr, "l10n_nl_reports_sbr.tax.report.wizard", "l10n_nl_reports.sbr.tax.report.wizard")
    util.rename_model(cr, "l10n_nl_reports_sbr_icp.icp.wizard", "l10n_nl_reports.sbr.icp.wizard")

    util.rename_xmlid(
        cr,
        "l10n_nl_reports.l10n_nl_reports_sbr_icp_icp_wizard_form",
        "l10n_nl_reports.l10n_nl_reports_sbr_icp_wizard_form",
    )

    util.remove_field(cr, "res.company", "l10n_nl_reports_sbr_password")
    util.remove_field(cr, "l10n_nl_reports.sbr.tax.report.wizard", "password")
    util.remove_field(cr, "l10n_nl_reports.sbr.icp.wizard", "password")
