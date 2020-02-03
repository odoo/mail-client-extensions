# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    def view_active(xid):
        cr.execute(
            """
            SELECT v.active
              FROM ir_model_data d
              JOIN ir_ui_view v ON d.model = 'ir.ui.view' AND d.res_id = v.id
             WHERE d.module = 'website_blog'
               AND d.name = %s
        """,
            [xid],
        )
        return bool(cr.fetchone()[0]) if cr.rowcount else False

    util.ENVIRON["s125_website_blog_options"] = {
        "list_view": not view_active("opt_blog_post_grid_layout"),
        "cover": view_active("opt_blog_post_cover_image"),
        "list_avatar": view_active("opt_blog_post_author_avatar"),
        "breadcrumb": view_active("blog_breadcrumb"),
        "comments": view_active("opt_blog_post_complete_comment"),
        "read_next": view_active("opt_blog_post_complete_read_next"),
        # "post_avatar": view_active("opt_blog_post_author_avatar_display"),
        "tweet": view_active("opt_blog_post_select_to_tweet"),
        "select_comment": view_active("opt_blog_post_select_to_comment"),
        "tags": view_active("opt_blog_rc_tags"),
        "archives": view_active("opt_blog_rc_history"),
        "followus": view_active("opt_blog_rc_follow_us"),
        "blogs": view_active("opt_blog_rc_blogs"),
    }

    views = util.splitlines(
        """
        latest_blogs
        blog_post_short
        blog_cover

        opt_blog_post_cover_image
        opt_blog_post_grid_layout
        opt_blog_post_author_avatar
        blog_breadcrumb
        opt_blog_post_complete_comment
        opt_blog_post_complete_read_next
        opt_blog_post_author_avatar_display

        opt_blog_post_select_to_tweet
        opt_blog_post_select_to_comment

        index
        index_right

        tag_category
        opt_blog_rc_tags
        opt_blog_rc_history
        opt_blog_rc_about_us
        opt_blog_rc_follow_us
        opt_blog_rc_status
        opt_blog_rc_blogs
    """
    )

    for view in views:
        util.remove_view(cr, "website_blog." + view)
