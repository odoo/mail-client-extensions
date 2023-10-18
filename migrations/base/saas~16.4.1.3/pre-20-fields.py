# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo.upgrade.util import expand_braces as eb


def migrate(cr, version):
    util.rename_field(cr, "res.partner", "display_name", "complete_name")

    if util.module_installed(cr, "mail"):
        util.move_model(cr, "res.users.settings", "mail", "base")
        # but keep some fields in mail
        for field in [
            "is_discuss_sidebar_category_channel_open",
            "is_discuss_sidebar_category_chat_open",
            "push_to_talk_key",
            "use_push_to_talk",
            "voice_active_duration",
            "volume_settings_ids",
        ]:
            util.move_field_to_module(cr, "res.users.settings", field, "base", "mail")
        # and views
        util.rename_xmlid(cr, *eb("{base,mail}.res_users_settings_view_form"))
        util.rename_xmlid(cr, *eb("{base,mail}.res_users_settings_view_tree"))

        util.move_field_to_module(cr, "res.users", "res_users_settings_ids", "mail", "base")
        util.move_field_to_module(cr, "res.users", "res_users_settings_id", "mail", "base")
