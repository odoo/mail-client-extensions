# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # explicitly remove field from `mail.thread` inherit as test modules are ignored during the generation of `inherit.py`.
    for name in "simple utm blacklist optout partner.unstored".split():
        util.remove_field(cr, f"mailing.test.{name}", "message_channel_ids")

    util.remove_field(cr, "mailing.performance", "message_channel_ids")
    util.remove_field(cr, "mailing.performance.blacklist", "message_channel_ids")
