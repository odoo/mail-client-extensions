# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_mail_channel.subscribe")
    util.remove_view(cr, "website_mail_channel.assets_editor")
