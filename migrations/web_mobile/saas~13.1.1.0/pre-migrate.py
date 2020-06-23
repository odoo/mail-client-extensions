# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "module_ocn_client")
    if util.module_installed(cr, "mail_mobile"):
        util.rename_xmlid(cr, *util.expand_braces("{web,mail}_mobile.res_config_settings_view_form"))
    else:
        util.remove_view(cr, "web_mobile.res_config_settings_view_form")
