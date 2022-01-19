# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "calendar_event", "access_token", "varchar")
    util.create_column(cr, "calendar_event", "videocall_channel_id", "integer")
