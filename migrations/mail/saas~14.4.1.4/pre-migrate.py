# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "mail.compose.message", "no_auto_thread", "reply_to_force_new")
    util.rename_field(cr, "mail.message", "no_auto_thread", "reply_to_force_new")
