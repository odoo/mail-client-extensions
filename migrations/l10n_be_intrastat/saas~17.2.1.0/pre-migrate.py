from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_be_intrastat.res_config_settings_view_form")
    util.move_field_to_module(
        cr, "res.config.settings", "intrastat_region_id", "l10n_be_intrastat", "account_intrastat"
    )
