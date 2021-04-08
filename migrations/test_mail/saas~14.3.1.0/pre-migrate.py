# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # explicitly remove field from `mail.thread` inherit as test modules are ignored during the generation of `inherit.py`.
    for name in "cc multi.company track.monetary track.compute container ticket activity track gateway simple".split():
        util.remove_field(cr, f"mail.test.{name}", "message_channel_ids")

    util.remove_field(cr, "mail.performance.tracking", "message_channel_ids")
    util.remove_field(cr, "mail.performance.thread", "message_channel_ids")
