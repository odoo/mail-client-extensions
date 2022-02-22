# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "social.post.template", "display_twitter_preview", "has_twitter_accounts")
