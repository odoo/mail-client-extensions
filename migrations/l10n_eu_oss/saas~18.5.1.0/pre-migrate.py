from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_eu_oss.res_config_settings_view_form")
