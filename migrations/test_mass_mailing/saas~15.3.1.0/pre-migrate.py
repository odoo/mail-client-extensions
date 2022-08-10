# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # explicitly remove field from `mail.thread` inherit as test modules are ignored during the generation of `inherit.py`.
    for field in {"message_unread", "message_unread_counter"}:
        for name in "simple utm blacklist optout partner.unstored".split():
            util.remove_field(cr, f"mailing.test.{name}", field)

        util.remove_field(cr, "mailing.performance", field)
        util.remove_field(cr, "mailing.performance.blacklist", field)
