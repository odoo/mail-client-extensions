# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_forum.post_reply")
    for pre, post in [
        # forum
        ("view_forum_forum_list", "forum_forum_view_tree"),
        ("view_forum_forum_form", "forum_forum_view_form"),
        ("forum_view_search", "forum_forum_view_search"),
        ("action_forum_forum", "forum_forum_action"),
        # post
        ("view_forum_post_form", "forum_post_view_form"),
        ("view_forum_post_search", "forum_post_view_search"),
        ("view_forum_post_graph", "forum_post_view_graph"),
        ("view_forum_post_list", "forum_post_view_tree"),
        ("action_forum_favorites", "forum_post_action_favorites"),
        ("action_forum_post", "forum_post_action"),
        ("action_forum_posts", "forum_post_action_forum_main"),
        # close reason
        ("forum_post_reasons_action", "forum_post_reason_action"),
    ]:
        util.rename_xmlid(cr, f"website_forum.{pre}", f"website_forum.{post}")

    util.rename_field(cr, "website", "forums_count", "forum_count")
