from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_co_pos.res_config_settings_view_form")
