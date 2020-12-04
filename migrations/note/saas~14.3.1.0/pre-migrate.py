# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # removal of channel following feature
    util.remove_field(cr, "note.note", "message_channel_ids")
