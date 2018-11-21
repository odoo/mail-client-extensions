# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("mail.{mail_channel_action_client_chat,action_discuss}"))
    util.rename_xmlid(cr, *eb("mail.{mail_channel_menu_root_chat,menu_root_discuss}"))
