# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # explicitly remove field from `mail.thread` inherit as test modules are ignored during the generation of `inherit.py`.
    models = """
        cc multi.company
        container ticket activity
        track track.selection track.monetary track.compute
        gateway gateway.groups
        simple field.type lang
    """
    for name in models.split():
        util.remove_field(cr, f"mail.test.{name}", "message_unread")
        util.remove_field(cr, f"mail.test.{name}", "message_unread_counter")

    for name in {"thread", "tracking"}:
        util.remove_field(cr, f"mail.performance.{name}", "message_unread")
        util.remove_field(cr, f"mail.performance.{name}", "message_unread_counter")
