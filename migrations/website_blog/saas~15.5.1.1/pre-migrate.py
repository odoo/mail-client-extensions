# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "website_blog.blog_edit_options")
    util.remove_view(cr, "website_blog.user_navbar_inherit_website_blog")
