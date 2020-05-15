# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, 'forum.forum', 'default_post_type')
    util.remove_field(cr, 'forum.forum', 'allow_question')
    util.remove_field(cr, 'forum.forum', 'allow_discussion')
    util.remove_field(cr, 'forum.forum', 'allow_link')
    util.remove_field(cr, 'forum.post', 'content_link')
    util.remove_field(cr, 'forum.post', 'post_type')
