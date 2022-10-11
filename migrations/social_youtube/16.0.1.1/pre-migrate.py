# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "social.stream.post", "youtube_video_duration")
    util.create_column(cr, "social_post", "youtube_video_privacy", "varchar", default="public")
