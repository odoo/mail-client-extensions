# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    views = util.splitlines("""
        website_blog
        latest_blogs
        blog_post_short
        opt_blog_post_short_tags
        blog_post_complete
        opt_blog_post_complete_comment
        opt_blog_post_complete_tags
        opt_blog_post_select_to_tweet

        index_right
        opt_blog_rc_tags
        opt_blog_rc_history
        opt_blog_rc_about_us
        opt_blog_rc_follow_us
        opt_blog_rc_blogs

        content_new_blogpost
    """)
    for v in views:
        util.force_noupdate(cr, 'website_blog.' + v, False)
