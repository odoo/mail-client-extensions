# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "marketing.test", "message_channel_ids")
    util.remove_field(cr, "marketing.test.utm", "message_channel_ids")
    util.remove_field(cr, "marketing.test.sms", "message_channel_ids")
