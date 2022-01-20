# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    if util.module_installed(cr, "website_event_jitsi"):
        util.rename_xmlid(cr, *eb("website_{,event_}jitsi.res_config_settings_view_form"))
        util.move_field_to_module(cr, "res.config.settings", "jitsi_server_domain", *eb("website_{,event_}jitsi"))
    else:
        util.remove_view(cr, "website_jitsi.res_config_settings_view_form")
        util.remove_field(cr, "res.config.settings", "jitsi_server_domain")
