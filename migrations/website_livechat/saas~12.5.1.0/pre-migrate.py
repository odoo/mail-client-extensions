# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "mail_channel", "livechat_visitor_id", "int4")
    util.create_column(cr, "mail_channel", "livechat_active", "boolean")
