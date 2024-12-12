from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "l10n_ee.tax_report_vat",
        "l10n_ee.tax_report",
    )

    if util.module_installed(cr, "l10n_ee_reports"):
        util.move_field_to_module(
            cr, "res.company", "l10n_ee_rounding_difference_loss_account_id", "l10n_ee_reports", "l10n_ee"
        )
        util.move_field_to_module(
            cr, "res.company", "l10n_ee_rounding_difference_profit_account_id", "l10n_ee_reports", "l10n_ee"
        )
