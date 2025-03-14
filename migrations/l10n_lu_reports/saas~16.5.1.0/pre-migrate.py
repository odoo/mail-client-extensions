from odoo.upgrade import util


def migrate(cr, version):
    for view in (
        "l10n_lu_annual_tax_report_template",
        "internal_layout",
        "view_l10n_lu_yearly_tax_report_manual_updated",
    ):
        util.remove_view(cr, f"l10n_lu_reports.{view}")
    util.remove_record(cr, "l10n_lu_reports.action_report_l10n_lu_tax_report")
