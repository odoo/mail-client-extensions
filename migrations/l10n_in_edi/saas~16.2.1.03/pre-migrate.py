from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_in_edi.res_config_settings_view_form_l10n_in_inherit_l10n_in_edi")
