# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "l10n_be_codabox_show_iap_token")
    util.remove_field(cr, "res.config.settings", "l10n_be_codabox_show_iap_token")
    util.remove_view(cr, "l10n_be_codabox.res_config_settings_view_form_codabox_bridge")
