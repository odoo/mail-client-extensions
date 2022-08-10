# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # explicitly remove field from `mail.thread` inherit as test modules are ignored during the generation of `inherit.py`.
    util.remove_field(cr, "mail.test.activity.bl.sms.voip", "message_unread")
    util.remove_field(cr, "mail.test.activity.bl.sms.voip", "message_unread_counter")
