from odoo.upgrade import util


def migrate(cr, version):
    # Remove DIOT menuitems as it now is a variant of the tax report.
    util.remove_record(cr, "l10n_mx_reports.action_account_report_diot")
    util.remove_menus(
        cr,
        [
            util.ref(cr, "l10n_mx_reports.account_reports_legal_mexican_statements_menu"),
            util.ref(cr, "l10n_mx_reports.menu_action_account_report_diot"),
        ],
    )
