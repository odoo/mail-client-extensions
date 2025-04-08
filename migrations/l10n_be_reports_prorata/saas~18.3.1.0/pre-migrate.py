from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "l10n_be_reports_prorata.view_account_financial_report_export",
        "l10n_be_reports_prorata.vat_return_submission_wizard_form",
    )
