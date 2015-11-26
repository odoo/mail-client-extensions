# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = util.splitlines("""
        # for csrf
        link_button
        new_link
        new_discussion
        new_question
        edit_post
        close_post
        post_reply
        post_answer
        post_comment
        edit_profile
    """)
    for v in views:
        util.force_noupdate(cr, 'website_forum.' + v, False)
