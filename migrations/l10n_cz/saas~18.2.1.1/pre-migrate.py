from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "l10n_cz_reports"):
        util.move_field_to_module(cr, "res.company", "l10n_cz_tax_office_id", "l10n_cz_reports", "l10n_cz")
        util.move_model(cr, "l10n_cz.tax_office", "l10n_cz_reports", "l10n_cz", move_data=True)
