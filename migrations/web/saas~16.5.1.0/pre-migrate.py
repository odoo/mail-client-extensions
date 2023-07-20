# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "res.config.settings", "web_app_name", "web_enterprise", "web")
    cr.execute(
        """
            UPDATE ir_config_parameter
               SET "key" = 'web.web_app_name'
             WHERE "key" = 'web_enterprise.web_app_name'
        """
    )

    util.rename_xmlid(cr, "web_enterprise.webclient_offline", "web.webclient_offline", on_collision="merge")
