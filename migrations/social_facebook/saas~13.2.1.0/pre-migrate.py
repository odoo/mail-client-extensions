# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "social_stream_post", "facebook_is_event_post", "boolean")
