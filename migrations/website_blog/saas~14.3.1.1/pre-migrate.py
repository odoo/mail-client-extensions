# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_blog.assets_snippet_s_latest_posts_js_000")
    util.remove_view(cr, "website_blog.assets_snippet_s_latest_posts_css_001")
    util.remove_view(cr, "website_blog.assets_snippet_s_latest_posts_css_000")
    util.remove_view(cr, "website_blog.s_latest_posts_options")
    util.remove_view(cr, "website_blog.s_latest_posts_card_template")
    util.remove_view(cr, "website_blog.s_latest_posts_horizontal_template")
    util.remove_view(cr, "website_blog.s_latest_posts_big_picture_template")
    util.remove_view(cr, "website_blog.s_latest_posts_list_template")
    util.remove_view(cr, "website_blog.s_latest_posts")
