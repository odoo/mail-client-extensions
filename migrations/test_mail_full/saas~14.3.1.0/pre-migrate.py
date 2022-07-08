# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # explicitly remove field from `mail.thread` inherit as test modules are ignored during the generation of `inherit.py`.
    for name in "portal sms sms.bl sms.bl.optout sms.partner sms.partner.2many".split():
        util.remove_field(cr, f"mail.test.{name}", "message_channel_ids")
