# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "mail.channel", "livechat_active", "website_livechat", "im_livechat")
