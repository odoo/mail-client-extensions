from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("{l10n_in_reports,l10n_in_asset}.view_l10n_in_asset_modify_form"))
    util.rename_xmlid(cr, *eb("{l10n_in_reports,l10n_in_asset}.view_l10n_in_account_asset_form"))
    util.move_field_to_module(cr, "account.asset", "l10n_in_value_residual", "l10n_in_reports", "l10n_in_asset")
    util.move_field_to_module(cr, "asset.modify", "l10n_in_value_residual", "l10n_in_reports", "l10n_in_asset")
    util.move_field_to_module(cr, "asset.modify", "l10n_in_fiscal_code", "l10n_in_reports", "l10n_in_asset")
