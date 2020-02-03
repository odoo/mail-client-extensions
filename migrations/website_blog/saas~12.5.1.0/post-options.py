# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    options = util.ENVIRON["s125_website_blog_options"]

    def active_view(xid, option):
        vid = util.ref(cr, "website_blog." + xid)
        active = options[option] if isinstance(option, str) else option
        cr.execute(
            """
            UPDATE ir_ui_view
               SET active = %s
             WHERE id = %s
        """,
            [active, vid],
        )

    active_view("opt_sidebar_blog_index_follow_us", "followus")
    active_view("opt_sidebar_blog_index_archives", "archives")
    active_view("opt_blog_post_archive_display", "archives")
    active_view("opt_sidebar_blog_index_tags", "tags")
    active_view("opt_blog_post_tags_display", "tags")
    active_view("opt_blog_post_blogs_display", "blogs")

    active_view("opt_posts_loop_show_cover", "cover")
    active_view("opt_posts_loop_show_author", "list_avatar")
    active_view("opt_blog_list_view", "list_view")

    active_view("opt_blog_post_regular_cover", "cover")
    active_view("opt_blog_post_breadcrumb", "breadcrumb")
    active_view("opt_blog_post_select_to_tweet", "tweet")
    active_view("opt_blog_post_comment", "comments")
    active_view("opt_blog_post_select_to_comment", "select_comment")
    active_view("opt_blog_post_read_next", "read_next")

    sidebar = options["tags"] or options["archives"] or options["followus"]
    active_view("opt_blog_sidebar_show", sidebar)
    active_view("opt_blog_post_sidebar", sidebar)
