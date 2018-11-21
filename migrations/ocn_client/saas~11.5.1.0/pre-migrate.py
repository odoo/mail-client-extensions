# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "ocn_client.res_config_settings_view_form")
    util.remove_view(cr, "ocn_client.assets_backend")

    util.remove_field(cr, "res.config.settings", "mail_push_notification")
    util.remove_field(cr, "res.config.settings", "fcm_api_key")
    util.remove_field(cr, "res.config.settings", "fcm_project_id")
