from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx.res_config_settings_view_form")
