# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # explicitly remove field from `mail.thread` inherit as test modules are ignored during the generation of `inherit.py`.
    for field in {"message_unread", "message_unread_counter"}:
        util.remove_field(cr, "marketing.test", field)
        util.remove_field(cr, "marketing.test.utm", field)
        util.remove_field(cr, "marketing.test.sms", field)
