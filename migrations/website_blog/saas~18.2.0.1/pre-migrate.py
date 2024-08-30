from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_blog.opt_blog_post_select_to_comment")
    util.remove_view(cr, "website_blog.opt_blog_post_select_to_tweet")
