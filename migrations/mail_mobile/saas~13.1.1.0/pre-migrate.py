# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "res_config_settings", "disable_redirect_firebase_dynamic_link", "boolean")
    util.create_column(cr, "res_config_settings", "enable_ocn", "boolean")

    util.env(cr)["ir.config_parameter"].set_param("mail_mobile.enable_ocn", True)
