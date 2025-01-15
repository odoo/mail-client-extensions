from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_blog.opt_blog_post_select_to_comment")
    util.remove_view(cr, "website_blog.opt_blog_post_select_to_tweet")

    util.remove_record(cr, "website_blog.s_blog_posts_000_js")
