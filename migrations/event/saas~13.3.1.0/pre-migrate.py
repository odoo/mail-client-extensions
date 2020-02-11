# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "use_hashtag")
    util.remove_field(cr, "event.type", "default_hashtag")
    util.remove_field(cr, "event.event", "twitter_hashtag")
